import pygame
from pygame.locals import *
from random import randint, choice

class Game:
    def __init__(self) -> None:
        pygame.init() 

        self.screen = pygame.display.set_mode((288, 512))
        pygame.display.set_caption('Flappy Bird')
        import_assets()
        pygame.display.set_icon(ICON)
        self.current_scene = 'menu'
        self.game_start_scene = GameStart()
        self.score = 0

        self.background = BACKGROUND

        self.base = Base()

        self.bird = pygame.sprite.GroupSingle()
        self.bird.add(Bird())

        self.pipe = pygame.sprite.Group()
        self.pipe_spawner = USEREVENT + 1
        pygame.time.set_timer(self.pipe_spawner, 1500)

    def get_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == QUIT: return True

            elif self.current_scene == 'over' and event.type in [KEYDOWN, MOUSEBUTTONDOWN]:
                self.reset()
            elif self.current_scene == 'game':
                if event.type == KEYDOWN and event.key == K_SPACE or event.type == MOUSEBUTTONDOWN:
                    self.bird.sprite.jump()
                if event.type == self.pipe_spawner:
                    self.pipe.add(Pipe(randint(192, 375), choice(['green', 'red'])))

        return False
                 
    def loop(self):
        clock = pygame.time.Clock()

        while True:
            if self.get_events(): break
            
            if self.current_scene == 'menu':
                self.game_start_scene.display()
            elif self.current_scene == 'over':
                game_over_rect = GAMEOVER.get_rect(midtop=(144, 100))
                self.screen.blit(GAMEOVER, game_over_rect)
            else:
                self.screen.blit(self.background['day'], (0, 0))

                self.pipe.update()
                self.pipe.draw(self.screen)

                self.base.draw(self.screen)

                self.bird.update()
                self.bird.draw(self.screen)

                display_score()

            pygame.display.update()
            clock.tick(30)

        pygame.quit()

    def reset(self):
        game.pipe.empty()
        game.bird.sprite.rect.center = (50, 250)
        game.bird.sprite.gravity = -5
        game.score = 0
        game.current_scene = 'menu'

class Bird(pygame.sprite.Sprite):
    def __init__(self, color='red') -> None:
        super().__init__()
        self.frames = BIRD.get(color, 'red')
        self.current_frame = 0
        self.frame_rate = .1
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(50,250))
        self.mask = pygame.mask.from_surface(self.image)
        self.gravity = 0

    def apply_gravity(self) -> None:
        self.gravity += 1
        self.rect.y += self.gravity

    def jump(self) -> None:
        self.gravity = -10

    def animate(self) -> None:
        self.current_frame = (self.current_frame + self.frame_rate) % 3
        self.image = self.frames[int(self.current_frame)]

    def change_color(self, color):
        self.frames = BIRD.get(color, 'red')

    def collison(self) -> None:
        if self.rect.bottom > 450:
            game.current_scene = 'over'
            self.rect.bottom = 450
        elif pygame.sprite.spritecollide(self, game.pipe, False, pygame.sprite.collide_mask):
            game.current_scene = 'over'

    def update(self) -> None:
        self.apply_gravity()
        self.collison()
        self.animate()
        
class Base():
    def __init__(self) -> None:
        super().__init__()
        self.image = BASE
        self.rect = [self.image.get_rect(x=0, y=450),
                     self.image.get_rect(x=288, y=450)]

    def move(self) -> None:
        for rect in self.rect:
            rect.x -= 4
            if rect.right < 0: rect.x = 280

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.move()
        surface.blits([(self.image, rect) for rect in self.rect])

class Pipe(pygame.sprite.Sprite):
    def __init__(self, y, color='green', flip=False) -> None:
        super().__init__()
        if flip:
            self.image = pygame.transform.flip(PIPE[color], False, True)
            self.rect = self.image.get_rect(left=288, y=y)
        else:
            self.image = PIPE[color]
            self.rect = self.image.get_rect(left=288, y=y)
            game.pipe.add(Pipe(y - 400, color, True))
        self.checked = False

    def move(self) -> None:
        self.rect.x -= 4
        if self.rect.right < 0:
            self.kill()

    def update(self) -> None:
        self.move()

