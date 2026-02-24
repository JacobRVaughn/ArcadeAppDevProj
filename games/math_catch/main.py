import asyncio
import random
import pygame

pygame.init()

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

TARGET_MIN, TARGET_MAX = 5, 11

SPAWN_START = 0.85
SPAWN_MIN = 0.35
SPAWN_ACCEL = 0.03

MULT_CHANCE = 0.12
NEG_CHANCE  = 0.15

# ---------- Colors ----------
BG = (16, 42, 90)
HUD = (215, 230, 255)
SUB = (161, 161, 170)

ORANGE = (255, 122, 24)

Y_FILL, Y_STROKE = (253, 224, 71), (245, 158, 11)
G_FILL, G_STROKE = (74, 222, 128), (22, 163, 74)
R_FILL, R_STROKE = (248, 113, 113), (220, 38, 38)

LABEL = (11, 27, 58)

# ---------- Helpers ----------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def new_target():
    return random.randint(TARGET_MIN, TARGET_MAX)

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
    balls.clear()

def reset_all(state, balls, basket):
    state["spawn_interval"] = SPAWN_START
    state["score"] = 0
    basket["x"] = W / 2 - BASKET_W / 2
    reset_round(state, balls)

def complete_round(state, balls):
    state["spawn_interval"] = max(SPAWN_MIN, state["spawn_interval"] - SPAWN_ACCEL)
    reset_round(state, balls)

def start_countdown(state, balls):
    state["phase"] = "countdown"
    state["countdown"] = 3.0
    state["spawn_timer"] = 0.0
    balls.clear()

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

# ---------- Data ----------
state = {
    "phase": "target",
    "target": 0,
    "current": 0,
    "score": 0,
    "countdown": 3.0,
    "spawn_timer": 0.0,
    "spawn_interval": SPAWN_START,
}
balls = []

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

def draw_center_text(big, small=None):
    b = font_big.render(big, True, HUD)
    screen.blit(b, b.get_rect(center=(W // 2, H // 2 - 10)))
    if small:
        sm = font_sub.render(small, True, SUB)
        screen.blit(sm, sm.get_rect(center=(W // 2, H // 2 + 26)))

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

            if state["current"] < 0:
                state["current"] = 0

            balls.pop(i)

            if state["current"] == state["target"]:
                complete_round(state, balls)
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
                if state["phase"] == "target":
                    start_countdown(state, balls)

        update(dt, keys)

        # render
        draw_background()
        draw_basket()

        if state["phase"] == "paused":
            draw_hud()
            for b in balls:
                draw_ball(b)  # shows frozen balls
            draw_pause_overlay()
        elif state["phase"] == "play":
            for b in balls:
                draw_ball(b)
            draw_hud()
        elif state["phase"] == "target":
            draw_hud()
            draw_center_text(f"Target: {state['target']}", "Click to start")
        elif state["phase"] == "countdown":
            draw_hud()
            draw_countdown()

        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()
    
asyncio.run(main())