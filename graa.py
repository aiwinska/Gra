import pygame
import random
import math
import sys
import os

pygame.init()
WIDTH, HEIGHT = 900, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ontogeneza: Symulator Rozwoju Organizmu - Faza 3")
clock = pygame.time.Clock()

# --- CZCIONKI ---
font_sm = pygame.font.SysFont("Arial", 16)
font_md = pygame.font.SysFont("Arial", 20)
font_lg = pygame.font.SysFont("Arial", 26)
font_title = pygame.font.SysFont("Arial", 36, bold=True)

# --- KOLORY ---
COLOR_BG = (22, 26, 32)
COLOR_UI_BG = (32, 38, 46)
COLOR_BAR_BG = (14, 16, 20)
COLOR_TEXT = (210, 215, 225)
COLOR_TEXT_MUTED = (140, 145, 155)
COLOR_GOLD = (230, 185, 80)
COLOR_GREEN = (65, 165, 100)
COLOR_RED = (190, 65, 65)
COLOR_ORANGE = (210, 130, 50)
COLOR_PURPLE = (150, 100, 200)

def fallback_oxygen():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surf, (70, 160, 220), (15, 15), 10)
    return surf


def fallback_glucose():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (90, 175, 90), [(15, 2), (28, 10), (28, 22), (15, 29), (2, 22), (2, 10)])
    return surf


def fallback_amino():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (200, 100, 140), [(15, 3), (27, 26), (3, 26)])
    return surf


def fallback_toxin():
    surf = pygame.Surface((35, 35), pygame.SRCALPHA)
    points = [(17, 2), (21, 14), (32, 14), (23, 22), (27, 33), (17, 26), (7, 33), (11, 22), (2, 14), (13, 14)]
    pygame.draw.polygon(surf, COLOR_RED, points)
    return surf


def fallback_receptor():
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(surf, (140, 175, 200), (25, 25), 24, 2)
    pygame.draw.circle(surf, (100, 130, 160), (25, 25), 8)
    return surf


def fallback_stem():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf, (100, 200, 255), (20, 20), 16)
    pygame.draw.circle(surf, (255, 255, 255), (20, 20), 6)
    return surf


def fallback_cancer():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf, (130, 40, 40), (20, 20), 18)
    pygame.draw.circle(surf, (50, 10, 10), (20, 20), 8)
    return surf


def fallback_tissue(color):
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (4, 4, 32, 32), border_radius=6)
    pygame.draw.rect(surf, (200, 200, 200), (4, 4, 32, 32), 1, border_radius=6)
    return surf


def load_image(filename, size, fallback_func):
    if os.path.exists(filename):
        try:
            img = pygame.image.load(filename).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            return fallback_func()
    return fallback_func()

IMAGES = {
    "oxygen": load_image("tlen.png", (30, 30), fallback_oxygen),
    "glucose": load_image("glukoza.png", (30, 30), fallback_glucose),
    "amino": load_image("aminokwas.png", (30, 30), fallback_amino),
    "toxin": load_image("kortyzol.png", (35, 35), fallback_toxin),
    "receptor": load_image("komorka_gracz.png", (50, 50), fallback_receptor),
    "stem": load_image("komorka_macierzysta.png", (40, 40), fallback_stem),
    "cancer": load_image("zmutowana_komorka.png", (40, 40), fallback_cancer),
    "t_nerve": load_image("tkanka_nerwowa.png", (40, 40), lambda: fallback_tissue((180, 140, 50))),
    "t_muscle": load_image("tkanka_miesniowa.png", (40, 40), lambda: fallback_tissue((190, 70, 70))),
    "t_bone": load_image("tkanka_kostna.png", (40, 40), lambda: fallback_tissue((160, 170, 180)))
}

class Resource(pygame.sprite.Sprite):
    def __init__(self, res_type, speed_multiplier=1.0):
        super().__init__()
        self.type = res_type
        self.image = IMAGES[self.type]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WIDTH - 50)
        self.rect.y = 120
        self.speed = random.uniform(1.3, 2.6) * speed_multiplier
        self.x_start = self.rect.x
        self.time_offset = random.random() * 10

    def update(self):
        self.rect.y += self.speed
        self.rect.x = self.x_start + math.sin(pygame.time.get_ticks() / 600 + self.time_offset) * 12
        if self.rect.y > HEIGHT:
            self.kill()


class PlayerReceptor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IMAGES["receptor"]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        self.speed = 7

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 120: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed


