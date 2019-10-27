from .constants import *
from numpy import random
import cmath

class Body:
    def __init__(self, mass, position, velocity, density=Density, color=None, name=None, charge=0):
        self.mass = mass 
        self.mass0 = mass
        self.density = density
        self.radius = int((mass / density) ** (1 / 3)) 
        
        self.color = color if color else tuple(randint(0, 255) for _ in '111')
        self.name = name
        
        self.position = V2(position) 
        self.velocity = V2(velocity)
        self.currentVelocity = V2(velocity)
        self.acceleration = V2(0, 0)
        
        self.charge = random.randint(-self.mass0, self.mass0)
        '''if name == "Star":
            self.charge = self.mass
        else:
            self.charge = 1
        '''
        if self.charge < 0 :
            self.color = (0,0,255)
        elif self.charge == 0:
            self.color = (0,255,0)
        elif self.charge > 0:
            self.color = (255,0,0)
        else:
            self.color = (0,0,0)
        
    def __repr__(self):
        return self.name if self.name else "Unnamed Body"

    def draw_on(self, screen):
        pg.draw.circle(screen, self.color, list(map(int, self.position)), int(self.radius), 0)

    def click_collision(self, mouse_pos):
        return self.position.distance_to(mouse_pos) < self.radius

    def force_of(self, other, G):
        d = other.position - self.position
        r = d.length()
        
        Gravitational = G * other.mass0 / r ** 3 * d  if r else V2(0, 0) #Need if r else V2(0,0) for ALL forces
        Coulombic = K * self.charge * other.charge / r ** 3 * d / self.mass0  if r else V2(0, 0)
        araw = Gravitational + Coulombic
        
        self.currentVelocity = self.velocity
        gammav = 1 / abs( cmath.sqrt( 1 - ( self.currentVelocity.length() / C ) ** 2 ) ) 
        
        aparallele = self.velocity.dot( araw ) / self.velocity.dot( self.velocity ) * self.velocity if self.velocity else V2( 0 , 0 )
        aperpendicular = self.velocity - aparallele
        atotal = gammav ** 3 * aparallele + gammav * aperpendicular # Special Relativistic stuff
        #self.acceleration = atotal
        return atotal
    
    def test_collision(self, other):
        return self.position.distance_to(other.position) < self.radius + other.radius  # Zero-tolerance collision

    def merge(self, other, prop_wins):  # Special case: perfectly inelastic collision results in merging of the two bodies
        m = self.mass0 
        mp = self.mass
        m2 = other.mass0
        mp2 = other.mass 
        v = self.velocity 
        v2 = other.velocity 
        x = self.position
        x2 = other.position 
        c1 = self.charge
        c2 = other.charge
        
        
        M = m + m2
        Mp = mp + mp2
        
        self.position = (x * mp + x2 * mp2) / Mp
        self.velocity = (v * mp + v2 * mp2) / Mp
        self.currentVelocity = ( self.velocity * m + other.velocity * m2 ) / M / abs( cmath.sqrt( 1 - self.velocity * other.velocity / C ** 2 ) )
        self.mass0 = M
        self.mass = M / abs( cmath.sqrt( 1 - ( self.currentVelocity.length() / C ) ** 2 ) )
        self.radius = int( ( self.mass0 ** 2 / ( self.density * m + other.density * m2 ) ) ** (1 / 3) )
        self.color = tuple( ( ( self.color[x] * mp + other.color[x] * mp2 ) / Mp ) for x in (0, 1, 2) )
        
        self.density = self.mass0 / self.radius ** 3
        
        self.charge = (c1+c2)
        
        # Check to see if the deleted body belongs to a properties window; If so, set win.body to the combined body
        for win in prop_wins:
            if win.body is self:
                win.merge()
            elif win.body is other:
                win.body = self
                win.merge()

    def collide(self, other, COR, prop_wins):
        m, m2, v, v2, x, x2 = self.mass, other.mass, self.velocity, other.velocity, self.position, other.position;
        M = m + m2
        # Explanation can be found at http://ericleong.me/research/circle-circle/
        if (x2 - x).length() == 0: return #self.merge(other, prop_wins)  # Ignore bodies in the exact same position
        n = (x2 - x).normalize()
        p = 2 * (v.dot(n) - v2.dot(n)) / M
        # TODO: properly incorporate COR.  This is currently incorrect, and is only a proof of concept
        #self.velocity, other.velocity = v - (p * m2 * n) * COR, v2 + (p * m * n) * COR
        self.velocity, other.velocity = (v - (p * m2 * n)) * COR, (v2 + (p * m * n)) * COR
        # Set position of bodies to outer boundary to prevent bodies from getting stuck together
        # this method of splitting the offset evenly works, but is imprecise.  It should be based off of velocity.
        offset = (self.radius + other.radius - (x2 - x).length()) * n
        self.position -= offset / 2
        other.position += offset / 2

    def update_radius(self):
        self.radius = (self.mass / self.density) ** (1 / 3)

    def apply_motion(self, time_factor):
        self.currentVelocity = self.velocity
        
        gammav = 1 / abs( cmath.sqrt( 1 - ( self.currentVelocity.length() / C )**2 ) )
        
        self.velocity += self.acceleration * time_factor / abs( cmath.sqrt( 1 + ( self.acceleration.length() * time_factor / C ) ** 2 ) ) if self.acceleration else V2(0,0)
        
        self.velocity = self.velocity / abs( cmath.sqrt( 1 - ( self.velocity.length() / C )**2 ) )
        
        self.position += self.velocity * time_factor / abs( cmath.sqrt( 1 - ( self.velocity.length() / C )**2 ) )
        
        self.mass = self.mass0 / abs( cmath.sqrt( 1 - ( self.velocity.length() / C ) ** 2 ) )
        
        self.update_radius()
        
        if self.name == "Star":
            #print(self.velocity, self.acceleration, self.mass, self.mass0, self.radius)
            print(self.velocity.length(), self.mass, self.radius)


def generate_bodies(body_args_list):
    return list(map(lambda args2: Body(*args2), body_args_list))
