import asyncio
import pygame
import random
import math

# ── Constants ──────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
FPS           = 60
ENEMY_SPEED   = 1.2
SPAWN_RATE    = 90   # frames between spawns (slightly faster than before)

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

# ── Question Bank (2nd Grade) ─────────────────────────────
# Format: {"prompt": "...", "correct": "word", "wrong": ["w1","w2","w3"]}
QUESTIONS = [
    # Dolch 2nd grade sight words — meaning / usage prompts
    {"prompt": "Zap the word that means 'a long time ago'",               "correct": "once",    "wrong": ["always", "often", "never"]},
    {"prompt": "Zap the word that means to pull toward you",              "correct": "bring",   "wrong": ["carry", "toss", "place"]},
    {"prompt": "Zap the word that means 'close to'",                      "correct": "near",    "wrong": ["under", "above", "around"]},
    {"prompt": "Zap the word that describes something done many times",   "correct": "often",   "wrong": ["once", "soon", "never"]},
    {"prompt": "Zap the word that means 'in addition to'",                "correct": "also",    "wrong": ["only", "just", "even"]},
    {"prompt": "Zap the word that means 'at this time'",                  "correct": "now",     "wrong": ["then", "soon", "later"]},
    {"prompt": "Zap the sight word: the person telling a story uses this","correct": "us",      "wrong": ["them", "those", "their"]},
    {"prompt": "Zap the word that is the opposite of 'found'",            "correct": "lost",    "wrong": ["kept", "gave", "told"]},
    {"prompt": "Zap the word that means 'every single one'",              "correct": "every",   "wrong": ["any", "some", "most"]},
    {"prompt": "Zap the word that means 'began to grow'",                 "correct": "grew",    "wrong": ["fell", "flew", "drew"]},
    {"prompt": "Zap the word that means 'at no time'",                    "correct": "never",   "wrong": ["always", "often", "still"]},
    {"prompt": "Zap the word that means 'to start'",                      "correct": "begin",   "wrong": ["carry", "leave", "those"]},
    {"prompt": "Zap the word that means 'more than a few but not all'",   "correct": "many",    "wrong": ["both", "none", "few"]},
    {"prompt": "Zap the word that means 'the same as'",                   "correct": "both",    "wrong": ["each", "much", "only"]},
    {"prompt": "Zap the word that means the opposite of 'before'",        "correct": "after",   "wrong": ["until", "since", "while"]},
    {"prompt": "Zap the word that means 'to be aware of'",                "correct": "know",    "wrong": ["show", "grow", "blow"]},
    {"prompt": "Zap the word that means 'to make something go away'",     "correct": "clean",   "wrong": ["bring", "carry", "start"]},
    {"prompt": "Zap the word that means 'to move through the air'",       "correct": "fly",     "wrong": ["dry", "try", "cry"]},
    {"prompt": "Zap the word that means 'very large'",                    "correct": "large",   "wrong": ["close", "light", "short"]},
    {"prompt": "Zap the word that means 'to put in a place'",             "correct": "place",   "wrong": ["space", "trace", "grace"]},
    {"prompt": "Zap the word that means 'the piece left over'",           "correct": "last",    "wrong": ["past", "fast", "cast"]},
    {"prompt": "Zap the word that means 'to move very fast on foot'",     "correct": "run",     "wrong": ["sun", "fun", "gun"]},
    {"prompt": "Zap the word that means 'belonging to them'",             "correct": "their",   "wrong": ["there", "they", "these"]},
    {"prompt": "Zap the word that means 'not the same'",                  "correct": "different","wrong": ["other", "better", "another"]},
    {"prompt": "Zap the word that means 'in the direction of'",           "correct": "toward",  "wrong": ["around", "behind", "inside"]},
    {"prompt": "Zap the word that means 'to think something is true'",    "correct": "believe", "wrong": ["receive", "achieve", "retrieve"]},
    {"prompt": "Zap the word that means 'not ever again'",                "correct": "stop",    "wrong": ["drop", "crop", "prop"]},
    {"prompt": "Zap the word that means 'to make a choice'",              "correct": "decide",  "wrong": ["divide", "provide", "beside"]},
    {"prompt": "Zap the word that means 'not warm'",                      "correct": "cold",    "wrong": ["bold", "fold", "hold"]},
    {"prompt": "Zap the word that means 'to go somewhere and come back'", "correct": "return",  "wrong": ["remain", "report", "remind"]},

    # Vocabulary / word meaning prompts
    {"prompt": "Zap the word that means 'a story that is not true'",      "correct": "fiction", "wrong": ["section", "mention", "caption"]},
    {"prompt": "Zap the word that means 'to give an answer'",             "correct": "reply",   "wrong": ["supply", "apply", "imply"]},
    {"prompt": "Zap the word that means 'the middle of something'",       "correct": "center",  "wrong": ["corner", "border", "shelter"]},
    {"prompt": "Zap the word that means 'to move quietly and carefully'", "correct": "creep",   "wrong": ["sweep", "steep", "sleep"]},
    {"prompt": "Zap the word that is a synonym for 'happy'",              "correct": "glad",    "wrong": ["mad", "bad", "sad"]},
    {"prompt": "Zap the word that means 'to say words out loud'",         "correct": "speak",   "wrong": ["sneak", "bleak", "freak"]},
    {"prompt": "Zap the word that means 'not loud'",                      "correct": "quiet",   "wrong": ["quite", "quote", "quilt"]},
    {"prompt": "Zap the word that means 'a type of weather with ice'",    "correct": "snow",    "wrong": ["slow", "show", "flow"]},
    {"prompt": "Zap the word that means 'to look at carefully'",          "correct": "watch",   "wrong": ["catch", "match", "patch"]},
    {"prompt": "Zap the word that means 'not heavy'",                     "correct": "light",   "wrong": ["night", "right", "sight"]},
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
        self.x     = x
        self.y     = y
        self.speed = 14
        self.alive = True

    def update(self):
        self.y -= self.speed
        if self.y < -20:
            self.alive = False

    def draw(self, surface):
        pygame.draw.line(surface, WHITE, (self.x, self.y),     (self.x, self.y + 18), 2)
        pygame.draw.line(surface, CYAN,  (self.x, self.y + 2), (self.x, self.y + 16), 4)
        pygame.draw.line(surface, WHITE, (self.x, self.y + 5), (self.x, self.y + 13), 1)

    def rect(self):
        return pygame.Rect(self.x - 4, self.y, 8, 20)


# ── Enemy Word ─────────────────────────────────────────────
class EnemyWord:
    COLORS_WRONG   = [RED,   ORANGE, PURPLE]
    COLORS_CORRECT = [GREEN, CYAN,   YELLOW]

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

        text_surf = font.render(word, True, WHITE)
        self.tw   = text_surf.get_width()
        self.th   = text_surf.get_height()
        self.w    = self.tw + 28
        self.h    = self.th + 18

    def update(self, frame):
        self.y       += self.speed
        self.wobble  += 0.04
        self.x       += math.sin(self.wobble) * self.wobble_amp
        self.x        = max(self.w // 2 + 10, min(WIDTH - self.w // 2 - 10, self.x))
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y)
        hw = self.w // 2
        hh = self.h // 2

        color     = WHITE if self.hit_flash > 0 else self.color
        body_rect = pygame.Rect(cx - hw, cy - hh, self.w, self.h)
        pygame.draw.rect(surface, DARK_GRAY, body_rect, border_radius=8)
        pygame.draw.rect(surface, color, body_rect, width=2, border_radius=8)

        wing_l = [(cx - hw, cy), (cx - hw - 12, cy - 8), (cx - hw - 12, cy + 8)]
        wing_r = [(cx + hw, cy), (cx + hw + 12, cy - 8), (cx + hw + 12, cy + 8)]
        pygame.draw.polygon(surface, color, wing_l)
        pygame.draw.polygon(surface, color, wing_r)
        pygame.draw.rect(surface, color, (cx - 4, cy + hh, 8, 8))

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
        r, g, b = self.color
        pygame.draw.circle(surface, (min(255, r), min(255, g), min(255, b)),
                           (int(self.x), int(self.y)), self.size)


# ── Player Ship ────────────────────────────────────────────
class Player:
    W, H  = 44, 38
    SPEED = 6

    def __init__(self):
        self.x              = WIDTH // 2
        self.y              = HEIGHT - 70
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
        if self.engine_flicker < 6:
            pygame.draw.ellipse(surface, ORANGE, (cx - 8, cy + 20, 16, 12))
            pygame.draw.ellipse(surface, YELLOW, (cx - 4, cy + 22, 8, 6))

        body  = [(cx, cy - 18), (cx - 18, cy + 18), (cx + 18, cy + 18)]
        pygame.draw.polygon(surface, BLUE, body)
        pygame.draw.polygon(surface, CYAN, body, 2)

        pygame.draw.ellipse(surface, CYAN,  (cx - 7, cy - 6, 14, 14))
        pygame.draw.ellipse(surface, WHITE, (cx - 4, cy - 3, 6, 6))

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
def draw_lives(surface, lives):
    for i in range(lives):
        x   = WIDTH - 30 - i * 28
        pts = [(x, 10), (x - 8, 22), (x + 8, 22)]
        pygame.draw.polygon(surface, CYAN, pts)


def wrap_prompt(prompt, font, max_width):
    """Break prompt into lines that fit within max_width."""
    words = prompt.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        if font.size(test)[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_prompt_box(surface, prompt, font):
    lines = wrap_prompt(f">> {prompt}", font, WIDTH - 40)
    line_h    = font.get_height() + 4
    box_h     = line_h * len(lines) + 18
    box       = pygame.Rect(10, 6, WIDTH - 20, box_h)
    pygame.draw.rect(surface, DARK_GRAY, box, border_radius=10)
    pygame.draw.rect(surface, CYAN, box, width=2, border_radius=10)
    for i, line in enumerate(lines):
        text = font.render(line, True, YELLOW)
        surface.blit(text, text.get_rect(centerx=WIDTH // 2, centery=6 + 9 + line_h * i + line_h // 2))
    return box_h   # return height so HUD elements can offset below it


# ── Score → XP conversion ──────────────────────────────────
def score_to_xp(score):
    """Simple linear: 1 XP per 5 points, capped at 500."""
    return min(500, score // 5)


# ── Main ───────────────────────────────────────────────────
async def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Word Blaster — 2nd Grade Sight Words")
    font     = pygame.font.SysFont("Consolas", 19, bold=True)
    big_font = pygame.font.SysFont("Consolas", 22, bold=True)
    hud_font = pygame.font.SysFont("Consolas", 17)
    clk      = pygame.time.Clock()

    stars = [Star() for _ in range(120)]

    player    = Player()
    lasers    = []
    enemies   = []
    particles = []
    score     = 0
    lives     = 3
    frame     = 0
    q_index   = 0

    random.shuffle(QUESTIONS)
    current_q   = QUESTIONS[q_index % len(QUESTIONS)]
    flash_msg   = ""
    flash_color = GREEN
    flash_timer = 0
    combo       = 0

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

        # ── Spawn enemies ──
        if frame % SPAWN_RATE == 0:
            wrong_choices = random.sample(current_q["wrong"], min(3, len(current_q["wrong"])))
            pool    = [current_q["correct"]] + wrong_choices
            random.shuffle(pool)
            x_slots = [100, 250, 400, 560, 700]
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
                    lives      -= 1
                    combo       = 0
                    flash_msg   = "Missed it! -1 Life"
                    flash_color = RED
                    flash_timer = 55
                enemies.remove(e)
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ── Collisions ──
        for l in lasers[:]:
            for e in enemies[:]:
                if l.alive and e.alive and l.rect().colliderect(e.rect()):
                    l.alive = False
                    if e.is_correct:
                        combo  += 1
                        pts     = 100 + (combo - 1) * 25
                        score  += pts
                        flash_msg   = f"NICE! +{pts}" + (f"  COMBO x{combo}!" if combo > 1 else "")
                        flash_color = GREEN
                        flash_timer = 65
                        q_index    += 1
                        current_q   = QUESTIONS[q_index % len(QUESTIONS)]
                        for _ in range(28):
                            particles.append(Particle(e.x, e.y, random.choice([GREEN, CYAN, YELLOW])))
                        enemies.clear()
                    else:
                        lives      -= 1
                        combo       = 0
                        flash_msg   = "Wrong word! -1 Life"
                        flash_color = RED
                        flash_timer = 65
                        for _ in range(14):
                            particles.append(Particle(e.x, e.y, random.choice([RED, ORANGE])))
                        if e in enemies:
                            enemies.remove(e)
                    break

        # ── Enemy too close ──
        player_rect = player.rect()
        for e in enemies[:]:
            if e.alive and e.y > HEIGHT - 90 and e.rect().colliderect(player_rect):
                lives      -= 1
                combo       = 0
                flash_msg   = "Enemy too close! -1 Life"
                flash_color = RED
                flash_timer = 55
                if e in enemies:
                    enemies.remove(e)

        if lives <= 0:
            running = False

        if flash_timer > 0:
            flash_timer -= 1

        # ── Draw ────────────────────────────────────────────
        screen.fill(BLACK)
        for s in stars:
            s.draw(screen)
        pygame.draw.line(screen, (40, 40, 80), (0, HEIGHT - 45), (WIDTH, HEIGHT - 45), 1)

        for e in enemies:
            if e.alive:
                e.draw(screen)
        for l in lasers:
            l.draw(screen)
        for p in particles:
            p.draw(screen)
        player.draw(screen)

        prompt_h = draw_prompt_box(screen, current_q["prompt"], big_font)
        hud_y    = prompt_h + 10

        # Score
        score_surf = big_font.render(f"SCORE: {score}", True, CYAN)
        screen.blit(score_surf, (14, hud_y))

        # Lives
        lives_label = hud_font.render("LIVES:", True, WHITE)
        screen.blit(lives_label, (WIDTH - 200, hud_y))
        draw_lives(screen, lives)

        # Combo
        if combo >= 2:
            combo_surf = big_font.render(f"COMBO x{combo}", True, ORANGE)
            screen.blit(combo_surf, combo_surf.get_rect(centerx=WIDTH // 2, y=hud_y))

        # Flash message
        if flash_timer > 0:
            msg_surf = big_font.render(flash_msg, True, flash_color)
            screen.blit(msg_surf, msg_surf.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 - 30))

        # Controls hint
        hint = hud_font.render("← → Move   |   SPACE Shoot", True, (60, 60, 100))
        screen.blit(hint, hint.get_rect(centerx=WIDTH // 2, y=HEIGHT - 22))

        pygame.display.flip()
        await asyncio.sleep(0)

    # ── Game Over Screen ──────────────────────────────────────
    # Show a brief on-screen game over while JS overlay loads
    xp_earned = score_to_xp(score)

    # Inject the game-over XP call via JavaScript (pybag/pygbag bridge)
    js_call = (
        f"showGameOverXP({{ gameId: 'word-blaster', score: {score}, xpEarned: {xp_earned} }});"
    )
    try:
        # pygbag exposes window via platform.window
        import platform
        platform.window.eval(js_call)
    except Exception:
        pass  # Running locally without pygbag — skip JS call

    for _ in range(FPS * 5):
        screen.fill(BLACK)
        for s in stars:
            s.update()
            s.draw(screen)
        go   = big_font.render("GAME OVER", True, RED)
        sc   = big_font.render(f"Final Score: {score}   XP Earned: +{xp_earned}", True, YELLOW)
        rest = font.render("Check your XP results above!", True, CYAN)
        screen.blit(go,   go.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 - 60))
        screen.blit(sc,   sc.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2))
        screen.blit(rest, rest.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 + 60))
        pygame.display.flip()
        clk.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())