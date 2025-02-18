import pygame
import math
import pygame_gui
import random

class BouncingBallGame:
    def __init__(self):
        pygame.init()
        
        self.WIDTH = 1000
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Bouncing Ball in Circle")
        
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT))
        self.create_gui_elements()
        
        self.CIRCLE_CENTER = (self.WIDTH // 2 - 100, self.HEIGHT // 2)
        self.CIRCLE_RADIUS = 200
        self.BALL_RADIUS = 20
        
        self.ball_x = self.CIRCLE_CENTER[0]
        self.ball_y = self.CIRCLE_CENTER[1]
        self.speed_x = 5
        self.speed_y = 0
        self.gravity = 0.5
        self.friction = 0.99
        
        self.coins = []
        self.coin_spawn_timer = 0
        self.coin_radius = 15
        self.spawn_coins_enabled = True
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.circle_hue = 0
        self.color_speed = 0.5

    def create_gui_elements(self):
        self.circle_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((820, 50), (150, 20)),
            start_value=200,
            value_range=(50, 400),
            manager=self.manager
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((820, 30), (150, 20)),
            text='Circle Radius',
            manager=self.manager
        )

        self.ball_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((820, 120), (150, 20)),
            start_value=20,
            value_range=(5, 80),
            manager=self.manager
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((820, 100), (150, 20)),
            text='Ball Size',
            manager=self.manager
        )

        self.boost_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((820, 190), (150, 20)),
            start_value=1.5,
            value_range=(0.5, 2.0),
            manager=self.manager
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((820, 170), (150, 20)),
            text='Bounce Boost',
            manager=self.manager
        )

        self.speed_limit_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((820, 260), (150, 20)),
            start_value=15,
            value_range=(5, 30),
            manager=self.manager
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((820, 240), (150, 20)),
            text='Speed Limit',
            manager=self.manager
        )

        self.coin_spawn_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((820, 330), (150, 20)),
            start_value=2.0,
            value_range=(0.5, 5.0),
            manager=self.manager
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((820, 310), (150, 20)),
            text='Coin Frequency (sec)',
            manager=self.manager
        )

        self.spawn_toggle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((820, 370), (150, 30)),
            text='Disable Spawn',
            manager=self.manager
        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.spawn_toggle_button:
                    self.spawn_coins_enabled = not self.spawn_coins_enabled
                    self.spawn_toggle_button.set_text(
                        'Enable Spawn' if not self.spawn_coins_enabled else 'Disable Spawn'
                    )
            
            self.manager.process_events(event)

    def spawn_coin(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, self.CIRCLE_RADIUS - self.coin_radius)
        x = self.CIRCLE_CENTER[0] + distance * math.cos(angle)
        y = self.CIRCLE_CENTER[1] + distance * math.sin(angle)
        self.coins.append({'x': x, 'y': y})

    def collect_coins(self):
        coins_to_remove = []
        ball_rect = pygame.Rect(
            self.ball_x - self.BALL_RADIUS,
            self.ball_y - self.BALL_RADIUS,
            self.BALL_RADIUS * 2,
            self.BALL_RADIUS * 2
        )
        
        for i, coin in enumerate(self.coins):
            coin_rect = pygame.Rect(
                coin['x'] - self.coin_radius,
                coin['y'] - self.coin_radius,
                self.coin_radius * 2,
                self.coin_radius * 2
            )
            if ball_rect.colliderect(coin_rect):
                coins_to_remove.append(i)
        
        for i in reversed(coins_to_remove):
            self.coins.pop(i)

    def update(self, time_delta):
        self.manager.update(time_delta)
        self.CIRCLE_RADIUS = self.circle_slider.get_current_value()
        self.BALL_RADIUS = self.ball_slider.get_current_value()
        boost_factor = self.boost_slider.get_current_value()
        speed_limit = self.speed_limit_slider.get_current_value()
        coin_spawn_interval = self.coin_spawn_slider.get_current_value()
        if self.spawn_coins_enabled:
            self.coin_spawn_timer += time_delta
            if self.coin_spawn_timer >= coin_spawn_interval:
                self.spawn_coin()
                self.coin_spawn_timer = 0
        
        self.collect_coins()
        self.speed_y += self.gravity
        self.ball_x += self.speed_x
        self.ball_y += self.speed_y
        self.speed_x *= self.friction
        self.speed_y *= self.friction
        self.check_collision(boost_factor, speed_limit)
        self.circle_hue = (self.circle_hue + self.color_speed) % 360

    def check_collision(self, boost_factor, speed_limit):
        distance = math.sqrt((self.ball_x - self.CIRCLE_CENTER[0])**2 + 
                           (self.ball_y - self.CIRCLE_CENTER[1])**2)
        if distance + self.BALL_RADIUS > self.CIRCLE_RADIUS:
            angle = math.atan2(self.ball_y - self.CIRCLE_CENTER[1],
                             self.ball_x - self.CIRCLE_CENTER[0])
            self.ball_x = self.CIRCLE_CENTER[0] + (self.CIRCLE_RADIUS - self.BALL_RADIUS) * math.cos(angle)
            self.ball_y = self.CIRCLE_CENTER[1] + (self.CIRCLE_RADIUS - self.BALL_RADIUS) * math.sin(angle)
            normal_x = (self.ball_x - self.CIRCLE_CENTER[0]) / distance
            normal_y = (self.ball_y - self.CIRCLE_CENTER[1]) / distance
            dot_product = self.speed_x * normal_x + self.speed_y * normal_y
            total_speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
            current_boost = boost_factor
            if total_speed > speed_limit:
                current_boost = 0.7
            self.speed_x = (self.speed_x - 2 * dot_product * normal_x) * current_boost
            self.speed_y = (self.speed_y - 2 * dot_product * normal_y) * current_boost

    def hsv_to_rgb(self, h, s, v):
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return ((r + m) * 255, (g + m) * 255, (b + m) * 255)

    def draw(self):
        self.screen.fill(self.BLACK)
        
        circle_color = self.hsv_to_rgb(self.circle_hue, 1, 1)
        pygame.draw.circle(self.screen, circle_color, self.CIRCLE_CENTER, self.CIRCLE_RADIUS, 2)
        
        for coin in self.coins:
            pygame.draw.circle(self.screen, self.YELLOW, 
                             (int(coin['x']), int(coin['y'])), 
                             self.coin_radius)
        
        pygame.draw.circle(self.screen, self.RED, 
                         (int(self.ball_x), int(self.ball_y)), 
                         int(self.BALL_RADIUS))
        
        self.manager.draw_ui(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            time_delta = self.clock.tick(60)/1000.0
            self.handle_events()
            self.update(time_delta)
            self.draw()

        pygame.quit()

if __name__ == '__main__':
    game = BouncingBallGame()
    game.run()
