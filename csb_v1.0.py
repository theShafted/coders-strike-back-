import sys
import math

# returns the distance between two points 
def distance(a, b):
    return math.sqrt((b[1]-a[1])**2 + (b[0]-a[0])**2)
 
# returns whether to use the boost or not
def boost(checkpoint, checkpoints, angle):
    dist = 0
    index = 0
    for i in range(len(checkpoints)):
        try:
            if distance(checkpoints[i+1], checkpoints[i]) > dist:
                dist = distance(checkpoints[i+1], checkpoints[i])
                index = i + 1
        except IndexError:
            if distance(checkpoints[-1], checkpoints[0]) > dist:
                index = -1
    if checkpoint == checkpoints[index] and angle <= 5:
        return True
    else:
        return False
 
# computes the thrust for the pod
def thrust(checkpoints, angle, cid, x, y, thrust, ptype):
    if ptype == "racer":     
        if angle < 90:
            if boost(checkpoints[cid], checkpoints, angle) and thrust != "SHIELD":
                return "BOOST"
            else:
                return 100
        elif angle >= 90:
            allign = max(min((1 - angle/90), 1), 0)
            proximity = max(min(distance(checkpoints[cid], [x, y])/1000, 1), 0)
            return 100 * math.floor(allign * proximity)
    elif ptype == "pseudoracer":
        if angle >= 90:
            allign = max(min((1 - angle/90), 1), 0)
            proximity = max(min(distance(checkpoints[cid], [x, y])/1000, 1), 0)
            if distance(checkpoints[cid], [x, y]) <= 1000:    
                return 100 * math.floor(allign * proximity)
            else:
                return 100 * math.floor(allign)
        elif distance(checkpoints[cid], [x, y]) <= 400:
            return "SHIELD"
        else:
            return 100
    else:
        chaser = cid
        if distance([chaser.x, chaser.y], [x, y]) <= 900:
            return "SHIELD"
        elif distance([chaser.x, chaser.y], [x, y]) > 900 and angle > 180:
            allign = max(min((1 - angle/90), 1), 0.5)
            proximity = max(min(distance([chaser.x, chaser.y], [x, y])/800, 1), 0.5)
            return 100 * math.floor(allign * proximity)
        else:
            return "BOOST"
        
# Pod class to store all of a pods data
class Pod():
    def __init__(self, x, y, vx, vy, angle, checkid):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = angle
        self.checkid = checkid
        self.relative = None
        self.targets = None
        self.thrust = 100
        self.type = None
        self.lap = 0
        self.chaser = None
 
    # returns the relative angle between a pod and the next checkpoint: (0, 180)
    def relativeangle(self, checkpoint):
        d = distance([self.x, self.y], list(checkpoint))
        cosine = (180/math.pi) * math.acos((self.x - checkpoint[0])/d)
        result = math.floor(cosine - abs(180 -self.angle))
        self.relative = abs(result)
 
    # returns a target for the pod to move towards
    def target(self, checkpoints):
        targetx = checkpoints[self.checkid][0] - 2.5 * self.vx
        targety = checkpoints[self.checkid][1] - 2.5 * self.vy
 
        if distance(checkpoints[self.checkid], [self.x, self.y]) <= 1000:
            try:    
                targetx = checkpoints[self.checkid+1][0] - 5 * self.vx
                targety = checkpoints[self.checkid+1][1] - 5 * self.vy
            except IndexError:
                targetx = checkpoints[0][0] - 2.5 * self.vx
                targety = checkpoints[0][1] - 2.5 * self.vy
        self.targets = [math.floor(targetx), math.floor(targety)]
 
    # returns whether to use a SHIELD or not
    def shield(self):
        self.thrust = "SHIELD"
 
    # returns which of the opponents pods the user chaser pod should intercept
    def chase(self, opponents, checkpoints):
        chaser = opponents[0]
        if opponents[0].lap > opponents[1].lap:
            return opponents[0]
        elif opponents[0].lap < opponents[1].lap:
            return opponents[1]
        else:
            if opponents[0].checkid == 0:
                return opponents[0]
            elif opponents[1].checkid == 0:
                return opponents[1]
            elif opponents[0].checkid > opponents[1].checkid:
                return opponents[0]
            elif opponents[0].checkid > opponents[1].checkid:
                return opponents[1]
            else:
                for oppo in opponents.values():
                    d = 100000000
                    if distance([oppo.x, oppo.y], checkpoints[oppo.checkid]) < d:
                        d = distance([oppo.x, oppo.y], checkpoints[oppo.checkid])
                        chaser = oppo
        return chaser
 
    # returns the number of laps elapsed for a pod
    def calclap(self, lapped):
        fin = lapped
        if self.checkid == 1 and not fin:
            fin = True
            return [1, fin]
        elif self.checkid > 2:
            fin = False
        return [0, fin]

checkpoints = []
laps = int(input())
checkpoint_count = int(input())
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    checkpoints.append((checkpoint_x, checkpoint_y))
pods = {}
opponents = {}
laps = [0, 0]
lapped = [False, False]

while True:
    for i in range(2):
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        pods[i] = Pod(x=x, y=y, vx=vx, vy=vy, angle=angle, checkid=next_check_point_id)

    for i in range(2):
        x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2 = [int(j) for j in input().split()]
        opponents[i] = Pod(x=x_2, y=y_2, vx=vx_2, vy=vy_2, angle=angle_2, checkid=next_check_point_id_2)
        
        # updates the opponents pods laps
        opponents[i].lap = laps[i]

    # determines which pod is the racer
    pods[0].type = "racer"
    pods[1].type = "interceptor"
 
    for i in opponents:

        # updates the opponents laps for each pod
        laps[i] += opponents[i].calclap(lapped[i])[0]
        lapped[i] = opponents[i].calclap(lapped[i])[1]
 
    for pod in pods.values():
        pod.relativeangle(checkpoints[pod.checkid])
        pod.target(checkpoints)
        if pod.type == "racer":
            pod.thrust = thrust(checkpoints, pod.relative, pod.checkid, pod.x, pod.y, pod.thrust, pod.type)
            print(f"{pod.targets[0]} {pod.targets[1]} {pod.thrust}")
        elif pod.type == "interceptor":

            # for the interceptor pod, returns the target as either a checkpoint or a enemy pod
            pod.chaser = pod.chase(opponents, checkpoints)
            pod.relativeangle([pod.chaser.x, pod.chaser.y])
            pod.thrust = thrust(checkpoints, pod.relative, pod.chaser, pod.x, pod.y, pod.thrust, pod.type)
            denemy = distance([pod.x, pod.y], [pod.chaser.x, pod.chaser.y])
            dcheck = distance([pod.x, pod.y], checkpoints[pod.chaser.checkid])
            if dcheck > denemy:
                print(f"{pod.chaser.x} {pod.chaser.y} {pod.thrust}")
            else:

                # to move the pod move towards the opponents checkpoint and wait
                pod.targetx = checkpoints[pod.chaser.checkid][0]
                pod.targety = checkpoints[pod.chaser.checkid][1]
                pod.relativeangle(checkpoints[pod.chaser.checkid])
                pod.thrust = thrust(checkpoints, pod.relative, pod.chaser.checkid, pod.x, pod.y, pod.thrust, "pseudoracer")
                print(f"{pod.targetx} {pod.targety} {pod.thrust}")
