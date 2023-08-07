
# module import section
import pygame as pg
import sys
from pygame.math import Vector2
from pygame import mixer
from random import choice, randint
import os

#basic setup
mixer.init()
pg.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 16)
clock = pg.time.Clock()
FPS = 60
pg.display.set_caption("Enemies Shoot Back")


# loading images
img_bg = pg.image.load("img/background-black.png").convert()
img_bg = pg.transform.scale(img_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

img_magazine = pg.image.load("img/gun_magazine.png").convert_alpha()
img_bullet = pg.image.load("img/projectile.png").convert_alpha()

scale_factor = 2
img_shep_walk_left = pg.image.load("img/shepard_walk_left.png").convert_alpha()
img_shep_walk_left = pg.transform.scale(img_shep_walk_left,
                                        (img_shep_walk_left.get_width() * scale_factor,
                                         img_shep_walk_left.get_height() * scale_factor))
img_shep_walk_right = pg.image.load("img/shepard_walk_right.png").convert_alpha()
img_shep_walk_right = pg.transform.scale(img_shep_walk_right,
                                         (img_shep_walk_right.get_width() * scale_factor,
                                          img_shep_walk_right.get_height() * scale_factor))

img_bomb = pg.image.load("img/pixel_laser_violet.png").convert_alpha()
img_ground_tile = pg.image.load("img/ground_tile.png").convert_alpha()

img_ufo_list = [pg.image.load(f"img/{img_num}.png").convert_alpha()
                for img_num in range(1,5)]

# the sliced image lists go here!
animation_dict = {
    "walk_left" : [],
    "walk_right" : []
    }

# loading a raw image sheet and returning a sliced sprite list
def load_sprite_sheet(raw_image_sheet, animation_steps):
    animation_list = []
    for x in range(animation_steps):
        temp_img = raw_image_sheet.subsurface(x * (raw_image_sheet.get_width() / 4), 0, (raw_image_sheet.get_width() / 4),
                                              raw_image_sheet.get_height())
        animation_list.append(temp_img)
    return animation_list
# store the sliced frames in the animation dictionary
animation_dict["walk_left"] = load_sprite_sheet(img_shep_walk_left, 4)
animation_dict["walk_right"] = load_sprite_sheet(img_shep_walk_right, 4)


explo_sound_list = [pg.mixer.Sound(f"sound/explo_snd_0{snd_num}.wav") for snd_num
                                   in range(0, 3)]

chara_hit_sound_list = [pg.mixer.Sound(f"sound/hit_snd_{snd_num}.wav")
                        for snd_num in range(0, 4)]

enemy_shot_sound_list = [pg.mixer.Sound(f"sound/hit_force_field_{snd_num}.wav")
                         for snd_num in range(0, 3)]
for snd in enemy_shot_sound_list:
    snd.set_volume(0.15)

cover_hit_fx = explo_sound_list[2]

shot_fx = pg.mixer.Sound("sound/shoot_01.wav")
shot_fx.set_volume(0.5)

reload_fx = pg.mixer.Sound("sound/energyCellReload.mp3")
mag_pickup_fx = pg.mixer.Sound("sound/Colt1911Reload.mp3")

##pg.mixer.music.load("sound/skipping_into_the_abyss.mp3")
pg.mixer.music.load("sound/Juhani_Junkala_0.wav")
pg.mixer.music.play(loops=-1)
pg.mixer.music.set_volume(0.25)






##font = pg.font.SysFont("Computer-Regular", 30)
##font_larger = pg.font.SysFont("Computer-Regular", 40)
font = pg.font.Font("font/Computerfont.ttf", 30)
font_larger = pg.font.Font("font/Computerfont.ttf", 40)
def draw_text(pos, color, font, text):
    text_img = font.render(text, False, color)
    text_rect = text_img.get_rect(topleft = (pos))
    screen.blit(text_img, text_rect)


def draw_healthbar(player_health, player_max_health, pos):
    base_rect = pg.Rect(pos[0], pos[1], 100, 10)
    health_rect = pg.Rect(pos[0], pos[1], 100 * (player_health / player_max_health), 10)
    pg.draw.rect(screen, "red", base_rect)
    pg.draw.rect(screen, "green", health_rect)


# tile class used for both the ground and the cover
class Tile():
    def __init__(self, pos, image, scale=1):
        self.image = pg.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
        self.rect = self.image.get_rect(topleft = (pos))

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.draw()


# ground set-up
ground_tile_list = []
ground_layout = [
        #0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],#0
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],#1
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],#2
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] #3
    ]