class Game:
    def __init__(self):
        self.state = "INTRO"
        self.current_tab = 1

        # POLA STATYSTYK GLOBALNYCH
        self.atp = 200
        self.o2 = 50
        self.glucose = 20
        self.amino = 20
        self.stem_cells = 0

        # POLA ETAPU 2 (MITOZA)
        self.dna_instability = 0.0
        self.cancer_cells = 0
        self.btn_divide = pygame.Rect(520, 340, 320, 45)
        self.btn_apoptosis = pygame.Rect(520, 400, 320, 45)

        # POLA ETAPU 3 (LABORATORIUM)
        self.tissue_nerve = 0
        self.tissue_muscle = 0
        self.tissue_bone = 0
        self.tissue_epithelial = 0


        self.btn_craft_nerve = pygame.Rect(520, 225, 340, 40)
        self.btn_craft_muscle = pygame.Rect(520, 310, 340, 40)
        self.btn_craft_bone = pygame.Rect(520, 395, 340, 40)
        self.btn_craft_epithelial = pygame.Rect(520, 480, 340, 40)



        self.sprites = pygame.sprite.Group()
        self.resources = pygame.sprite.Group()
        self.player = PlayerReceptor()
        self.sprites.add(self.player)

        self.tabs_ui = [
            {"id": 1, "rect": pygame.Rect(10, 10, 210, 40), "label": "1. Krwiobieg"},
            {"id": 2, "rect": pygame.Rect(230, 10, 210, 40), "label": "2. Mitoza"},
            {"id": 3, "rect": pygame.Rect(450, 10, 210, 40), "label": "3. Laboratorium"},
            {"id": 4, "rect": pygame.Rect(670, 10, 210, 40), "label": "4. Atlas ciała"}
        ]
        # --- NOWE POLA ETAPU 4 (ATLAS CIAŁA) ---
        self.organ_brain = False
        self.organ_heart = False
        self.organ_skeleton = False
        self.organ_lungs = False
        self.organ_stomach = False


        self.btn_build_brain = pygame.Rect(520, 170, 340, 40)
        self.btn_build_heart = pygame.Rect(520, 225, 340, 40)
        self.btn_build_lungs = pygame.Rect(520, 280, 340, 40)
        self.btn_build_stomach = pygame.Rect(520, 335, 340, 40)


        self.organ_pos = {
            "brain": [535, 470],
            "heart": [615, 470],
            "lungs": [695, 470],
            "stomach": [775, 470]
        }

        # --- ROZBUDOWANY ETAP 3 & 4 (NOWE TKANKI, ORGANY I DRAG & DROP) ---
        self.tissue_epithelial = 0
        self.btn_craft_epithelial = pygame.Rect(520, 310, 340, 40)

        self.organ_brain = False
        self.organ_heart = False
        self.organ_lungs = False
        self.organ_stomach = False

        self.placed_brain = False
        self.placed_heart = False
        self.placed_lungs = False
        self.placed_stomach = False

        self.btn_craft_nerve = pygame.Rect(500, 200, 360, 45)
        self.btn_craft_muscle = pygame.Rect(500, 300, 360, 45)
        self.btn_craft_bone = pygame.Rect(500, 400, 360, 45)
        self.btn_craft_epithelial = pygame.Rect(500, 500, 360, 45)

        self.organ_pos = {
            "brain": [540, 440],
            "heart": [620, 440],
            "lungs": [700, 440],
            "stomach": [780, 440]
        }

        self.dragging_organ = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.target_brain = pygame.Rect(220, 200, 70, 50)
        self.target_lungs = pygame.Rect(200, 290, 110, 60)
        self.target_heart = pygame.Rect(235, 300, 40, 40)
        self.target_stomach = pygame.Rect(220, 380, 70, 50)

        self.level2_unlocked = False
        self.level3_unlocked = False
        self.level4_unlocked = False
    def metabolize(self):
        burned = 0
        while self.glucose >= 1 and self.o2 >= 6 and burned < 2:
            self.glucose -= 1
            self.o2 -= 6
            self.atp += 38
            burned += 1

        if self.cancer_cells > 0:
            self.atp -= self.cancer_cells * 4

        if self.atp <= 0:
            self.state = "GAME_OVER"

    def update_instability(self):
        if self.dna_instability > 0:
            self.dna_instability = max(0.0, self.dna_instability - 0.25)

    def trigger_mitosis(self):
        if self.atp >= 50:
            self.atp -= 50
            if random.uniform(0, 100) < self.dna_instability:
                self.cancer_cells += 1
            else:
                self.stem_cells += 1
            self.dna_instability = min(100.0, self.dna_instability + 30.0)

    def trigger_apoptosis(self):
        if self.cancer_cells > 0 and self.atp >= 100:
            self.atp -= 100
            self.cancer_cells -= 1

    def craft_tissue(self, tissue_type):
        # Definicja kosztów biologicznych
        if tissue_type == "nerve" and self.stem_cells >= 1 and self.amino >= 5 and self.atp >= 150:
            self.stem_cells -= 1
            self.amino -= 5
            self.atp -= 150
            self.tissue_nerve += 1
        elif tissue_type == "muscle" and self.stem_cells >= 1 and self.amino >= 8 and self.atp >= 80:
            self.stem_cells -= 1
            self.amino -= 8
            self.atp -= 80
            self.tissue_muscle += 1
        elif tissue_type == "bone" and self.stem_cells >= 1 and self.amino >= 4 and self.atp >= 50:
            self.stem_cells -= 1
            self.amino -= 4
            self.atp -= 50
            self.tissue_bone += 1
        elif tissue_type == "epithelial" and self.stem_cells >= 1 and self.amino >= 6 and self.atp >= 70:
            self.stem_cells -= 1
            self.amino -= 6
            self.atp -= 70
            self.tissue_epithelial += 1

    def build_organ(self, organ_type):
        if organ_type == "brain" and not self.organ_brain:
            if self.tissue_nerve >= 2 and self.tissue_epithelial >= 1 and self.atp >= 60:
                self.tissue_nerve -= 2
                self.tissue_epithelial -= 1
                self.atp -= 60
                self.organ_brain = True
        elif organ_type == "heart" and not self.organ_heart:
            if self.tissue_muscle >= 2 and self.tissue_nerve >= 1 and self.tissue_epithelial >= 1 and self.atp >= 70:
                self.tissue_muscle -= 2
                self.tissue_nerve -= 1
                self.tissue_epithelial -= 1
                self.atp -= 70
                self.organ_heart = True
        elif organ_type == "lungs" and not self.organ_lungs:
            if self.tissue_epithelial >= 2 and self.tissue_bone >= 1 and self.atp >= 60:
                self.tissue_epithelial -= 2
                self.tissue_bone -= 1
                self.atp -= 60
                self.organ_lungs = True
        elif organ_type == "stomach" and not self.organ_stomach:
            if self.tissue_epithelial >= 2 and self.tissue_muscle >= 1 and self.tissue_nerve >= 1 and self.atp >= 50:
                self.tissue_epithelial -= 2
                self.tissue_muscle -= 1
                self.tissue_nerve -= 1
                self.atp -= 50
                self.organ_stomach = True

    def is_stage2_unlocked(self):
        if self.atp >= 300 and self.amino >= 30: self.level2_unlocked = True
        return self.level2_unlocked

    def is_stage3_unlocked(self):
        if self.stem_cells >= 10: self.level3_unlocked = True
        return self.level3_unlocked

    def is_stage4_unlocked(self):
        if self.tissue_nerve >= 2 and self.tissue_muscle >= 2 and self.tissue_bone >= 2 and self.tissue_epithelial >= 2:
            self.level4_unlocked = True
        return self.level4_unlocked

    def draw_intro(self, surface):
        surface.fill((16, 18, 22))
        surface.blit(font_title.render("ONTOGENEZA: PROTOKÓŁ ROZWOJU", True, COLOR_TEXT), (50, 50))

        instructions = [
            "Cel główny: Wykształcenie struktur tkankowych i organów ludzkiego ciała.",
            "Aktualny status: Stadium początkowe (Zygota).",
            "",
            "--- ETAP 1: AKUMULACJA METABOLICZNA ---",
            "W celu zapoczątkowania podziału komórkowego konieczne jest zabezpieczenie energii.",
            "Sterowanie komórką odbywa się za pomocą klawiszy STRZAŁEK.",
            "Wychwytuj spadające cząsteczki organiczne:",
            "  * TLEN & GLUKOZA: Automatyczna synteza energii komórkowej (ATP) w stosunku 6:1.",
            "  * AMINOKWASY: Podstawowy budulec niezbędny do późniejszego różnicowania tkanek.",
            "  * KORTYZOL (Czerwone struktury): Czynnik stresogenny. Powoduje utratę 50 jednostek ATP.",
            "",
            "--- WARUNKI INICJACJI KOLEJNEJ FAZY ---",
            "Wymagane parametry krytyczne: minimum 300 jednostek ATP oraz 30 aminokwasów.",
            "Po osiągnięciu progu system odblokuje sekcję '2. Mitoza'.",
            "",
            "Naciśnij SPACJĘ, aby uruchomić pobieranie zasobów w krwiobiegu."
        ]
        for i, line in enumerate(instructions):
            color = COLOR_GOLD if "WARUNKI" in line or "PARAMETRY" in line.upper() else COLOR_TEXT
            if "SPACJĘ" in line: color = COLOR_GREEN
            surface.blit(font_md.render(line, True, color), (50, 140 + i * 28))

    def draw_ui(self, surface):
        pygame.draw.rect(surface, COLOR_UI_BG, (0, 0, WIDTH, 110))
        s2_unlocked = self.is_stage2_unlocked()
        s3_unlocked = self.is_stage3_unlocked()
        s4_unlocked = self.is_stage4_unlocked()

        for tab in self.tabs_ui:
            if tab["id"] == 1:
                color = COLOR_GREEN if self.current_tab == 1 else (60, 70, 80)
            elif tab["id"] == 2:
                color = COLOR_GREEN if self.current_tab == 2 else (50, 80, 60) if s2_unlocked else (45, 45, 50)
            elif tab["id"] == 3:
                color = COLOR_GREEN if self.current_tab == 3 else (50, 80, 60) if s3_unlocked else (45, 45, 50)
            elif tab["id"] == 4:
                color = COLOR_GREEN if self.current_tab == 4 else (50, 80, 60) if s4_unlocked else (45, 45, 50)

            pygame.draw.rect(surface, color, tab["rect"], border_radius=4)
            pygame.draw.rect(surface, (80, 90, 100), tab["rect"], 1, border_radius=4)

            if tab["id"] == 2 and not s2_unlocked:
                label = tab["label"] + " [Zablokowane]"
            elif tab["id"] == 3 and not s3_unlocked:
                label = tab["label"] + " [Zablokowane]"
            elif tab["id"] == 4 and not s4_unlocked:
                label = tab["label"] + " [Zablokowane]"
            else:
                label = tab["label"]

            text_color = (255, 255, 255) if self.current_tab == tab["id"] else COLOR_TEXT_MUTED
            text_surf = font_sm.render(label, True, text_color)
            surface.blit(text_surf, text_surf.get_rect(center=tab["rect"].center))

        res_bg = pygame.Rect(10, 60, WIDTH - 20, 40)
        pygame.draw.rect(surface, COLOR_BAR_BG, res_bg, border_radius=4)

        res_text = f"ATP: {self.atp}  |  Tlen: {self.o2}  |  Glukoza: {self.glucose}  |  Aminokwasy: {self.amino}  |  Komórki: {self.stem_cells}"
        surface.blit(font_md.render(res_text, True, COLOR_GOLD), (25, 70))

        # Paski informacyjne pod zakładkami
        if self.current_tab == 1 and not s2_unlocked:
            hint = font_sm.render(f"Cel fazy 1: 300 ATP i 30 aminokwasów, aby odblokować Mitozę.", True,
                                  (180, 130, 130))
            surface.blit(hint, (25, 115))
        elif self.current_tab == 2 and not s3_unlocked:
            hint = font_sm.render(
                f"Cel fazy 2: Wyhoduj bezpiecznie 10 komórek macierzystych (aktualnie: {self.stem_cells}/10).", True,
                COLOR_GOLD)
            surface.blit(hint, (25, 115))
        elif self.current_tab == 3 and not s4_unlocked:
            hint = font_sm.render(
                f"Cel fazy 3: Wytwórz min. po 2 sztuki każdej tkanki (Nerwowa: {self.tissue_nerve}/2, Mięśniowa: {self.tissue_muscle}/2, Kostna: {self.tissue_bone}/2)",
                True, COLOR_GOLD)
            surface.blit(hint, (25, 115))

        pygame.draw.line(surface, (70, 80, 90), (0, 110), (WIDTH, 110), 2)

game = Game()

SPAWN_TICK = pygame.USEREVENT + 1
METABOLISM_TICK = pygame.USEREVENT + 2

pygame.time.set_timer(SPAWN_TICK, 420)
pygame.time.set_timer(METABOLISM_TICK, 1500)