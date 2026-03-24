# -*- coding: utf-8 -*-
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

# Castle palette
CASTLE_STONE  = (160, 150, 140)
CASTLE_DARK   = (110, 100,  90)
CASTLE_LIGHT  = (200, 195, 185)
CASTLE_ROOF   = (100,  60, 140)
CASTLE_ROOF_D = ( 70,  35, 100)
CASTLE_GATE   = ( 40,  30,  20)
CASTLE_WINDOW = (180, 220, 255)
CASTLE_FLAG_R = (220,  50,  50)
CASTLE_FLAG_Y = (255, 215,   0)

# Enemy-specific palettes
SLIME_BODY    = (80,  210,  90)
SLIME_DARK    = (40,  140,  50)
SLIME_SHINE   = (180, 255, 180)
SLIME_EYE     = (255, 255, 255)

GOBLIN_BODY   = (180, 120,  50)
GOBLIN_DARK   = (120,  70,  20)
GOBLIN_MOUTH  = (200,  80,  60)
GOBLIN_TOOTH  = (240, 230, 200)
GOBLIN_EAR    = (220, 140,  60)

TROLL_BODY    = (100, 130,  80)
TROLL_DARK    = ( 60,  90,  40)
TROLL_MOSS    = ( 80, 160,  60)
TROLL_MOUTH   = (160,  60,  40)
TROLL_TOOTH   = (220, 220, 180)

DRAGON_BODY   = (200,  50,  50)
DRAGON_DARK   = (140,  20,  20)
DRAGON_WING   = (230,  80,  40)
DRAGON_BELLY  = (255, 180, 120)
DRAGON_FIRE   = (255, 220,  50)
DRAGON_HORN   = (255, 200,  50)

GHOST_BODY    = (200, 210, 255)
GHOST_DARK    = (140, 150, 220)
GHOST_GLOW    = (230, 235, 255)
GHOST_EYE     = ( 80,  60, 160)

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
        "emoji": "1",
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
        "emoji": "A",
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
        "emoji": "*",
        "question": lambda: _shape_q(),
        "desc": "Blasts shapes knowledge!",
    },
}

def generate_path(cols=16, rows=10, min_length=25, max_attempts=200):
    for attempt in range(max_attempts):
        path = []
        start_row = random.randint(1, rows - 2)
        path.append((0, start_row))
        visited = {(0, start_row)}

        for step in range(400):
            x, y = path[-1]
            candidates = []
            for dx, dy, weight in [(1, 0, 4), (0, 1, 2), (0, -1, 2), (-1, 0, 1)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx <= cols - 1 and 1 <= ny <= rows - 2):
                    continue
                if (nx, ny) in visited:
                    continue
                adj_count = sum(
                    1 for cx, cy in [(nx+1,ny),(nx-1,ny),(nx,ny+1),(nx,ny-1)]
                    if (cx, cy) in visited and not (cx == x and cy == y)
                )
                if adj_count > 0:
                    continue
                candidates.extend([(nx, ny)] * weight)

            if not candidates:
                break

            nx, ny = random.choice(candidates)
            path.append((nx, ny))
            visited.add((nx, ny))

            if nx == cols - 1:
                break

        if path[-1][0] == cols - 1 and len(path) >= min_length:
            return path

    return _fallback_path(rows)


def _fallback_path(rows=10):
    mid = rows // 2
    path = [(x, mid) for x in range(16)]
    return path

RAW_PATH = []
PATH_SET = set()

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

def answer_to_str(ans):
    return str(ans).upper().strip()