# cover set-up
cover_layout = [
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1]
    ]

# create the tiled ground
def generate_ground(ground_tile_list, ground_layout, Tile, tile_img):
    for row_index, row in enumerate(ground_layout):
        for col_index, col in enumerate(row):
            if col == 1:
                x_pos = col_index * tile_img.get_width()
                y_pos = (SCREEN_HEIGHT - tile_img.get_height() * 4) + (row_index * tile_img.get_height())
                new_tile = Tile((x_pos, y_pos), tile_img)
                ground_tile_list.append(new_tile)
    return ground_tile_list

ground_tile_list = generate_ground(ground_tile_list, ground_layout, Tile, img_ground_tile)




# object list setup
bullet_list = []
ufo_list = []
bomb_list = []
mag_list = []

# score and highscore declaration
score = 0
highscore = 0
# file loading (if it exists)
if os.path.exists("score.txt"):
    with open("score.txt", "r") as file:
        highscore = int(file.read())

# won, pause, and number of enemy_waves setup
game_won = False
pause = False
enemy_wave = 1         


# blueprint for the ammo pickups
class AmmoObject():
    def __init__(self, pos, speed, image, scale):
        self.image = pg.transform.scale(image, (image.get_width() * scale,
                                                image.get_height() * scale))
        self.pos = Vector2(pos)
        self.rect = self.image.get_rect(center = (self.pos))
        self.speed = speed
        self.direction = Vector2(0, 1)
        self.delta_y = 0
        self.offscreen = False
        self.ammo_load = 8

    def move(self):
        self.delta_y = self.speed * self.direction.y
        self.pos.y += self.delta_y
        self.rect.center = self.pos

    def draw(self):
        screen.blit(self.image, self.rect)

    def offscreen_check(self):
        if not self.offscreen:
            if self.rect.top > SCREEN_HEIGHT:
                self.offscreen = True

    def update(self):
        self.move()
        self.offscreen_check()
        self.draw()

        
# blueprint for the ufos
class EnemyObject():
    def __init__(self, pos, speed, image, scale):
        self.image = pg.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
        self.pos = Vector2(pos)
        self.rect = self.image.get_rect(center = (self.pos))
        self.speed = speed
        self.move_count = 0
        self.direction = Vector2(1,0)
        self.delta_x = 0

    def move(self):
        if self.move_count <= 100:
            self.delta_x = self.speed * self.direction.x
            self.pos.x += self.delta_x
            self.rect.center = self.pos
            self.move_count += 1
        else:
            self.direction.x *= -1
            self.move_count = -100
            
    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.move()
        self.draw()

# everything related to the player character
class PlayerObject():
    def __init__(self, pos, speed, direction, animation_dict):
        self.anim_update_interval = 120 #ms per frame
        self.frame_update_time = pg.time.get_ticks()
##        self.facing = "right"
        self.pos = Vector2(pos)
        self.direction = Vector2(direction)
        self.frame_index = 0
