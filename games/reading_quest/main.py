import asyncio
import pygame
import random
import math

# ── Constants ──────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
FPS           = 60
ENEMY_SPEED   = 1.2
SPAWN_RATE    = 100  # frames between spawns

# Colors
BLACK      = (0,   0,   10)
WHITE      = (255, 255, 255)
GREEN      = (80,  255, 160)
RED        = (255, 70,  70)
BLUE       = (60,  140, 255)
PURPLE     = (180, 80,  255)
YELLOW     = (255, 230, 50)
CYAN       = (50,  230, 255)
ORANGE     = (255, 160, 50)
DARK_GRAY  = (20,  20,  40)
STAR_COLOR = (200, 200, 255)

# ── Question Bank ─────────────────────────────────────────
# Format: {"prompt": "...", "correct": "word", "wrong": ["w1","w2","w3"]}
QUESTIONS = [
    # Sight words
    {"prompt": "Zap the word that means the opposite of 'off'",   "correct": "on",     "wrong": ["up", "no", "go"]},
    {"prompt": "Zap the word that means 'not big'",               "correct": "small",  "wrong": ["tall", "fast", "bright"]},
    {"prompt": "Zap the sight word: something you do with a book","correct": "read",   "wrong": ["jump", "blue", "over"]},
    {"prompt": "Zap the word that is a color",                    "correct": "red",    "wrong": ["run", "said", "they"]},
    {"prompt": "Zap the word that means 'not in'",                "correct": "out",    "wrong": ["and", "the", "was"]},
    {"prompt": "Zap the sight word: opposite of 'she'",           "correct": "he",     "wrong": ["me", "be", "we"]},
    {"prompt": "Zap the word that means 'myself'",                "correct": "me",     "wrong": ["my", "am", "is"]},
    {"prompt": "Zap the sight word that means 'also'",            "correct": "too",    "wrong": ["to", "two", "do"]},
    {"prompt": "Zap the word that means 'more than one'",         "correct": "many",   "wrong": ["much", "more", "most"]},
    {"prompt": "Zap the sight word: where you live",              "correct": "home",   "wrong": ["some", "come", "dome"]},

    # CVC words
    {"prompt": "Zap the CVC word: a pet that says 'meow'",        "correct": "cat",    "wrong": ["bat", "hat", "rat"]},
    {"prompt": "Zap the CVC word: opposite of 'cold'",            "correct": "hot",    "wrong": ["hop", "hog", "hob"]},
    {"prompt": "Zap the CVC word: a baby dog",                    "correct": "pup",    "wrong": ["pub", "bud", "bug"]},
    {"prompt": "Zap the CVC word: what you sit on",               "correct": "mat",    "wrong": ["man", "map", "mad"]},
    {"prompt": "Zap the CVC word: a flying animal",               "correct": "bat",    "wrong": ["bad", "ban", "bag"]},
    {"prompt": "Zap the CVC word: used to cut",                   "correct": "axe",    "wrong": ["age", "ace", "ape"]},
    {"prompt": "Zap the CVC word: a container for fish",          "correct": "tub",    "wrong": ["rub", "sub", "hub"]},
    {"prompt": "Zap the CVC word: a round toy",                   "correct": "ball",   "wrong": ["tall", "call", "fall"]},
    {"prompt": "Zap the CVC word: what light does",               "correct": "lit",    "wrong": ["bit", "fit", "hit"]},
    {"prompt": "Zap the CVC word: you do this in bed",            "correct": "nap",    "wrong": ["lap", "tap", "cap"]},
]

# ── Stars (background) ────────────────────────────────────
class Star:
    def __init__(self):
        self.x     = random.randint(0, WIDTH)
        self.y     = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.3, 1.5)
        self.size  = random.choice([1, 1, 1, 2])
        self.alpha = random.randint(120, 255)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, STAR_COLOR, (int(self.x), int(self.y)), self.size)


