from random import randint, uniform
from pygame.math import Vector2 as V2
from math import hypot, pi, sin, cos, sqrt

G = .00001

K = 1 #this is anoyingly correct - 9*10**9

C = 500

mergePercent = .9

alphaDistancePercent = 3/2

decayConstantN = 0
decayConstant = 9 #the actual likely hood is (decayConstantN + 1) / (decayConstant + 1)

Density = 0.1

COR = 1.0  # Coefficient of Restitution

# Set simulation hard clock speed (fps)
clock_speed = 120