##        self.anim = "walk"
##        self.action = f"{self.anim}_{self.facing}"
        self.action = "walk_right"
        self.animation_dict = animation_dict
        self.image = self.animation_dict[self.action][self.frame_index]
        self.rect = self.image.get_rect(center = (self.pos))
        self.delta_x = 0
        self.speed = speed
        self.fired = False
        self.alive = True
        self.hit_box = self.rect.inflate(-60, -10)
        self.health = 3
        self.max_health = self.health
        self.max_bullets = 32
        self.ammo_pool = self.max_bullets
        self.mag_size = 8
        self.bullets_in_mag = self.mag_size
        self.mag_num = self.ammo_pool // self.mag_size
        self.reloaded = False


    def get_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            self.direction.x = 1
            self.update_action("walk_right")
        elif keys[pg.K_a]:
            self.direction.x = -1
            self.update_action("walk_left")
        else:
            self.direction.x = 0
            self.frame_index = 0


        if keys[pg.K_SPACE] and not self.fired and (not self.bullets_in_mag <= 0):
            self.fired = True
            self.shoot_bullet()
        if not keys[pg.K_SPACE]:
            self.fired = False

        if keys[pg.K_r] and not self.reloaded and (self.bullets_in_mag < self.mag_size)\
        and (self.ammo_pool >= 0):
            self.reloaded = True
            if self.reloaded:
                reload_fx.play()
                rounds_missing = self.mag_size - self.bullets_in_mag
                if rounds_missing < self.ammo_pool:
                    self.ammo_pool -= rounds_missing
                    self.bullets_in_mag += rounds_missing
                else:
                    self.bullets_in_mag += self.ammo_pool
                    self.ammo_pool -= self.ammo_pool
        if not keys[pg.K_r]:
            self.reloaded = False

    def shoot_bullet(self):
        if self.fired:
           self.bullets_in_mag -= 1 
           shot_fx.play()
           bullet = BulletObject((self.rect.centerx, self.rect.centery), 10, (0,-1), img_bullet)
           bullet_list.append(bullet)

    def move(self):
        self.delta_x = self.speed * self.direction.x
        self.screen_boundary_check()
        self.pos.x += self.delta_x
        self.hit_box.center = self.pos
        self.rect.center = self.pos

    def screen_boundary_check(self):
        if self.rect.left + self.delta_x < 0:
            self.delta_x = 0 - self.rect.left
            self.frame_index = 0
        elif self.rect.right + self.delta_x > SCREEN_WIDTH:
            self.delta_x = SCREEN_WIDTH - self.rect.right
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.frame_update_time = pg.time.get_ticks()

    def animate(self):
        self.image = self.animation_dict[self.action][self.frame_index]
        current_time = pg.time.get_ticks()
        if current_time - self.frame_update_time > self.anim_update_interval:
            self.frame_index += 1
            self.frame_update_time = pg.time.get_ticks()

        if self.frame_index >= len(self.animation_dict[self.action]):
            self.frame_index = 0

    def draw(self):
        screen.blit(self.image, self.rect)
        
    def update(self):
        self.get_input()
        self.move()
        self.animate()
        self.draw()

# blueprint for the player bullets 
class BulletObject():
    def __init__(self, pos, speed, direction, image):
        self.image = image
        self.pos = Vector2(pos)
        self.rect = self.image.get_rect(center = (self.pos))
        self.hit_box = self.rect.inflate(- 85, -55)
        self.direction = Vector2(direction)
        self.speed = speed
        self.delta_x = 0
        self.delta_y = 0
        self.offscreen = False


    def move(self):
        if self.direction.magnitude != 0:
            self.direction = self.direction.normalize()
        self.delta_x = self.speed * self.direction.x
        self.delta_y = self.speed * self.direction.y
        self.pos.x += self.delta_x
        self.pos.y += self.delta_y
        self.rect.center = self.pos
        self.hit_box.center = self.pos
        
        #if self.pos.y >= 0:
    def offscreen_check(self):
        if not self.offscreen:
            if self.rect.bottom < 0:
                self.offscreen = True

    def draw(self):
        screen.blit(self.image, self.rect)


    def update(self):
        self.move()
        self.offscreen_check()
        self.draw()


# draws the enemy ufo grid
def enemy_setup(img_ufo_list):
    for col in range(7):
        for row in range(3):
            x = 200 + 100 * col
            y = 100 + 100 * row
            ufo = EnemyObject((x,y),1,choice(img_ufo_list),0.1)
            ufo_list.append(ufo)
    return img_ufo_list

img_ufo_list = enemy_setup(img_ufo_list)


# the ufo projectiles that inherit from the bullet class the player uses
class Bomb(BulletObject):
    def __init__(self, pos, speed, direction, image):
        super().__init__(pos, speed, direction, image)

    def offscreen_check(self):
        if self.offscreen:
            if self.rect.top > SCREEN_HEIGHT:
                self.offscreen = True



