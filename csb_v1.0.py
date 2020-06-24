import sys
import math
 
# Vector Class to handle all vectorial operations
class Vector():
 
    # Initialize a vector with its x-y coordinates in the game world
    def __init__(self, x, y):
        self.x = x
        self.y = y
 
    def vector(self):
        return (self.x, self.y)
 
    # Outputs the magnitude of the vector or the distance between two vectors
    def mag(self, vector=None, sq=True):
        vector = Vector(0, 0) if vector == None else vector
        result = sum((i - j)**2 for i, j in zip(self.vector(), vector.vector()))
        return result if sq else math.sqrt(result) 
    
    # Outputs the resultant vector of the vector addition of two vectors
    def add(self, vector):
        return Vector(*[math.floor(i+j) for i, j in zip(self.vector(), vector.vector())])
 
    # Outputs the resultant vector of the vector subtraction of two vectors
    def sub(self, vector):
        return Vector(*[i-j for i, j in zip(vector.vector(), self.vector())])
 
    def mul(self, scalar):
        return Vector(int(self.x*scalar), self.y*scalar)
    
    # Outputs the dot product of two vectors
    def dot(self, vector):
        return sum(i*j for i, j in zip(self.vector(), vector.vector()))
 
    # Outputs the cross product of two vectors
    def cros(self, vector):
        return self.x*vector.y - self.y*vector.x
 
# Path class to track the position of each checkpoint
class Path():
 
    # Initialize a list to store all checkpoints
    def __init__(self):
        self.path = []
    
    # Add a new checkpoint to the list
    def push(self, node):
        self.path.append(node)
 
    # Outputs the current list of stored checkpoints
    def get(self):
        return self.path
 
