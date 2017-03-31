from Presets import *


def display(screen, bodies):
    #clear last frame
    screen.fill(bg_color)

    #display all bodies
    for b in bodies:
        #screen.blit(b.image, b.position)
        b.draw_on(screen)

    #flip display
    pg.display.update()



def main():

    # construct bodies list
    # bodies = [
    #     Body(10, 10, [200, 200], [0, 0]),
    #     Body(10, 10, [60, 60], [0, 0]),
    #     Body(10, 10, [100, 150], [0, 0])
    # ]
    bodies = star_system(500, 30, 100, 2, 5, 40, 100)


    # initialize screen
    width, height = 800, 600
    screen = pg.display.set_mode((width, height))

    # initialize game clock and set tick to 60
    clock = pg.time.Clock()
    clock.tick(60)

    done = False
    while not done:
        # user input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        # display current frame
        display(screen, bodies)

        # calculate forces and apply acceleration
        for body in bodies:
            for other in bodies:
                if other is not body:
                    acceleration = body.effect_of(other)
                    body.apply_acceleration(acceleration)

        # apply velocity (update position)
        for body in bodies:
            body.apply_velocity()


    pg.quit()








if __name__ == "__main__":
    main()