# cover object class
class Cover():
    def __init__(self, pos, tile_image, cover_layout):
        self.pos = pos
        self.tile_image_scaled = pg.transform.scale(tile_image, (tile_image.get_width() * 0.5, tile_image.get_height() * 0.5))
        self.cover_layout = cover_layout
        self.cover_tile_list = []

    # creates the cover tile grid
    def generate_grid(self):
        for row_index, row in enumerate(self.cover_layout):
            for col_index, col in enumerate(row):
                if col == 1:
                    x = self.pos[0] + (col_index * self.tile_image_scaled.get_width())
                    y = self.pos[1] + (row_index * self.tile_image_scaled.get_height())
                    tile = Tile((x,y),self.tile_image_scaled)
                    self.cover_tile_list.append(tile)

    # draws tiles and checks for collisions   
    def update(self, bomb_list, bullet_list):
        for tile_index, tile in enumerate(self.cover_tile_list):
            
            for bomb_index, bomb in enumerate(bomb_list):
                if bomb.hit_box.colliderect(tile.rect):
                    cover_hit_fx.play()
                    del self.cover_tile_list[tile_index]
                    del bomb_list[bomb_index]
                    break
                

            for bullet_index, bullet in enumerate(bullet_list):
                if bullet.hit_box.colliderect(tile.rect):
                    cover_hit_fx.play()
                    del self.cover_tile_list[tile_index]
                    del bullet_list[bullet_index]
                    break

            tile.update()

        return bomb_list, bullet_list

        
    
# creating instances of main game objects
sheppy = PlayerObject((SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100), 5, (0,0), animation_dict)

left_cover = Cover((SCREEN_WIDTH / 4 - 200, SCREEN_HEIGHT - 300), img_ground_tile, cover_layout)
left_cover.generate_grid()

middle_cover = Cover((SCREEN_WIDTH / 2 - 75, SCREEN_HEIGHT - 300), img_ground_tile, cover_layout)
middle_cover.generate_grid()

right_cover = Cover((SCREEN_WIDTH - 220, SCREEN_HEIGHT - 300), img_ground_tile, cover_layout)
right_cover.generate_grid()