# ── Laser ─────────────────────────────────────────────────
class Laser:
    def __init__(self, x, y):
        self.x    = x
        self.y    = y
        self.speed = 14
        self.alive = True

    def update(self):
        self.y -= self.speed
        if self.y < -20:
            self.alive = False

    def draw(self, surface):
        # Glowing laser bolt
        pygame.draw.line(surface, WHITE,  (self.x, self.y),      (self.x, self.y + 18), 2)
        pygame.draw.line(surface, CYAN,   (self.x, self.y + 2),  (self.x, self.y + 16), 4)
        pygame.draw.line(surface, WHITE,  (self.x, self.y + 5),  (self.x, self.y + 13), 1)

    def rect(self):
        return pygame.Rect(self.x - 4, self.y, 8, 20)


# ── Enemy Word ─────────────────────────────────────────────
class EnemyWord:
    COLORS_WRONG   = [RED,    ORANGE, PURPLE]
    COLORS_CORRECT = [GREEN,  CYAN,   YELLOW]

    def __init__(self, word, x, is_correct, font):
        self.word       = word
        self.x          = float(x)
        self.y          = float(-40)
        self.is_correct = is_correct
        self.font       = font
        self.speed      = ENEMY_SPEED + random.uniform(0, 0.8)
        self.alive      = True
        self.wobble     = random.uniform(0, math.pi * 2)
        self.wobble_amp = random.uniform(0.4, 1.2)
        self.color      = random.choice(self.COLORS_CORRECT if is_correct else self.COLORS_WRONG)
        self.hit_flash  = 0

        # Ship shape size based on word length
        text_surf    = font.render(word, True, WHITE)
        self.tw      = text_surf.get_width()
        self.th      = text_surf.get_height()
        self.w       = self.tw + 28
        self.h       = self.th + 18

    def update(self, frame):
        self.y        += self.speed
        self.wobble   += 0.04
        self.x        += math.sin(self.wobble) * self.wobble_amp
        self.x         = max(self.w // 2 + 10, min(WIDTH - self.w // 2 - 10, self.x))
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y)
        hw = self.w // 2
        hh = self.h // 2

        # Body
        color = WHITE if self.hit_flash > 0 else self.color
        body_rect = pygame.Rect(cx - hw, cy - hh, self.w, self.h)
        pygame.draw.rect(surface, DARK_GRAY, body_rect, border_radius=8)
        pygame.draw.rect(surface, color, body_rect, width=2, border_radius=8)

        # Alien "wings"
        wing_l = [(cx - hw, cy), (cx - hw - 12, cy - 8), (cx - hw - 12, cy + 8)]
        wing_r = [(cx + hw, cy), (cx + hw + 12, cy - 8), (cx + hw + 12, cy + 8)]
        pygame.draw.polygon(surface, color, wing_l)
        pygame.draw.polygon(surface, color, wing_r)

        # "Cannon" nub at bottom
        pygame.draw.rect(surface, color, (cx - 4, cy + hh, 8, 8))

        # Word label
        label = self.font.render(self.word, True, WHITE if self.hit_flash == 0 else DARK_GRAY)
        surface.blit(label, label.get_rect(center=(cx, cy)))

    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def hit(self):
        self.hit_flash = 8
        self.alive     = False


# ── Explosion Particle ─────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        angle     = random.uniform(0, math.pi * 2)
        speed     = random.uniform(2, 7)
        self.x    = x
        self.y    = y
        self.vx   = math.cos(angle) * speed
        self.vy   = math.sin(angle) * speed
        self.life = random.randint(20, 45)
        self.max  = self.life
        self.color= color
        self.size = random.randint(2, 6)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.15
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max))
        r, g, b = self.color
        fade = (min(255, r), min(255, g), min(255, b))
        pygame.draw.circle(surface, fade, (int(self.x), int(self.y)), self.size)


