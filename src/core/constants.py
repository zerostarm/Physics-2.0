from random import randint, uniform
from pygame.math import Vector2 as V2
from math import hypot, pi, sin, cos, sqrt

G = .5

K = 10 #this is anoyingly correct - 9*10**9

C = 100

Density = 0.1

COR = 1.0  # Coefficient of Restitution

# Set simulation hard clock speed (fps)
clock_speed = 120