bg_col = (0, 0, 0)
run = True
while run:
    # frame timer
    clock.tick(FPS)
    pg.display.set_caption(f"Enemies Shoot Back | FPS: {clock.get_fps():.1f}")
    # drawing the background
    screen.fill(bg_col)
    screen.blit(img_bg,(0,0))
    # drawing the Heads Up Display
    draw_text((SCREEN_WIDTH / 2 - 130, 0), "white", font, "Health: ")
    draw_healthbar(sheppy.health, sheppy.max_health, (SCREEN_WIDTH / 2 - 40, 15))
    draw_text((10, 0), "white", font, f"Score: {score}")
    draw_text((200, 0), "white", font, f"Wave: {enemy_wave}")
    screen.blit(img_magazine, (SCREEN_WIDTH - 175, 15))
    draw_text((SCREEN_WIDTH - 130, 5), "white", font, f"Pool: {sheppy.ammo_pool}")
    draw_text((SCREEN_WIDTH - 130, 25), "white", font, f"Rounds: {sheppy.bullets_in_mag}")
    draw_text((SCREEN_WIDTH - 130, 50), "white", font, f"Mags: {sheppy.mag_num}")
    draw_text((SCREEN_WIDTH - 400, 5), "white", font, f"HiScore: {highscore}")

    # draws the ground
    for tile_index, tile in enumerate(ground_tile_list):
        tile.update()
        for bomb_index, bomb in enumerate(bomb_list):
            if bomb.hit_box.colliderect(tile.rect):
                del bomb_list[bomb_index]

        for mag_index, mag in enumerate(mag_list):
            if mag.rect.colliderect(tile.rect):
                mag.direction.y = 0


    # draw the cover
    bomb_list, bullet_list = left_cover.update(bomb_list, bullet_list)
    bomb_list, bullet_list = middle_cover.update(bomb_list, bullet_list)
    bomb_list, bullet_list = right_cover.update(bomb_list, bullet_list)

    # window event handler
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            run = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                if pause == False:
                    pause = True
                elif pause == True:
                    pause = False
                

    # game object update
    if sheppy.alive and not game_won and not pause:
        for ufo_index, ufo in enumerate(ufo_list):
            ufo.update()
            max_value = 500 # 1 in 500 chance to get a 25
            # 1 in bombing chance to get a 25; the smaller the returned number the greater the likelihood to spawn a bomb
            bombing_chance = max_value -(enemy_wave * 10) if max_value > 30 else 30
            if randint(1, bombing_chance) == 25:
                enemy_shot_sound_list[randint(0,2)].play()
                bomb = Bomb(ufo.pos, 4, (0,1), img_bomb)
                bomb_list.append(bomb)
            # check for bullet collision with ufos
            for bullet_index, bullet in enumerate(bullet_list):
                if bullet.rect.colliderect(ufo.rect):
                    explo_sound_list[randint(0,2)].play()
                    score += 100
                    if score > highscore:
                        highscore = score

                    #check bullet to ammo pool ratio if it is less than 3/4
                    if sheppy.ammo_pool / sheppy.max_bullets < 0.75:
                        # then there is a 20% chance of spawning a magazine
                        if randint(1, 5) == 3:
                            mag = AmmoObject(ufo.pos, 3, img_magazine, 0.75)
                            mag_list.append(mag)
                        
                    del ufo_list[ufo_index]
                    del bullet_list[bullet_index]
                    break


    
            
    #if sheppy.alive and not game_won:
        for bomb_index, bomb in enumerate(bomb_list):
            bomb.update()
            if bomb.hit_box.colliderect(sheppy.hit_box):
                chara_hit_sound_list[randint(0,3)].play()
                del bomb_list[bomb_index]
                sheppy.health -= 1
            
            if bomb.offscreen:
                del bomb_list[bomb_index]
        # check player dead or alive state
        if sheppy.health <= 0:
            sheppy.alive = False
            
        # update each bullet fired
        for index, bullet in enumerate(bullet_list):
            bullet.update()
            if bullet.offscreen:
                del bullet_list[index]

        # magazine pickup and offscreen check
        for mag_index, mag in enumerate(mag_list):
            mag.update()
            if sheppy.ammo_pool < sheppy.max_bullets:
                if mag.rect.colliderect(sheppy.hit_box):
                    mag_pickup_fx.play()
                    sheppy.ammo_pool += mag.ammo_load
                    del mag_list[mag_index]

            if mag.offscreen:
                del mag_list[mag_index]
        # update the player
        sheppy.update()

        
    # player end / game over messages
    # game over state
    if not sheppy.alive:
        draw_text((SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2), "white", font_larger, "Game Over (For now.)")
        draw_text((SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 + 100), "white", font_larger, "Press Enter to restart and continue!")
        with open("score.txt", "w") as file:
            file.write(str(highscore))
    # game won state and high score save
    if sheppy.alive and len(ufo_list) == 0:
        game_won = True
        draw_text((SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2), "white", font_larger, "You Win! (They won't be back so soon!)")
        draw_text((SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 + 100), "white", font_larger, "Press Enter to continue to the next wave!")
        with open("score.txt", "w") as file:
            file.write(str(highscore))
    # game paused state
    if pause:
        draw_text((SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2), "white", font_larger, "Game Paused!")
    

    # level and player reset
    if len(ufo_list) == 0 or sheppy.alive == False:
        keys = pg.key.get_pressed()
        if keys[pg.K_RETURN]:
            enemy_wave += 1
            ufo_list.clear()
            img_ufo_list = enemy_setup(img_ufo_list)
            if sheppy.alive == False:
                score = 0
                sheppy.alive = True
                enemy_wave = 1
            sheppy.health = sheppy.max_health
            game_won = False
            sheppy.ammo_pool = sheppy.max_bullets

    # window update
    pg.display.update()
# exitiing the interpreter
pg.quit()
sys.exit()