class GameStart:
    def __init__(self) -> None:
        self.surface = pygame.Surface((288, 512))
        self.surface.fill('skyblue')

        self.birds = [pygame.transform.scale_by(BIRD['blue'][1], 3),
                      pygame.transform.scale_by(BIRD['red'][1], 3),
                      pygame.transform.scale_by(BIRD['yellow'][1], 3)]
        self.current_bird = 0
        self.birds_rect = self.birds[self.current_bird].get_rect(center=(144, 150))
        self.surface.blit(self.birds[self.current_bird], self.birds_rect)
        
        left_btn = pygame.transform.rotate(SELECT_BTN, 90)
        self.left = left_btn.get_rect(midleft=(10, 150))
        self.surface.blit(left_btn, self.left)

        right_btn = pygame.transform.rotate(SELECT_BTN, -90)
        self.right = left_btn.get_rect(midright=(278, 150))
        self.surface.blit(right_btn, self.right)

        self.start = START_BTN.get_rect(center=(144, 300))
        self.surface.blit(START_BTN, self.start)
    def display(self) -> None:
        if pygame.mouse.get_pressed()[0]:
            if self.start.collidepoint(pygame.mouse.get_pos()):
                colors = ['blue', 'red', 'yellow']
                game.bird.sprite.change_color(colors[self.current_bird])
                game.current_scene = 'game'
            elif self.right.collidepoint(pygame.mouse.get_pos()):
                self.current_bird = (self.current_bird + 1) % 3
                self.surface.blit(self.birds[self.current_bird], self.birds_rect)
            elif self.left.collidepoint(pygame.mouse.get_pos()):
                self.current_bird = (self.current_bird - 1) % 3
                self.surface.blit(self.birds[self.current_bird], self.birds_rect)
            pygame.time.wait(100)
        game.screen.blit(self.surface, (0,0))

def display_score():
    for pipe in game.pipe.sprites():
        if not pipe.checked:
            rect = pygame.Rect(pipe.rect.x, pipe.rect.y, 52, -80)
            if game.bird.sprite.rect.colliderect(rect):
                game.score += 1
                pipe.checked = True

    score = str(game.score)
    score_rect = pygame.Rect(0, 25, len(score)* 28, 36)
    score_rect.centerx = 144

    for i in range(len(score)):
        game.screen.blit(NUMBERS[int(score[i])], score_rect)
        score_rect.x += 28

def import_assets():
    global ICON, BACKGROUND, BASE, PIPE, BIRD, NUMBERS, GAMEOVER, START_BTN, SELECT_BTN

    ICON = pygame.image.load('favicon.ico').convert()

    BACKGROUND = { 'day': pygame.image.load('sprites/background/background-day.png').convert(),
                'night': pygame.image.load('sprites/background/background-night.png').convert()}

    BASE = pygame.image.load('sprites/base.png').convert()

    PIPE = {'green': pygame.image.load('sprites/pipe/pipe-green.png').convert_alpha(),
            'red': pygame.image.load('sprites/pipe/pipe-red.png').convert_alpha()}

    BIRD = {
            'red': [ pygame.image.load('sprites/red_bird/redbird-downflap.png').convert_alpha(),
                    pygame.image.load('sprites/red_bird/redbird-midflap.png').convert_alpha(),
                    pygame.image.load('sprites/red_bird/redbird-upflap.png').convert_alpha()],
            'blue': [ pygame.image.load('sprites/blue_bird/bluebird-downflap.png').convert_alpha(),
                    pygame.image.load('sprites/blue_bird/bluebird-midflap.png').convert_alpha(),
                    pygame.image.load('sprites/blue_bird/bluebird-upflap.png').convert_alpha()],
            'yellow': [ pygame.image.load('sprites/yellow_bird/yellowbird-downflap.png').convert_alpha(),
                    pygame.image.load('sprites/yellow_bird/yellowbird-midflap.png').convert_alpha(),
                    pygame.image.load('sprites/yellow_bird/yellowbird-upflap.png').convert_alpha()]
            }

    NUMBERS = [pygame.image.load('sprites/numbers/0.png').convert_alpha(),
            pygame.image.load('sprites/numbers/1.png').convert_alpha(),
            pygame.image.load('sprites/numbers/2.png').convert_alpha(),
            pygame.image.load('sprites/numbers/3.png').convert_alpha(),
            pygame.image.load('sprites/numbers/4.png').convert_alpha(),
            pygame.image.load('sprites/numbers/5.png').convert_alpha(),
            pygame.image.load('sprites/numbers/6.png').convert_alpha(),
            pygame.image.load('sprites/numbers/7.png').convert_alpha(),
            pygame.image.load('sprites/numbers/8.png').convert_alpha(),
            pygame.image.load('sprites/numbers/9.png').convert_alpha()]
    
    GAMEOVER = pygame.image.load('sprites/gameover.png').convert_alpha()

    START_BTN = pygame.image.load('sprites/button/start_btn.png').convert()

    SELECT_BTN = pygame.image.load('sprites/button/select_btn.png').convert_alpha()

if __name__ == '__main__':
    game = Game()
    game.loop()