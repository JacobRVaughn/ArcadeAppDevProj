import asyncio
import pygame
from dataclasses import dataclass
import math

pygame.init()

XP_EARNED = 10
GAME_ID = "physics"
_xp_fired = False

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 20)
SMALL_FONT = pygame.font.SysFont("arial", 16)
TITLE_FONT = pygame.font.SysFont("arial", 22, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 34, bold=True)

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
DARK_GRAY = (90, 90, 90)
BLUE = (60, 130, 255)
GREEN = (80, 200, 120)
YELLOW = (240, 200, 60)
RED = (220, 70, 70)
PURPLE = (140, 90, 200)
ICE_BLUE = (225, 245, 255)
POPUP_BG = (255, 250, 250)
LIGHT_GRAY = (225, 225, 225)

FORCE_INFO = {
    "F": {
        "title": "Applied Force",
        "formula": "F = push/pull force",
        "desc": "The force used to launch the box.",
    },
    "f": {
        "title": "Friction",
        "formula": "f = μN",
        "desc": "Static: f ≤ μsN   |   Kinetic: f = μkN",
    },
    "N": {
        "title": "Normal Force",
        "formula": "N = mg",
        "desc": "The force of the ground on the box.",
    },
    "W": {
        "title": "Weight",
        "formula": "W = mg",
        "desc": "The force of gravity pulling down on the box.",
    },
}

HELP_TEXT = [
    "Use the sliders to change things like mass, gravity, and launch force.",
    "Click Launch to send the box toward the goal.",
    "Click the force labels to see what each force means."
]


def clamp(value, low, high):
    return max(low, min(high, value))


@dataclass
class Slider:
    x: int
    y: int
    w: int
    label: str
    min_val: float
    max_val: float
    value: float
    enabled: bool = True

    def __post_init__(self):
        self.handle_radius = 10
        self.dragging = False

    def knob_x(self):
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.x + t * self.w)

    def handle_event(self, event):
        if not self.enabled:
            self.dragging = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if abs(mx - self.knob_x()) <= self.handle_radius + 4 and abs(my - self.y) <= 18:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, _ = event.pos
            t = clamp((mx - self.x) / self.w, 0, 1)
            self.value = self.min_val + t * (self.max_val - self.min_val)

    def draw(self, surface):
        track_color = DARK_GRAY if self.enabled else LIGHT_GRAY
        knob_color = BLUE if (self.dragging and self.enabled) else (GRAY if self.enabled else (210, 210, 210))
        label_color = BLACK if self.enabled else DARK_GRAY

        pygame.draw.line(surface, track_color, (self.x, self.y), (self.x + self.w, self.y), 6)
        pygame.draw.circle(surface, knob_color, (self.knob_x(), self.y), self.handle_radius)

        text = f"{self.label}: {self.value:.2f}"
        if not self.enabled:
            text += " (locked)"
        label = FONT.render(text, True, label_color)
        surface.blit(label, (self.x, self.y - 34))


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    color: tuple

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        txt = FONT.render(self.text, True, BLACK)
        surface.blit(
            txt,
            (self.rect.centerx - txt.get_width() // 2,
             self.rect.centery - txt.get_height() // 2),
        )

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


@dataclass
class Level:
    name: str
    description: str
    mode: str
    goal_rect: pygame.Rect
    start_x: int = 120
    start_s: float = 0.0
    friction_locked: bool = False
    fixed_mu_s: float = 0.05
    fixed_mu_k: float = 0.02


def draw_arrow(surface, start, end, color, label=None, label_pos=None, width=4, head_len=12, head_width=8):
    pygame.draw.line(surface, color, start, end, width)

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)

    left = (
        end[0] - head_len * math.cos(angle) + head_width * math.sin(angle),
        end[1] - head_len * math.sin(angle) - head_width * math.cos(angle),
    )
    right = (
        end[0] - head_len * math.cos(angle) - head_width * math.sin(angle),
        end[1] - head_len * math.sin(angle) + head_width * math.cos(angle),
    )
    pygame.draw.polygon(surface, color, [end, left, right])

    label_rect = None
    if label:
        txt = SMALL_FONT.render(label, True, color)
        if label_pos is None:
            label_pos = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        label_rect = txt.get_rect(center=label_pos)
        surface.blit(txt, label_rect)

    return label_rect


