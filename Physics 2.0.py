from functools import reduce
from operator import add
from pygame.math import Vector2 as V2
import pygame as pg, os

from src.display.tkinter_windows import create_menu
from src.core import *
from numpy.matlib import rand
import numpy as np
import random



def init_display():
    pg.init()
    info = pg.display.Info()
    dims = (int(info.current_w * 0.6), int(info.current_h * 0.75))
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.display.set_icon(pg.image.load('AtomIcon.png'))
    screen = pg.display.set_mode(dims, pg.RESIZABLE)
    pg.display.set_caption("Physics Simulator 2.0")
    return screen, V2(dims)


def refresh_display(settings_window, screen, bodies, cam):
    screen.fill(settings_window.bg_color)  # comment out this line for a fun time ;)
    if settings_window.walls.get():
        pg.draw.rect(screen, (0, 0, 0), pg.Rect(0, 0, *cam.dims), 3)
    for b in bodies:
        # Calculate coordinates and radius adjusted for camera
        x, y = (b.position - cam.position - cam.dims / 2) * cam.scale + cam.dims / 2
        b.update_radius()
        try:
            pg.draw.circle(screen, b.color, (np.int64(x), np.int64(y)), np.int64(b.radius * cam.scale), 0)
        except:
            pass
        # The radius should be calculated in such a way that the camera can be zoomed indefinitely.
        # Currently, the properties of an object can reach a distinct threshold, after which they become invisible.
    pg.display.update()


def update_windows(settings_window):
    arr = [0, 0, [0] * 5]
    if settings_window.alive:
        settings_window.update()
        try:
            arr = [settings_window.gravity_slider.get() / 100, settings_window.COR_slider.get(),
                   [settings_window.time_slider.get() / 100,
                    settings_window.collision.get(), settings_window.walls.get(), settings_window.g_field.get(),
                    settings_window.gravity_on.get()]]
        except:
            pass
    for window in settings_window.properties_windows:
        if window.alive:
            window.update()
        else:
            settings_window.properties_windows.remove(window)
    return arr


def handle_mouse(*args):
    settings_window, camera, event, bodies, dims, G, COR, scroll = args
    if event.button == 1:
        pos = camera.position + (pg.mouse.get_pos() - dims / 2) / camera.scale + dims / 2
        for b in bodies:
            if b.click_collision(pos) and b not in [win.body for win in settings_window.properties_windows]:
                if not settings_window.alive:  # Respawn the main window if it is dead
                    settings_window.__init__(bodies, camera, dims, [G, COR])  # This still does not fix all errors
                settings_window.properties_windows.append(
                    create_menu("BodyProperties", bodies, camera, dims, len(settings_window.properties_windows), b))
    elif event.button == 4:
        camera.scale = min(camera.scale * 1.1, 100)
        scroll.scale /= 1.1
    elif event.button == 5:
        camera.scale = max(camera.scale / 1.1, 0.01)
        scroll.scale *= 1.1


def handle_events(*args):
    settings_window, camera, scroll, done, dims, screen, bodies, G, COR = args
    for event in pg.event.get():
        if event.type == pg.VIDEORESIZE:
            width, height = event.w, event.h
            dims, screen = V2(width, height), pg.display.set_mode((width, height), pg.RESIZABLE)
        elif event.type == pg.KEYDOWN:
            scroll.key(event.key, 1)
            camera.key_down(event.key)
        elif event.type == pg.KEYUP:
            scroll.key(event.key, 0)
            camera.key_up(event.key)
        elif event.type == pg.MOUSEBUTTONDOWN:
            handle_mouse(settings_window, camera, event, bodies, dims, G, COR, scroll)
        done |= event.type == pg.QUIT
    return done, dims, screen