# ── Player Ship ────────────────────────────────────────────
class Player:
    W, H   = 44, 38
    SPEED  = 6

    def __init__(self):
        self.x      = WIDTH // 2
        self.y      = HEIGHT - 70
        self.shoot_cooldown = 0
        self.engine_flicker = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]  and self.x - self.W // 2 > 0:
            self.x -= self.SPEED
        if keys[pygame.K_RIGHT] and self.x + self.W // 2 < WIDTH:
            self.x += self.SPEED
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.engine_flicker = (self.engine_flicker + 1) % 10

    def draw(self, surface):
        cx = self.x
        cy = self.y
        # Engine glow (flicker)
        if self.engine_flicker < 6:
            pygame.draw.ellipse(surface, ORANGE, (cx - 8, cy + 20, 16, 12))
            pygame.draw.ellipse(surface, YELLOW, (cx - 4, cy + 22, 8, 6))

        # Body
        body = [(cx, cy - 18), (cx - 18, cy + 18), (cx + 18, cy + 18)]
        pygame.draw.polygon(surface, BLUE, body)
        pygame.draw.polygon(surface, CYAN, body, 2)

        # Cockpit
        pygame.draw.ellipse(surface, CYAN, (cx - 7, cy - 6, 14, 14))
        pygame.draw.ellipse(surface, WHITE, (cx - 4, cy - 3, 6, 6))

        # Wings
        lwing = [(cx - 18, cy + 18), (cx - 30, cy + 28), (cx - 10, cy + 18)]
        rwing = [(cx + 18, cy + 18), (cx + 30, cy + 28), (cx + 10, cy + 18)]
        pygame.draw.polygon(surface, PURPLE, lwing)
        pygame.draw.polygon(surface, PURPLE, rwing)
        pygame.draw.polygon(surface, CYAN, lwing, 1)
        pygame.draw.polygon(surface, CYAN, rwing, 1)

    def try_shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 18
            return Laser(self.x, self.y - 20)
        return None

    def rect(self):
        return pygame.Rect(self.x - self.W // 2, self.y - self.H // 2, self.W, self.H)


# ── HUD helpers ────────────────────────────────────────────
def draw_lives(surface, lives, icon_font):
    for i in range(lives):
        x = WIDTH - 30 - i * 28
        # Little ship icon for each life
        pts = [(x, 10), (x - 8, 22), (x + 8, 22)]
        pygame.draw.polygon(surface, CYAN, pts)


def draw_prompt_box(surface, prompt, font, big_font):
    box = pygame.Rect(10, 10, WIDTH - 20, 50)
    pygame.draw.rect(surface, DARK_GRAY, box, border_radius=10)
    pygame.draw.rect(surface, CYAN, box, width=2, border_radius=10)
    text = big_font.render(f"⚡ {prompt}", True, YELLOW)
    surface.blit(text, text.get_rect(centerx=WIDTH // 2, centery=35))


# ── Main ───────────────────────────────────────────────────
async def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Word Blaster -- Sight Word Shooter")
    font     = pygame.font.SysFont("Consolas", 19, bold=True)
    big_font = pygame.font.SysFont("Consolas", 22, bold=True)
    hud_font = pygame.font.SysFont("Consolas", 17)
    clk      = pygame.time.Clock()

    # Stars
    stars = [Star() for _ in range(120)]

    player        = Player()
    lasers        = []
    enemies       = []
    particles     = []
    score         = 0
    lives         = 3
    frame         = 0
    q_index       = 0
    random.shuffle(QUESTIONS)
    current_q     = QUESTIONS[q_index % len(QUESTIONS)]
    flash_msg     = ""
    flash_color   = GREEN
    flash_timer   = 0
    combo         = 0

    running = True
    while running:
        clk.tick(FPS)
        frame += 1

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    laser = player.try_shoot()
                    if laser:
                        lasers.append(laser)

        keys = pygame.key.get_pressed()
        player.update(keys)

        # ── Spawn enemy words ──
        if frame % SPAWN_RATE == 0:
            pool    = [current_q["correct"]] + random.sample(current_q["wrong"], min(3, len(current_q["wrong"])))
            random.shuffle(pool)
            x_slots = [120, 280, 440, 600, 720]
            random.shuffle(x_slots)
            for i, word in enumerate(pool[:len(x_slots)]):
                enemies.append(EnemyWord(word, x_slots[i], word == current_q["correct"], font))

        # ── Update ──
        for s in stars:
            s.update()
        for l in lasers[:]:
            l.update()
            if not l.alive:
                lasers.remove(l)
        for e in enemies[:]:
            e.update(frame)
            if e.y > HEIGHT + 60:
                if e.is_correct:
                    # missed the correct word — lose a life
                    lives     -= 1
                    combo      = 0
                    flash_msg   = "Missed it! -1"
                    flash_color = RED
                    flash_timer = 55
                enemies.remove(e)
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ── Laser ↔ Enemy collisions ──
        for l in lasers[:]:
            for e in enemies[:]:
                if l.alive and e.alive and l.rect().colliderect(e.rect()):
                    l.alive = False
                    if e.is_correct:
                        # 🎉 Correct!
                        combo  += 1
                        pts     = 100 + (combo - 1) * 25
                        score  += pts
                        flash_msg   = f"NICE! +{pts}" + (" COMBO x{combo}!" if combo > 1 else "")
                        flash_color = GREEN
                        flash_timer = 65
                        q_index    += 1
                        current_q   = QUESTIONS[q_index % len(QUESTIONS)]
                        # Boom particles
                        for _ in range(28):
                            particles.append(Particle(e.x, e.y, random.choice([GREEN, CYAN, YELLOW])))
                        # Clear remaining enemies for this round
                        enemies.clear()
                    else:
                        # Wrong word shot
                        lives      -= 1
                        combo       = 0
                        flash_msg   = "Wrong word! -1"
                        flash_color = RED
                        flash_timer = 65
                        for _ in range(14):
                            particles.append(Particle(e.x, e.y, random.choice([RED, ORANGE])))
                        enemies.remove(e)
                    break

        # ── Player ship hit by enemy reaching bottom boundary ──
        player_rect = player.rect()
        for e in enemies[:]:
            if e.alive and e.y > HEIGHT - 90 and e.rect().colliderect(player_rect):
                lives -= 1
                combo  = 0
                flash_msg   = "Enemy too close! -1"
                flash_color = RED
                flash_timer = 55
                enemies.remove(e)

        if lives <= 0:
            running = False

        if flash_timer > 0:
            flash_timer -= 1

        # ── Draw ────────────────────────────────────────────
        screen.fill(BLACK)

        # Starfield
        for s in stars:
            s.draw(screen)

        # Ground line / boundary
        pygame.draw.line(screen, (40, 40, 80), (0, HEIGHT - 45), (WIDTH, HEIGHT - 45), 1)

        # Enemies
        for e in enemies:
            if e.alive:
                e.draw(screen)

        # Lasers
        for l in lasers:
            l.draw(screen)

        # Particles
        for p in particles:
            p.draw(screen)

        # Player
        player.draw(screen)

        # Prompt box
        draw_prompt_box(screen, current_q["prompt"], font, big_font)

        # HUD - Score
        score_surf = big_font.render(f"SCORE: {score}", True, CYAN)
        screen.blit(score_surf, (14, 62))

        # HUD - Lives
        lives_label = hud_font.render("LIVES:", True, WHITE)
        screen.blit(lives_label, (WIDTH - 200, 62))
        draw_lives(screen, lives, hud_font)

        # Combo indicator
        if combo >= 2:
            combo_surf = big_font.render(f"COMBO x{combo}", True, ORANGE)
            screen.blit(combo_surf, combo_surf.get_rect(centerx=WIDTH // 2, y=68))

        # Flash message
        if flash_timer > 0:
            alpha    = min(255, flash_timer * 5)
            msg_surf = big_font.render(flash_msg, True, flash_color)
            screen.blit(msg_surf, msg_surf.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 - 30))

        # Controls hint
        hint = hud_font.render("← → Move   |   SPACE Shoot", True, (60, 60, 100))
        screen.blit(hint, hint.get_rect(centerx=WIDTH // 2, y=HEIGHT - 22))

        pygame.display.flip()
        await asyncio.sleep(0)

    # ── Game Over Screen ──
    for _ in range(FPS * 5):
        screen.fill(BLACK)
        for s in stars:
            s.update()
            s.draw(screen)
        go   = big_font.render("GAME OVER", True, RED)
        sc   = big_font.render(f"Final Score: {score}", True, YELLOW)
        rest = font.render("Refresh to play again!", True, CYAN)
        screen.blit(go,   go.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 - 60))
        screen.blit(sc,   sc.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2))
        screen.blit(rest, rest.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 + 60))
        pygame.display.flip()
        clk.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())