def draw_dashed_arrow(surface, start, end, color, label=None, label_pos=None, dash_len=10, gap_len=7, width=3):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        return None

    ux = dx / dist
    uy = dy / dist

    n = 0.0
    while n < dist - dash_len:
        p1 = (start[0] + ux * n, start[1] + uy * n)
        p2 = (start[0] + ux * (n + dash_len), start[1] + uy * (n + dash_len))
        pygame.draw.line(surface, color, p1, p2, width)
        n += dash_len + gap_len

    draw_arrow(surface, (end[0] - ux * 1, end[1] - uy * 1), end, color, label=label, label_pos=label_pos, width=width)


ground_y = 520
box_w, box_h = 70, 70

goal_flat = pygame.Rect(760, ground_y - 80, 140, 80)
goal_ice = pygame.Rect(760, ground_y - 80, 140, 80)

LEVELS = {
    1: Level(
        name="LEVEL ONE",
        description="Flat ground. Use all sliders.",
        mode="flat",
        goal_rect=goal_flat,
        start_x=120,
        friction_locked=False,
    ),
    2: Level(
        name="LEVEL TWO",
        description="Ice. Friction sliders are locked low.",
        mode="flat",
        goal_rect=goal_ice,
        start_x=120,
        friction_locked=True,
        fixed_mu_s=0.03,
        fixed_mu_k=0.01,
    ),
}

sliders = [
    Slider(60, 70, 320, "Mass (kg)", 1.0, 20.0, 5.0),
    Slider(60, 150, 320, "Static friction μs", 0.0, 1.5, 0.30),
    Slider(60, 230, 320, "Kinetic friction μk", 0.0, 1.5, 0.20),
    Slider(60, 310, 320, "Gravity (m/s²)", 1.0, 20.0, 9.81),
    Slider(60, 390, 320, "Launch force", 0.0, 300.0, 120.0),
]

launch_button = Button(pygame.Rect(60, ground_y + 80, 140, 45), "Launch", GREEN)
reset_button = Button(pygame.Rect(220, ground_y + 80, 140, 45), "Reset", YELLOW)
menu_button = Button(pygame.Rect(380, ground_y + 80, 140, 45), "Menu", LIGHT_GRAY)
help_button = Button(pygame.Rect(WIDTH - 55, 15, 40, 40), "?", BLUE)

level_buttons = [
    Button(pygame.Rect(360, 300, 280, 60), "Level One", GREEN),
    Button(pygame.Rect(360, 380, 280, 60), "Level Two", BLUE),
]

game_state = "menu"
current_level_id = 1
active_force_key = None
popup_anchor = (0, 0)
show_help = False

box_flat_x = 120
vx = 0.0
running_motion = False
won = False

def trigger_xp_overlay():
    try:
        from platform import window

        js_code = f"""
(function() {{
  var score   = 1;
  var xp      = {XP_EARNED};
  var gameId  = "{GAME_ID}";

  var targetWin = window.top || window;
  var targetDoc = targetWin.document;

  function runOverlay() {{
    if (typeof targetWin.showGameOverXP === "function") {{
      targetWin.showGameOverXP({{ gameId: gameId, score: score, xpEarned: xp }});
    }} else {{
      if (!targetDoc.getElementById("xpo-script")) {{
        var s = targetDoc.createElement("script");
        s.id  = "xpo-script";
        s.src = "/ArcadeAppDevProj/game-over-xp.js";
        s.onload = function() {{
          targetWin.showGameOverXP({{ gameId: gameId, score: score, xpEarned: xp }});
        }};
        targetDoc.head.appendChild(s);
      }}
    }}
  }}

  runOverlay();
}})();
"""
        window.eval(js_code)

    except Exception as e:
        print(f"[XP overlay] skipped: {e}")

