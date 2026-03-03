import asyncio
import random
import pygame
from pathlib import Path

pygame.init()

# ---------- Audio ----------
# NOTE: For web builds (pygbag), audio support can vary by browser.
# This will still work for desktop pygame; if mixer init fails, we disable sounds gracefully.
SOUNDS_ENABLED = True
try:
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)  # allow overlapping sounds
except Exception:
    SOUNDS_ENABLED = False

_ASSET_DIR = Path(__file__).resolve().parent
def _load_sound(name: str):
    if not SOUNDS_ENABLED:
        return None
    try:
        return pygame.mixer.Sound(str(_ASSET_DIR / name))
    except Exception:
        return None

SND_NORMAL = _load_sound("catch1.mp3")  # normal
SND_MULT   = _load_sound("catch2.mp3")  # multiplier
SND_NEG    = _load_sound("catch3.mp3")  # negative

def play_catch_sound(ball_type: str):
    if not SOUNDS_ENABLED:
        return
    snd = None
    if ball_type == "mult":
        snd = SND_MULT
    elif ball_type == "neg":
        snd = SND_NEG
    else:
        snd = SND_NORMAL

    if snd is None:
        return
    # Sound.play() uses the first available channel; with multiple channels it can overlap.
    try:
        snd.play()
    except Exception:
        pass

# ---------- Config ----------
W, H = 900, 600
FPS = 60

BASKET_W, BASKET_H = 120, 34
BASKET_SPEED = 520

BALL_VALUES = [1, 2, 3, 4, 5]
MULT_VALUES = [2, 3, 4]
NEG_VALUES  = [-1, -2, -3, -4, -5]

BALL_MIN_R = int(18 * 1.3)
BALL_MAX_R = int(26 * 1.3)


SPAWN_START = 0.85
SPAWN_MIN = 0.35
SPAWN_ACCEL = 0.03

MULT_CHANCE = 0.12
NEG_CHANCE  = 0.15

# ---------- Colors ----------
BG = (16, 42, 90)
HUD = (215, 230, 255)
SUB = (161, 161, 170)
WARN = (248, 113, 113)

ORANGE = (255, 122, 24)

Y_FILL, Y_STROKE = (253, 224, 71), (245, 158, 11)
G_FILL, G_STROKE = (74, 222, 128), (22, 163, 74)
R_FILL, R_STROKE = (248, 113, 113), (220, 38, 38)

LABEL = (11, 27, 58)

EASY_BTN = (34, 197, 94)
MED_BTN  = (234, 179, 8)
HARD_BTN = (239, 68, 68)
BTN_TXT  = (255, 255, 255)

# ---------- Helpers ----------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def new_target():
    diff = state.get("difficulty")

    if diff == "easy":
        return random.randint(0, 10)
    elif diff == "medium":
        return random.randint(10, 30)
    elif diff == "hard":
        return random.randint(30, 100)
    else:
        # Fallback (should not normally happen)
        return random.randint(0, 10)

def circle_rect_collide(cx, cy, r, rx, ry, rw, rh):
    closest_x = clamp(cx, rx, rx + rw)
    closest_y = clamp(cy, ry, ry + rh)
    dx = cx - closest_x
    dy = cy - closest_y
    return dx * dx + dy * dy <= r * r

# ---------- Game objects ----------
class Ball:
    __slots__ = ("x", "y", "r", "vy", "value", "type")
    def __init__(self, x, y, r, vy, value, ball_type):
        self.x = x
        self.y = y
        self.r = r
        self.vy = vy
        self.value = value
        self.type = ball_type  # "normal" | "mult" | "neg"

class PopText:
    __slots__ = ("x", "y", "text", "age", "duration", "base_alpha")
    def __init__(self, x, y, text, duration=0.6, base_alpha=128):
        self.x = x
        self.y = y
        self.text = text
        self.age = 0.0
        self.duration = duration
        self.base_alpha = base_alpha

    def update(self, dt):
        self.age += dt
        # float up slightly
        self.y -= 45.0 * dt

    def alive(self):
        return self.age < self.duration

    def draw(self, surface):
        t = self.age / self.duration
        if t < 0.0:
            t = 0.0
        if t > 1.0:
            t = 1.0

        # Grow from 1.0x to ~2.0x
        scale = 1.0 + 1.0 * t

        # Fade out from 50% opacity to 0
        alpha = int(self.base_alpha * (1.0 - t))

        txt_surf = font_pop.render(self.text, True, (255, 255, 255))
        txt_surf.set_alpha(alpha)

        w, h = txt_surf.get_size()
        sw, sh = max(1, int(w * scale)), max(1, int(h * scale))
        txt_surf = pygame.transform.smoothscale(txt_surf, (sw, sh))

        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)

