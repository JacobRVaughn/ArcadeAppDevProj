"""
Math & Letters Kingdom - Educational Tower Defense
A fun tower defense game for kids ages 5-10
Compatible with pygbag for web deployment
"""

import asyncio
import pygame
import math
import random
import sys

# --- Constants ---
SCREEN_W, SCREEN_H = 960, 640
FPS = 60
TILE = 48

# Colors
WHITE    = (255, 255, 255)
BLACK    = (10,  10,  20)
BG       = (34,  139, 34)
PATH_C   = (210, 180, 140)
PANEL_C  = (25,  50,  90)
GOLD     = (255, 215, 0)
RED      = (220, 50,  50)
BLUE     = (60,  120, 230)
CYAN     = (80,  220, 220)
ORANGE   = (255, 140, 0)
PURPLE   = (160, 60,  200)
PINK     = (255, 100, 180)
GREEN    = (50,  200, 80)
DARK_G   = (20,  80,  30)
LIGHT_G  = (80,  180, 80)
GRAY     = (120, 120, 140)
DARK_B   = (15,  30,  60)
YELLOW   = (255, 240, 50)
TEAL     = (0,   180, 160)

# --- Path Definition (tile coords) ---
RAW_PATH = [
    (0,2),(1,2),(2,2),(3,2),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),
    (5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),(13,7),(14,7),
    (14,6),(14,5),(14,4),(14,3),(14,2),(13,2),(12,2),(11,2),(10,2),(9,2),
    (9,3),(9,4),(9,5),(9,6),(8,6),(7,6),(6,6),(6,5),(6,4),(6,3),
    (7,3),(8,3),(8,4),(8,5),(7,5),(7,4),
    # loop ends - enemies loop back if no castle found
]

# --- Tower Definitions ---
TOWERS = {
    "number": {
        "name": "Number Tower",
        "cost": 50,
        "color": BLUE,
        "range": 120,
        "fire_rate": 60,
        "damage": 2,
        "proj_color": CYAN,
        "emoji": "1️⃣",
        "question": lambda: _math_q(),
        "desc": "Shoots math at enemies!",
    },
    "letter": {
        "name": "Letter Tower",
        "cost": 40,
        "color": PURPLE,
        "range": 100,
        "fire_rate": 45,
        "damage": 1,
        "proj_color": PINK,
        "emoji": "🔤",
        "question": lambda: _letter_q(),
        "desc": "Slows enemies with spelling!",
        "slow": True,
    },
    "star": {
        "name": "Star Tower",
        "cost": 80,
        "color": GOLD,
        "range": 150,
        "fire_rate": 90,
        "damage": 4,
        "proj_color": YELLOW,
        "emoji": "⭐",
        "question": lambda: _shape_q(),
        "desc": "Blasts shapes knowledge!",
    },
}

# --- Educational Question Generators ---
def _math_q():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    ops = [
        (f"What is {a} + {b}?", a + b),
        (f"What is {max(a,b)} - {min(a,b)}?", max(a,b) - min(a,b)),
        (f"What is {a} + {a}?", a + a),
        (f"Count to {a}: what comes after {a-1}?", a) if a > 1 else (f"What is 1 + 1?", 2),
    ]
    return random.choice(ops)

def _letter_q():
    words = [
        ("What letter starts 'Apple'?", "A"),
        ("What letter starts 'Ball'?", "B"),
        ("What letter starts 'Cat'?", "C"),
        ("What letter starts 'Dog'?", "D"),
        ("What letter starts 'Egg'?", "E"),
        ("What letter starts 'Fish'?", "F"),
        ("What letter starts 'Goat'?", "G"),
        ("What letter starts 'Hat'?", "H"),
        ("What letter ends 'Cat'?", "T"),
        ("What letter ends 'Dog'?", "G"),
        ("What is the 1st letter of the alphabet?", "A"),
        ("What is the last letter of the alphabet?", "Z"),
    ]
    return random.choice(words)

