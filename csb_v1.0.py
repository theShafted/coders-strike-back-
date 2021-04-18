# Edit from repo 1 2
import sys
import math
 
# Outputs the relative angle between a pod and a specified target: (-180, 180)
def getAngle(pod, target):
    rangle = math.radians(pod.angle)
    dvector = Vector(math.cos(rangle), math.sin(rangle))
    pvector = target.sub(pod.position)
    cangle = dvector.dot(pvector)/pvector.mag(False)
    direction = dvector.cross(pvector)
    result = round(math.degrees(math.acos(cangle)))
    return result if direction >= 0 else -result
 
# Simulates a turn for a given pod
def simulate(pod):
    sid = pod.id
    checkpoint = pod.path[sid]
    angle = math.radians(pod.angle)
    dvector = Vector(math.cos(angle), math.sin(angle))
    thrust = dvector.mul(650) if pod.thrust() == "BOOST" else dvector.mul(pod.thrust())
    offset = pod.velocity.add(thrust).mul(2.3)
    if pod.position.sub(pod.velocity.add(thrust)).sub(checkpoint).mag() < 10**6:
        try:
            checkpoint = pod.path[sid+1]
        except IndexError:
            checkpoint = pod.path[0]
        
        if abs(getAngle(pod, checkpoint)) >= 90:
            offset = pod.velocity.add(thrust).mul(5)
        else:
            offset = pod.velocity.mul(5)
    
    pcdist = pod.position.sub(pod.path[sid-1]).mag()
    ccdist = pod.position.sub(pod.path[sid]).mag()
    if (pcdist < 10**6 and thrust.mag() < 1600) or (ccdist < 10**6):
        if abs(getAngle(pod, checkpoint)) >= 90:
            offset = pod.velocity.add(thrust).mul(12)
        else:
            offset = pod.path[pod.id].sub(checkpoint).mul(0.5)
 
    target = checkpoint.sub(offset)
    angle = getAngle(pod, target)
    rotation = angle if abs(angle) <= 18 else 18*angle/abs(angle) 
    dangle = (pod.angle + rotation)%360
    
    path = Path()
    path.path = pod.path
    spod = Pod(pod.position.get(), pod.velocity.get(), angle, sid, path)
    
    dvector = Vector(math.cos(math.radians(dangle)),math.sin(math.radians(dangle)))
    try:
        avector = dvector.mul(spod.thrust())
    except TypeError:
        avector = dvector.mul(650) if pod.thrust() == "BOOST" else Vector(0,0)
    vvector = Vector(*list(map(round, pod.velocity.add(avector).get())))
    pvector = Vector(*list(map(round, pod.position.add(vvector).get())))
 
    if pvector.sub(checkpoint).mag() < 360000:
        try:
            sid += 1
            checkpoint = spod.path[sid]
        except IndexError:
            sid = 0
 
    return Pod(pvector.get(), vvector.get(), dangle, sid, path), avector
 
# Vector class to compute math operations
class Vector():
    def __init__(self, x, y):
        self.x = x
        self.y = y
 
    # returns a list of the x-y components of the vector
    def get(self):
        return [self.x, self.y]
 
    # returns the resultant vector of the vector addition of two vectors
    def add(self, vector):
        return Vector(*[i+j for i, j in zip(self.get(), vector.get())])
 
    # returns the resultant vector of the vector subtraction of two vectors
    def sub(self, vector):
        return Vector(*[i-j for i, j in zip(self.get(), vector.get())])
 
    # returns the dot product of two vectors
    def dot(self, vector):
        return sum(i*j for i, j in zip(self.get(), vector.get()))
 
    # returns the cross product of two vectors
    def cross(self, vector):
        return self.x*vector.y - vector.x*self.y
 
    # returns the scalar multiple the vector
    def mul(self, scalar):
        return Vector(round(self.x*scalar), round(self.y*scalar))
 
    # returns the magnitude of the vector
    def mag(self, sq=True):
        magnitude = self.x**2 + self.y**2
        return magnitude if sq else math.sqrt(magnitude)
 
# Path class to store all the checkpoints data
class Path():
    def __init__(self):
        self.path = []
 
    # pushes a new checkpoint to the list
    def push(self, node):
        self.path.append(Vector(*node))
 
    # returns a list of all checkpoints
    def get(self):
        return self.path
 