def spawn_ball(balls):
    r = random.randint(BALL_MIN_R, BALL_MAX_R)
    roll = random.random()

    if roll < MULT_CHANCE:
        ball_type = "mult"
        value = random.choice(MULT_VALUES)
    elif roll < MULT_CHANCE + NEG_CHANCE:
        ball_type = "neg"
        value = random.choice(NEG_VALUES)
    else:
        ball_type = "normal"
        value = random.choice(BALL_VALUES)

    x = random.randint(r, W - r)
    y = -r
    vy = random.uniform(140, 240)
    balls.append(Ball(x, y, r, vy, value, ball_type))

# ---------- State ----------
def reset_round(state, balls):
    state["phase"] = "target"
    state["target"] = new_target()
    state["current"] = 0
    state["countdown"] = 3.0
    state["spawn_timer"] = 0.0
    state["warn_blink_t"] = 0.0
    balls.clear()
    pop_texts.clear()

def reset_all(state, balls, basket):
    state["spawn_interval"] = SPAWN_START
    state["score"] = 0
    basket["x"] = W / 2 - BASKET_W / 2

    # Go back to difficulty selection; do not generate a target yet
    state["phase"] = "difficulty"
    state["difficulty"] = None
    state["target"] = 0
    state["current"] = 0
    state["countdown"] = 3.0
    state["spawn_timer"] = 0.0
    state["warn_blink_t"] = 0.0
    balls.clear()
    pop_texts.clear()

def complete_round(state, balls):
    state["spawn_interval"] = max(SPAWN_MIN, state["spawn_interval"] - SPAWN_ACCEL)
    reset_round(state, balls)

def start_countdown(state, balls):
    state["phase"] = "countdown"
    state["countdown"] = 3.0
    state["spawn_timer"] = 0.0
    state["warn_blink_t"] = 0.0
    balls.clear()
    pop_texts.clear()

def toggle_pause(state):
    if state["phase"] == "play":
        state["phase"] = "paused"
    elif state["phase"] == "paused":
        state["phase"] = "play"

# ---------- Pygame setup ----------
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Math Catch (Pygame)")
clock = pygame.time.Clock()

font_hud = pygame.font.SysFont("arial", 18)
font_basket = pygame.font.SysFont("arial", 18, bold=True)
font_ball = pygame.font.SysFont("arial", 18, bold=True)
font_big = pygame.font.SysFont("arial", 56, bold=True)
font_med = pygame.font.SysFont("arial", 32, bold=True)
font_count = pygame.font.SysFont("arial", 96, bold=True)
font_sub = pygame.font.SysFont("arial", 20)
font_pop = pygame.font.SysFont("arial", 40, bold=True)

# ---------- Data ----------
state = {
    "phase": "difficulty",
    "difficulty": None,
    "target": 0,
    "current": 0,
    "score": 0,
    "countdown": 3.0,
    "spawn_timer": 0.0,
    "warn_blink_t": 0.0,
    "spawn_interval": SPAWN_START,
}
balls = []
pop_texts = []

basket = {
    "x": W / 2 - BASKET_W / 2,
    "y": H - 60,
    "w": BASKET_W,
    "h": BASKET_H,
}

reset_all(state, balls, basket)

# ---------- Draw ----------
def draw_background():
    screen.fill(BG)

def draw_basket():
    rect = pygame.Rect(int(basket["x"]), int(basket["y"]), basket["w"], basket["h"])
    pygame.draw.rect(screen, ORANGE, rect, border_radius=8)

    txt = font_basket.render(str(state["current"]), True, (255, 255, 255))
    screen.blit(txt, txt.get_rect(center=rect.center))

def draw_ball(b: Ball):
    if b.type == "mult":
        fill, stroke = G_FILL, G_STROKE
        label = f"x{b.value}"
    elif b.type == "neg":
        fill, stroke = R_FILL, R_STROKE
        label = str(b.value)
    else:
        fill, stroke = Y_FILL, Y_STROKE
        label = str(b.value)

    pygame.draw.circle(screen, fill, (int(b.x), int(b.y)), int(b.r))
    pygame.draw.circle(screen, stroke, (int(b.x), int(b.y)), int(b.r), 2)

    txt = font_ball.render(label, True, LABEL)
    screen.blit(txt, txt.get_rect(center=(int(b.x), int(b.y) + 1)))

