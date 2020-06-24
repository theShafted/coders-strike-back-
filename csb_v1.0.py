import sys
import math
 
# Outputs the distance between two points
def distance(a, b):
    return math.sqrt(sum((i - j)**2 for i, j in zip(a, b)))
 
# Outputs the dot product of two vectors
def dot(a, b):
    return sum(i*j for i, j in zip(a, b))
 
# Pod class to store information on each pod
class Pod():
    def __init__(self, position, velocity, angle, targetid, path, boosted):
        self.position = position
        self.velocity = velocity
        self.angle = angle
        self.targetid = targetid
        self.path = path.get()
        self.stuck = False
        self.boosted = boosted
 
    # Outputs a target vector for the pod
    def target(self):
        checkpoint = self.path[self.targetid]
        offset = (0, 0)
        if distance(self.path[self.targetid], self.position) <= 3000:
            try:
                checkpoint = self.path[self.targetid+1]
            except IndexError:
                checkpoint = self.path[0]
 
            t = [a-b for a, b in zip(self.path[self.targetid], self.position)]
            try:
                angle = (self.angler(self.path[self.targetid])%54)*(t[1]+t[0])/abs(t[0]+t[1])
            except ZeroDivisionError:
                angle = 0
            velocity = [math.cos(math.radians(angle))*300, math.sin(math.radians(angle))*300]
            position = [a+3*b for a, b in zip(self.position, velocity)]
            dist = distance(position, self.path[self.targetid])
            angle = self.angler(self.path[self.targetid])
            if dist > 600 and (angle >= 90 or angle <= 270):
                checkpoint = self.path[self.targetid]
            offset = self.velocity
        result = [a-b-2*c for a, b, c in zip(checkpoint, self.velocity, offset)]
        return result
 
    # Calculate the relative angle between a target and the pods' direction
    def angler(self, target=None):
        if target == None:
            target = self.target()
        angle = math.radians(self.angle)
        uvec = (math.cos(angle), math.sin(angle))
        pvec = [a-b for a, b in zip(target, self.position)]
        dist = distance(self.position, target)
        cosine = (uvec[0] * pvec[0] + uvec[1] * pvec[1]) / dist
        return abs(math.floor(math.degrees(math.acos(cosine))))
 
    # Outputs different values of thrust according to specific conditions
    def thrust(self, epods, stuck=False):
        dmax = 0
        index = 0
        thrust = 100
        boost = False
        for i in range(len(self.path)):
            try:
                if distance(self.path[i], self.path[i+1]) >= dmax:
                    dmax = distance(self.path[i], self.path[i+1])
                    index = i+1
            except IndexError:
                if distance(self.path[i], self.path[0]) >= dmax:
                    dmax = distance(self.path[i], self.path[0])
                    index = 0
 
        if not self.boosted and self.targetid == index and self.angler() <= 3:
            boost = True
            self.boosted = True
        else:
            boost = False
 
        if self.angler() <= 90 or self.angler() >= 270:
            allign = max(min((1 - self.angler()/90), 1), 0)
            proximity = max(min(distance(self.path[self.targetid], self.position)/100, 1), 0)
            thrust = math.floor(100 * allign * proximity)
        else:
            thrust = 0
 
        thrust = 100 if stuck else thrust
        
        for pod in epods.values():
            eposition = [a+b for a, b in zip(pod.position, pod.velocity)]
            uposition = [a+b for a, b in zip(self.position, self.velocity)]
            
            angle = self.angler(pod.position) - self.angler()
 
            if distance(uposition, eposition) <= 800 and (angle<90 or angle>270):
                boost = False
                thrust = "SHIELD"
 
        return ["BOOST", self.boosted] if boost else [thrust, self.boosted]
 
# Path class to track the position of each checkpoint
class Path():
    def __init__(self):
        self.path = []
    
    def push(self, node):
        self.path.append(node)
 
    def get(self):
        return self.path
 
 
path = Path()
upods = {}
epods = {}
boosted = [False, False]
laps = int(input())
checkpoint_count = int(input())
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    path.push(node=(checkpoint_x, checkpoint_y))
 
# game loop
while True:
    for i in range(2):
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        upods[i] = Pod(position=(x, y), velocity=(vx, vy), angle=angle, targetid=next_check_point_id, path=path, boosted=boosted[i])
        
    for i in range(2):
        x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2 = [int(j) for j in input().split()]
        epods[i] = Pod(position=(x_2, y_2), velocity=(vx_2, vy_2), angle=angle_2, targetid=next_check_point_id_2, path=path, boosted=0)

    i=0
    for pod in upods.values(): 
        print(f"{pod.target()[0]} {pod.target()[1]} {pod.thrust(epods)[0]}")
        boosted[i] = pod.thrust(epods)[1]
        i += 1