import asyncio
import random
import sys
import pygame
import csv
import os

pygame.init()
pygame.mixer.init()

# =========================
# Window setup
# =========================
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Capital Escape")
clock = pygame.time.Clock()

# =========================
# Colors
# =========================
BG = (15, 30, 70)
ROAD = (40, 40, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (60, 200, 120)
RED = (220, 70, 70)
YELLOW = (240, 210, 80)
LIGHT_BLUE = (140, 190, 255)
DARK_BOX = (30, 30, 30)
GRAY = (180, 180, 180)

# =========================
# Fonts
# =========================
title_font = pygame.font.SysFont("Sans Serif", 40)
question_font = pygame.font.SysFont("Sans Serif", 32)
choice_font = pygame.font.SysFont("Sans Serif", 26)
hud_font = pygame.font.SysFont("Sans Serif", 24)
big_font = pygame.font.SysFont("Sans Serif", 56)

# =========================
# Data
# =========================
capital_data = []

try:
    # Get directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "capital_data.csv")

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            capital_data.append((row["Capital"], row["Country"]))
except Exception as e:
    print("Error loading CSV:", e)
    sys.exit()


# =========================
# Assets
# =========================
base_dir = os.path.dirname(os.path.abspath(__file__))
user_img_path = os.path.join(base_dir, "user.png")

try:
    user_image = pygame.image.load(user_img_path).convert_alpha()
    # Scale to a reasonable size for the player
    user_image = pygame.transform.smoothscale(user_image, (150, 150))
except Exception as e:
    print("Error loading user.png:", e)
    user_image = None

# Load mob image
mob_img_path = os.path.join(base_dir, "mob.png")

try:
    mob_image = pygame.image.load(mob_img_path).convert_alpha()
    mob_image = pygame.transform.smoothscale(mob_image, (320, 180))
except Exception as e:
    print("Error loading mob.png:", e)
    mob_image = None

# Load running sounds
user_run_snd_path = os.path.join(base_dir, "running_user.ogg")
mob_run_snd_path = os.path.join(base_dir, "running_mob.ogg")

try:
    user_run_sound = pygame.mixer.Sound(user_run_snd_path)
except Exception as e:
    print("Error loading running_user.ogg:", e)
    user_run_sound = None

try:
    mob_run_sound = pygame.mixer.Sound(mob_run_snd_path)
except Exception as e:
    print("Error loading running_mob.ogg:", e)
    mob_run_sound = None

all_countries = [country for _, country in capital_data]

def get_active_capital_data():
    difficulty = state["difficulty"]
    if difficulty is None:
        return []

    settings = DIFFICULTY_SETTINGS[difficulty]
    count = settings["count"]
    if count is None:
        return capital_data
    return capital_data[:count]

DIFFICULTY_SETTINGS = {
    "easy": {"time_limit": 10.0, "count": 20},
    "medium": {"time_limit": 7.0, "count": 50},
    "hard": {"time_limit": 5.0, "count": None},
}

# =========================
# Game state
# =========================
runner_x = WIDTH // 2
mob_x = WIDTH // 2

RUNNER_START = (WIDTH // 2, 450)
MOB_START = (WIDTH // 2, 600)
RUNNER_SPEED = 200
MOB_SPEED = 200
CAUGHT_DISTANCE = 38
RUNNER_LANE_TARGETS = [
    (250, 325),
    (500, 325),
    (750, 325),
]

# Mob stops at a fixed point on the same road, closer to the screen
MOB_LANE_TARGETS = [
    (250, 445),
    (500, 445),
    (750, 445),
]
# Middle road is intentionally slower so the animation/sound lasts a bit longer.
LANE_SPEED_MULTIPLIERS = [1.0, 0.72, 1.0]

state = {
    "phase": "difficulty",   # difficulty / play / animating / game_over
    "difficulty": None,
    "score": 0,
    "capital": "",
    "correct_country": "",
    "choices": [],
    "time_left": 0,
    "question_number": 0,
    "selected_choice": None,
    "answer_correct": False,
    "animation_stage": None,   # None / runner_to_lane / mob_follow / mob_catch
    "runner_pos": [RUNNER_START[0], RUNNER_START[1]],
    "mob_pos": [MOB_START[0], MOB_START[1]],
    "runner_target": None,
    "mob_target": None,
    "runner_anim_speed": RUNNER_SPEED,
    "mob_anim_speed": MOB_SPEED,
    "user_run_channel": None,
    "mob_run_channel": None,
    "mob_run_started_at": None,
    "xp_overlay_fired": False,
}

# =========================
# Choice buttons
# =========================
# Clickable road choice areas (top = far end, bottom = near end)
choice_rects = [
    pygame.Rect(200, 200, 180, 90),
    pygame.Rect(410, 200, 180, 90),
    pygame.Rect(620, 200, 180, 90),
]

difficulty_rects = {
    "easy": pygame.Rect(200, 250, 180, 90),
    "medium": pygame.Rect(400, 250, 180, 90),
    "hard": pygame.Rect(600, 250, 180, 90),
}

# =========================
# Character positions
# =========================

def trigger_xp_overlay(won: bool):
    """Fire the JS game-over XP overlay exactly once via pygbag's window bridge."""
    if state.get("xp_overlay_fired"):
        return
    state["xp_overlay_fired"] = True

    xp_earned = 300 if won else 100

    try:
        from platform import window  # pygbag injects this in the browser
        js_code = f"""
(function() {{
  var score   = {state['score']};
  var xp      = {xp_earned};
  var gameId  = "capital-escape";
  // Use top-level window so the overlay renders above the iframe
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
        print(f"[XP overlay] not in browser, skipped. ({e})")

def generate_question():
    """Pick a random capital and create 3 choices based on difficulty."""
    active_data = get_active_capital_data()
    if not active_data:
        return

    capital, correct = random.choice(active_data)

    active_countries = [country for _, country in active_data]
    wrong_choices = [c for c in active_countries if c != correct]
    wrongs = random.sample(wrong_choices, 2)

    choices = [correct] + wrongs
    random.shuffle(choices)

    state["capital"] = capital
    state["correct_country"] = correct
    state["choices"] = choices
    state["time_left"] = DIFFICULTY_SETTINGS[state["difficulty"]]["time_limit"]
    state["question_number"] += 1


def stop_running_sounds():
    if state["user_run_channel"]:
        try:
            state["user_run_channel"].stop()
        except Exception:
            pass
    if state["mob_run_channel"]:
        try:
            state["mob_run_channel"].stop()
        except Exception:
            pass
    state["user_run_channel"] = None
    state["mob_run_channel"] = None
    state["mob_run_started_at"] = None


def start_user_running_sound():
    if user_run_sound is None:
        return
    if state["user_run_channel"] is None or not state["user_run_channel"].get_busy():
        try:
            state["user_run_channel"] = user_run_sound.play(-1)
        except Exception:
            state["user_run_channel"] = None


def stop_user_running_sound():
    if state["user_run_channel"]:
        try:
            state["user_run_channel"].stop()
        except Exception:
            pass
    state["user_run_channel"] = None


def start_mob_running_sound():
    if mob_run_sound is None:
        return
    if state["mob_run_channel"] is None or not state["mob_run_channel"].get_busy():
        try:
            # Start from a random point so the mob sound is less repetitive.
            clip_len = mob_run_sound.get_length()
            max_start = max(0.0, min(clip_len - 2.2, 6.0))
            random_start = random.uniform(0.0, max_start) if max_start > 0 else 0.0
            state["mob_run_channel"] = mob_run_sound.play(start=random_start)
            state["mob_run_started_at"] = pygame.time.get_ticks()
        except Exception:
            try:
                state["mob_run_channel"] = mob_run_sound.play()
                state["mob_run_started_at"] = pygame.time.get_ticks()
            except Exception:
                state["mob_run_channel"] = None
                state["mob_run_started_at"] = None


def stop_mob_running_sound():
    if state["mob_run_channel"]:
        try:
            state["mob_run_channel"].stop()
        except Exception:
            pass
    state["mob_run_channel"] = None
    state["mob_run_started_at"] = None


def reset_positions():
    state["runner_pos"] = [RUNNER_START[0], RUNNER_START[1]]
    state["mob_pos"] = [MOB_START[0], MOB_START[1]]
    state["selected_choice"] = None
    state["answer_correct"] = False
    state["animation_stage"] = None
    state["runner_target"] = None
    state["mob_target"] = None
    state["runner_anim_speed"] = RUNNER_SPEED
    state["mob_anim_speed"] = MOB_SPEED
    stop_running_sounds()


def move_toward(pos, target, speed, dt):
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    dist = (dx * dx + dy * dy) ** 0.5
    if dist == 0:
        return True

    step = speed * dt
    if dist <= step:
        pos[0], pos[1] = target[0], target[1]
        return True

    pos[0] += dx / dist * step
    pos[1] += dy / dist * step
    return False


def distance_between(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


def get_lane_target(index):
    return RUNNER_LANE_TARGETS[index]


def reset_game():
    state["phase"] = "difficulty"
    state["difficulty"] = None
    state["score"] = 0
    state["question_number"] = 0
    state["capital"] = ""
    state["correct_country"] = ""
    state["choices"] = []
    state["time_left"] = 0
    state["xp_overlay_fired"] = False
    reset_positions()
    

def start_difficulty(mode):
    state["difficulty"] = mode
    state["phase"] = "play"
    state["score"] = 0
    state["question_number"] = 0
    state["xp_overlay_fired"] = False
    reset_positions()
    generate_question()


def draw_runner(x, y):
    # Draw player using image (fallback to circle if missing)
    if user_image:
        rect = user_image.get_rect(center=(x, y))
        screen.blit(user_image, rect)
    else:
        pygame.draw.circle(screen, YELLOW, (x, y), 25)


def draw_mob(x, y):
    # Draw mob using image (fallback to rectangle if missing)
    if mob_image:
        rect = mob_image.get_rect(center=(x, y))
        screen.blit(mob_image, rect)
    else:
        pygame.draw.rect(screen, RED, (x - 40, y - 20, 80, 40))


def draw_background():
    screen.fill(BG)

    # Three perspective roads (left, middle, right)
    road_polys = [
        [(80, HEIGHT), (250, 250), (390, 250), (330, HEIGHT)],
        [(330, HEIGHT), (430, 250), (570, 250), (670, HEIGHT)],
        [(670, HEIGHT), (610, 250), (750, 250), (920, HEIGHT)],
    ]

    for poly in road_polys:
        pygame.draw.polygon(screen, ROAD, poly)
        pygame.draw.polygon(screen, GRAY, poly, 3)

    # Question panel
    pygame.draw.rect(screen, DARK_BOX, (120, 40, 760, 170), border_radius=20)
    pygame.draw.rect(screen, GRAY, (120, 40, 760, 170), 2, border_radius=20)

def get_choice_label_rect(index):
    rect = choice_rects[index]
    label_w, label_h = 170, 56
    label_x = rect.centerx - label_w // 2
    label_y = 280
    if index == 0:
        label_y = 295
    elif index == 2:
        label_y = 295
    return pygame.Rect(label_x, label_y, label_w, label_h)

def draw_hud():
    score_text = hud_font.render(f"Score: {state['score']}", True, WHITE)
    timer_text = hud_font.render(f"Time: {state['time_left']:.1f}", True, WHITE)
    q_text = hud_font.render(f"Question: {state['question_number']}", True, WHITE)

    screen.blit(score_text, (35, 12))
    screen.blit(timer_text, (430, 12))
    screen.blit(q_text, (810, 12))


def draw_question():
    title = title_font.render("Capital Escape", True, WHITE)
    screen.blit(title, (400, 55))

    prompt = question_font.render("Which country has this capital?", True, LIGHT_BLUE)
    screen.blit(prompt, (330, 110))

    capital_text = big_font.render(state["capital"], True, YELLOW)
    capital_rect = capital_text.get_rect(center=(WIDTH // 2, 170))
    screen.blit(capital_text, capital_rect)

def draw_difficulty_screen(mouse_pos):
    title = big_font.render("Choose Difficulty", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    screen.blit(title, title_rect)

    subtitle = question_font.render("Select a mode to begin", True, LIGHT_BLUE)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 170))
    screen.blit(subtitle, subtitle_rect)

    labels = {
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
    }

    for key, rect in difficulty_rects.items():
        hovered = rect.collidepoint(mouse_pos)

        if key == "easy":
            base_color = GREEN
        elif key == "medium":
            base_color = YELLOW
        else:
            base_color = RED

        # Slightly brighten on hover
        color = base_color if not hovered else tuple(min(255, c + 40) for c in base_color)
        pygame.draw.rect(screen, color, rect, border_radius=18)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=18)

        label = question_font.render(labels[key], True, WHITE)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)


def draw_choices(mouse_pos):
    for i in range(len(choice_rects)):
        label_rect = get_choice_label_rect(i)
        hovered = label_rect.collidepoint(mouse_pos)

        box_color = GREEN if hovered else (70, 130, 190)

        pygame.draw.rect(screen, box_color, label_rect, border_radius=14)
        pygame.draw.rect(screen, WHITE, label_rect, 2, border_radius=14)

        label = choice_font.render(state["choices"][i], True, WHITE)
        text_rect = label.get_rect(center=label_rect.center)
        screen.blit(label, text_rect)


def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    msg = big_font.render("Caught by the Mob!", True, RED)
    msg_rect = msg.get_rect(center=(WIDTH // 2, 220))
    screen.blit(msg, msg_rect)

    score_msg = question_font.render(f"Final Score: {state['score']}", True, WHITE)
    score_rect = score_msg.get_rect(center=(WIDTH // 2, 300))
    screen.blit(score_msg, score_rect)

    replay_msg = question_font.render("Press R to replay", True, YELLOW)
    replay_rect = replay_msg.get_rect(center=(WIDTH // 2, 360))
    screen.blit(replay_msg, replay_rect)


def handle_choice(choice_index):
    selected_country = state["choices"][choice_index]
    state["selected_choice"] = choice_index
    state["answer_correct"] = (selected_country == state["correct_country"])
    state["runner_target"] = RUNNER_LANE_TARGETS[choice_index]
    state["mob_target"] = None

    lane_mult = LANE_SPEED_MULTIPLIERS[choice_index]
    state["runner_anim_speed"] = RUNNER_SPEED * lane_mult
    state["mob_anim_speed"] = MOB_SPEED * lane_mult

    state["animation_stage"] = "runner_to_lane"
    state["phase"] = "animating"
    start_user_running_sound()


reset_game()
async def main():
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state["phase"] == "difficulty":
                    for mode, rect in difficulty_rects.items():
                        if rect.collidepoint(event.pos):
                            start_difficulty(mode)
                            break
                elif state["phase"] == "play":
                    for i in range(len(choice_rects)):
                        if get_choice_label_rect(i).collidepoint(event.pos):
                            handle_choice(i)
                            break

        if state["phase"] == "play":
            state["time_left"] -= dt
            if state["time_left"] <= 0:
                stop_running_sounds()
                state["phase"] = "game_over"
                trigger_xp_overlay(won=False)

        elif state["phase"] == "animating":
            stage = state["animation_stage"]

            # Step 1: runner moves to the selected road first
            if stage == "runner_to_lane":
                start_user_running_sound()
                runner_reached = move_toward(state["runner_pos"], state["runner_target"], state["runner_anim_speed"], dt)

                if runner_reached:
                    stop_user_running_sound()
                    choice_index = state["selected_choice"]
                    if state["answer_correct"]:
                        state["mob_target"] = MOB_LANE_TARGETS[choice_index]
                        state["animation_stage"] = "mob_follow"
                        start_mob_running_sound()
                    else:
                        state["mob_target"] = state["runner_target"]
                        state["animation_stage"] = "mob_catch"
                        start_mob_running_sound()

            # Step 2A: correct answer -> mob moves to its fixed target on the same road
            elif stage == "mob_follow":
                if state["mob_run_channel"] and state["mob_run_started_at"] is not None:
                    if pygame.time.get_ticks() - state["mob_run_started_at"] >= 2600:
                        stop_mob_running_sound()
                mob_reached = move_toward(state["mob_pos"], state["mob_target"], state["mob_anim_speed"], dt)

                if mob_reached:
                    stop_mob_running_sound()
                    state["score"] += 100
                    generate_question()
                    reset_positions()
                    state["phase"] = "play"

            # Step 2B: wrong answer -> mob moves to the runner and catches them
            elif stage == "mob_catch":
                if state["mob_run_channel"] and state["mob_run_started_at"] is not None:
                    if pygame.time.get_ticks() - state["mob_run_started_at"] >= 2000:
                        stop_mob_running_sound()
                move_toward(state["mob_pos"], state["mob_target"], state["mob_anim_speed"] * 1.35, dt)

                if distance_between(state["runner_pos"], state["mob_pos"]) <= CAUGHT_DISTANCE:
                    stop_mob_running_sound()
                    state["phase"] = "game_over"
                    trigger_xp_overlay(won=False)

        # Draw
        draw_background()
        draw_hud()

        # Draw player and mob using animated positions
        draw_runner(int(state["runner_pos"][0]), int(state["runner_pos"][1]))
        draw_mob(int(state["mob_pos"][0]), int(state["mob_pos"][1]))

        if state["phase"] == "difficulty":
            draw_difficulty_screen(mouse_pos)
        elif state["phase"] == "play":
            draw_question()
            draw_choices(mouse_pos)
        elif state["phase"] == "animating":
            draw_question()
            draw_choices((-999, -999))
        else:
            draw_question()
            draw_choices((-999, -999))
            draw_game_over()

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()
asyncio.run(main())