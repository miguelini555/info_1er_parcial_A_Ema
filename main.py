import math
import logging
import arcade
import pymunk

from game_object import Bird, Yellow, Blue, Column, Pig
from game_logic import get_impulse_vector, Point2D, get_distance

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 1800
HEIGHT = 800
TITLE = "Angry birds"
GRAVITY = -900


class App(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("assets/img/background3.png")
        # crear espacio de pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        self.space.add(floor_body, floor_shape)

        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        self.add_columns()
        self.add_pigs()

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False

        # agregar un collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler
        self.current_bird_type = "red"

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.R:
            self.current_bird_type = "red"
        elif symbol == arcade.key.Y:
            self.current_bird_type = "yellow"
        elif symbol == arcade.key.B:
            self.current_bird_type = "blue"
        elif symbol == arcade.key.G:
            for bird in self.birds:
                if isinstance(bird, Yellow):
                    if bird.body.velocity.length > 10:
                        bird.activate_speed()
                        logger.debug("TECLA G PRESIONADA")
                        break
        elif symbol == arcade.key.F:
            for bird in self.birds:
                if isinstance(bird, Blue):
                    velocity = bird.body.velocity.length
                    if velocity > 10:
                        if bird.body.position.y > 50:
                            new_birds = bird.split(self.space, self.birds)
                            for b in new_birds:
                                self.sprites.append(b)
                            break
        

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in self.world:
                if obj.shape in arbiter.shapes:
                    obj.remove_from_sprite_lists()
                    self.space.remove(obj.shape, obj.body)

        return True

    def add_columns(self):
        for x in range(WIDTH // 2, WIDTH, 400):
            column = Column(x, 50, self.space)
            self.sprites.append(column)
            self.world.append(column)        
        for x in range(WIDTH // 3, WIDTH, 400):
            column1 = Column(x, 50, self.space)
            self.sprites.append(column1)
            self.world.append(column1)

    def add_pigs(self):
        pig1 = Pig(WIDTH / 2, 100, self.space)
        self.sprites.append(pig1)
        self.world.append(pig1)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)  # actualiza la simulacion de las fisicas
        self.update_collisions()
        self.sprites.update(delta_time)

    def update_collisions(self):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.start_point = Point2D(x, y)
            self.end_point = Point2D(x, y)
            self.draw_line = True
            logger.debug(f"Start Point: {self.start_point}")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            self.end_point = Point2D(x, y)
            logger.debug(f"Dragging to: {self.end_point}")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            logger.debug(f"Releasing from: {self.end_point}")
            self.draw_line = False
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)
            bird_type = self.current_bird_type
            if bird_type == "red":
                bird = Bird(
                    "assets/img/red-bird3.png",
                    impulse_vector,
                    x,
                    y,
                    self.space,
                    radius=12
                )
            elif bird_type == "yellow":
                bird = Yellow(
                    impulse_vector,
                    x,
                    y,
                    self.space
                )
            elif bird_type == "blue":
                bird = Blue(
                    impulse_vector,
                    x,
                    y,
                    self.space
                )
            self.sprites.append(bird)
            self.birds.append(bird)    

    def on_draw(self):
        self.clear()
        # arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y,
                             arcade.color.BLACK, 3)


def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    game = App()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()