def get_level():
    return LEVELS[current_level_id]


def set_level(level_id):
    global current_level_id, game_state, active_force_key, show_help
    current_level_id = level_id
    game_state = "game"
    active_force_key = None
    show_help = False

    level = get_level()

    friction_enabled = not level.friction_locked
    sliders[1].enabled = friction_enabled
    sliders[2].enabled = friction_enabled

    if level.friction_locked:
        sliders[1].value = level.fixed_mu_s
        sliders[2].value = level.fixed_mu_k

    reset_game()


def reset_game():
    global box_flat_x, vx, running_motion, won, active_force_key, show_help, _xp_fired

    level = get_level()
    box_flat_x = level.start_x
    vx = 0.0
    running_motion = False
    won = False
    active_force_key = None
    show_help = False
    _xp_fired = False


def go_to_menu():
    global game_state, active_force_key, show_help
    game_state = "menu"
    active_force_key = None
    show_help = False


def get_mu_values():
    level = get_level()
    if level.friction_locked:
        return level.fixed_mu_s, level.fixed_mu_k
    return sliders[1].value, sliders[2].value


def get_box_rect():
    return pygame.Rect(int(box_flat_x), ground_y - box_h, box_w, box_h)


def launch_box():
    global vx, running_motion, won

    level = get_level()
    mass = sliders[0].value
    gravity = sliders[3].value
    force = sliders[4].value
    mu_s, mu_k = get_mu_values()

    max_static = mu_s * mass * gravity
    if force <= max_static:
        vx = 0.0
        running_motion = False
        won = False
        return

    net_force = force - mu_k * mass * gravity
    vx = max(0.0, (net_force / mass) * 0.35)
    running_motion = True
    won = False


def check_win():
    global won, _xp_fired
    won = goal_rect_for_level().colliderect(get_box_rect())
    if won and not _xp_fired:
        _xp_fired = True
        trigger_xp_overlay()


def update_physics(dt):
    global box_flat_x, vx, running_motion, won

    mu_s, mu_k = get_mu_values()
    gravity = sliders[3].value

    if running_motion:
        friction_accel = mu_k * gravity

        if vx > 0:
            vx -= friction_accel * dt
            if vx < 0:
                vx = 0.0

        box_flat_x += vx * 120 * dt
        box_flat_x = clamp(box_flat_x, 20, WIDTH - box_w - 20)

        if abs(vx) < 0.02:
            vx = 0.0
            running_motion = False
            check_win()


def goal_rect_for_level():
    return get_level().goal_rect


def draw_level_scene():
    level = get_level()
    goal_rect = goal_rect_for_level()

    if level.friction_locked:
        pygame.draw.rect(screen, ICE_BLUE, (0, ground_y, WIDTH, HEIGHT - ground_y))
    else:
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEIGHT))

    pygame.draw.rect(screen, DARK_GRAY, (0, ground_y, WIDTH, 8))

    pygame.draw.rect(screen, (200, 255, 200), goal_rect)
    pygame.draw.rect(screen, GREEN, goal_rect, 4)