# Pod class to handle all the player behaviours
class Pod():
 
    # Initialize all information on the current state of the pod
    def __init__(self, position, velocity, angle, id, path, cooldown=0, boosted=None, check=0):
        self.position = Vector(*position)
        self.velocity = Vector(*velocity)
        self.angle = angle
        self.id = id
        self.path = path.get()
        self.boosted = boosted
 
        # States whether the pod is in an inoperable state
        self.inoperable = False
        self.checks = check
        self.cooldown = cooldown
 
    # returns the relative angle between the pod and a target: (-180, 180)
    def rangle(self, target=None, sign=False):
        target = self.path[self.id] if target == None else target
        radangle = math.radians(self.angle)
        uvector = Vector(math.cos(radangle), math.sin(radangle))
        pvector = self.position.sub(target)
        cosine = uvector.dot(pvector)/pvector.mag(sq=False)
        direction = uvector.cros(pvector)
        result = math.degrees(math.acos(cosine))
        result = result if not sign else result/abs(result)
        
        return result if direction >= 0 else -result
 
    # computes and returns the thrust value for the pod
    def thrust(self, epods, inoperable=None):
        thrust = 100
        bindex = None
        dmax = 0
        boost = False
        inoperable = self.inoperable if inoperable == None else inoperable
 
        # update the pod's checkpoint if its in close range with the curent target
        for i in range(len(self.path)):
            try:
                if self.path[i].mag(self.path[i+1]) >= dmax:
                    dmax = self.path[i].mag(self.path[i+1])
                    bindex = i+1
            except IndexError:
                if self.path[i].mag(self.path[0]) >= dmax:
                    bindex = 0
        
        # boost the pod if the conditions are met and it hasn't been boosted prior
        if not self.boosted and self.id == bindex and abs(self.rangle()) <= 3 and self.cooldown == 0:
            boost = True
            thrust = "BOOST"
        else:
            boost = False
 
        # variate the thrust value in accordance with its angle and proximity in relation with its target
        if abs(self.rangle()) <= 90:
            allign = max(min((1 - abs(self.rangle())/90), 1), 0)
            proximity = max(min(self.path[self.id].mag(self.position)/1440000, 1), 0)
            thrust = math.floor(100 * allign * proximity)
        else:
            thrust = 0
 
        thrust = 100 if inoperable else thrust
 
        # simluate a turn to know the pods information a turn in advance to take the appropriate action
        for pod in epods.values():
            uangle = self.rangle() if self.rangle() < 18 else 18*self.rangle(sign=True)
            udangle = math.radians(self.angle + uangle)
            udvector = Vector(math.cos(udangle), math.sin(udangle))
            try:
                uavector = udvector.mul(thrust)
            except TypeError:
                uavector = udvector.mul(650) if thrust == "BOOST" else udvector.mul(0)
            uvvector = self.velocity.mul(0.85).add(uavector)
            upvector = self.position.add(uvvector)
 
            eangle = pod.rangle() if pod.rangle() < 18 else 18*pod.rangle(sign=True)
            edangle = math.radians(pod.angle + eangle)
            edvector = Vector(math.cos(edangle), math.sin(edangle))
            eavector = edvector.mul(100) if thrust != "BOOST" else edvector.mul(650)
            evvector = pod.velocity.mul(0.85).add(eavector)
            epvector = pod.position.add(evvector)
 
            angle = self.rangle(target=pod.position) - self.rangle()
 
            # shield the pod if it collides with enemy pod and its trajectory is hindered
            if upvector.mag(vector=epvector) <= 640000 and abs(angle) <= 90:
                self.cooldown = 4
                thrust = "SHIELD"
 
        return "BOOST" if boost else thrust
 
    # computes and returns the target value for the pod to move towards
    def target(self, epods):

        # simulate a turn to take appropriate action for the pod in advance
        checkpoint = self.path[self.id]
        offset = self.velocity.mul(3)   
        angle = self.rangle(target=checkpoint) if self.rangle(target=checkpoint) < 18 else 18*self.rangle(target=checkpoint, sign=True)
        dangle = math.radians(self.angle + angle)
        dvector = Vector(math.cos(dangle), math.sin(dangle))
        try:
            avector = dvector.mul(self.thrust(epods))
        except TypeError:
            avector = dvector.mul(650) if self.thrust(epods) == "BOOST" else dvector.mul(0)
        vvector = self.velocity.mul(0.85).add(avector)
        pvector = self.position.add(vvector)
        
        if checkpoint.mag(vector=pvector) <= 4*10**6:
            try:
                checkpoint = self.path[self.id+1]
            except IndexError:
                checkpoint = self.path[0]    
 
            angle = self.rangle(target=checkpoint) if self.rangle(target=checkpoint) < 18 else 18*self.rangle(target=checkpoint, sign=True)
            dangle = math.radians(self.angle + angle)
            dvector = Vector(math.cos(dangle), math.sin(dangle))
            try:
                avector = dvector.mul(self.thrust(epods))
            except TypeError:
                avector = dvector.mul(650) if self.thrust(epods) == "BOOST" else dvector.mul(0)
            vvector = self.velocity.mul(0.85).add(avector)
            pvector = self.position.add(vvector)
            offset = vvector.mul(3)
 
            # revert the checkpoint to previous one if pod becomes immovable
            if pvector.add(vvector.mul(2)).mag(vector=self.path[self.id]) > 3600:
                checkpoint = self.path[self.id]
                if self.thrust(epods) == 0:
                    self.inoperable = True
            
        # return a value with a calculated offset with respect to the current checkpoint.
        return offset.sub(checkpoint)
 
path = Path()
upods = {}
epods = {}
 
boosted = [False, False]
checks = [0, 0, 0, 0]
cooldown = [0, 0]
inoperables = [False, False]
 
laps = int(input())
checkpoint_count = int(input())
 
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    path.push(node=Vector(checkpoint_x, checkpoint_y))
 
# game loop
while True:
    for i in range(2):
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        
        try:
            if upods[i].id != next_check_point_id:
                upods[i].inoperable = False
                checks[i] += 1 
            boosted[i] = upods[i].boosted
            cooldown[i] = max(upods[i].cooldown - 1, 0)
            inoperables[i] = upods[i].inoperable
        except KeyError:
            checks[i] = 0
            boosted[i] = False
            cooldown[i] = 0
            inoperables[i] = False
 
        upods[i] = Pod(position=(x, y), velocity=(vx, vy), angle=angle, id=next_check_point_id, path=path, cooldown=cooldown[i], boosted=boosted[i], check=checks[i])
        upods[i].inoperable = inoperables[i]
    for i in range(2):
        x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2 = [int(j) for j in input().split()]
        try:
            checks[i+2] += 1 if epods[i].id != next_check_point_id_2 else 0
        except KeyError:
            checks[i+2] = 0
 
        epods[i] = Pod(position=(x_2, y_2), velocity=(vx_2, vy_2), angle=angle_2, id=next_check_point_id_2, path=path, check=checks[i+2])
 
    for pod in upods.values():
        print(f"{pod.target(epods).x} {pod.target(epods).y} {pod.thrust(epods)}")
