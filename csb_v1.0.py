import sys
import math

# Class to manage all checkpoints to know when to BOOST
class CheckPointManager():
    def __init__(self):
        self.checkpoint = 0
        self.checkpoints = []
        self.lap = 1
 
    # returns the distance between two points
    def distance(self, a, b):
        return pow(pow((a[0] - b[0]), 2) + pow((a[1] - b[1]), 2), 0.5)
 
    # returns the maximum distance between two checkpoints and index of the first one
    def maximum(self):
        dist = 0
        index = 0
        for i in range(len(self.checkpoints) - 1):
            try:
                if self.distance(self.checkpoints[i], self.checkpoints[i+1]) > dist:
                    dist = self.distance(self.checkpoints[i], self.checkpoints[i+1])
                    index = i
            except IndexError:
                if self.distance(self.checkpoints[0], self.checkpoints[i]) > dist:
                    dist = self.distance(self.checkpoints[0], self.checkpoints[i])
                    index = 0
        return index
 
    # returns whether to use the boost or not depending on the current position of the pod
    def boost(self, x, y):
        self.checkpoint = (x, y)
        if self.checkpoint not in self.checkpoints:
            self.checkpoints.append(self.checkpoint)
        elif self.checkpoint == self.checkpoints[0] and len(self.checkpoints) > 1:
            self.lap += 1
        
        if self.lap >= 2:
            index = self.maximum()
            if self.checkpoints[index + 1] == self.checkpoint:
                return True
            else:
                False
 
manager = CheckPointManager()
thrust = 100
posx, posy = 0, 0

while True:
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]
 
    if next_checkpoint_angle > 90 or next_checkpoint_angle < -90:
        if thrust == "BOOST":
            thrust = 100
        thrust = math.floor(thrust * max(min(1 - abs(next_checkpoint_angle)/90, 1), 0) * max(min(next_checkpoint_dist/1200, 1), 0))
    else:
        thrust = 100
    
    # use the boost only when the next checkpoint angle is less than 3 degrees
    if (abs(next_checkpoint_angle) < 3) and manager.boost(next_checkpoint_x, next_checkpoint_y):
        thrust = "BOOST"
 
    print(f"{next_checkpoint_x - 3 *(x-posx)} {next_checkpoint_y - 3*(y-posy)} {thrust}")
    
    # offset to claculate speed of the pod and improvise checkpoint tracking
    posx, posy = x, y