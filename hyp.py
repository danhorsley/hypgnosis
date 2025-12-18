import pygame
import random

pygame.init()

SIZE = 5
CELL = 100
WIDTH = SIZE * CELL + 300
HEIGHT = SIZE * CELL + 100
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hypgnosis – Tight Prototype")
FONT_BIG = pygame.font.Font(None, 80)
FONT_MED = pygame.font.Font(None, 60)
FONT_SMALL = pygame.font.Font(None, 40)
CLOCK = pygame.time.Clock()

# Tight config
TARGET_SUM = 4  # Starts low, new game randomizes 3-6
MAX_PIECES = 2

SWAP_PAIRS = {6: 9, 9: 6}

class Piece:
    def __init__(self, grid_x, grid_y):
        self.grid_pos = (grid_x, grid_y)
        self.value = self.calculate_value()

    def calculate_value(self):
        x, y = self.grid_pos
        if x == y:
            return 0
        return (x + 1) + (y + 1)

    def is_swapper(self):
        return self.grid_pos[0] == self.grid_pos[1]

    def reflected_value(self):
        v = self.value
        if self.is_swapper():
            return SWAP_PAIRS.get(v, v)
        return v

# Game state
mirror_col = 2  # FIXED
pieces = set()  # Only row 0, cols 0-1
particles = []

def reset_game():
    global TARGET_SUM, pieces
    pieces.clear()
    TARGET_SUM = random.randint(3, 6)

reset_game()

def grid_to_screen(gx, gy):
    return 50 + gx * CELL, 50 + gy * CELL

def screen_to_grid(sx, sy):
    return (sx - 50) // CELL, (sy - 50) // CELL

def get_reflected_sum():
    total = 0
    # Reflection positions: col3 sym col1, col4 sym col0
    for sym_x in [3, 4]:
        phys_x = 2 * mirror_col - sym_x
        if (phys_x, 0) in pieces:
            total += Piece(phys_x, 0).reflected_value()
    return total

running = True
won = False
while running:
    current_sum = get_reflected_sum()
    piece_count = len(pieces)
    won = current_sum == TARGET_SUM

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx, gy = screen_to_grid(mx, my)

            # New Game
            if mx < 200 and my < 60:
                reset_game()
                particles = []
                continue

            # Toggle ONLY row 0, left cols 0-1
            if gy == 0 and gx < mirror_col and gx in [0,1]:
                pos = (gx, 0)
                if pos in pieces:
                    pieces.remove(pos)
                elif piece_count < MAX_PIECES:
                    pieces.add(pos)

    # Particles
    if won and random.random() < 0.5:
        for _ in range(15):
            particles.append([WIDTH // 2 + random.randint(-100,100), HEIGHT // 2 + random.randint(-50,50), 
                              random.uniform(-3,3), random.uniform(-5,0), random.randint(30,60)])

    # Draw
    SCREEN.fill((10, 10, 20))

    # Grid
    for x in range(SIZE):
        for y in range(SIZE):
            rect = pygame.Rect(grid_to_screen(x, y), (CELL, CELL))
            base_color = (80, 80, 120) if x < mirror_col else (50, 50, 90)
            if y == 0:  # Highlight row 0
                pygame.draw.rect(SCREEN, (*base_color, 100), rect)
            pygame.draw.rect(SCREEN, base_color, rect, 3 if (x, y) in pieces else 1)

    # Fixed mirror seam
    seam_x = grid_to_screen(mirror_col, 0)[0] + CELL // 2
    pygame.draw.line(SCREEN, (150, 50, 255), (seam_x, 50), (seam_x, HEIGHT - 50), 10)

    # Physical pieces (row 0 only)
    for gx, gy in pieces:
        center = grid_to_screen(gx, gy)
        center = (center[0] + CELL//2, center[1] + CELL//2)
        p = Piece(gx, gy)
        color = (255, 150, 100) if p.is_swapper() else (100, 220, 255)
        pygame.draw.circle(SCREEN, color, center, 40)
        text = FONT_BIG.render(str(p.value), True, (0, 0, 0))
        SCREEN.blit(text, text.get_rect(center=center))

    # Reflections row 0
    for sym_x in [3, 4]:
        phys_x = 2 * mirror_col - sym_x
        if (phys_x, 0) in pieces:
            center = grid_to_screen(sym_x, 0)
            center = (center[0] + CELL//2, center[1] + CELL//2)
            p = Piece(phys_x, 0)
            ref_val = p.reflected_value()
            swapped = ref_val != p.value
            color = (255, 215, 0, 200) if swapped else (200, 200, 200)
            pygame.draw.circle(SCREEN, color, center, 40, 10)
            text = FONT_BIG.render(str(ref_val), True, (255, 255, 200))
            SCREEN.blit(text, text.get_rect(center=center))

    # New Game button
    new_rect = pygame.Rect(20, 20, 180, 50)
    pygame.draw.rect(SCREEN, (0, 160, 220), new_rect, border_radius=10)
    new_text = FONT_SMALL.render("NEW GAME", True, (255, 255, 255))
    SCREEN.blit(new_text, new_text.get_rect(center=new_rect.center))

    # UI
    ui_x = SIZE * CELL + 60
    FONT_MED.render("TARGET", True, (200, 200, 200))
    SCREEN.blit(FONT_MED.render("TARGET", True, (200, 200, 200)), (ui_x, 50))
    SCREEN.blit(FONT_BIG.render(str(TARGET_SUM), True, (255, 215, 0)), (ui_x, 110))

    SCREEN.blit(FONT_MED.render("CURRENT", True, (200, 200, 200)), (ui_x, 220))
    SCREEN.blit(FONT_BIG.render(str(current_sum), True, (0, 255, 0) if won else (255, 255, 255)), (ui_x, 280))

    count_text = FONT_SMALL.render(f"Pieces: {piece_count}/{MAX_PIECES}", True, (200, 200, 200))
    SCREEN.blit(count_text, (ui_x, 380))

    # Win
    if won:
        win_text = FONT_BIG.render("GOLD!", True, (255, 215, 0))
        SCREEN.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
        for p in particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
            if p[4] <= 0:
                particles.remove(p)
                continue
            pygame.draw.circle(SCREEN, (255, 215, 0), (int(p[0]), int(p[1])), 8)

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()