# Pod class to store all data on each pod
class Pod():
    def __init__(self, position, velocity, angle, checkid, path):
        self.position = Vector(*position)
        self.velocity = Vector(*velocity)
        self.angle = angle
        self.id = checkid
        self.path = path.get()
 
        self.acc = 0
        self.nboosted = True
        self.shieldcd = 0
        self.checks = 0
        self.type = None
 
    # returns a target vector for the pod
    def target(self):
        checkpoint = self.path[self.id]
        spod, thrust = simulate(self)
        offset = self.velocity.add(thrust).mul(2.3)
 
        if spod.position.add(offset).sub(checkpoint).mag() < 10**6:
            try:
                checkpoint = self.path[self.id+1]
            except IndexError:
                checkpoint = self.path[0]
            
            if abs(getAngle(spod, checkpoint)) >= 90:
                offset = spod.velocity.add(thrust).mul(5)
            else:
                offset = spod.velocity.mul(5)
 
        pcdist = spod.position.sub(spod.path[spod.id-1]).mag()
        ccdist = spod.position.sub(spod.path[spod.id]).mag()
        if (pcdist < 10**6 and thrust.mag() < 1600) or (ccdist < 10**6):
            spod, thrust = simulate(spod)
            
            if abs(getAngle(spod, checkpoint)) >= 90:
                offset = spod.velocity.add(thrust).mul(12)
            else:
                offset = self.path[self.id].sub(spod.position).mul(0.5)
        
        return checkpoint.sub(offset)
 
    # returns whether the pod is to be boosted or not
    def getboost(self):
        dmax = 0
        index = 0
        nboost = self.nboosted
        target = self.path[self.id]
        for i in range(len(self.path)):
            try:
                if self.path[i].sub(self.path[i+1]).mag() >= dmax:
                    dmax = self.path[i].sub(self.path[i+1]).mag()
                    index = i+1
            except IndexError:
                if self.path[i].sub(self.path[0]).mag() >= dmax:
                    dmax = self.path[i].sub(self.path[0]).mag()
                    index = 0
                    
        if self.shieldcd == 0 and self.id == index and nboost and abs(getAngle(self, target)) <= 3:
            return True
        else:
            return False
 
    # returns a thrust value for the pod 
    def thrust(self, epods=None):
        maxthrust = 100
        thrust = 100
        target = self.path[self.id]
        if self.type != "racer" and epods != None:
            target = epods[0] if epods[0].checks >= epods[1].checks else epods[1]
            target = target.target()
        proximity = min(1, target.sub(self.position).mag()/4000000)
        allignment = min(1, max(0, 1 - abs(getAngle(self, target)/90)))
        
        if abs(getAngle(self, target)) <= 10:
            thrust = math.floor(maxthrust * max(0.4, proximity))
        else:
            thrust =  math.floor(maxthrust*proximity*allignment)
 
        return "BOOST" if self.getboost() else thrust
 
    # returns whether the pod is to be shielded or not
    def getshield(self, epods):
        for pod in epods.values():
            uposition = self.position.add(self.velocity.mul(2))
            eposition = pod.position.add(pod.velocity.mul(2))
 
            tvector = self.path[self.id].sub(self.position)
            pvector = pod.position.sub(self.position)
            angle = tvector.dot(pvector)/(tvector.mag(sq=False)*pvector.mag(sq=False))
            dist = uposition.sub(eposition).mag()
 
            if dist <= 640000 and angle <= 90:
                self.shieldcd = 4
                return True
            else:
                return False
 
    def intercept(self, epods):
        target = epods[0] if epods[0].checks >= epods[1].checks else epods[1]
        target, thrust = simulate(target)
 
        tdist = target.position.sub(self.position).mag()
        cdist = self.position.sub(target.path[target.id]).mag()
 
        if tdist < cdist:
            return target.position
        else:
            return target.path[target.id]
 
path = Path()
upods = {}
epods = {}
 
nboosted = [True, True]
cooldown = [0, 0]
checks = [0, 0, 0, 0]
 
laps = int(input())
checkpoint_count = int(input())
 
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    path.push([checkpoint_x, checkpoint_y])
 
# game loop
while True:
    for i in range(2):
        x, y, vx, vy, angle, check_point_id = [int(j) for j in input().split()]
        try:
            checks[i] += 1 if upods[i].id != check_point_id else 0
        except KeyError:
            checks[i] = 0
 
        upods[i] = Pod([x,y], [vx,vy], angle, check_point_id, path)
        upods[i].nboosted = nboosted[i]
        upods[i].shieldcd = max(cooldown[i]-1, 0)
        upods[i].checks = checks[i]
 
    for i in range(2):
        x_2, y_2, vx_2, vy_2, angle_2, check_point_id_2 = [int(j) for j in input().split()]
        try:
            checks[i+2] += 1 if epods[i].id != check_point_id_2 else 0
        except KeyError:
            checks[i+2] = 0
 
        epods[i] = Pod([x_2, y_2], [vx_2, vy_2], angle_2, check_point_id_2, path)
        epods[i].checks = checks[i+2]
    # To debug: print("Debug messages...", file=sys.stderr)
    if upods[0].checks > upods[1].checks:
        upods[0].type = "racer"
        upods[1].type = "interceptor"
    else:
        upods[1].type = "racer"
        upods[0].type = "interceptor"
 
    i = 0
    for pod in upods.values():
        if pod.type == "racer":
            pod.acc = "SHIELD" if pod.getshield(epods) else pod.thrust(epods)
            print(pod.target().x, pod.target().y, pod.acc)
        else:
            pod.acc = pod.thrust(epods)
            print(pod.intercept(epods).x, pod.intercept(epods).y, pod.acc)
 
        nboosted[i] = False if pod.thrust() == "BOOST" else nboosted[i]
        cooldown[i] = pod.shieldcd
        i += 1