def draw_force_popup(surface, key, anchor):
    info = FORCE_INFO[key]

    title_surf = TITLE_FONT.render(info["title"], True, BLACK)
    formula_surf = FONT.render(info["formula"], True, BLACK)
    desc_surf = SMALL_FONT.render(info["desc"], True, DARK_GRAY)

    pad = 12
    gap = 6
    content_w = max(title_surf.get_width(), formula_surf.get_width(), desc_surf.get_width())
    content_h = title_surf.get_height() + formula_surf.get_height() + desc_surf.get_height() + gap * 2
    box_w = content_w + pad * 2
    box_h = content_h + pad * 2 + 6

    x = clamp(anchor[0] + 16, 10, WIDTH - box_w - 10)
    y = clamp(anchor[1] - box_h - 16, 10, HEIGHT - box_h - 10)

    box = pygame.Rect(x, y, box_w, box_h)
    pygame.draw.rect(surface, POPUP_BG, box, border_radius=10)
    pygame.draw.rect(surface, BLACK, box, 2, border_radius=10)

    close_surf = SMALL_FONT.render("x", True, BLACK)
    surface.blit(close_surf, (box.right - 16, box.y + 6))

    surface.blit(title_surf, (box.x + pad, box.y + pad))
    surface.blit(formula_surf, (box.x + pad, box.y + pad + title_surf.get_height() + gap))
    surface.blit(desc_surf, (box.x + pad, box.y + pad + title_surf.get_height() + gap + formula_surf.get_height() + 4))


def draw_help_popup(surface):
    title = TITLE_FONT.render("How to Play", True, BLACK)
    pad = 14
    spacing = 8

    line_surfs = [SMALL_FONT.render(text, True, BLACK) for text in HELP_TEXT]
    content_w = max([title.get_width()] + [s.get_width() for s in line_surfs])
    content_h = title.get_height() + 10 + sum(s.get_height() for s in line_surfs) + spacing * (len(line_surfs) - 1)

    box_w = content_w + pad * 2
    box_h = content_h + pad * 2 + 8

    x = WIDTH - box_w - 20
    y = 70
    box = pygame.Rect(x, y, box_w, box_h)

    pygame.draw.rect(surface, POPUP_BG, box, border_radius=10)
    pygame.draw.rect(surface, BLACK, box, 2, border_radius=10)

    surface.blit(title, (box.x + pad, box.y + pad))

    cur_y = box.y + pad + title.get_height() + 10
    for s in line_surfs:
        surface.blit(s, (box.x + pad, cur_y))
        cur_y += s.get_height() + spacing

    close_surf = SMALL_FONT.render("x", True, BLACK)
    surface.blit(close_surf, (box.right - 16, box.y + 6))