def _shape_q():
    shapes = [
        ("How many sides does a triangle have?", 3),
        ("How many sides does a square have?", 4),
        ("How many sides does a rectangle have?", 4),
        ("How many corners does a circle have?", 0),
        ("How many sides does a pentagon have?", 5),
        ("How many sides does a hexagon have?", 6),
    ]
    return random.choice(shapes)

# Convert answer to string for comparison
def answer_to_str(ans):
    return str(ans).upper().strip()

# --- Path in pixels ---
def path_pixels():
    return [(x * TILE + TILE//2, y * TILE + TILE//2) for x, y in RAW_PATH]

PATH_SET = set(RAW_PATH)

# ─── Classes ────────────────────────────────────────────────────────────────

class Enemy:
    TYPES = [
        {"name": "Slime",   "color": GREEN,  "hp": 5,  "speed": 1.2, "reward": 10, "size": 16, "shape": "circle"},
        {"name": "Goblin",  "color": ORANGE, "hp": 10, "speed": 1.5, "reward": 15, "size": 14, "shape": "rect"},
        {"name": "Troll",   "color": GRAY,   "hp": 20, "speed": 0.8, "reward": 25, "size": 20, "shape": "circle"},
        {"name": "Dragon",  "color": RED,    "hp": 40, "speed": 0.6, "reward": 50, "size": 22, "shape": "diamond"},
        {"name": "Ghost",   "color": (200,200,255), "hp": 8, "speed": 2.0, "reward": 20, "size": 12, "shape": "circle"},
    ]

    def __init__(self, etype, wave):
        t = self.TYPES[etype % len(self.TYPES)]
        scale = 1 + (wave - 1) * 0.15
        self.name   = t["name"]
        self.color  = t["color"]
        self.hp     = int(t["hp"] * scale)
        self.max_hp = self.hp
        self.speed  = t["speed"]
        self.reward = t["reward"]
        self.size   = t["size"]
        self.shape  = t["shape"]
        self.path   = path_pixels()
        self.pidx   = 0
        self.x, self.y = self.path[0]
        self.alive  = True
        self.reached_end = False
        self.slow_timer = 0
        self.wobble = random.uniform(0, math.pi * 2)

    def update(self):
        self.wobble += 0.1
        spd = self.speed * (0.5 if self.slow_timer > 0 else 1.0)
        if self.slow_timer > 0:
            self.slow_timer -= 1
        if self.pidx + 1 >= len(self.path):
            self.reached_end = True
            self.alive = False
            return
        tx, ty = self.path[self.pidx + 1]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < spd:
            self.pidx += 1
            self.x, self.y = tx, ty
        else:
            self.x += dx / dist * spd
            self.y += dy / dist * spd

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        s = self.size
        c = self.color
        if self.slow_timer > 0:
            c = (min(c[0]+80,255), min(c[1]+80,255), 255)

        if self.shape == "circle":
            pygame.draw.circle(surf, c, (cx, cy), s)
            pygame.draw.circle(surf, BLACK, (cx, cy), s, 2)
            # eyes
            eye_y = cy - s//4
            pygame.draw.circle(surf, WHITE, (cx-s//3, eye_y), s//4)
            pygame.draw.circle(surf, WHITE, (cx+s//3, eye_y), s//4)
            pygame.draw.circle(surf, BLACK, (cx-s//3, eye_y), s//6)
            pygame.draw.circle(surf, BLACK, (cx+s//3, eye_y), s//6)
        elif self.shape == "rect":
            rect = pygame.Rect(cx-s, cy-s, s*2, s*2)
            pygame.draw.rect(surf, c, rect, border_radius=4)
            pygame.draw.rect(surf, BLACK, rect, 2, border_radius=4)
            eye_y = cy - s//3
            pygame.draw.circle(surf, WHITE, (cx-s//3, eye_y), s//4)
            pygame.draw.circle(surf, WHITE, (cx+s//3, eye_y), s//4)
            pygame.draw.circle(surf, BLACK, (cx-s//3, eye_y), s//6)
            pygame.draw.circle(surf, BLACK, (cx+s//3, eye_y), s//6)
        elif self.shape == "diamond":
            pts = [(cx, cy-s*2), (cx+s, cy), (cx, cy+s*2), (cx-s, cy)]
            pygame.draw.polygon(surf, c, pts)
            pygame.draw.polygon(surf, BLACK, pts, 2)
            pygame.draw.circle(surf, YELLOW, (cx-s//3, cy-s//2), s//3)
            pygame.draw.circle(surf, YELLOW, (cx+s//3, cy-s//2), s//3)

        # HP bar
        bar_w = s * 2
        hp_frac = self.hp / self.max_hp
        pygame.draw.rect(surf, RED,   (cx - s, cy - s - 8, bar_w, 5))
        pygame.draw.rect(surf, GREEN, (cx - s, cy - s - 8, int(bar_w * hp_frac), 5))

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False


class Projectile:
    def __init__(self, x, y, target, damage, color, slow=False):
        self.x, self.y = float(x), float(y)
        self.target = target
        self.damage = damage
        self.color  = color
        self.slow   = slow
        self.speed  = 6
        self.alive  = True
        self.radius = 6

    def update(self):
        if not self.target.alive:
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.target.take_damage(self.damage)
            if self.slow:
                self.target.slow_timer = 90
            self.alive = False
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surf, self.color, (cx, cy), self.radius)
        pygame.draw.circle(surf, WHITE, (cx, cy), self.radius, 2)


class Tower:
    def __init__(self, tx, ty, ttype):
        self.tx, self.ty = tx, ty  # tile coords
        self.px = tx * TILE + TILE // 2
        self.py = ty * TILE + TILE // 2
        self.ttype = ttype
        info = TOWERS[ttype]
        self.range     = info["range"]
        self.fire_rate = info["fire_rate"]
        self.damage    = info["damage"]
        self.color     = info["color"]
        self.proj_color= info["proj_color"]
        self.slow      = info.get("slow", False)
        self.timer     = 0
        self.level     = 1
        self.anim      = 0

    def update(self, enemies, projectiles):
        self.anim += 0.05
        self.timer -= 1
        if self.timer > 0:
            return
        # find nearest enemy in range
        best = None
        best_dist = self.range
        for e in enemies:
            if not e.alive:
                continue
            d = math.hypot(e.x - self.px, e.y - self.py)
            if d < best_dist:
                best_dist = d
                best = e
        if best:
            projectiles.append(Projectile(
                self.px, self.py, best,
                self.damage * self.level,
                self.proj_color, self.slow
            ))
            self.timer = max(10, self.fire_rate - (self.level - 1) * 5)

    def draw(self, surf, selected=False):
        px, py = self.px, self.py
        # base
        base_r = TILE // 2 - 4
        pygame.draw.circle(surf, (40, 40, 60), (px, py), base_r + 3)
        pygame.draw.circle(surf, self.color, (px, py), base_r)
        # animated ring
        ring_r = int(base_r + 3 + math.sin(self.anim) * 2)
        pygame.draw.circle(surf, self.color, (px, py), ring_r, 2)

        # tower type symbol
        font_s = pygame.font.SysFont("arial", 18, bold=True)
        labels = {"number": "1+", "letter": "A", "star": "★"}
        label = labels.get(self.ttype, "?")
        txt = font_s.render(label, True, WHITE)
        surf.blit(txt, txt.get_rect(center=(px, py)))

        # level stars
        for i in range(self.level):
            sx = px - 8 + i * 8
            pygame.draw.circle(surf, GOLD, (sx, py + base_r + 6), 3)

        if selected:
            pygame.draw.circle(surf, YELLOW, (px, py), self.range, 1)
            pygame.draw.circle(surf, YELLOW, (px, py), base_r + 5, 3)

    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.range  = int(TOWERS[self.ttype]["range"] * (1 + 0.25 * (self.level - 1)))
            return True
        return False

    def upgrade_cost(self):
        return TOWERS[self.ttype]["cost"] * self.level


class FloatingText:
    def __init__(self, x, y, text, color=GOLD, size=22):
        self.x = x
        self.y = float(y)
        self.text = text
        self.color = color
        self.size = size
        self.life = 80
        self.max_life = 80

    def update(self):
        self.y -= 0.8
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * self.life / self.max_life)
        font = pygame.font.SysFont("arial", self.size, bold=True)
        txt = font.render(self.text, True, self.color)
        txt.set_alpha(alpha)
        surf.blit(txt, txt.get_rect(center=(self.x, int(self.y))))


class QuizPopup:
    """Pop-up quiz for kids when placing a tower."""
    def __init__(self, question, answer, on_success, on_fail):
        self.question   = question
        self.answer     = answer_to_str(answer)
        self.on_success = on_success
        self.on_fail    = on_fail
        self.user_input = ""
        self.active     = True
        self.result     = None  # None, "correct", "wrong"
        self.result_timer = 0
        self.w, self.h  = 480, 260
        self.x = (SCREEN_W - self.w) // 2
        self.y = (SCREEN_H - self.h) // 2

    def handle_event(self, event):
        if not self.active:
            return
        if self.result:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._check()
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            elif len(self.user_input) < 8:
                if event.unicode.isprintable():
                    self.user_input += event.unicode.upper()

    def _check(self):
        if self.user_input.strip() == self.answer:
            self.result = "correct"
        else:
            self.result = "wrong"
        self.result_timer = 90

    def update(self):
        if self.result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                if self.result == "correct":
                    self.on_success()
                else:
                    self.on_fail()
                self.active = False

    def draw(self, surf):
        # Backdrop
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 30, 180))
        surf.blit(overlay, (0, 0))

        # Panel
        panel = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surf, DARK_B, panel, border_radius=20)
        pygame.draw.rect(surf, CYAN, panel, 3, border_radius=20)

        # Title
        f_title = pygame.font.SysFont("arial", 22, bold=True)
        t = f_title.render("🎓 Quiz Time! Answer to place tower!", True, GOLD)
        surf.blit(t, t.get_rect(centerx=SCREEN_W//2, y=self.y + 20))

        # Question
        f_q = pygame.font.SysFont("arial", 26, bold=True)
        q_surf = f_q.render(self.question, True, WHITE)
        surf.blit(q_surf, q_surf.get_rect(centerx=SCREEN_W//2, y=self.y + 70))

        if self.result == "correct":
            msg = f_q.render("✅ Correct! Great job!", True, GREEN)
            surf.blit(msg, msg.get_rect(centerx=SCREEN_W//2, y=self.y + 120))
        elif self.result == "wrong":
            msg = f_q.render(f"❌ Answer: {self.answer} — Try again!", True, RED)
            surf.blit(msg, msg.get_rect(centerx=SCREEN_W//2, y=self.y + 120))
        else:
            # Input box
            box = pygame.Rect(self.x + 100, self.y + 115, self.w - 200, 45)
            pygame.draw.rect(surf, WHITE, box, border_radius=10)
            pygame.draw.rect(surf, BLUE, box, 3, border_radius=10)
            f_in = pygame.font.SysFont("arial", 28, bold=True)
            in_surf = f_in.render(self.user_input + "|", True, BLACK)
            surf.blit(in_surf, in_surf.get_rect(center=box.center))

            hint = pygame.font.SysFont("arial", 16).render("Type your answer and press ENTER", True, GRAY)
            surf.blit(hint, hint.get_rect(centerx=SCREEN_W//2, y=self.y + 175))


# ─── Main Game ──────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Math & Letters Kingdom 🏰")
        self.clock  = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.gold      = 150
        self.lives     = 10
        self.wave      = 0
        self.score     = 0
        self.towers    = []
        self.enemies   = []
        self.projs     = []
        self.floats    = []
        self.quiz      = None
        self.selected_tower_type = "number"
        self.selected_tower      = None   # placed tower selected for upgrade
        self.state     = "title"   # title, playing, wave_complete, game_over, win
        self.wave_timer     = 0
        self.spawn_queue    = []
        self.spawn_timer    = 0
        self.between_waves  = True
        self.total_waves    = 8
        self.path_pixels    = path_pixels()
        self.bg_surf        = self._make_bg()
        self.correct_count  = 0
        self.wrong_count    = 0
        self._bg_anim       = 0

    def _make_bg(self):
        surf = pygame.Surface((SCREEN_W, SCREEN_H))
        # Grass
        surf.fill(BG)
        # Grass texture spots
        for _ in range(300):
            gx = random.randint(0, SCREEN_W)
            gy = random.randint(0, SCREEN_H)
            pygame.draw.circle(surf, DARK_G, (gx, gy), random.randint(2, 6))

        # Draw path tiles
        path_set = set(RAW_PATH)
        for tx, ty in path_set:
            rect = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
            pygame.draw.rect(surf, PATH_C, rect)
            pygame.draw.rect(surf, (180, 150, 110), rect, 1)

        # Start & End markers
        sx, sy = RAW_PATH[0]
        ex, ey = RAW_PATH[-1]
        pygame.draw.rect(surf, GREEN, (sx*TILE, sy*TILE, TILE, TILE))
        pygame.draw.rect(surf, RED,   (ex*TILE, ey*TILE, TILE, TILE))
        f = pygame.font.SysFont("arial", 14, bold=True)
        surf.blit(f.render("START", True, WHITE), (sx*TILE+2, sy*TILE+16))
        surf.blit(f.render("CASTLE", True, WHITE),(ex*TILE+2, ey*TILE+16))

        # Right panel background
        pygame.draw.rect(surf, DARK_B, (TILE * 16, 0, SCREEN_W - TILE * 16, SCREEN_H))
        return surf

    # ── Wave Logic ──────────────────────────────────────────────────────────

    def start_wave(self):
        self.wave += 1
        self.between_waves = False
        count = 5 + self.wave * 3
        self.spawn_queue = []
        for i in range(count):
            etype = (i + self.wave) % len(Enemy.TYPES)
            self.spawn_queue.append(etype)
        self.spawn_timer = 0
        self.floats.append(FloatingText(
            SCREEN_W // 2, 80, f"Wave {self.wave}!", ORANGE, 36))

    def update_wave(self):
        if self.between_waves:
            return
        self.spawn_timer -= 1
        if self.spawn_timer <= 0 and self.spawn_queue:
            etype = self.spawn_queue.pop(0)
            self.enemies.append(Enemy(etype, self.wave))
            self.spawn_timer = 40

        if not self.spawn_queue and not any(e.alive for e in self.enemies):
            self.between_waves = True
            if self.wave >= self.total_waves:
                self.state = "win"
            else:
                bonus = 20 + self.wave * 5
                self.gold += bonus
                self.floats.append(FloatingText(
                    SCREEN_W//2, 100, f"Wave Clear! +{bonus}🪙", GOLD, 30))

    # ── Placement ───────────────────────────────────────────────────────────

    def try_place_tower(self, tx, ty):
        if (tx, ty) in PATH_SET:
            return
        if tx >= 16 or tx < 0 or ty < 0 or ty * TILE >= SCREEN_H:
            return
        for t in self.towers:
            if t.tx == tx and t.ty == ty:
                return
        cost = TOWERS[self.selected_tower_type]["cost"]
        if self.gold < cost:
            self.floats.append(FloatingText(
                tx*TILE+24, ty*TILE, "Not enough gold!", RED, 18))
            return

        # Ask a quiz question!
        info = TOWERS[self.selected_tower_type]
        q, a = info["question"]()
        placed_tx, placed_ty = tx, ty
        ttype = self.selected_tower_type

        def on_success():
            self.gold -= cost
            self.towers.append(Tower(placed_tx, placed_ty, ttype))
            self.correct_count += 1
            self.floats.append(FloatingText(
                placed_tx*TILE+24, placed_ty*TILE, "+Tower! 🎉", GREEN, 22))

        def on_fail():
            self.wrong_count += 1
            self.floats.append(FloatingText(
                placed_tx*TILE+24, placed_ty*TILE, "Try again!", RED, 20))

        self.quiz = QuizPopup(q, a, on_success, on_fail)

    # ── Main Loop ───────────────────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.quiz and self.quiz.active:
                self.quiz.handle_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                if self.state == "title" and event.key == pygame.K_SPACE:
                    self.state = "playing"
                    self.start_wave()
                elif self.state in ("game_over", "win") and event.key == pygame.K_r:
                    self.reset()
                    self.state = "playing"
                    self.start_wave()
                elif event.key == pygame.K_1:
                    self.selected_tower_type = "number"
                    self.selected_tower = None
                elif event.key == pygame.K_2:
                    self.selected_tower_type = "letter"
                    self.selected_tower = None
                elif event.key == pygame.K_3:
                    self.selected_tower_type = "star"
                    self.selected_tower = None
                elif event.key == pygame.K_SPACE and self.state == "playing" and self.between_waves:
                    self.start_wave()
                elif event.key == pygame.K_u and self.selected_tower:
                    cost = self.selected_tower.upgrade_cost()
                    if self.gold >= cost and self.selected_tower.upgrade():
                        self.gold -= cost
                        self.floats.append(FloatingText(
                            self.selected_tower.px, self.selected_tower.py,
                            "Upgraded! ⬆", CYAN, 20))

            if event.type == pygame.MOUSEBUTTONDOWN and self.state == "playing":
                mx, my = pygame.mouse.get_pos()
                tx, ty = mx // TILE, my // TILE
                # Check if clicking a placed tower
                clicked_tower = None
                for t in self.towers:
                    if t.tx == tx and t.ty == ty:
                        clicked_tower = t
                        break
                if clicked_tower:
                    self.selected_tower = clicked_tower
                elif event.button == 1:
                    self.try_place_tower(tx, ty)

        return True

    def update(self):
        if self.state != "playing":
            return
        self._bg_anim += 1

        if self.quiz and self.quiz.active:
            self.quiz.update()
            return

        self.update_wave()

        for t in self.towers:
            t.update(self.enemies, self.projs)
        for p in self.projs:
            p.update()
        for e in self.enemies:
            e.update()
            if e.reached_end:
                self.lives -= 1
                if self.lives <= 0:
                    self.lives = 0
                    self.state = "game_over"
        for f in self.floats:
            f.update()

        # rewards
        for e in self.enemies:
            if not e.alive and e.reward > 0:
                self.gold += e.reward
                self.score += e.reward
                self.floats.append(FloatingText(int(e.x), int(e.y)-10,
                    f"+{e.reward}🪙", GOLD, 18))
                e.reward = 0

        self.enemies  = [e for e in self.enemies if e.alive or not e.reached_end]
        self.enemies  = [e for e in self.enemies if not (not e.alive and e.reward == 0 and not e.reached_end) or True]
        self.enemies  = [e for e in self.enemies if e.hp > 0 or not e.alive]
        self.enemies  = [e for e in self.enemies if e.alive]
        self.projs    = [p for p in self.projs if p.alive]
        self.floats   = [f for f in self.floats if f.life > 0]

    # ── Drawing ─────────────────────────────────────────────────────────────

    def draw_title(self):
        self.screen.fill((10, 20, 50))
        # Stars
        for i in range(80):
            sx = (i * 137) % SCREEN_W
            sy = (i * 79)  % SCREEN_H
            r  = 1 + (i % 3)
            pygame.draw.circle(self.screen, WHITE, (sx, sy), r)

        f_big   = pygame.font.SysFont("arial", 64, bold=True)
        f_med   = pygame.font.SysFont("arial", 28, bold=True)
        f_small = pygame.font.SysFont("arial", 20)

        title = f_big.render("🏰 Math & Letters Kingdom", True, GOLD)
        self.screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=100))

        sub = f_med.render("An Educational Tower Defense Adventure!", True, CYAN)
        self.screen.blit(sub, sub.get_rect(centerx=SCREEN_W//2, y=185))

        lines = [
            "Place towers to stop the monsters!",
            "Answer a question to place each tower.",
            "Keys: [1] Number Tower  [2] Letter Tower  [3] Star Tower",
            "[SPACE] Start Wave   [U] Upgrade selected tower",
        ]
        for i, line in enumerate(lines):
            s = f_small.render(line, True, WHITE)
            self.screen.blit(s, s.get_rect(centerx=SCREEN_W//2, y=260 + i * 34))

        blink = abs(math.sin(pygame.time.get_ticks() / 400))
        start = f_med.render("Press SPACE to Start!", True,
                              (int(blink*200+55), int(blink*200+55), 255))
        self.screen.blit(start, start.get_rect(centerx=SCREEN_W//2, y=420))

        # Tower previews
        tw_x = SCREEN_W // 2 - 150
        for i, (k, info) in enumerate(TOWERS.items()):
            cx = tw_x + i * 150
            pygame.draw.circle(self.screen, info["color"], (cx, 520), 28)
            pygame.draw.circle(self.screen, WHITE, (cx, 520), 28, 2)
            f = pygame.font.SysFont("arial", 20, bold=True)
            labels = {"number": "1+", "letter": "A", "star": "★"}
            lbl = f.render(labels[k], True, WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=(cx, 520)))
            nm = pygame.font.SysFont("arial", 14).render(info["name"], True, GRAY)
            self.screen.blit(nm, nm.get_rect(centerx=cx, y=555))

    def draw_panel(self):
        px = TILE * 16
        # Already drawn in bg
        font_b = pygame.font.SysFont("arial", 18, bold=True)
        font_s = pygame.font.SysFont("arial", 15)

        # Stats
        stats = [
            (f"🪙 Gold: {self.gold}", GOLD),
            (f"❤️  Lives: {self.lives}", RED),
            (f"🌊 Wave: {self.wave}/{self.total_waves}", CYAN),
            (f"⭐ Score: {self.score}", YELLOW),
        ]
        for i, (txt, col) in enumerate(stats):
            s = font_b.render(txt, True, col)
            self.screen.blit(s, (px + 10, 15 + i * 28))

        # Divider
        pygame.draw.line(self.screen, GRAY, (px+5, 130), (SCREEN_W-5, 130), 2)

        # Towers
        s = font_b.render("🏗 Build (click grid):", True, WHITE)
        self.screen.blit(s, (px + 10, 138))

        for i, (k, info) in enumerate(TOWERS.items()):
            y = 165 + i * 75
            selected = (k == self.selected_tower_type)
            color = CYAN if selected else DARK_B
            rect = pygame.Rect(px+6, y, SCREEN_W - px - 12, 68)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, info["color"], rect, 2, border_radius=10)
            # circle preview
            pygame.draw.circle(self.screen, info["color"], (px+28, y+34), 18)
            pygame.draw.circle(self.screen, BLACK, (px+28, y+34), 18, 2)
            fl = font_b.render(["1+","A","★"][i], True, WHITE)
            self.screen.blit(fl, fl.get_rect(center=(px+28, y+34)))
            # name + cost
            nm = font_b.render(f"[{i+1}] {info['name']}", True, WHITE)
            self.screen.blit(nm, (px+52, y+8))
            cost_s = font_s.render(f"Cost: {info['cost']}🪙  {info['desc']}", True, GRAY)
            self.screen.blit(cost_s, (px+52, y+30))
            range_s = font_s.render(f"Range {info['range']} | Dmg {info['damage']}", True, GRAY)
            self.screen.blit(range_s, (px+52, y+48))

        # Divider
        pygame.draw.line(self.screen, GRAY, (px+5, 398), (SCREEN_W-5, 398), 2)

        # Selected tower info
        if self.selected_tower:
            t = self.selected_tower
            info = TOWERS[t.ttype]
            s = font_b.render("Selected Tower:", True, CYAN)
            self.screen.blit(s, (px+10, 405))
            self.screen.blit(font_s.render(f"{info['name']} Lv{t.level}", True, WHITE), (px+10, 427))
            uc = t.upgrade_cost()
            if t.level < 3:
                self.screen.blit(font_s.render(f"[U] Upgrade: {uc}🪙", True, GOLD), (px+10, 447))
            else:
                self.screen.blit(font_s.render("Max Level!", True, GREEN), (px+10, 447))
        else:
            hint = font_s.render("Click a tower to select", True, GRAY)
            self.screen.blit(hint, (px+10, 410))

        # Wave button
        if self.between_waves and self.wave < self.total_waves:
            bw = SCREEN_W - px - 20
            brect = pygame.Rect(px+10, SCREEN_H - 60, bw, 44)
            pulse = abs(math.sin(pygame.time.get_ticks() / 300))
            bc = (int(50 + pulse*100), int(180 + pulse*60), int(50 + pulse*100))
            pygame.draw.rect(self.screen, bc, brect, border_radius=12)
            pygame.draw.rect(self.screen, WHITE, brect, 2, border_radius=12)
            bt = font_b.render("SPACE → Next Wave!", True, WHITE)
            self.screen.blit(bt, bt.get_rect(center=brect.center))

        # Quiz stats
        qs = font_s.render(f"✅{self.correct_count}  ❌{self.wrong_count}", True, WHITE)
        self.screen.blit(qs, (px+10, SCREEN_H - 80))

    def draw_hud_wave_status(self):
        if not self.between_waves:
            remaining = len(self.spawn_queue) + sum(1 for e in self.enemies if e.alive)
            font = pygame.font.SysFont("arial", 18, bold=True)
            s = font.render(f"Enemies remaining: {remaining}", True, WHITE)
            self.screen.blit(s, (10, SCREEN_H - 30))

    def draw_overlay(self, title, sub, color):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 200))
        self.screen.blit(overlay, (0, 0))
        f1 = pygame.font.SysFont("arial", 72, bold=True)
        f2 = pygame.font.SysFont("arial", 30)
        f3 = pygame.font.SysFont("arial", 22)
        t1 = f1.render(title, True, color)
        self.screen.blit(t1, t1.get_rect(centerx=SCREEN_W//2, y=180))
        t2 = f2.render(sub, True, WHITE)
        self.screen.blit(t2, t2.get_rect(centerx=SCREEN_W//2, y=280))
        t3 = f3.render(f"Score: {self.score}  |  Correct Answers: {self.correct_count}", True, CYAN)
        self.screen.blit(t3, t3.get_rect(centerx=SCREEN_W//2, y=330))
        t4 = f3.render("Press [R] to play again!", True, GOLD)
        self.screen.blit(t4, t4.get_rect(centerx=SCREEN_W//2, y=380))

    def draw(self):
        if self.state == "title":
            self.draw_title()
            pygame.display.flip()
            return

        self.screen.blit(self.bg_surf, (0, 0))

        for t in self.towers:
            t.draw(self.screen, selected=(t == self.selected_tower))
        for e in self.enemies:
            e.draw(self.screen)
        for p in self.projs:
            p.draw(self.screen)
        for f in self.floats:
            f.draw(self.screen)

        self.draw_panel()
        self.draw_hud_wave_status()

        if self.quiz and self.quiz.active:
            self.quiz.draw(self.screen)

        if self.state == "game_over":
            self.draw_overlay("GAME OVER!", "The monsters reached the castle!", RED)
        elif self.state == "win":
            self.draw_overlay("YOU WIN! 🏆", "You saved the kingdom!", GOLD)

        pygame.display.flip()

    async def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(0)


# ─── Entry Point ─────────────────────────────────────────────────────────────

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())