def draw_hud():
    # target centered top
    t = font_hud.render(f"Target: {state['target']}", True, HUD)
    screen.blit(t, t.get_rect(midtop=(W // 2, 10)))

    # score top-right
    s = font_hud.render(f"Score: {state['score']}", True, HUD)
    screen.blit(s, s.get_rect(topright=(W - 16, 10)))
    
def draw_blink_warning_if_needed():
    if state["target"] <= 0:
        return
    if state["current"] < 3 * state["target"]:
        return

    # Blink ~2 times per second
    blink_on = (int(state.get("warn_blink_t", 0.0) * 4) % 2) == 0
    if not blink_on:
        return

    msg = "WARNING: NUMBER IS GETTING TOO BIG"
    txt = font_sub.render(msg, True, WARN)
    screen.blit(txt, txt.get_rect(midtop=(W // 2, 34)))

def draw_center_text(big, small=None):
    b = font_big.render(big, True, HUD)
    screen.blit(b, b.get_rect(center=(W // 2, H // 2 - 10)))
    if small:
        sm = font_sub.render(small, True, SUB)
        screen.blit(sm, sm.get_rect(center=(W // 2, H // 2 + 26)))

def draw_difficulty_screen():
    title = font_big.render("Select Difficulty", True, HUD)
    screen.blit(title, title.get_rect(center=(W // 2, H // 2 - 150)))

    bw, bh = 260, 80
    gap = 26
    total_w = bw * 3 + gap * 2
    start_x = W // 2 - total_w // 2
    y = H // 2 - bh // 2

    easy_rect = pygame.Rect(start_x, y, bw, bh)
    med_rect  = pygame.Rect(start_x + bw + gap, y, bw, bh)
    hard_rect = pygame.Rect(start_x + (bw + gap) * 2, y, bw, bh)

    pygame.draw.rect(screen, EASY_BTN, easy_rect, border_radius=14)
    pygame.draw.rect(screen, MED_BTN,  med_rect,  border_radius=14)
    pygame.draw.rect(screen, HARD_BTN, hard_rect, border_radius=14)

    # Optional subtle outline
    pygame.draw.rect(screen, (0, 0, 0), easy_rect, width=2, border_radius=14)
    pygame.draw.rect(screen, (0, 0, 0), med_rect,  width=2, border_radius=14)
    pygame.draw.rect(screen, (0, 0, 0), hard_rect, width=2, border_radius=14)

    easy_txt = font_med.render("Easy", True, BTN_TXT)
    med_txt  = font_med.render("Medium", True, BTN_TXT)
    hard_txt = font_med.render("Hard", True, BTN_TXT)

    screen.blit(easy_txt, easy_txt.get_rect(center=easy_rect.center))
    screen.blit(med_txt,  med_txt.get_rect(center=med_rect.center))
    screen.blit(hard_txt, hard_txt.get_rect(center=hard_rect.center))

    hint = font_sub.render("Choose one to begin", True, SUB)
    screen.blit(hint, hint.get_rect(center=(W // 2, H // 2 + 120)))

    return easy_rect, med_rect, hard_rect

def draw_pause_overlay():
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))
    screen.blit(overlay, (0, 0))

    box_w, box_h = 520, 220
    box = pygame.Rect(W // 2 - box_w // 2, H // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(screen, (30, 30, 30), box, border_radius=18)
    pygame.draw.rect(screen, (56, 56, 56), box, width=2, border_radius=18)

    t = font_big.render("PAUSED", True, HUD)
    screen.blit(t, t.get_rect(center=(W // 2, box.y + 110)))

    sub = font_sub.render("Press ESC to resume", True, SUB)
    screen.blit(sub, sub.get_rect(center=(W // 2, box.y + 152)))

def draw_countdown():
    # target in accent color
    tgt = font_med.render(f"Target: {state['target']}", True, (99, 102, 241))
    screen.blit(tgt, tgt.get_rect(center=(W // 2, H // 2 - 90)))

    t = max(0.0, state["countdown"])
    if t > 0.5:
        txt = font_count.render(str(int(t + 0.9999)), True, HUD)  # ceil
    else:
        txt = font_count.render("GO!", True, HUD)
    screen.blit(txt, txt.get_rect(center=(W // 2, H // 2 + 24)))

# ---------- Update ----------
def update(dt, keys):
    if state["phase"] == "paused":
        return

    state["warn_blink_t"] = state.get("warn_blink_t", 0.0) + dt
    # Update pop text effects regardless of phase (except paused)
    for i in range(len(pop_texts) - 1, -1, -1):
        pop_texts[i].update(dt)
        if not pop_texts[i].alive():
            pop_texts.pop(i)

    # move basket (even on target/countdown to match your JS feel)
    vx = 0.0
    if keys["left"]:
        vx -= BASKET_SPEED
    if keys["right"]:
        vx += BASKET_SPEED
    basket["x"] = clamp(basket["x"] + vx * dt, 0, W - basket["w"])

    if state["phase"] == "countdown":
        state["countdown"] -= dt
        if state["countdown"] <= 0:
            state["phase"] = "play"
            state["spawn_timer"] = 0.0
            balls.clear()
        return

    if state["phase"] != "play":
        balls.clear()
        return

    # spawn
    state["spawn_timer"] += dt
    if state["spawn_timer"] >= state["spawn_interval"]:
        state["spawn_timer"] = 0.0
        spawn_ball(balls)

    # update balls
    rx, ry, rw, rh = basket["x"], basket["y"], basket["w"], basket["h"]

    for i in range(len(balls) - 1, -1, -1):
        b = balls[i]
        b.y += b.vy * dt

        # catch
        if circle_rect_collide(b.x, b.y, b.r, rx, ry, rw, rh):
            if b.type == "mult":
                state["current"] *= b.value
            else:
                state["current"] += b.value  # neg values subtract automatically

            state["score"] += 100

            play_catch_sound(b.type)

            # Pop text effect (e.g., "+5" grows then fades)
            if b.type == "mult":
                pop_label = f"x{b.value}"
            else:
                pop_label = f"+{b.value}" if b.value > 0 else str(b.value)

            pop_texts.append(PopText(b.x, basket["y"], pop_label))

            if state["current"] < 0:
                state["current"] = 0

            balls.pop(i)

            # Losing condition: current number reaches 5× target
            if state["current"] >= 5 * state["target"] and state["target"] > 0:
                state["score"] = 0
                state["phase"] = "game_over"
                balls.clear()
                return

            if state["current"] == state["target"]:
                state["phase"] = "win"
                balls.clear()
                return
            continue

        # missed
        if b.y - b.r > H:
            balls.pop(i)

# ---------- Main loop ----------
async def main():
    keys = {"left": False, "right": False}
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(0.05, dt)  # mimic JS cap

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    keys["left"] = True
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    keys["right"] = True
                elif event.key == pygame.K_r:
                    reset_all(state, balls, basket)
                elif event.key == pygame.K_ESCAPE:
                    toggle_pause(state)

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    keys["left"] = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    keys["right"] = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state["phase"] in ("game_over", "win"):
                    reset_all(state, balls, basket)
                    continue
                if state["phase"] == "difficulty":
                    mx, my = event.pos
                    # Recompute the same button rects used for drawing
                    bw, bh = 260, 80
                    gap = 26
                    total_w = bw * 3 + gap * 2
                    start_x = W // 2 - total_w // 2
                    y = H // 2 - bh // 2
                    easy_rect = pygame.Rect(start_x, y, bw, bh)
                    med_rect  = pygame.Rect(start_x + bw + gap, y, bw, bh)
                    hard_rect = pygame.Rect(start_x + (bw + gap) * 2, y, bw, bh)

                    if easy_rect.collidepoint(mx, my):
                        state["difficulty"] = "easy"
                        reset_round(state, balls)
                    elif med_rect.collidepoint(mx, my):
                        state["difficulty"] = "medium"
                        reset_round(state, balls)
                    elif hard_rect.collidepoint(mx, my):
                        state["difficulty"] = "hard"
                        reset_round(state, balls)

                elif state["phase"] == "target":
                    start_countdown(state, balls)

        update(dt, keys)

        # render
        draw_background()
        draw_basket()
        for p in pop_texts:
            p.draw(screen)

        if state["phase"] == "paused":
            draw_hud()
            for b in balls:
                draw_ball(b)  # shows frozen balls
            draw_pause_overlay()
            draw_blink_warning_if_needed()
        elif state["phase"] == "play":
            for b in balls:
                draw_ball(b)
            draw_hud()
            draw_blink_warning_if_needed()
        elif state["phase"] == "game_over":
            draw_hud()
            draw_center_text("Game Over", "Press R to restart")
        elif state["phase"] == "win":
            draw_hud()
            draw_center_text("Congratulations!", "Press R or click to replay")
        elif state["phase"] == "difficulty":
            # No HUD yet; just the selection screen
            draw_difficulty_screen()
        elif state["phase"] == "target":
            draw_hud()

            big = font_big.render(f"Target: {state['target']}", True, HUD)
            screen.blit(big, big.get_rect(center=(W // 2, H // 2 - 70)))

            small = font_sub.render("Click to start", True, SUB)
            screen.blit(small, small.get_rect(center=(W // 2, H // 2 + 10)))

            warn = font_sub.render("Don't let the number grow big!", True, WARN)
            screen.blit(warn, warn.get_rect(center=(W // 2, H // 2 + 44)))
        elif state["phase"] == "countdown":
            draw_hud()
            draw_countdown()

        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()
    
asyncio.run(main())