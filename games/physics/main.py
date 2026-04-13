import pygame
import sys
from dataclasses import dataclass

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 20)

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
DARK_GRAY = (90, 90, 90)
BLUE = (60, 130, 255)
GREEN = (80, 200, 120)
YELLOW = (240, 200, 60)

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

    def __post_init__(self):
        self.handle_radius = 10
        self.dragging = False

    def knob_x(self):
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.x + t * self.w)

    def handle_event(self, event):
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
        pygame.draw.line(surface, DARK_GRAY, (self.x, self.y), (self.x + self.w, self.y), 6)
        pygame.draw.circle(surface, BLUE if self.dragging else GRAY, (self.knob_x(), self.y), self.handle_radius)
        label = FONT.render(f"{self.label}: {self.value:.2f}", True, BLACK)
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
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                           self.rect.centery - txt.get_height() // 2))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

ground_y = 520
box_w, box_h = 70, 70
box_x = 120
box_y = ground_y - box_h
vx = 0.0
running_motion = False
won = False

goal_rect = pygame.Rect(760, ground_y - 80, 140, 80)

# TODO: Format units better
sliders = [
    Slider(60, 70, 320, "Mass (kg)", 1.0, 20.0, 5.0),
    Slider(60, 150, 320, "Static friction μs", 0.0, 1.5, 0.30),
    Slider(60, 230, 320, "Kinetic friction μk", 0.0, 1.5, 0.20),
    Slider(60, 310, 320, "Gravity (m/s²)", 1.0, 20.0, 9.81),
    Slider(60, 390, 320, "Launch force", 0.0, 300.0, 120.0),
]

launch_button = Button(pygame.Rect(60, ground_y + 40, 140, 45), "Launch", GREEN)
reset_button = Button(pygame.Rect(220, ground_y + 40, 140, 45), "Reset", YELLOW)

def reset_game():
    global box_x, vx, running_motion, won
    box_x = 120
    vx = 0.0
    running_motion = False
    won = False

def launch_box():
    global vx, running_motion, won

    mass = sliders[0].value
    mu_s = sliders[1].value
    mu_k = sliders[2].value
    gravity = sliders[3].value
    force = sliders[4].value

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

def update_physics(dt):
    global box_x, vx, running_motion, won

    mu_k = sliders[2].value
    gravity = sliders[3].value

    if running_motion:
        friction_accel = mu_k * gravity

        if vx > 0:
            vx -= friction_accel * dt
            if vx < 0:
                vx = 0.0

        box_x += vx * 120 * dt
        box_x = clamp(box_x, 20, WIDTH - box_w - 20)

        if abs(vx) < 0.02:
            vx = 0.0
            running_motion = False

    box_rect = pygame.Rect(int(box_x), box_y, box_w, box_h)
    won = (not running_motion) and goal_rect.contains(box_rect)

def draw():
    screen.fill(WHITE)

    pygame.draw.rect(screen, DARK_GRAY, (0, ground_y, WIDTH, 8))
    pygame.draw.rect(screen, (200, 255, 200), goal_rect)
    pygame.draw.rect(screen, GREEN, goal_rect, 4)

    box_rect = pygame.Rect(int(box_x), box_y, box_w, box_h)
    pygame.draw.rect(screen, BLUE, box_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=8)

    for s in sliders:
        s.draw(screen)

    launch_button.draw(screen)
    reset_button.draw(screen)

    if won:
        txt = FONT.render("WIN", True, GREEN)
        screen.blit(txt, (goal_rect.centerx - txt.get_width() // 2, goal_rect.y - 28))

    pygame.display.flip()

def main():
    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for s in sliders:
                s.handle_event(event)

            if launch_button.clicked(event):
                launch_box()

            if reset_button.clicked(event):
                reset_game()

        update_physics(dt)
        draw()

if __name__ == "__main__":
    main()