def handle_bodies(*args):
    G, COR, time_factor, collision, walls, g_field, gravity, scroll, bodies, camera, dims, frame_count, settings_window = args
    
    if time_factor != 0:
        for body in bodies:  # Reset previous calculations
            body.acceleration = V2(0, 0)
        
        for b, body in enumerate(bodies):  # Calculate forces and set acceleration, if mutual gravitation is enabled
            for o in range(len(bodies) - 1, b, -1):
                if collision and bodies[o].test_collision(body):
                    if not COR:  # Only remove second body if collision is perfectly inelastic
                        if bodies[b].mass0 < constants.mergePercent*bodies[o].mass0 or bodies[o].mass0 < constants.mergePercent*bodies[b].mass0:
                            bodies[o].merge(bodies[b], settings_window.properties_windows)
                            bodies.pop(b)
                        else:
                            subcor = bodies[b].mass0 / bodies[o].mass0 if bodies[o].mass0 > bodies[b].mass0 else bodies[o].mass0 / bodies[b].mass0
                            bodies[o].collide(bodies[b], subcor, settings_window.properties_windows)
                        break
                    bodies[o].collide(bodies[b], COR, settings_window.properties_windows)
                if gravity:
                    force = body.force_of(bodies[o], G)  # This is a misnomer; `force` is actually acceleration / mass
                    body.acceleration += bodies[o].mass0 * force
                    bodies[o].acceleration -= body.mass0 * force
            body.acceleration.y += G / 50 * g_field  # Uniform gravitational field
            body.apply_motion(time_factor)
            body.position += scroll.val
            if not frame_count % 100 and body.position.length() > 100000:  # TODO: find a good value from this boundary
                bodies.remove(body)
                for window in settings_window.properties_windows:
                    if window.body is body:
                        settings_window.properties_windows.remove(window)
                        window.destroy()
                        break
            if walls:  # Wall collision
                d, r = ((body.position - camera.position) - dims / 2) * camera.scale + dims / 2, body.radius * camera.scale
                for i in 0, 1:
                    x = d[i]  # x is the dimension (x,y) currently being tested / edited
                    if x <= r or x >= dims[i] - r:
                        if COR == 0:
                            body.velocity[i] *= -1  # Reflect the perpendicular velocity when merge and walls
                        else :
                            body.velocity[i] *= -COR # Reflect the perpendicular velocity when not merge and walls
                        body.position[i] = (2 * (x < r) - 1) * (r - dims[i] / 2) / camera.scale + dims[i] / 2 + \
                                           camera.position[i]  # Place body back into frame
            
            specmass = bodies[b].get_mass0() - abs(bodies[b].get_charge())**2
            if specmass < 0  and random.randint(0, constants.decayConstant) <= constants.decayConstantN:
                #print(str(bodies[b].get_mass0()) + " " + str(abs(bodies[b].get_charge())))
                splitter = bodies[b].split(specmass, len(bodies) + 1, settings_window.properties_windows)
                if  splitter.get_mass0()== 0:
                    continue
                else:
                    bodies.append(splitter)
            

class Scroll:
    def __init__(self):
        self.down, self.map, self.val, self.scale = [0, 0, 0, 0], [pg.K_a, pg.K_w, pg.K_d, pg.K_s], V2(0, 0), 1

    def key(self, key, down):
        if key in self.map:
            self.down[self.map.index(key)] = down

    def update_value(self):
        self.val = (self.val + self.scale * (V2(self.down[:2]) - self.down[2:])) * .95


class Camera:
    def __init__(self, dims):
        self.position, self.velocity, self.dims, self.scale, self.map = V2(0, 0), V2(0, 0), dims, 1, [pg.K_RIGHT,
                                                                                                      pg.K_LEFT,
                                                                                                      pg.K_UP,
                                                                                                      pg.K_DOWN]

    def key_down(self, key):
        if key in self.map:
            self.velocity = V2((3 / self.scale, 0) if key in self.map[:2] else (0, 3 / self.scale)).elementwise() * (
                (self.map.index(key) not in (1, 2)) * 2 - 1)

    def key_up(self, key):
        if key in self.map:
            self.velocity = self.velocity.elementwise() * ((0, 1) if key in self.map[:2] else (1, 0))

    def move_to_com(self, bodies):
        total_mass = sum(b.mass for b in bodies)
        self.position = reduce(add, (b.position * b.mass for b in bodies)) / total_mass - self.dims / 2

    def move_to_body(self, body):
        self.position = body.position - self.dims / 2

    def apply_velocity(self):
        self.position += self.velocity


def main():
    screen, dims = init_display()
    bodies, camera, scroll = [], Camera(dims), Scroll()

    settings_window, clock, done, frame_count = create_menu("Settings", bodies, camera, dims,
                                                            [constants.G, constants.COR]), pg.time.Clock(), False, 0
                        
    while not done:
        clock.tick(constants.clock_speed)
        frame_count += 1

        camera.apply_velocity()
        G, COR, misc_settings = update_windows(settings_window)
        done, dims, screen = handle_events(settings_window, camera, scroll, done, dims, screen, bodies, G, COR)
        handle_bodies(G, COR, *misc_settings, scroll, bodies, camera, dims, frame_count, settings_window)
        refresh_display(settings_window, screen, bodies, camera)
        scroll.update_value()

    pg.quit()
    if settings_window.alive: settings_window.destroy(), self.destroy()


if __name__ == "__main__":
    main()