def draw_help_button(surface):
    pygame.draw.rect(surface, WHITE, help_button.rect, border_radius=10)
    pygame.draw.rect(surface, BLACK, help_button.rect, 2, border_radius=10)
    txt = FONT.render("?", True, BLACK)
    surface.blit(
        txt,
        (help_button.rect.centerx - txt.get_width() // 2,
         help_button.rect.centery - txt.get_height() // 2 - 1),
    )


def get_force_layout(box_rect):
    mass = sliders[0].value
    gravity = sliders[3].value
    applied = sliders[4].value
    mu_s, mu_k = get_mu_values()

    weight = mass * gravity
    normal = weight

    if running_motion:
        friction = mu_k * normal
    else:
        friction = min(applied, mu_s * normal)

    scale = 0.22
    max_len = 90

    centerx = box_rect.centerx
    centery = box_rect.centery
    top = box_rect.top
    bottom = box_rect.bottom
    left = box_rect.left
    right = box_rect.right

    applied_len = clamp(applied * scale, 0, max_len)
    friction_len = clamp(friction * scale, 0, max_len)
    vertical_len = clamp(weight * scale, 20, max_len)

    layout = {
        "F": {
            "visible": applied_len >= 3,
            "start": (centerx, centery),
            "end": (right + applied_len, centery),
            "color": RED,
            "label_pos": (right + 55, centery - 18),
            "label": "F",
        },
        "f": {
            "visible": friction_len >= 3,
            "start": (centerx, centery),
            "end": (left - friction_len, centery),
            "color": PURPLE,
            "label_pos": (left - 20, centery - 18),
            "label": "f",
        },
        "N": {
            "visible": True,
            "start": (centerx, top - 6),
            "end": (centerx, top - 6 - vertical_len),
            "color": GREEN,
            "label_pos": (centerx + 20, top - 18 - vertical_len // 2),
            "label": "N",
        },
        "W": {
            "visible": True,
            "start": (centerx, bottom + 6),
            "end": (centerx, bottom + 6 + vertical_len),
            "color": DARK_GRAY,
            "label_pos": (centerx + 20, bottom + 18 + vertical_len // 2),
            "label": "W",
        },
    }
    return layout


def get_force_hitboxes(box_rect):
    layout = get_force_layout(box_rect)
    hits = {}
    for key, item in layout.items():
        if not item["visible"]:
            continue
        txt = SMALL_FONT.render(item["label"], True, item["color"])
        rect = txt.get_rect(center=item["label_pos"]).inflate(12, 10)
        hits[key] = rect
    return hits


def draw_force_vectors(box_rect):
    layout = get_force_layout(box_rect)

    for key, item in layout.items():
        if not item["visible"]:
            continue
        draw_arrow(
            screen,
            item["start"],
            item["end"],
            item["color"],
            label=item["label"],
            label_pos=item["label_pos"],
        )


def draw_game():
    screen.fill(WHITE)
    draw_level_scene()

    box_rect = get_box_rect()
    draw_force_vectors(box_rect)

    pygame.draw.rect(screen, BLUE, box_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=8)

    for s in sliders:
        s.draw(screen)

    launch_button.draw(screen)
    reset_button.draw(screen)
    menu_button.draw(screen)
    draw_help_button(screen)

    level = get_level()
    level_title = TITLE_FONT.render(level.name, True, BLACK)
    level_desc = SMALL_FONT.render(level.description, True, DARK_GRAY)
    screen.blit(level_title, (420, 18))
    screen.blit(level_desc, (420, 46))

    if active_force_key is not None:
        draw_force_popup(screen, active_force_key, popup_anchor)

    if show_help:
        draw_help_popup(screen)

    if won:
        txt = FONT.render("WIN", True, GREEN)
        screen.blit(txt, (goal_rect_for_level().centerx - txt.get_width() // 2, goal_rect_for_level().y - 28))

    pygame.display.flip()


def draw_menu():
    screen.fill(WHITE)

    title = BIG_FONT.render("Friction Simulator", True, BLACK)
    subtitle = FONT.render("Pick a level to play", True, DARK_GRAY)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 170))

    info_lines = [
        "Level 1: flat ground, all sliders",
        "Level 2: ice, friction sliders are locked low",
    ]
    y = 520
    for line in info_lines:
        surf = SMALL_FONT.render(line, True, BLACK)
        screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
        y += 26

    for btn in level_buttons:
        btn.draw(screen)

    pygame.display.flip()


async def main():
    global active_force_key, popup_anchor, show_help

    while True:
        dt = clock.tick(60) / 1000.0

        if game_state == "menu":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                if level_buttons[0].clicked(event):
                    set_level(1)
                elif level_buttons[1].clicked(event):
                    set_level(2)

            draw_menu()
            await asyncio.sleep(0)
            continue

        box_rect = get_box_rect()
        force_hits = get_force_hitboxes(box_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            for s in sliders:
                s.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if help_button.clicked(event):
                    show_help = not show_help
                    active_force_key = None
                elif menu_button.clicked(event):
                    go_to_menu()
                else:
                    clicked_force = False

                    for key, rect in force_hits.items():
                        if rect.collidepoint(event.pos):
                            active_force_key = key
                            popup_anchor = event.pos
                            clicked_force = True
                            show_help = False
                            break

                    if not clicked_force:
                        active_force_key = None
                        show_help = False

                if launch_button.clicked(event):
                    launch_box()
                    active_force_key = None
                    show_help = False

                if reset_button.clicked(event):
                    reset_game()

        update_physics(dt)
        draw_game()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())