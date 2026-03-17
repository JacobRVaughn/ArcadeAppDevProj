import asyncio
import pygame
import random

# ── Constants ──────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
FPS           = 60
GRAVITY       = 2.5
WORD_SPEED    = 2
SPAWN_RATE    = 90   # frames between spawns

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GREEN  = (79,  255, 140)
RED    = (255, 80,  80)
BLUE   = (79,  93,  255)
GRAY   = (40,  40,  60)
YELLOW = (255, 220, 50)

# ── Question Bank ───────────────────────────────────────────
# Format: { "prompt": "...", "correct": "word", "wrong": ["w1","w2","w3"] }
QUESTIONS = [
    {"prompt": "A word that describes a noun",         "correct": "adjective",  "wrong": ["verb", "pronoun", "adverb"]},
    {"prompt": "Opposite of 'ancient'",                "correct": "modern",     "wrong": ["old", "historic", "antique"]},
    {"prompt": "A word meaning very happy",            "correct": "elated",     "wrong": ["sad", "angry", "tired"]},
    {"prompt": "Synonym for 'brave'",                  "correct": "courageous", "wrong": ["fearful", "timid", "weak"]},
    {"prompt": "A word that replaces a noun",          "correct": "pronoun",    "wrong": ["verb", "adjective", "noun"]},
    {"prompt": "Opposite of 'expand'",                 "correct": "shrink",     "wrong": ["grow", "stretch", "widen"]},
    {"prompt": "A word meaning to look quickly",       "correct": "glance",     "wrong": ["stare", "gaze", "peer"]},
    {"prompt": "Synonym for 'angry'",                  "correct": "furious",    "wrong": ["happy", "calm", "joyful"]},
    {"prompt": "A word that shows action",             "correct": "verb",       "wrong": ["noun", "adjective", "article"]},
    {"prompt": "Opposite of 'complex'",                "correct": "simple",     "wrong": ["hard", "difficult", "involved"]},
]

# ── Falling Word class ──────────────────────────────────────
class FallingWord:
    def __init__(self, word, x, is_correct, font):
        self.word       = word
        self.x          = x
        self.y          = -30
        self.is_correct = is_correct
        self.font       = font
        self.speed      = WORD_SPEED + random.uniform(0, 1.2)
        self.caught     = False

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        color = GREEN if self.is_correct else RED
        text  = self.font.render(self.word, True, color)
        rect  = text.get_rect(center=(self.x, int(self.y)))
        pygame.draw.rect(surface, GRAY, rect.inflate(16, 10), border_radius=6)
        surface.blit(text, rect)
        return rect

# ── Bucket / Player ─────────────────────────────────────────
class Bucket:
    W, H = 100, 18

    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50

    def update(self, keys):
        if keys[pygame.K_LEFT]  and self.x - self.W // 2 > 0:
            self.x -= 6
        if keys[pygame.K_RIGHT] and self.x + self.W // 2 < WIDTH:
            self.x += 6

    def draw(self, surface):
        rect = pygame.Rect(self.x - self.W // 2, self.y, self.W, self.H)
        pygame.draw.rect(surface, BLUE, rect, border_radius=6)

    def rect(self):
        return pygame.Rect(self.x - self.W // 2, self.y, self.W, self.H)

# ── Main game loop ───────────────────────────────────────────
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Word Blitz — EduQuest")
    clock  = pygame.font.SysFont("Arial", 20)
    font   = pygame.font.SysFont("Arial", 20)
    big    = pygame.font.SysFont("Arial", 32, bold=True)
    small  = pygame.font.SysFont("Arial", 15)
    clk    = pygame.time.Clock()

    bucket        = Bucket()
    falling_words = []
    score         = 0
    lives         = 3
    frame         = 0
    q_index       = 0
    random.shuffle(QUESTIONS)
    current_q     = QUESTIONS[q_index % len(QUESTIONS)]
    flash_msg     = ""
    flash_timer   = 0

    running = True
    while running:
        clk.tick(FPS)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        bucket.update(keys)

        # Spawn words
        if frame % SPAWN_RATE == 0:
            pool    = [current_q["correct"]] + random.sample(current_q["wrong"], min(2, len(current_q["wrong"])))
            random.shuffle(pool)
            x_slots = [160, 320, 480, 640]
            random.shuffle(x_slots)
            for i, word in enumerate(pool):
                falling_words.append(
                    FallingWord(word, x_slots[i], word == current_q["correct"], font)
                )

        # Update + collision
        bucket_rect = bucket.rect()
        for w in falling_words[:]:
            w.update()
            word_rect = pygame.Rect(w.x - 50, int(w.y) - 15, 100, 30)
            if word_rect.colliderect(bucket_rect) and not w.caught:
                w.caught = True
                if w.is_correct:
                    score      += 100
                    flash_msg   = "Correct!"
                    flash_timer = 60
                    q_index    += 1
                    current_q   = QUESTIONS[q_index % len(QUESTIONS)]
                    falling_words = [x for x in falling_words if x.caught]
                else:
                    lives      -= 1
                    flash_msg   = "Wrong!"
                    flash_timer = 60
            if w.y > HEIGHT + 40:
                falling_words.remove(w) if w in falling_words else None

        if lives <= 0:
            running = False

        if flash_timer > 0:
            flash_timer -= 1

        # ── Draw ────────────────────────────────────────────
        screen.fill((15, 15, 30))

        # Prompt box
        prompt_surf = big.render(f"Catch: {current_q['prompt']}", True, YELLOW)
        screen.blit(prompt_surf, prompt_surf.get_rect(centerx=WIDTH // 2, y=18))

        for w in falling_words:
            if not w.caught:
                w.draw(screen)

        bucket.draw(screen)

        # HUD
        score_surf = font.render(f"Score: {score}", True, WHITE)
        lives_surf = font.render(f"Lives: {lives}", True, RED) 
        screen.blit(score_surf, (12, 12))
        screen.blit(lives_surf, (12, 38))

        if flash_timer > 0:
            col   = GREEN if "Correct" in flash_msg else RED
            flash = big.render(flash_msg, True, col)  
            screen.blit(flash, flash.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2))


        ctrl = small.render("← → Arrow keys to move", True, GRAY)
        screen.blit(ctrl, ctrl.get_rect(centerx=WIDTH // 2, y=HEIGHT - 22))

        pygame.display.flip()
        await asyncio.sleep(0)

    # Game over screen
    screen.fill((15, 15, 30))
    go   = big.render("GAME OVER", True, RED)
    sc   = big.render(f"Final Score: {score}", True, YELLOW)
    rest = font.render("Refresh to play again", True, WHITE)
    screen.blit(go,   go.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 - 50))
    screen.blit(sc,   sc.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2))
    screen.blit(rest, rest.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2 + 50))
    pygame.display.flip()
    await asyncio.sleep(5)
    pygame.quit()

asyncio.run(main())