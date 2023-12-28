import pygame
import os
from pygame.math    import Vector2 as vec

#------------------------------------------------------------------------------
# Constants

PATH            = os.path.dirname(os.path.abspath(__file__))
IMG_PLAYER_BAR  = f"{PATH}\\img\\player_bar.png"
IMG_CPU_BAR     = f"{PATH}\\img\\cpu_bar.png"
IMG_BALL        = f"{PATH}\\img\\ball.png"
IMG_FIELD       = f"{PATH}\\img\\field.jpg"
WAV_HIT         = f"{PATH}\\fx\\hit.wav"

WIDTH           = 780
HEIGHT          = 468
BG_SCALE        = 0.41
SPRITE_SCALE    = 0.5

PLAYER_SPEED    = vec(  0.00,   0.1)
BALL_VEL        = vec(- 0.05, - 0.05)
BALL_GAIN       = 1.00002
DELAY_TRIGGER   = 50

#------------------------------------------------------------------------------
# Functions

def resize_image(image, scale):
    new_width   = int(scale * image.get_width())
    new_height  = int(scale * image.get_height())
    new_image   = pygame.transform.scale(image, (new_width, new_height))
    return new_image

#------------------------------------------------------------------------------
# Game Objects

class Player(pygame.sprite.Sprite):
    
    def __init__(self, is_player, *groups) -> None:
        super().__init__(*groups)

        if is_player: self.img = IMG_PLAYER_BAR
        else:         self.img = IMG_CPU_BAR
        self.image  = resize_image(pygame.image.load(self.img), 0.5)
        self.rect   = self.image.get_rect()
        self.speed  = PLAYER_SPEED
        self.pos    = vec(10,40)
        self.delay  = 0
        self.dir    = None
        
        self.rect.topleft = self.pos
        
    def move_to_middle(self):
        self.pos    = vec(10 , (HEIGHT + self.image.get_height()) / 2)

    def move_up(self):
        max_distance = self.speed.y
        if self.pos.y > max_distance:
            self.pos -= self.speed
        self.rect.topleft = self.pos

    def move_down(self):
        max_distance = HEIGHT - self.image.get_height()
        if self.pos.y < max_distance:
            self.pos += self.speed
        self.rect.topleft = self.pos

    def change_direction(self, direction):
        if self.delay == DELAY_TRIGGER:
            self.dir = direction
        else:
            self.delay += 1

    def cpu_move(self, ball):
        if   self.rect.top >= ball.rect.top:
            self.change_direction("Up")
        elif self.rect.bottom <= ball.rect.bottom:
            self.change_direction("Down")
        else:
            self.change_direction(None)
        
        if self.dir == "Up": self.move_up()
        if self.dir == "Down": self.move_down()
        
class Ball(pygame.sprite.Sprite):
    
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        
        self.image  = resize_image(pygame.image.load(IMG_BALL), SPRITE_SCALE)
        self.rect   = self.image.get_rect()
        self.gain   = BALL_GAIN
        self.vel    = vec(0,0) + BALL_VEL
        self.move_to_middle()
        
    def move_to_middle(self):
        self.pos    = vec(
            (WIDTH  + self.image.get_width() ) / 2 , 
            (HEIGHT + self.image.get_height()) / 2)
        self.vel    = vec(0,0) + BALL_VEL
        print(f"{self.vel} \t {BALL_VEL}")

    def move(self):
        global HEIGHT
        
        self.vel   *= self.gain
        max_top     = self.vel.y
        max_bottom  = HEIGHT - self.vel.y
        if max_top    < 0:      max_top = 0
        if max_bottom > HEIGHT: max_bottom = HEIGHT
        
        if (
            self.rect.top    <= max_top or
            self.rect.bottom >= max_bottom
        ):
            self.vel.y *= -1
            
        self.pos += self.vel
        self.rect.topleft = self.pos
        self.check_for_score()
        
    def check_for_score(self):
        max_distance = WIDTH - self.vel.x
        if self.pos.x <= 0:
            self.move_to_middle()
            return "player 1"
        elif self.pos.x >= max_distance:
            self.move_to_middle()
            return "player 2"
        else:
            return None

#------------------------------------------------------------------------------
# Game initialization

background      = resize_image(pygame.image.load(IMG_FIELD), BG_SCALE)
player_1        = Player(True)
player_2        = Player(False)
ball            = Ball()

player_2_x      = WIDTH - player_2.image.get_width() - 10
player_2.pos    = vec(player_2_x, player_2.rect.top)

screen          = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong!")

#------------------------------------------------------------------------------
# Main game loop

running = True
while running:

    # Draw sprites
    screen.blit(background,(0,0))
    screen.blit(player_1.image, player_1.pos)
    screen.blit(player_2.image, player_2.pos)
    screen.blit(ball.image, ball.pos)
    pygame.display.flip()

    # Process game collisions
    if (
        ball.rect.colliderect(player_1.rect) or
        ball.rect.colliderect(player_2.rect)
    ):
        ball.vel.x *= -1

    # Game events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys_pressed    = pygame.key.get_pressed()
    if keys_pressed[pygame.K_UP]:     player_1.move_up()
    if keys_pressed[pygame.K_DOWN]:   player_1.move_down()
    
    ball.move()
    player_2.cpu_move(ball)

#------------------------------------------------------------------------------
# Quit Pygame

pygame.quit()