def path_pixels():
    return [(x * TILE + TILE//2, y * TILE + TILE//2) for x, y in RAW_PATH]


# ─── Castle Drawing ──────────────────────────────────────────────────────────

def draw_castle(surf, cx, cy, tile_size=48):
    x = cx
    y = cy
    w = tile_size
    h = tile_size

    keep_l = x + w // 4
    keep_r = x + 3 * w // 4
    keep_t = y + h // 3
    keep_b = y + h - 2
    keep_w = keep_r - keep_l
    keep_h = keep_b - keep_t

    pygame.draw.rect(surf, CASTLE_DARK,
                     (keep_l - 2, keep_t + 2, keep_w + 4, keep_h + 2),
                     border_radius=2)
    pygame.draw.rect(surf, CASTLE_STONE,
                     (keep_l, keep_t, keep_w, keep_h),
                     border_radius=2)
    pygame.draw.rect(surf, CASTLE_LIGHT,
                     (keep_l, keep_t, 3, keep_h))

    lt_l = x + 2
    lt_r = x + w // 4 + 4
    lt_t = y + h // 4
    lt_b = y + h - 2
    lt_w = lt_r - lt_l
    lt_h = lt_b - lt_t

    pygame.draw.rect(surf, CASTLE_DARK,
                     (lt_l - 1, lt_t + 2, lt_w + 2, lt_h + 2),
                     border_radius=2)
    pygame.draw.rect(surf, CASTLE_STONE,
                     (lt_l, lt_t, lt_w, lt_h),
                     border_radius=2)
    pygame.draw.rect(surf, CASTLE_LIGHT, (lt_l, lt_t, 2, lt_h))

    rt_l = x + 3 * w // 4 - 4
    rt_r = x + w - 2
    rt_t = y + h // 4
    rt_b = y + h - 2
    rt_w = rt_r - rt_l
    rt_h = rt_b - rt_t

    pygame.draw.rect(surf, CASTLE_DARK,
                     (rt_l - 1, rt_t + 2, rt_w + 2, rt_h + 2),
                     border_radius=2)
    pygame.draw.rect(surf, CASTLE_STONE,
                     (rt_l, rt_t, rt_w, rt_h),
                     border_radius=2)
    pygame.draw.rect(surf, CASTLE_LIGHT, (rt_l, rt_t, 2, rt_h))

    def draw_merlons(surf, left, top, width, count=3):
        slot_w = width // count
        for i in range(count):
            mx = left + i * slot_w
            pygame.draw.rect(surf, CASTLE_STONE,
                             (mx + 1, top - 5, slot_w - 2, 6),
                             border_radius=1)
            pygame.draw.rect(surf, CASTLE_LIGHT,
                             (mx + 1, top - 5, 1, 6))

    draw_merlons(surf, lt_l, lt_t, lt_w, 2)
    draw_merlons(surf, rt_l, rt_t, rt_w, 2)
    draw_merlons(surf, keep_l, keep_t, keep_w, 3)

    def draw_cone_roof(surf, left, top, width, height=10):
        apex_x = left + width // 2
        apex_y = top - height
        pts = [
            (left - 1,         top),
            (left + width + 1, top),
            (apex_x,           apex_y),
        ]
        pygame.draw.polygon(surf, CASTLE_ROOF, pts)
        pygame.draw.polygon(surf, CASTLE_ROOF_D, pts, 1)

    draw_cone_roof(surf, lt_l, lt_t - 4, lt_w, 10)
    draw_cone_roof(surf, rt_l, rt_t - 4, rt_w, 10)
    draw_cone_roof(surf, keep_l + keep_w // 4, keep_t - 4,
                   keep_w // 2, 12)

    spire_cx = keep_l + keep_w // 2
    spire_ty = keep_t - 16
    pygame.draw.line(surf, (80, 60, 40),
                     (spire_cx, spire_ty),
                     (spire_cx, spire_ty + 10), 1)
    flag_pts = [
        (spire_cx,     spire_ty),
        (spire_cx + 7, spire_ty + 3),
        (spire_cx,     spire_ty + 6),
    ]
    pygame.draw.polygon(surf, CASTLE_FLAG_R, flag_pts)

    gate_w = max(6, keep_w // 3)
    gate_h = keep_h // 2
    gate_l = keep_l + (keep_w - gate_w) // 2
    gate_t = keep_b - gate_h

    pygame.draw.rect(surf, CASTLE_GATE,
                     (gate_l, gate_t, gate_w, gate_h),
                     border_radius=3)
    pygame.draw.ellipse(surf, CASTLE_GATE,
                        (gate_l, gate_t - gate_w // 4,
                         gate_w, gate_w // 2))

    bar_gap = max(2, gate_w // 3)
    for bx in range(gate_l + bar_gap, gate_l + gate_w, bar_gap):
        pygame.draw.line(surf, (70, 55, 40),
                         (bx, gate_t),
                         (bx, keep_b), 1)

    def draw_window(surf, wx, wy, ww=4, wh=5):
        pygame.draw.rect(surf, CASTLE_GATE,   (wx, wy, ww, wh), border_radius=1)
        pygame.draw.rect(surf, CASTLE_WINDOW, (wx+1, wy+1, ww-2, wh-2))

    draw_window(surf, lt_l + lt_w // 2 - 2, lt_t + lt_h // 3)
    draw_window(surf, rt_l + rt_w // 2 - 2, rt_t + rt_h // 3)
    draw_window(surf, keep_l + keep_w // 4 - 2, keep_t + keep_h // 4)
    draw_window(surf, keep_l + 3 * keep_w // 4 - 2, keep_t + keep_h // 4)

    pygame.draw.rect(surf, (60, 40, 20), (x, y, w, h), 2)


# ─── Enemy Art Functions ─────────────────────────────────────────────────────

def draw_slime(surf, cx, cy, s, wobble, slow_tint=False, hp_frac=1.0):
    """Blobby bouncy slime — squishes vertically with wobble."""
    t = wobble
    # Squish/stretch: wider when bouncing down, taller when up
    squish_x = s + int(math.sin(t * 2) * s * 0.35)
    squish_y = s - int(math.sin(t * 2) * s * 0.25)

    body_col  = (120, 230, 100) if not slow_tint else (160, 200, 255)
    dark_col  = (50,  150,  50) if not slow_tint else (100, 140, 220)
    shine_col = (200, 255, 190) if not slow_tint else (210, 230, 255)

    # Drop shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 80),
                        (cx - squish_x + 3, cy + squish_y - 4,
                         squish_x * 2, 8))

    # Body blob — approximate with overlapping circles for blobby look
    body_rect = pygame.Rect(cx - squish_x, cy - squish_y,
                            squish_x * 2, squish_y * 2)
    pygame.draw.ellipse(surf, dark_col,
                        (cx - squish_x + 2, cy - squish_y + 3,
                         squish_x * 2, squish_y * 2))
    pygame.draw.ellipse(surf, body_col, body_rect)

    # Blobby bumps on top
    for bx_off, by_off, br in [(-squish_x//2, -squish_y+2, s//3),
                                 (0,           -squish_y,   s//4),
                                 (squish_x//2, -squish_y+2, s//3)]:
        pygame.draw.circle(surf, body_col, (cx + bx_off, cy + by_off), br)
        pygame.draw.circle(surf, dark_col, (cx + bx_off, cy + by_off), br, 2)

    # Shine highlight
    pygame.draw.ellipse(surf, shine_col,
                        (cx - squish_x//2, cy - squish_y + 2,
                         squish_x//2, squish_y//3))

    # Cute eyes — wide-set, big pupils wobble
    eye_y = cy - squish_y // 4
    for ex_off in [-squish_x // 3, squish_x // 3]:
        ex = cx + ex_off
        pygame.draw.circle(surf, WHITE,          (ex, eye_y), s // 4 + 1)
        pygame.draw.circle(surf, (20, 20, 40),   (ex, eye_y), s // 5)
        pygame.draw.circle(surf, (100, 180, 255),(ex, eye_y), s // 7)   # iris
        pygame.draw.circle(surf, BLACK,          (ex, eye_y), s // 9)   # pupil
        pygame.draw.circle(surf, WHITE,          (ex - 1, eye_y - 1), max(1, s // 10))  # shine

    # Little smile
    smile_y = cy + squish_y // 3
    smile_w = squish_x // 2
    pygame.draw.arc(surf, dark_col,
                    (cx - smile_w, smile_y - 3, smile_w * 2, 8),
                    math.pi, math.pi * 2, 2)

    # Outline
    pygame.draw.ellipse(surf, dark_col, body_rect, 2)

    # HP bar
    bar_w = s * 2
    pygame.draw.rect(surf, RED,   (cx - s, cy - s - 10, bar_w, 5))
    pygame.draw.rect(surf, GREEN, (cx - s, cy - s - 10, int(bar_w * hp_frac), 5))
    pygame.draw.rect(surf, BLACK, (cx - s, cy - s - 10, bar_w, 5), 1)


def draw_goblin(surf, cx, cy, s, wobble, slow_tint=False, hp_frac=1.0):
    """Fierce toothy goblin — orange-brown, big ears, huge grin."""
    t = wobble
    run_bob = int(math.sin(t * 3) * 2)   # head bobs while running
    cy2 = cy + run_bob

    body_col  = (200, 130,  55) if not slow_tint else (180, 160, 220)
    dark_col  = (130,  75,  20) if not slow_tint else (110, 100, 180)
    ear_col   = (230, 150,  70) if not slow_tint else (200, 175, 235)

    # Body (rounded rect, slightly squashed)
    body_rect = pygame.Rect(cx - s, cy2 - s // 2, s * 2, int(s * 1.2))
    pygame.draw.rect(surf, dark_col,
                     (cx - s + 2, cy2 - s // 2 + 3, s * 2, int(s * 1.2)),
                     border_radius=6)
    pygame.draw.rect(surf, body_col, body_rect, border_radius=6)

    # Head
    head_r = int(s * 0.85)
    head_y = cy2 - s - head_r // 2
    pygame.draw.circle(surf, dark_col, (cx + 2, head_y + 2), head_r)
    pygame.draw.circle(surf, body_col, (cx,     head_y),     head_r)

    # Big pointy ears
    for ex_sign in [-1, 1]:
        ear_x = cx + ex_sign * (head_r - 2)
        ear_pts = [
            (ear_x,                       head_y),
            (ear_x + ex_sign * (s // 2),  head_y - s // 2 - 4),
            (ear_x + ex_sign * (s // 4),  head_y + s // 4),
        ]
        pygame.draw.polygon(surf, dark_col, ear_pts)
        inner_ear = [
            (ear_x + ex_sign * 2,              head_y),
            (ear_x + ex_sign * (s // 2 - 2),  head_y - s // 2 - 1),
            (ear_x + ex_sign * (s // 4),       head_y + s // 4 - 2),
        ]
        pygame.draw.polygon(surf, PINK, inner_ear)

    # Eyes — angry / fierce (angled brows)
    eye_y = head_y - head_r // 6
    for ex_sign, ex_off in [(-1, -head_r//3), (1, head_r//3)]:
        ex = cx + ex_off
        pygame.draw.circle(surf, WHITE,       (ex, eye_y), s // 4)
        pygame.draw.circle(surf, (220, 80, 0),(ex, eye_y), s // 5)   # amber iris
        pygame.draw.circle(surf, BLACK,       (ex, eye_y), s // 7)   # pupil
        pygame.draw.circle(surf, WHITE,       (ex - 1, eye_y - 1), max(1, s // 10))
        # angry brow
        brow_ox = ex_sign * s // 5
        pygame.draw.line(surf, dark_col,
                         (ex - s//5, eye_y - s//4 + brow_ox),
                         (ex + s//5, eye_y - s//4 - brow_ox), 2)

    # Wide toothy grin
    mouth_y  = head_y + head_r // 3
    mouth_w  = head_r - 2
    pygame.draw.arc(surf, dark_col,
                    (cx - mouth_w, mouth_y, mouth_w * 2, head_r // 2),
                    math.pi, math.pi * 2, 3)
    # Teeth — jagged
    tooth_top = mouth_y + 2
    for i, tx_off in enumerate(range(-mouth_w + 4, mouth_w - 2, 7)):
        tooth_col = (240, 235, 210) if i % 2 == 0 else (200, 195, 170)
        pygame.draw.polygon(surf, tooth_col, [
            (cx + tx_off,     tooth_top),
            (cx + tx_off + 3, tooth_top),
            (cx + tx_off + 1, tooth_top + 5),
        ])

    # Little nose bump
    pygame.draw.circle(surf, dark_col, (cx, head_y + head_r // 6), 3)
    pygame.draw.circle(surf, (180, 100, 40), (cx - 2, head_y + head_r // 6 - 1), 2)

    # Outline
    pygame.draw.circle(surf, dark_col, (cx, head_y), head_r, 2)
    pygame.draw.rect(surf,   dark_col, body_rect, 2, border_radius=6)

    # HP bar
    bar_w = s * 2
    pygame.draw.rect(surf, RED,   (cx - s, cy - s - 10, bar_w, 5))
    pygame.draw.rect(surf, GREEN, (cx - s, cy - s - 10, int(bar_w * hp_frac), 5))
    pygame.draw.rect(surf, BLACK, (cx - s, cy - s - 10, bar_w, 5), 1)


def draw_troll(surf, cx, cy, s, wobble, slow_tint=False, hp_frac=1.0):
    """Mossy grumpy troll — big & hulking, covered in moss patches."""
    t = wobble
    thud = max(0, int(math.sin(t * 1.5) * 3))   # heavy stomp bob
    cy2 = cy + thud

    body_col = (105, 135,  80) if not slow_tint else (140, 160, 210)
    dark_col = ( 60,  90,  40) if not slow_tint else ( 80, 100, 170)
    moss_col = ( 90, 170,  65) if not slow_tint else (130, 185, 220)

    # Broad body
    body_rect = pygame.Rect(cx - int(s * 1.3), cy2 - s // 2, int(s * 2.6), int(s * 1.4))
    pygame.draw.rect(surf, dark_col,
                     (cx - int(s*1.3)+3, cy2 - s//2 + 4,
                      int(s*2.6), int(s*1.4)), border_radius=8)
    pygame.draw.rect(surf, body_col, body_rect, border_radius=8)

    # Big round head
    head_r = int(s * 1.0)
    head_y = cy2 - s - head_r // 2 + 2
    pygame.draw.circle(surf, dark_col, (cx + 3, head_y + 3), head_r)
    pygame.draw.circle(surf, body_col, (cx,     head_y),     head_r)

    # Moss patches scattered on body & head
    moss_spots = [
        (cx - s//2, cy2 - s//3, s//3, s//4),
        (cx + s//3, cy2 - s//4, s//4, s//3),
        (cx - s//5, head_y - head_r//3, s//3, s//4),
        (cx + head_r//2, head_y, s//4, s//5),
    ]
    for mx, my, mw, mh in moss_spots:
        pygame.draw.ellipse(surf, moss_col, (mx, my, mw, mh))
        pygame.draw.ellipse(surf, dark_col, (mx, my, mw, mh), 1)

    # Small mossy stubble tufts on head top
    for tx_off in [-head_r//2, -head_r//5, head_r//4]:
        tuft_x = cx + tx_off
        tuft_y = head_y - head_r
        for k in range(3):
            pygame.draw.line(surf, moss_col,
                             (tuft_x + k * 2, tuft_y),
                             (tuft_x + k * 2 - 1, tuft_y - 5), 2)

    # Grumpy furrowed eyes
    eye_y = head_y
    for ex_off in [-head_r//3, head_r//3]:
        ex = cx + ex_off
        pygame.draw.circle(surf, (50, 80, 30), (ex, eye_y), s // 4 + 1)
        pygame.draw.circle(surf, (200, 210, 150), (ex, eye_y), s // 4)
        pygame.draw.circle(surf, BLACK,            (ex, eye_y), s // 6)
        pygame.draw.circle(surf, WHITE,            (ex - 1, eye_y - 1), max(1, s // 9))
        # heavy brow line
        pygame.draw.line(surf, dark_col,
                         (ex - s//4 - 2, eye_y - s//3 + (2 if ex_off < 0 else -2)),
                         (ex + s//4,     eye_y - s//3), 3)

    # Grumpy downturned mouth
    mouth_y = head_y + head_r // 3
    pygame.draw.arc(surf, dark_col,
                    (cx - head_r//2, mouth_y - 4, head_r, head_r // 2),
                    0, math.pi, 3)
    # Stubby protruding lower teeth
    for tx_off in [-4, 2]:
        pygame.draw.rect(surf, (220, 215, 180),
                         (cx + tx_off, mouth_y - 1, 4, 6),
                         border_radius=1)

    # Big warty nose
    pygame.draw.ellipse(surf, dark_col,
                        (cx - 5, head_y + head_r // 8 - 1, 12, 8))
    pygame.draw.ellipse(surf, (130, 110, 70),
                        (cx - 4, head_y + head_r // 8 - 1, 10, 7))
    # Wart
    pygame.draw.circle(surf, (90, 75, 40), (cx + 4, head_y + head_r // 8 + 2), 2)

    # Outline
    pygame.draw.circle(surf, dark_col, (cx, head_y), head_r, 2)
    pygame.draw.rect(surf,   dark_col, body_rect, 2, border_radius=8)

    # HP bar
    bar_w = int(s * 2.6)
    pygame.draw.rect(surf, RED,   (cx - s - 3, cy - s - 10, bar_w, 5))
    pygame.draw.rect(surf, GREEN, (cx - s - 3, cy - s - 10, int(bar_w * hp_frac), 5))
    pygame.draw.rect(surf, BLACK, (cx - s - 3, cy - s - 10, bar_w, 5), 1)


def draw_dragon(surf, cx, cy, s, wobble, slow_tint=False, hp_frac=1.0):
    """Winged smoky dragon — red body, big wings, fire breath puff."""
    t = wobble
    wing_flap = int(math.sin(t * 4) * s * 0.5)   # wings flap

    body_col  = (210,  55,  55) if not slow_tint else (180, 140, 220)
    dark_col  = (145,  20,  20) if not slow_tint else (110,  90, 175)
    belly_col = (255, 190, 130) if not slow_tint else (230, 210, 255)
    wing_col  = (235,  85,  45) if not slow_tint else (200, 160, 240)
    wing_dark = (170,  45,  20) if not slow_tint else (140, 100, 200)

    # Wings — drawn behind body
    for wx_sign in [-1, 1]:
        wing_tip_x = cx + wx_sign * (s * 2 + 4)
        wing_tip_y = cy - s - wing_flap * wx_sign
        wing_root_x = cx + wx_sign * s
        wing_pts = [
            (wing_root_x, cy - s // 2),
            (wing_tip_x,  wing_tip_y),
            (wing_tip_x - wx_sign * s, wing_tip_y + s),
            (wing_root_x, cy),
        ]
        pygame.draw.polygon(surf, wing_dark, [(x+2,y+2) for x,y in wing_pts])
        pygame.draw.polygon(surf, wing_col,  wing_pts)
        # Wing membrane lines
        for k in range(1, 4):
            frac = k / 4
            lx = int(wing_root_x + (wing_tip_x - wing_root_x) * frac)
            ly = int((cy - s//2) + (wing_tip_y - (cy - s//2)) * frac)
            pygame.draw.line(surf, wing_dark, (wing_root_x, cy - s//2), (lx, ly), 1)
        pygame.draw.polygon(surf, wing_dark, wing_pts, 2)

    # Tail
    tail_pts = [
        (cx + s, cy + s // 2),
        (cx + s * 2, cy + s),
        (cx + s * 2 + 4, cy + s - 4),
        (cx + s * 2 + 2, cy + s + 4),
        (cx + s, cy + s),
    ]
    pygame.draw.polygon(surf, dark_col, tail_pts)
    pygame.draw.polygon(surf, body_col, tail_pts)
    # tail spike
    pygame.draw.polygon(surf, DRAGON_HORN, [
        (cx + s*2 + 2, cy + s - 2),
        (cx + s*2 + 10, cy + s - 6),
        (cx + s*2 + 4, cy + s + 4),
    ])

    # Body
    body_rect = pygame.Rect(cx - s, cy - s // 2, s * 2, int(s * 1.3))
    pygame.draw.ellipse(surf, dark_col,
                        (cx - s + 3, cy - s//2 + 4, s*2, int(s*1.3)))
    pygame.draw.ellipse(surf, body_col, body_rect)
    # Belly scales
    belly_rect = pygame.Rect(cx - s//2, cy - s//4, s, int(s * 0.9))
    pygame.draw.ellipse(surf, belly_col, belly_rect)
    # Scale texture lines on belly
    for i in range(3):
        sy_off = i * (s // 3)
        pygame.draw.arc(surf, (220, 160, 100),
                        (cx - s//3, cy - s//4 + sy_off, s//1.5, s//4),
                        0, math.pi, 1)

    # Neck + Head
    neck_pts = [
        (cx - s//3, cy - s//2),
        (cx + s//3, cy - s//2),
        (cx + s//4, cy - s - 4),
        (cx - s//4, cy - s - 4),
    ]
    pygame.draw.polygon(surf, dark_col, [(x+2,y+2) for x,y in neck_pts])
    pygame.draw.polygon(surf, body_col, neck_pts)

    head_r = int(s * 0.75)
    head_y = cy - s - head_r + 2
    pygame.draw.circle(surf, dark_col, (cx + 2, head_y + 2), head_r)
    pygame.draw.circle(surf, body_col, (cx,     head_y),     head_r)

    # Horns
    for hx_sign in [-1, 1]:
        horn_base_x = cx + hx_sign * (head_r // 2)
        horn_pts = [
            (horn_base_x - 3,               head_y - head_r + 4),
            (horn_base_x + 3,               head_y - head_r + 4),
            (horn_base_x + hx_sign * 4,     head_y - head_r - 10),
        ]
        pygame.draw.polygon(surf, DRAGON_HORN, horn_pts)
        pygame.draw.polygon(surf, (200, 150, 20), horn_pts, 1)

    # Eyes — slit pupils, glowing
    eye_y = head_y - head_r // 5
    for ex_off in [-head_r//3, head_r//3]:
        ex = cx + ex_off
        pygame.draw.circle(surf, (255, 200, 50), (ex, eye_y), s // 4 + 1)
        pygame.draw.circle(surf, (240, 120,  0), (ex, eye_y), s // 4)
        # Slit pupil
        pygame.draw.ellipse(surf, (10, 5, 0),
                            (ex - 2, eye_y - s//5, 4, int(s * 0.4)))
        pygame.draw.circle(surf, (255, 240, 100), (ex - 1, eye_y - 2), 2)

    # Snout / jaw
    jaw_pts = [
        (cx - head_r + 2, head_y + head_r // 4),
        (cx + head_r - 2, head_y + head_r // 4),
        (cx + head_r,     head_y + head_r // 2),
        (cx - head_r,     head_y + head_r // 2),
    ]
    pygame.draw.polygon(surf, dark_col, [(x+1,y+1) for x,y in jaw_pts])
    pygame.draw.polygon(surf, body_col, jaw_pts)
    # Dragon teeth
    tooth_y = head_y + head_r // 2
    for tx_off in range(-head_r + 5, head_r - 3, 7):
        pygame.draw.polygon(surf, (230, 220, 190), [
            (cx + tx_off,     tooth_y),
            (cx + tx_off + 3, tooth_y),
            (cx + tx_off + 1, tooth_y + 6),
        ])

    # Fire puff from mouth (smoke + flame orbs)
    fire_x = cx + head_r
    fire_y = head_y + head_r // 3
    fire_phase = abs(math.sin(t * 5))
    for k in range(3):
        smoke_r = 4 + k * 3 + int(fire_phase * 2)
        smoke_alpha = max(40, 130 - k * 40)
        smoke_x = fire_x + k * 7 + int(fire_phase * 3)
        smoke_y = fire_y - k * 3
        smoke_col = (
            min(255, 255 - k * 30),
            min(255, 100 + k * 20),
            30 + k * 10
        )
        pygame.draw.circle(surf, smoke_col, (smoke_x, smoke_y), smoke_r)
        pygame.draw.circle(surf, (255, 230, 50), (smoke_x, smoke_y), smoke_r - 2)

    # Back spines
    for i in range(4):
        spine_x = cx - s + i * (s // 2)
        spine_y = cy - s // 2
        pygame.draw.polygon(surf, DRAGON_HORN, [
            (spine_x - 3, spine_y),
            (spine_x + 3, spine_y),
            (spine_x,     spine_y - 7 - i),
        ])

    # Outline
    pygame.draw.circle(surf, dark_col, (cx, head_y), head_r, 2)
    pygame.draw.ellipse(surf, dark_col, body_rect, 2)

    # HP bar
    bar_w = s * 2
    pygame.draw.rect(surf, RED,   (cx - s, cy - s * 2 - 6, bar_w, 5))
    pygame.draw.rect(surf, GREEN, (cx - s, cy - s * 2 - 6, int(bar_w * hp_frac), 5))
    pygame.draw.rect(surf, BLACK, (cx - s, cy - s * 2 - 6, bar_w, 5), 1)


def draw_ghost(surf, cx, cy, s, wobble, slow_tint=False, hp_frac=1.0):
    """Wispy spooky ghost — floats up/down, translucent layers, wavy tail."""
    t = wobble
    float_bob = int(math.sin(t * 2) * 4)   # gentle floating
    cy2 = cy + float_bob

    body_col  = (210, 218, 255) if not slow_tint else (200, 230, 255)
    dark_col  = (130, 140, 220) if not slow_tint else (160, 190, 245)
    glow_col  = (240, 244, 255) if not slow_tint else (225, 240, 255)
    eye_col   = ( 70,  55, 170) if not slow_tint else (110, 130, 220)

    # Outer glow aura (soft bloom)
    glow_r = s + 6 + int(math.sin(t * 3) * 2)
    glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
    for gr in range(glow_r, 0, -2):
        alpha = int(18 * (gr / glow_r))
        pygame.draw.circle(glow_surf, (*glow_col, alpha),
                           (glow_r * 2, glow_r * 2), gr)
    surf.blit(glow_surf, (cx - glow_r * 2, cy2 - glow_r * 2))

    # Wispy tail — wave of overlapping circles tapering down
    tail_points = 6
    for i in range(tail_points, 0, -1):
        frac   = i / tail_points
        tail_r = int(s * 0.7 * frac)
        tail_y = cy2 + s // 2 + (tail_points - i) * (s // 3)
        wave_x = cx + int(math.sin(t * 2 + i * 0.8) * s * 0.3)
        alpha  = int(200 * frac)
        tc     = (*body_col, alpha)
        # Draw as circle (SRCALPHA approach)
        ts = pygame.Surface((tail_r * 4, tail_r * 4), pygame.SRCALPHA)
        pygame.draw.circle(ts, tc, (tail_r * 2, tail_r * 2), tail_r)
        surf.blit(ts, (wave_x - tail_r * 2, tail_y - tail_r * 2))

    # Main body — rounded top, wispy bottom
    # Back layer (slightly darker)
    pygame.draw.circle(surf, dark_col, (cx + 2, cy2 + 2), s)
    # Main body circle
    pygame.draw.circle(surf, body_col, (cx, cy2), s)
    # Inner bright spot
    pygame.draw.circle(surf, glow_col,
                       (cx - s // 4, cy2 - s // 4),
                       s // 2)

    # Spooky hollow eyes (dark voids)
    eye_y  = cy2 - s // 5
    eye_rx, eye_ry = s // 4 + 1, s // 3 + 1   # oval eyes
    for ex_off in [-s // 3, s // 3]:
        ex = cx + ex_off
        # White of eye
        pygame.draw.ellipse(surf, (240, 240, 255),
                            (ex - eye_rx, eye_y - eye_ry, eye_rx*2, eye_ry*2))
        # Dark hollow iris
        pygame.draw.ellipse(surf, eye_col,
                            (ex - eye_rx + 2, eye_y - eye_ry + 2,
                             eye_rx*2 - 4, eye_ry*2 - 4))
        # Tiny inner glow spark
        pygame.draw.circle(surf, (200, 180, 255),
                           (ex - 2, eye_y - 2), max(2, s // 8))
        pygame.draw.circle(surf, WHITE,
                           (ex - 3, eye_y - 3), max(1, s // 12))

    # Wavy spooky mouth — O shape
    mouth_y = cy2 + s // 3
    pygame.draw.ellipse(surf, eye_col,
                        (cx - s // 4, mouth_y - 3, s // 2, s // 3))
    pygame.draw.ellipse(surf, (80, 65, 180),
                        (cx - s // 5, mouth_y - 1, s // 2 - 4, s // 4))

    # Wispy tendrils floating around
    for i in range(3):
        angle = t * 1.5 + i * (math.pi * 2 / 3)
        tx_end = cx   + int(math.cos(angle) * (s + 6))
        ty_end = cy2  + int(math.sin(angle) * (s + 4))
        pygame.draw.line(surf, (*dark_col, 120), (cx, cy2),
                         (tx_end, ty_end), 2)

    # Outline glow ring
    pygame.draw.circle(surf, dark_col, (cx, cy2), s, 2)

    # HP bar
    bar_w = s * 2
    pygame.draw.rect(surf, RED,   (cx - s, cy - s - 10, bar_w, 5))
    pygame.draw.rect(surf, GREEN, (cx - s, cy - s - 10, int(bar_w * hp_frac), 5))
    pygame.draw.rect(surf, BLACK, (cx - s, cy - s - 10, bar_w, 5), 1)


# ─── Classes ────────────────────────────────────────────────────────────────

class Enemy:
    TYPES = [
        {"name": "Slime",   "color": GREEN,  "hp": 5,  "speed": 1.2, "reward": 10, "size": 16, "shape": "slime"},
        {"name": "Goblin",  "color": ORANGE, "hp": 10, "speed": 1.5, "reward": 15, "size": 14, "shape": "goblin"},
        {"name": "Troll",   "color": GRAY,   "hp": 20, "speed": 0.8, "reward": 25, "size": 20, "shape": "troll"},
        {"name": "Dragon",  "color": RED,    "hp": 40, "speed": 0.6, "reward": 50, "size": 22, "shape": "dragon"},
        {"name": "Ghost",   "color": (200,200,255), "hp": 8, "speed": 2.0, "reward": 20, "size": 12, "shape": "ghost"},
    ]

    # Map shape name -> TYPES index for safe lookup
    SHAPE_INDEX = {t["shape"]: i for i, t in enumerate(TYPES)}

    def __init__(self, etype, wave):
        # Clamp etype to valid range
        etype = max(0, min(etype, len(self.TYPES) - 1))
        t = self.TYPES[etype]
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

        # Guard: need at least 2 path points to move
        if len(self.path) < 2:
            self.reached_end = True
            self.alive = False
            return

    def update(self):
        if not self.alive:
            return
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
        if dist == 0 or dist < spd:
            self.pidx += 1
            self.x, self.y = float(tx), float(ty)
        else:
            self.x += dx / dist * spd
            self.y += dy / dist * spd

    def draw(self, surf):
        if not self.alive:
            return
        cx, cy   = int(self.x), int(self.y)
        s        = self.size
        slow     = self.slow_timer > 0
        hp_frac  = max(0.0, self.hp / max(1, self.max_hp))

        try:
            if   self.shape == "slime":  draw_slime (surf, cx, cy, s, self.wobble, slow, hp_frac)
            elif self.shape == "goblin": draw_goblin(surf, cx, cy, s, self.wobble, slow, hp_frac)
            elif self.shape == "troll":  draw_troll (surf, cx, cy, s, self.wobble, slow, hp_frac)
            elif self.shape == "dragon": draw_dragon(surf, cx, cy, s, self.wobble, slow, hp_frac)
            elif self.shape == "ghost":  draw_ghost (surf, cx, cy, s, self.wobble, slow, hp_frac)
            else:
                # Fallback: plain circle so nothing crashes
                pygame.draw.circle(surf, self.color, (cx, cy), s)
        except Exception as e:
            print(f"[draw error] {self.shape} @ ({cx},{cy}) s={s}: {e}")
            pygame.draw.circle(surf, self.color, (cx, cy), s)

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
        base_r = TILE // 2 - 4
        pygame.draw.circle(surf, (40, 40, 60), (px, py), base_r + 3)
        pygame.draw.circle(surf, self.color, (px, py), base_r)
        ring_r = int(base_r + 3 + math.sin(self.anim) * 2)
        pygame.draw.circle(surf, self.color, (px, py), ring_r, 2)

        font_s = pygame.font.SysFont("arial", 18, bold=True)
        labels = {"number": "1+", "letter": "A", "star": "*"}
        label = labels.get(self.ttype, "?")
        txt = font_s.render(label, True, WHITE)
        surf.blit(txt, txt.get_rect(center=(px, py)))

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
        self.result     = None
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
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 30, 180))
        surf.blit(overlay, (0, 0))

        panel = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surf, DARK_B, panel, border_radius=20)
        pygame.draw.rect(surf, CYAN, panel, 3, border_radius=20)

        f_title = pygame.font.SysFont("arial", 22, bold=True)
        t = f_title.render("Quiz Time! Answer to place tower!", True, GOLD)
        surf.blit(t, t.get_rect(centerx=SCREEN_W//2, y=self.y + 20))

        f_q = pygame.font.SysFont("arial", 26, bold=True)
        q_surf = f_q.render(self.question, True, WHITE)
        surf.blit(q_surf, q_surf.get_rect(centerx=SCREEN_W//2, y=self.y + 70))

        if self.result == "correct":
            msg = f_q.render("Correct! Great job!", True, GREEN)
            surf.blit(msg, msg.get_rect(centerx=SCREEN_W//2, y=self.y + 120))
        elif self.result == "wrong":
            msg = f_q.render(f"Answer: {self.answer} Try again!", True, RED)
            surf.blit(msg, msg.get_rect(centerx=SCREEN_W//2, y=self.y + 120))
        else:
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
        self.max_waves = 4
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Math & Letters Kingdom")
        self.clock  = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.gold      = 150
        self.lives     = 10
        self.wave      = 0
        self.max_waves = 4
        self.score     = 0
        self.towers    = []
        self.enemies   = []
        self.projs     = []
        self.floats    = []          # <-- this is the correct name
        self.quiz      = None
        self.selected_tower_type = "number"
        self.selected_tower      = None
        self.state     = "title"
        self.wave_active    = False  # <-- ADD THIS, was missing entirely
        self.spawn_queue    = []
        self.spawn_timer    = 0
        self.spawn_delay    = 90
        self.between_waves  = True
        self.total_waves    = 4      # <-- fix this too, was 8

        global RAW_PATH, PATH_SET
        random.seed(pygame.time.get_ticks())
        RAW_PATH = generate_path()
        PATH_SET = set(RAW_PATH)

        self.path_pixels    = path_pixels()
        self.bg_surf        = self._make_bg()
        self.correct_count  = 0
        self.wrong_count    = 0
        self._bg_anim       = 0

    def _make_bg(self):
        surf = pygame.Surface((SCREEN_W, SCREEN_H))
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

        # Start marker (green tile with label)
        sx, sy = RAW_PATH[0]
        pygame.draw.rect(surf, GREEN, (sx*TILE, sy*TILE, TILE, TILE))
        f = pygame.font.SysFont("arial", 13, bold=True)
        surf.blit(f.render("START", True, WHITE), (sx*TILE+2, sy*TILE+17))

        # ── Castle end marker ────────────────────────────────────────────────
        ex, ey = RAW_PATH[-1]
        # Draw a grass-colored base first so the path tile is covered
        pygame.draw.rect(surf, PATH_C, (ex*TILE, ey*TILE, TILE, TILE))
        # Draw the castle illustration
        draw_castle(surf, ex * TILE, ey * TILE, TILE)

        # Right panel background
        pygame.draw.rect(surf, DARK_B, (TILE * 16, 0, SCREEN_W - TILE * 16, SCREEN_H))
        return surf

    # ── Wave Logic ──────────────────────────────────────────────────────────

    def start_wave(self):
        if self.wave >= self.max_waves:
            return
        self.wave += 1
        self.between_waves = False   # <-- hide the "next wave" button

        wave_plans = {
            1: [("slime",  6)],
            2: [("slime",  4), ("goblin", 3)],
            3: [("goblin", 4), ("troll",  2)],
            4: [("troll",  3), ("dragon", 2), ("ghost", 3)],
        }
        plan = wave_plans.get(self.wave, [("slime", 5)])
        self.spawn_queue = []
        for shape, count in plan:
            etype = Enemy.SHAPE_INDEX.get(shape, 0)
            for _ in range(count):
                self.spawn_queue.append(etype)

        random.shuffle(self.spawn_queue)
        self.spawn_timer  = 0
        self.spawn_delay  = 90
        self.wave_active  = True


    def update_wave(self):
        if not self.wave_active:
            return

        # Spawn next enemy
        self.spawn_timer -= 1
        if self.spawn_timer <= 0 and self.spawn_queue:
            etype = self.spawn_queue.pop(0)
            enemy = Enemy(etype, self.wave)
            if enemy.alive:
                self.enemies.append(enemy)
            self.spawn_timer = self.spawn_delay

        # Remove any enemy that is dead OR reached the end
        self.enemies = [e for e in self.enemies if e.alive and not e.reached_end]

        # Wave is over when queue empty AND no enemies on field
        if not self.spawn_queue and not self.enemies:
            self.wave_active  = False
            self.between_waves = True        # <-- allow player to start next wave
            bonus = 20 + self.wave * 10

            if self.wave >= self.max_waves:
                self.state = "win"
            else:
                self.gold += bonus
                self.floats.append(           # <-- was self.floating_texts (wrong name)
                    FloatingText(
                        SCREEN_W // 2, SCREEN_H // 2,
                        f"Wave {self.wave} Clear!  +{bonus}G",
                        GOLD, 28
                    )
                )

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

        info = TOWERS[self.selected_tower_type]
        q, a = info["question"]()
        placed_tx, placed_ty = tx, ty
        ttype = self.selected_tower_type

        def on_success():
            self.gold -= cost
            self.towers.append(Tower(placed_tx, placed_ty, ttype))
            self.correct_count += 1
            self.floats.append(FloatingText(
                placed_tx*TILE+24, placed_ty*TILE, "+Tower! ", GREEN, 22))

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
                            "Upgraded!", CYAN, 20))

            if event.type == pygame.MOUSEBUTTONDOWN and self.state == "playing":
                mx, my = pygame.mouse.get_pos()
                tx, ty = mx // TILE, my // TILE
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

        # Update enemies (move along path) and handle reached_end
        for e in self.enemies:
            e.update()
            if e.reached_end:
                self.lives -= 1
                e.alive = False
                if self.lives <= 0:
                    self.lives = 0
                    self.state = "game_over"

        # Award gold for killed enemies
        for e in self.enemies:
            if not e.alive and e.reward > 0:
                self.gold  += e.reward
                self.score += e.reward
                self.floats.append(FloatingText(
                    int(e.x), int(e.y) - 10,
                    f"+{e.reward}", GOLD, 18))
                e.reward = 0

        # Final cleanup — update_wave handles enemy list too but this
        # catches any stragglers marked dead by towers / reached_end above
        self.enemies = [e for e in self.enemies if e.alive and not e.reached_end]
        self.projs   = [p for p in self.projs  if p.alive]
        for f in self.floats:
            f.update()
        self.floats  = [f for f in self.floats  if f.life > 0]


    # ── Drawing ─────────────────────────────────────────────────────────────

    def draw_title(self):
        self.screen.fill((10, 20, 50))
        for i in range(80):
            sx = (i * 137) % SCREEN_W
            sy = (i * 79)  % SCREEN_H
            r  = 1 + (i % 3)
            pygame.draw.circle(self.screen, WHITE, (sx, sy), r)

        f_big   = pygame.font.SysFont("arial", 64, bold=True)
        f_med   = pygame.font.SysFont("arial", 28, bold=True)
        f_small = pygame.font.SysFont("arial", 20)

        title = f_big.render("Math & Letters Kingdom", True, GOLD)
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
            labels = {"number": "1+", "letter": "A", "star": "*"}
            lbl = f.render(labels[k], True, WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=(cx, 520)))
            nm = pygame.font.SysFont("arial", 14).render(info["name"], True, GRAY)
            self.screen.blit(nm, nm.get_rect(centerx=cx, y=555))

    def draw_panel(self):
        px = TILE * 16
        font_b = pygame.font.SysFont("arial", 18, bold=True)
        font_s = pygame.font.SysFont("arial", 15)

        stats = [
            (f"Gold: {self.gold}", GOLD),
            (f"Lives: {self.lives}", RED),
            (f"Wave: {self.wave}/{self.total_waves}", CYAN),
            (f"Score: {self.score}", YELLOW),
        ]
        for i, (txt, col) in enumerate(stats):
            s = font_b.render(txt, True, col)
            self.screen.blit(s, (px + 10, 15 + i * 28))

        pygame.draw.line(self.screen, GRAY, (px+5, 130), (SCREEN_W-5, 130), 2)

        s = font_b.render("Build (click grid):", True, WHITE)
        self.screen.blit(s, (px + 10, 138))

        for i, (k, info) in enumerate(TOWERS.items()):
            y = 165 + i * 75
            selected = (k == self.selected_tower_type)
            color = CYAN if selected else DARK_B
            rect = pygame.Rect(px+6, y, SCREEN_W - px - 12, 68)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, info["color"], rect, 2, border_radius=10)
            pygame.draw.circle(self.screen, info["color"], (px+28, y+34), 18)
            pygame.draw.circle(self.screen, BLACK, (px+28, y+34), 18, 2)
            fl = font_b.render(["1+","A","*"][i], True, WHITE)
            self.screen.blit(fl, fl.get_rect(center=(px+28, y+34)))
            nm = font_b.render(f"[{i+1}] {info['name']}", True, WHITE)
            self.screen.blit(nm, (px+52, y+8))
            cost_s = font_s.render(f"Cost: {info['cost']}  {info['desc']}", True, GRAY)
            self.screen.blit(cost_s, (px+52, y+30))
            range_s = font_s.render(f"Range {info['range']} | Dmg {info['damage']}", True, GRAY)
            self.screen.blit(range_s, (px+52, y+48))

        pygame.draw.line(self.screen, GRAY, (px+5, 398), (SCREEN_W-5, 398), 2)

        if self.selected_tower:
            t = self.selected_tower
            info = TOWERS[t.ttype]
            s = font_b.render("Selected Tower:", True, CYAN)
            self.screen.blit(s, (px+10, 405))
            self.screen.blit(font_s.render(f"{info['name']} Lv{t.level}", True, WHITE), (px+10, 427))
            uc = t.upgrade_cost()
            if t.level < 3:
                self.screen.blit(font_s.render(f"[U] Upgrade: {uc}", True, GOLD), (px+10, 447))
            else:
                self.screen.blit(font_s.render("Max Level!", True, GREEN), (px+10, 447))
        else:
            hint = font_s.render("Click a tower to select", True, GRAY)
            self.screen.blit(hint, (px+10, 410))

        if self.between_waves and self.wave < self.total_waves:
            bw = SCREEN_W - px - 20
            brect = pygame.Rect(px+10, SCREEN_H - 60, bw, 44)
            pulse = abs(math.sin(pygame.time.get_ticks() / 300))
            bc = (int(50 + pulse*100), int(180 + pulse*60), int(50 + pulse*100))
            pygame.draw.rect(self.screen, bc, brect, border_radius=12)
            pygame.draw.rect(self.screen, WHITE, brect, 2, border_radius=12)
            bt = font_b.render("SPACE -> Next Wave!", True, WHITE)
            self.screen.blit(bt, bt.get_rect(center=brect.center))

        qs = font_s.render(f"Correct: {self.correct_count}  Wrong: {self.wrong_count}", True, WHITE)
        self.screen.blit(qs, (px+10, SCREEN_H - 80))

    def draw_hud_wave_status(self):
        if not self.between_waves:
            remaining = len(self.spawn_queue) + sum(1 for e in self.enemies if e.alive)
            font = pygame.font.SysFont("arial", 18, bold=True)
            s = font.render(f"Enemies remaining: {remaining}", True, WHITE)
            self.screen.blit(s, (10, SCREEN_H - 30))

        # Wave counter — shows e.g. "Wave 2 / 4"
        wave_label = f"Wave {self.wave} / {self.max_waves}"
        # ...existing code...

        # Show "FINAL WAVE!" warning on wave 4
        if self.wave == self.max_waves and self.wave_active:
            font = pygame.font.SysFont("Arial", 20, bold=True)
            warn = font.render("⚔ FINAL WAVE!", True, RED)
            self.screen.blit(warn, warn.get_rect(centerx=SCREEN_W//2, y=SCREEN_H-30))

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
            self.draw_overlay("YOU WIN!", "You saved the kingdom!", GOLD)

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