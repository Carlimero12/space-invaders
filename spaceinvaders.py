import pygame
import random
import os
a = [255, 0, 0]
b = [255, 255, 0]
c = [0, 0, 255]
class Cheat():
    cheatmode = False
    hardmode = False
    hardmode_manual = 0

class Bullet:
    def __init__(self, x, y, speed=10):
        self.rect = pygame.Rect(x, y, 10, 20)
        self.speed = speed
        self.color = random.choice([a, b, c])

    def move(self):
        self.rect.y -= self.speed

class Enemy:
    def __init__(self, x, y, type="green", damage=1, speed=2):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.type = type
        self.damage = damage
        self.speed = speed

    def move(self):
        self.rect.y += self.speed

class Player:
    def __init__(self, x, y, speed=5, hp=20):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.last_shot_time = 0
    def move(self, dx, screen_width):
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= 150 and not Cheat.cheatmode == True:
            self.last_shot_time = current_time
            return Bullet(self.rect.centerx - 5, self.rect.top)
        elif Cheat.cheatmode == True and current_time - self.last_shot_time >= 50:
            self.last_shot_time = current_time
            return Bullet(self.rect.centerx - 5, self.rect.top)
        else:
            return None 


class SpaceInvaders:
    def __init__(self):
        pygame.mixer.init()
        self.last_hit_time = 0
        self.mode_hardmode = Cheat.hardmode
        self.shooting = None
        self.screen_width = 800
        self.screen_height = 600
        self.screen = None
        self.clock = None
        self.player = None
        self.aliens = []
        self.bullets = []
        self.score = 0
        self.cooldownoff = Cheat.cheatmode
        self.game_over = False
        self.font = None
        self.wave = 1
        self.hp = 20
        self.max_hp = 20
        self.frame_rate = 60
        self.player_speed = 10 
        self.aliens_speed_green = 3
        self.aliens_speed_red = 2
        self.player_move = 0
        self.highscore = 0
        self.hit_interval = 200
        self.is_paused = False
        self.last_shot_time = 0
        self.sprites_folder = "Sprites"
        if Cheat.cheatmode == True:
            self.alien_speed_bomb = 1000
        else:
            self.alien_speed_bomb = 5
        self.slowmode = False
        self.highscore_file = 'spacestats.txt'
        self.load_highscore()
        self.cheatetrun = 0
        self.switch = False
        self.switch_called = 0
        self.MY_EVENT = pygame.USEREVENT + 1

    def initialize(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        self.player = Player(self.screen_width // 2 - 25, self.screen_height - 50)

        self.load_assets()

        self.font = pygame.font.SysFont("Arial", 30)

    def load_assets(self):
        try:
            required_files = [
                "ship.png", "Alien.png", "AlienRed.png", "shoot.wav", "explosion.wav", "hit.wav", "game_over.wav", 
                "boss_hit.wav", "boss_death.wav", "retribution.wav", "boss_music.wav"
            ]
            for file in required_files:
                file_path = os.path.join(self.sprites_folder, file)
                if not os.path.isfile(file_path):
                    raise FileNotFoundError(f"Missing file: {file}")

            self.player_sprite = pygame.image.load(os.path.join(self.sprites_folder, "ship.png")).convert_alpha()
            self.player_sprite = pygame.transform.scale(self.player_sprite, (50, 50))

            self.alien_sprite = pygame.image.load(os.path.join(self.sprites_folder, "Alien.png")).convert_alpha()
            self.alien_sprite = pygame.transform.scale(self.alien_sprite, (50, 50))

            self.alien_red_sprite = pygame.image.load(os.path.join(self.sprites_folder, "AlienRed.png")).convert_alpha()
            self.alien_red_sprite = pygame.transform.scale(self.alien_red_sprite, (50, 50))

            self.bomb_sprite = pygame.image.load(os.path.join(self.sprites_folder, "bomb.png")).convert_alpha()
            self.bomb_sprite = pygame.transform.scale(self.bomb_sprite, (50, 50))

            self.shoot_sound = pygame.mixer.Sound(os.path.join(self.sprites_folder, "shoot.wav"))
            self.explosion_sound = pygame.mixer.Sound(os.path.join(self.sprites_folder, "explosion.wav"))
            self.hit_sound = pygame.mixer.Sound(os.path.join(self.sprites_folder, "hit.wav"))
            self.game_over_sound = pygame.mixer.Sound(os.path.join(self.sprites_folder, "game_over.wav"))
            self.boss_hit_sound = pygame.mixer.Sound(os.path.join(self.sprites_folder, "boss_hit.wav"))
            self.boss_death_sound = pygame.mixer.Sound(os.path.join(self.sprites_folder, "boss_death.wav"))
            self.background_music = pygame.mixer.Sound(os.path.join(self.sprites_folder, "retribution.wav"))
            self.boss_music = pygame.mixer.Sound(os.path.join(self.sprites_folder, "boss_music.wav"))

        except Exception as e:
            print(f"Error loading assets: {e}")
            raise e

    def load_highscore(self):
        if os.path.exists(self.highscore_file):
            with open(self.highscore_file, 'r') as f:
                try:
                    self.highscore = int(f.read().strip())
                except ValueError:
                    self.highscore = 0
        else:
            with open(self.highscore_file, 'w') as f:
                f.write('0')
            self.highscore = 0

    def update_highscore(self):
        if self.score > self.highscore and self.cheatetrun <= 0:
            self.highscore = self.score
            with open(self.highscore_file, 'w') as f:
                f.write(str(self.highscore))

    def create_aliens(self):
        aliens = []
        num_aliens = self.wave * 3
        if Cheat.hardmode == True: minimum = 5 
        else: minimum = 25
        if num_aliens > minimum:
            tomuch = num_aliens - minimum
            num_aliens = num_aliens - tomuch
        rows = 5
        cols = num_aliens // rows
        alien_types = [
            ("green", 0.5),    # 50% chance for green aliens
            ("red", 0.3),      # 30% chance for red aliens
            ("bomb", 0.01)   # 0.01% chance for bomb aliens
        ]

        for row in range(rows):
            for col in range(cols):
                x = random.randint(50, self.screen_width - 50)
                y = random.randint(-100, -50)
                random_choice = random.random()
                cumulative_probability = 0
                alien_type = "green"
                if Cheat.hardmode == False:
                    for atype, probability in alien_types:
                        cumulative_probability += probability
                        if random_choice <= cumulative_probability:
                            alien_type = atype
                            break
                else:
                    alien_type = "bomb"

                if alien_type == "red":
                    alien = Enemy(x, y, type=alien_type, damage=5, speed=self.aliens_speed_red)
                elif alien_type == "green":
                    alien = Enemy(x, y, type=alien_type, damage=1, speed=self.aliens_speed_green)
                elif alien_type == "bomb":
                    alien = Enemy(x, y, type=alien_type, damage=self.hp, speed=self.alien_speed_bomb)
                aliens.append(alien)

        return aliens

    def move_aliens(self):
        if not self.is_paused == True:
            for alien in self.aliens[:]:
                alien.move()
                if alien.rect.y > self.screen_height-2:
                    alien.rect.y = random.randint(-100, -50)
                    alien.rect.x = random.randint(50, self.screen_width - 50)

    def shoot_bullet(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_shot_time >= 150 and not Cheat.cheatmode == True:
            self.shoot_sound.play()
            bullet = self.player.shoot()
            if bullet:
                self.bullets.append(bullet)
            self.last_shot_time = current_time
        elif Cheat.cheatmode == True and current_time - self.last_shot_time >= 50:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.append(bullet)
        else:
            return None

    def move_bullets(self):
        for bullet in self.bullets[:]:
            if bullet is None:
                continue

            bullet.move()

            if bullet.rect.y < 0:
                self.bullets.remove(bullet)
                continue

            for alien in self.aliens[:]:
                if bullet.rect.colliderect(alien.rect):
                    self.score += 1
                    self.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    heal = "n" if random.random() > 0.01 else "y"
                    if alien.type == "bomb":
                        self.hp = self.hp + 20
                        self.boss_death_sound.play()
                    elif heal == 'y' and not alien.type == "bomb":
                        self.explosion_sound.play()
                        SpaceInvaders.heal_player(self, amount=random.randint(1,3))
                    elif heal == 'n' and not alien.type == "bomb":
                        self.explosion_sound.play()
                        heal = None
                    break

    def heal_player(self, amount):
        if not Cheat.hardmode == True:
            self.hp = min(self.hp + amount, self.max_hp)
        else:
            self.hp = min(self.hp + amount, self.max_hp - 2)

    def handle_collisions(self):
        for alien in self.aliens[:]:
            current_time = pygame.time.get_ticks()
            if alien.rect.colliderect(self.player.rect) and current_time - self.last_hit_time >= self.hit_interval:
                notunder = self.hp - 100
                if alien.type == "bomb" and notunder <= 0:
                    self.hp -= 100
                elif alien.type == "bomb" and self.hp < 100:
                    self.hp = 0
                else:
                    self.hp -= alien.damage
                self.aliens.remove(alien)
                self.last_hit_time = current_time

                if self.hp <= 0:
                    self.hp = 0
                    if alien.type == "bomb":
                        self.boss_hit_sound.play(loops=2)
                    self.game_over = True
                    break
    
    def switchchange(self):
        if self.switch_called >= 0:
            self.switch_called += 1
            pygame.time.set_timer(millis=10000, event=self.MY_EVENT)

    def run_game(self):
        self.background_music.play(loops=-1)
        MY_EVENT = self.MY_EVENT
        while not self.game_over:
            if self.shooting == True and self.is_paused == False:
                self.shoot_bullet()
            elif self.wave >= 20:
                Cheat.hardmode = True
            elif self.is_paused == True:
                self.background_music.stop()
                self.shoot_sound.stop()
                self.player_speed = 0
            elif self.is_paused == False and self.slowmode == False:
                self.player_speed = 10
            elif self.slowmode == True and self.is_paused == False:
                self.player_speed = 5
            elif self.slowmode == False and self.is_paused == False:
                self.player_speed = 10
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == MY_EVENT:
                    Cheat.cheatmode = False
                    Cheat.hardmode = True
                    self.alien_speed_bomb = 1000
                    self.shooting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player_move = -self.player_speed
                    elif event.key == pygame.K_h and self.mode_hardmode == False:
                        Cheat.hardmode = True
                        print("on")
                        Cheat.hardmode_manual += 1
                    elif event.key == pygame.K_7:
                        if Cheat.cheatmode == True and self.mode_hardmode == False and self.is_paused == False:
                            Cheat.cheatmode = False
                            print("ok then not")
                        elif Cheat.cheatmode == False and self.mode_hardmode == False and self.is_paused == False:
                            Cheat.cheatmode = True
                            print("cheater")
                            self.switchchange()
                            self.cheatetrun += 1
                    elif event.key == pygame.K_p:
                        if self.is_paused == True:
                            self.is_paused = False
                            print("unpaused")
                            self.background_music.stop()
                            self.background_music.play(loops=-1)
                        elif self.is_paused == False:
                            self.is_paused = True
                            print("paused")
                    elif event.key == pygame.K_x and self.is_paused == False:
                        if self.slowmode == True:
                            self.slowmode = False
                            print("Slowmode off")
                        else:
                            self.slowmode = True
                            print("Slowmode on")
                    elif event.key == pygame.K_r:
                        self.update_highscore()
                        for alien in self.aliens[:]:
                            self.aliens.remove(alien)
                        self.wave = 1
                        self.hp = self.max_hp
                        self.score = 0
                        self.is_paused = False
                        Cheat.cheatmode = False
                        Cheat.hardmode = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player_move = self.player_speed
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_z:
                        if Cheat.cheatmode == True and self.is_paused == False:
                            self.shooting = True
                        elif not self.is_paused == True:
                            self.shoot_bullet()
                elif event.type == pygame.KEYUP:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d,] and self.is_paused == False:
                        self.player_move = 0
                    elif event.key == pygame.K_SPACE and Cheat.cheatmode == True and self.is_paused == False or event.key == pygame.K_z and Cheat.cheatmode == True and self.is_paused == False:
                        self.shooting = False
            self.player.move(self.player_move, self.screen_width)
            self.move_aliens()
            self.move_bullets()
            self.handle_collisions()

            self.screen.blit(self.player_sprite, self.player.rect)

            for alien in self.aliens:
                if alien.type == "red":
                    self.screen.blit(self.alien_red_sprite, alien.rect)
                elif alien.type == "green":
                    self.screen.blit(self.alien_sprite, alien.rect)
                elif alien.type == "bomb":
                    self.screen.blit(self.bomb_sprite, alien.rect)

            for bullet in self.bullets:
                pygame.draw.rect(self.screen, bullet.color, bullet.rect)

            num_aliens = len(self.aliens)
            score_text = self.font.render(f"Score: {self.score}", True, (0, 155, 155))
            health_text = self.font.render(f"Health: {self.hp}", True, (0, 155, 155))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(health_text, (10, 40))

            highscore = self.font.render(f"Highscore: {self.highscore}", True, (b))
            self.screen.blit(highscore, (self.screen_width // 2 - 100, 10))

            wave_text = self.font.render(f"Wave: {self.wave}", True, (0, 155, 155))
            self.screen.blit(wave_text, (self.screen_width - 150, 10))

            enemies_left = self.font.render(f"Aliens_Left: {num_aliens}", True, (0, 155, 155))
            self.screen.blit(enemies_left, (10, 80))

            if self.game_over and self.cheatetrun <= 0 and Cheat.hardmode_manual <= 0:
                game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
                self.screen.blit(game_over_text, (self.screen_width // 2 - 100, self.screen_height // 2 - 30))

            elif self.game_over and not self.cheatetrun <= 0:
                DeathScreen = [
                    "Game Over.",
                    "Highscore is unsaved CHEATER!"
                ]
                # Starting position for multi-line text
                start_y = self.screen_height // 2 - 30

                for index, line in enumerate(DeathScreen):
                    rendered_line = self.font.render(line, True, (255, 0, 0))
                    # Adjust line height (e.g., 40 pixels apart)
                    line_y = start_y + index * 40
                    self.screen.blit(rendered_line, (self.screen_width // 2 - 150, line_y))

            elif self.game_over and not self.cheatetrun <= 0 and Cheat.hardmode_manual >= 0:
                DeathScreen = [
                    "Game Over.",
                    "Highscore Saved in other file!",
                    "Because of Hardmode!"
                ]
                # Starting position for multi-line text
                start_y = self.screen_height // 2 - 30

                for index, line in enumerate(DeathScreen):
                    rendered_line = self.font.render(line, True, (255, 0, 0))
                    # Adjust line height (e.g., 40 pixels apart)
                    line_y = start_y + index * 40
                    self.screen.blit(rendered_line, (self.screen_width // 2 - 150, line_y))

            pygame.display.update()
            self.clock.tick(self.frame_rate)

            if len(self.aliens) == 0:
                self.wave += 1
                self.aliens = self.create_aliens()
        
        if self.cheatetrun <= 0 and Cheat.hardmode_manual == False:
            self.update_highscore()
        pygame.mixer.Sound.stop(self.background_music)
        pygame.mixer.Sound.play(self.game_over_sound)
        pygame.time.delay(12000)
        pygame.quit()

if __name__ == "__main__":
    game_ended = False
    game = SpaceInvaders()
    def run_loop():
        while not game_ended == True:
            game.initialize()
            game.run_game()
            answer = input("Wanna try again? (y/n)\n ")
            if answer == "y":
                game_ended = False
            elif answer == "n":
                game_ended == True
            else:
                print("please reopen the game via the File(Reason: Invalid Operator)")
