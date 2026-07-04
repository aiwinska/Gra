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

        # Przycisk tworzenia tkanek (wyrównane z logiką rysowania w zakładce 3)
        self.btn_craft_nerve = pygame.Rect(500, 200, 360, 45)
        self.btn_craft_muscle = pygame.Rect(500, 300, 360, 45)
        self.btn_craft_bone = pygame.Rect(500, 400, 360, 45)
        self.btn_craft_epithelial = pygame.Rect(500, 500, 360, 45)

        # SPRITE'Y (ETAP 1)
        self.sprites = pygame.sprite.Group()
        self.resources = pygame.sprite.Group()
        self.player = PlayerReceptor()
        self.sprites.add(self.player)

        # PASEK NAWIGACYJNY (MENU GÓRNE)
        self.tabs_ui = [
            {"id": 1, "rect": pygame.Rect(10, 10, 160, 40), "label": "1. Krwiobieg"},
            {"id": 2, "rect": pygame.Rect(180, 10, 160, 40), "label": "2. Mitoza"},
            {"id": 3, "rect": pygame.Rect(350, 10, 160, 40), "label": "3. Laboratorium"},
            {"id": 4, "rect": pygame.Rect(520, 10, 160, 40), "label": "4. Atlas ciała"}
        ]
        # Przycisk dla zakładki 5 (Baza danych) przesunięty, by nie nachodził na resztę
        self.btn_tab5 = pygame.Rect(690, 10, 160, 40)

        # BLOKADY ETAPÓW
        self.level2_unlocked = False
        self.level3_unlocked = False
        self.level4_unlocked = False

        # --- ETAP 4: STATUSY BUDOWY NARZĄDÓW ---
        self.organ_brain = False
        self.organ_heart = False
        self.organ_lungs = False
        self.organ_stomach = False

        # Statusy umieszczenia narządów na sylwetce (Drag & Drop)
        self.placed_brain = False
        self.placed_heart = False
        self.placed_lungs = False
        self.placed_stomach = False

        # Przyciski fabryki narządów w panelu bocznym
        self.btn_build_brain = pygame.Rect(520, 170, 340, 40)
        self.btn_build_heart = pygame.Rect(520, 225, 340, 40)
        self.btn_build_lungs = pygame.Rect(520, 280, 340, 40)
        self.btn_build_stomach = pygame.Rect(520, 335, 340, 40)

        # Początkowe pozycje narządów w magazynie inkubatora (dolny prawy róg)
        self.organ_pos = {
            "brain": [540, 470],
            "heart": [620, 470],
            "lungs": [700, 470],
            "stomach": [780, 470]
        }

        # Strefy dopasowania (anatomia sylwetki po lewej stronie ekranu)
        self.target_brain = pygame.Rect(220, 200, 70, 50)
        self.target_lungs = pygame.Rect(200, 290, 110, 60)
        self.target_heart = pygame.Rect(235, 300, 40, 40)
        self.target_stomach = pygame.Rect(220, 380, 70, 50)

        # Logika przeciągania myszką
        self.dragging_organ = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # GLOBALNY SŁOWNIK STATYSTYK I OSIĄGNIĘĆ
        self.stats = {
            "total_clicks": 0,
            "atp_generated": 0,
            "tissues_crafted": 0,
            "organs_built": 0,
            "failed_attempts": 0
        }

        # LEKSYKON (ETAP 5) - PRZYCISKI MENU BOCZNEGO
        self.lexicon_selected = "intro"
        self.btn_lex_intro = pygame.Rect(60, 210, 160, 30)
        self.btn_lex_nerve = pygame.Rect(60, 250, 160, 30)
        self.btn_lex_muscle = pygame.Rect(60, 290, 160, 30)
        self.btn_lex_epith = pygame.Rect(60, 330, 160, 30)
        self.btn_lex_bone = pygame.Rect(60, 370, 160, 30)
        self.btn_lex_brain = pygame.Rect(60, 410, 160, 30)
        self.btn_lex_heart = pygame.Rect(60, 450, 160, 30)
        self.btn_lex_lungs = pygame.Rect(60, 490, 160, 30)
        self.btn_lex_stomach = pygame.Rect(60, 530, 160, 30)
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

    def get_achievements_list(self):
        achievements = [
            ("Początek Bioinżynierii", "Stwórz swoją pierwszą tkankę", self.stats["tissues_crafted"] >= 1),
            ("Fabrykant Tkanek", "Wyhoduj łącznie 10 tkanek", self.stats["tissues_crafted"] >= 10),
            ("Pierwszy Oddech", "Zbuduj organ: Płuca", self.organ_lungs),
            ("Władca Myśli", "Zbuduj organ: Mózg", self.organ_brain),
            ("Pełny Organizm", "Zbuduj wszystkie 4 narządy",
             self.organ_brain and self.organ_heart and self.organ_lungs and self.organ_stomach),
            ("Potęga Mitochondrium", "Wygeneruj łącznie 500 ATP", self.stats["atp_generated"] >= 500),
            ("Pracowity Naukowiec", "Kliknij w grze ponad 200 razy", self.stats["total_clicks"] >= 200),
            ("Błędy Laboranta", "Spróbuj zbudować coś bez zasobów 5 razy", self.stats["failed_attempts"] >= 5)
        ]
        return achievements
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

while True:
    if game.state == "INTRO":
        game.draw_intro(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: game.state = "PLAY"
    elif game.state == "PLAY":
        screen.fill(COLOR_BG)
        if game.current_tab == 2: game.update_instability()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Przełączanie zakładek
                for tab in game.tabs_ui:
                    if tab["rect"].collidepoint(event.pos):
                        if tab["id"] == 2 and not game.is_stage2_unlocked(): continue
                        if tab["id"] == 3 and not game.is_stage3_unlocked(): continue
                        if tab["id"] == 4 and not game.is_stage4_unlocked(): continue
                        game.current_tab = tab["id"]

                # Kliknięcia w Etapie 2
                if game.current_tab == 2:
                    if game.btn_divide.collidepoint(event.pos): game.trigger_mitosis()
                    if game.btn_apoptosis.collidepoint(event.pos): game.trigger_apoptosis()

                # Kliknięcia w Etapie 3
                if game.current_tab == 3:
                    if game.btn_craft_nerve.collidepoint(event.pos):
                        game.craft_tissue("nerve")
                    if game.btn_craft_muscle.collidepoint(event.pos):
                        game.craft_tissue("muscle")
                    if game.btn_craft_bone.collidepoint(event.pos):
                        game.craft_tissue("bone")
                    if game.btn_craft_epithelial.collidepoint(event.pos):
                        game.craft_tissue("epithelial")

                # Kliknięcia i chwytanie w Etapie 4
                if game.current_tab == 4:
                    if game.btn_build_brain.collidepoint(event.pos): game.build_organ("brain")
                    if game.btn_build_heart.collidepoint(event.pos): game.build_organ("heart")
                    if game.btn_build_lungs.collidepoint(event.pos): game.build_organ("lungs")
                    if game.btn_build_stomach.collidepoint(event.pos): game.build_organ("stomach")

                    for organ, pos in game.organ_pos.items():
                        if getattr(game, f"organ_{organ}") and not getattr(game, f"placed_{organ}"):
                            rect = pygame.Rect(pos[0], pos[1], 70, 50)
                            if rect.collidepoint(event.pos):
                                game.dragging_organ = organ
                                game.drag_offset_x = event.pos[0] - pos[0]
                                game.drag_offset_y = event.pos[1] - pos[1]
                                break

            if event.type == pygame.MOUSEMOTION:
                game.stats["total_clicks"] += 1
                if game.btn_tab5.collidepoint(event.pos):
                    game.current_tab = 5
                if game.current_tab == 5:
                    if game.btn_lex_intro.collidepoint(event.pos):
                        game.lexicon_selected = "intro"
                    elif game.btn_lex_nerve.collidepoint(event.pos):
                        game.lexicon_selected = "nerve"
                    elif game.btn_lex_muscle.collidepoint(event.pos):
                        game.lexicon_selected = "muscle"
                    elif game.btn_lex_epith.collidepoint(event.pos):
                        game.lexicon_selected = "epith"
                    elif game.btn_lex_bone.collidepoint(event.pos):
                        game.lexicon_selected = "bone"
                    elif game.btn_lex_brain.collidepoint(event.pos):
                        game.lexicon_selected = "brain"
                    elif game.btn_lex_heart.collidepoint(event.pos):
                        game.lexicon_selected = "heart"
                    elif game.btn_lex_lungs.collidepoint(event.pos):
                        game.lexicon_selected = "lungs"
                    elif game.btn_lex_stomach.collidepoint(event.pos):
                        game.lexicon_selected = "stomach"
                if game.current_tab == 4 and game.dragging_organ:
                    game.organ_pos[game.dragging_organ][0] = event.pos[0] - game.drag_offset_x
                    game.organ_pos[game.dragging_organ][1] = event.pos[1] - game.drag_offset_y

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if game.current_tab == 4 and game.dragging_organ:
                    organ = game.dragging_organ
                    pos = game.organ_pos[organ]
                    target = getattr(game, f"target_{organ}")

                    if target.collidepoint(pos[0] + 35, pos[1] + 25):
                        game.organ_pos[organ] = [target.x, target.y]
                        setattr(game, f"placed_{organ}", True)
                    else:
                        reset_pos = {"brain": [540, 440], "heart": [620, 440], "lungs": [700, 440],
                                     "stomach": [780, 440]}
                        game.organ_pos[organ] = reset_pos[organ]

                    game.dragging_organ = None

                    if game.placed_brain and game.placed_heart and game.placed_lungs and game.placed_stomach:
                        game.state = "VICTORY"


            if event.type == SPAWN_TICK and game.current_tab == 1:
                choices = ["oxygen"] * 6 + ["glucose"] * 2 + ["amino"] * 2 + ["toxin"] * 1
                res = Resource(random.choice(choices))
                game.sprites.add(res)
                game.resources.add(res)

            if event.type == METABOLISM_TICK: game.metabolize()
        # ETAP 1: KRWIOBIEG
        if game.current_tab == 1:
            game.sprites.update()
            hits = pygame.sprite.spritecollide(game.player, game.resources, True)
            for hit in hits:
                if hit.type == "oxygen": game.o2 += 1
                if hit.type == "glucose": game.glucose += 1
                if hit.type == "amino": game.amino += 1
                if hit.type == "toxin": game.atp -= 50
            game.sprites.draw(screen)

        # ETAP 2: MITOZA
        elif game.current_tab == 2:
            pygame.draw.rect(screen, (28, 33, 40), (40, 150, 430, 540), border_radius=4)
            pygame.draw.rect(screen, (50, 60, 70), (40, 150, 430, 540), 1, border_radius=4)
            screen.blit(font_lg.render("PROTOKÓŁ MEDYCZNY: MITOZA", True, COLOR_GOLD), (60, 170))
            bio_text = [
                "1. Replikacja DNA: Przed podziałem enzymy", "muszą skopiować cały genom komórki.", "",
                "2. Punkty kontrolne: Komórka weryfikuje błędy.", "Zbyt szybkie tempo zmusza aparat replikacyjny",
                "do ignorowania uszkodzeń strukturalnych.", "",
                "3. Kancerogeneza: Niestabilne DNA tworzy", "komórki zmutowane. Nie budują tkanek, lecz",
                "drenują energię organizmu (-4 ATP / cykl).", "",
                "4. Apoptoza: Sterowana śmierć komórki", "wywołana przez mechanizmy obronne (Koszt: ATP)."
            ]
            for i, line in enumerate(bio_text):
                color = COLOR_GOLD if any(x in line for x in ["1.", "2.", "3.", "4."]) else COLOR_TEXT
                screen.blit(font_sm.render(line, True, color), (60, 220 + i * 22))

            screen.blit(font_title.render("ZARZĄDZANIE REPLIKACJĄ", True, COLOR_TEXT), (520, 160))
            screen.blit(font_md.render("Niestabilność aparatu enzymatycznego:", True, COLOR_TEXT), (520, 230))
            bar_rect = pygame.Rect(520, 260, 320, 25)
            pygame.draw.rect(screen, COLOR_BAR_BG, bar_rect, border_radius=4)
            fill_color = COLOR_GREEN if game.dna_instability < 40 else COLOR_ORANGE if game.dna_instability < 70 else COLOR_RED
            if game.dna_instability > 0:
                pygame.draw.rect(screen, fill_color, (520, 260, int((game.dna_instability / 100.0) * 320), 25),
                                 border_radius=4)
            pygame.draw.rect(screen, (100, 110, 120), bar_rect, 1, border_radius=4)
            screen.blit(font_sm.render(f"Ryzyko mutacji przy podziale: {int(game.dna_instability)}%", True, COLOR_TEXT),
                        (520, 295))

            pygame.draw.rect(screen, COLOR_GREEN if game.atp >= 50 else (50, 60, 55), game.btn_divide, border_radius=4)
            screen.blit(font_md.render("Inicjuj podział (Koszt: 50 ATP)", True, (255, 255, 255)), (540, 350))
            pygame.draw.rect(screen, COLOR_RED if game.cancer_cells > 0 and game.atp >= 100 else (55, 45, 45),
                             game.btn_apoptosis, border_radius=4)
            screen.blit(font_md.render("Uruchom apoptozę (Koszt: 100 ATP)", True, (255, 255, 255)), (540, 410))

            screen.blit(font_lg.render("Stan populacji komórkowej:", True, COLOR_TEXT), (520, 480))
            screen.blit(IMAGES["stem"], (520, 530))
            screen.blit(font_md.render(f"Komórki macierzyste: {game.stem_cells} / 10", True, COLOR_TEXT), (580, 540))
            screen.blit(IMAGES["cancer"], (520, 590))
            screen.blit(font_md.render(f"Komórki zmutowane: {game.cancer_cells}", True,
                                       COLOR_RED if game.cancer_cells > 0 else COLOR_TEXT), (580, 600))
            if game.cancer_cells > 0: screen.blit(
                font_sm.render(f"Obciążenie: -{game.cancer_cells * 4} ATP / cykl", True, COLOR_RED), (580, 625))


        # ETAP 3: LABORATORIUM

        elif game.current_tab == 3:
            # Lewy panel informacyjny
            pygame.draw.rect(screen, (28, 33, 40), (40, 150, 430, 540), border_radius=4)
            pygame.draw.rect(screen, (50, 60, 70), (40, 150, 430, 540), 1, border_radius=4)
            screen.blit(font_lg.render("PROTOKÓŁ RÓŻNICOWANIA", True, COLOR_GOLD), (60, 170))

            instrukcje = [
                "Witaj w Laboratorium Tkanek.", "",
                "Twoim zadaniem na tym etapie jest",
                "przekształcenie zebranych wcześniej",
                "komórek macierzystych i aminokwasów",
                "w wyspecjalizowane tkanki.", "",
                "ZASADY:",
                "- Każda tkanka ma swój własny koszt.",
                "- Potrzebujesz energii (ATP) do syntezy.", "",
                "CEL GŁÓWNY (WARUNEK AWANSU):",
                "Wyhoduj minimum po 2 sztuki z każdego",
                "rodzaju tkanki (Nerwowa, Mięśniowa,",
                "Kostna, Nabłonkowa).", "",
                "Gdy zdobędziesz wymaganą ilość,",
                "Etap 4 odblokuje się automatycznie!"
            ]
            for i, linia in enumerate(instrukcje):
                kolor = COLOR_GREEN if "CEL GŁÓWNY" in linia or "minimum" in linia else COLOR_TEXT
                screen.blit(font_sm.render(linia, True, kolor), (60, 220 + (i * 22)))

            # Prawy panel zarządzania produkcją
            screen.blit(font_title.render("PRODUKCJA TKANEK", True, COLOR_TEXT), (500, 135))

            # 1. Tkanka Nerwowa
            screen.blit(font_md.render(f" Tkanka Nerwowa | W magazynie: {game.tissue_nerve}/2", True, (100, 180, 255)),
                        (500, 175))
            c_nerve = game.stem_cells >= 1 and game.amino >= 5 and game.atp >= 50
            pygame.draw.rect(screen, (40, 70, 110) if c_nerve else (55, 60, 65), game.btn_craft_nerve, border_radius=6)
            pygame.draw.rect(screen, (100, 180, 255) if c_nerve else (90, 95, 100), game.btn_craft_nerve, 1,
                             border_radius=6)
            screen.blit(font_sm.render("Syntezuj: 1 Macierzysta, 5 Amino, 50 ATP", True, (255, 255, 255)), (515, 213))

            # 2. Tkanka Mięśniowa
            screen.blit(font_md.render(f" Tkanka Mięśniowa | W magazynie: {game.tissue_muscle}/2", True, COLOR_RED),
                        (500, 275))
            c_muscle = game.stem_cells >= 1 and game.amino >= 8 and game.atp >= 40
            pygame.draw.rect(screen, (110, 40, 40) if c_muscle else (55, 60, 65), game.btn_craft_muscle,
                             border_radius=6)
            pygame.draw.rect(screen, COLOR_RED if c_muscle else (90, 95, 100), game.btn_craft_muscle, 1,
                             border_radius=6)
            screen.blit(font_sm.render("Syntezuj: 1 Macierzysta, 8 Amino, 40 ATP", True, (255, 255, 255)), (515, 313))

            # 3. Tkanka Kostna
            screen.blit(font_md.render(f" Tkanka Kostna | W magazynie: {game.tissue_bone}/2", True, (220, 220, 220)),
                        (500, 375))
            c_bone = game.stem_cells >= 1 and game.amino >= 12 and game.atp >= 60
            pygame.draw.rect(screen, (70, 75, 80) if c_bone else (55, 60, 65), game.btn_craft_bone, border_radius=6)
            pygame.draw.rect(screen, (180, 185, 190) if c_bone else (90, 95, 100), game.btn_craft_bone, 1,
                             border_radius=6)
            screen.blit(font_sm.render("Syntezuj: 1 Macierzysta, 12 Amino, 60 ATP", True, (255, 255, 255)), (515, 413))

            # 4. Tkanka Nabłonkowa
            screen.blit(
                font_md.render(f" Tkanka Nabłonkowa | W magazynie: {game.tissue_epithelial}/2", True, COLOR_PURPLE),
                (500, 475))
            c_epi = game.stem_cells >= 1 and game.amino >= 6 and game.atp >= 70
            pygame.draw.rect(screen, (80, 40, 100) if c_epi else (55, 60, 65), game.btn_craft_epithelial,
                             border_radius=6)
            pygame.draw.rect(screen, COLOR_PURPLE if c_epi else (90, 95, 100), game.btn_craft_epithelial, 1,
                             border_radius=6)
            screen.blit(font_sm.render("Syntezuj: 1 Macierzysta, 6 Amino, 70 ATP", True, (255, 255, 255)), (515, 513))

            # ========================================================================
            # ETAP 4: ATLAS CIAŁA
            # ========================================================================
        elif game.current_tab == 4:
            # Lewy panel anatomii
            pygame.draw.rect(screen, (28, 33, 40), (40, 150, 430, 540), border_radius=4)
            pygame.draw.rect(screen, (50, 60, 70), (40, 150, 430, 540), 1, border_radius=4)
            screen.blit(font_lg.render("MAPOWANIE ANATOMICZNE OSOBNIKA", True, COLOR_GOLD), (60, 165))

            # Sylwetka człowieka w tle
            pygame.draw.rect(screen, (42, 48, 58), (200, 260, 110, 200), border_radius=15)
            pygame.draw.circle(screen, (42, 48, 58), (255, 225), 32)

            # KOLEJNOŚĆ WARSTW (Z-ORDER): Najpierw duże i głębokie narządy, małe na wierzch!
            z_order = [
                ("lungs", "Płuca", COLOR_PURPLE, game.target_lungs),
                ("stomach", "Żołądek", COLOR_ORANGE, game.target_stomach),
                ("heart", "Serce", COLOR_RED, game.target_heart),
                ("brain", "Mózg", (100, 180, 255), game.target_brain)
            ]

            for key, nazwa, kolor, target in z_order:
                if getattr(game, f"placed_{key}"):
                    # Narząd zajmuje CAŁY swój obszar, dostaje ramkę i wyśrodkowany tekst
                    pygame.draw.rect(screen, kolor, target, border_radius=8)
                    pygame.draw.rect(screen, (255, 255, 255), target, 1, border_radius=8)
                    t_surf = font_sm.render(nazwa, True, (255, 255, 255))
                    screen.blit(t_surf, (target.x + (target.width - t_surf.get_width()) // 2,
                                         target.y + (target.height - t_surf.get_height()) // 2))
                else:
                    # Cień pustego miejsca na narząd
                    pygame.draw.rect(screen, (24, 28, 35), target, border_radius=4)
                    pygame.draw.rect(screen, (60, 70, 85), target, 1)
                    screen.blit(font_sm.render(nazwa[0], True, COLOR_TEXT_MUTED), (target.x + 8, target.y + 6))

            # Prawy panel: Fabryka
            screen.blit(font_title.render("FABRYKA NARZĄDÓW", True, COLOR_TEXT), (520, 130))

            # 1. Mózg
            c_brain = not game.organ_brain and game.tissue_nerve >= 2 and game.tissue_epithelial >= 1 and game.atp >= 60
            pygame.draw.rect(screen,
                             (100, 180, 255) if c_brain else (50, 55, 65) if not game.organ_brain else COLOR_GREEN,
                             game.btn_build_brain, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255) if c_brain else (90, 95, 100), game.btn_build_brain, 1,
                             border_radius=6)
            lbl_b = "GOTOWE: Mózg" if game.organ_brain else "Mózg (2x Nerw, 1x Nabł, 60 ATP)"
            screen.blit(font_sm.render(lbl_b, True, (255, 255, 255)),
                        (game.btn_build_brain.x + 12, game.btn_build_brain.y + 10))

            # 2. Serce
            c_heart = not game.organ_heart and game.tissue_muscle >= 2 and game.tissue_nerve >= 1 and game.tissue_epithelial >= 1 and game.atp >= 70
            pygame.draw.rect(screen, COLOR_RED if c_heart else (65, 45, 45) if not game.organ_heart else COLOR_GREEN,
                             game.btn_build_heart, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255) if c_heart else (90, 95, 100), game.btn_build_heart, 1,
                             border_radius=6)
            lbl_h = "GOTOWE: Serce" if game.organ_heart else "Serce (2x Mięś, 1x Nerw, 1x Nabł, 70 ATP)"
            screen.blit(font_sm.render(lbl_h, True, (255, 255, 255)),
                        (game.btn_build_heart.x + 12, game.btn_build_heart.y + 10))

            # 3. Płuca
            c_lungs = not game.organ_lungs and game.tissue_epithelial >= 2 and game.tissue_bone >= 1 and game.atp >= 60
            pygame.draw.rect(screen, COLOR_PURPLE if c_lungs else (55, 45, 60) if not game.organ_lungs else COLOR_GREEN,
                             game.btn_build_lungs, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255) if c_lungs else (90, 95, 100), game.btn_build_lungs, 1,
                             border_radius=6)
            lbl_l = "GOTOWE: Płuca" if game.organ_lungs else "Płuca (2x Nabł, 1x Kost, 60 ATP)"
            screen.blit(font_sm.render(lbl_l, True, (255, 255, 255)),
                        (game.btn_build_lungs.x + 12, game.btn_build_lungs.y + 10))

            # 4. Żołądek
            c_stom = not game.organ_stomach and game.tissue_epithelial >= 2 and game.tissue_muscle >= 1 and game.tissue_nerve >= 1 and game.atp >= 50
            pygame.draw.rect(screen,
                             COLOR_ORANGE if c_stom else (60, 50, 45) if not game.organ_stomach else COLOR_GREEN,
                             game.btn_build_stomach, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255) if c_stom else (90, 95, 100), game.btn_build_stomach, 1,
                             border_radius=6)
            lbl_s = "GOTOWE: Żołądek" if game.organ_stomach else "Żołądek (2x Nabł, 1x Mięś, 1x Nerw, 50 ATP)"
            screen.blit(font_sm.render(lbl_s, True, (255, 255, 255)),
                        (game.btn_build_stomach.x + 12, game.btn_build_stomach.y + 10))

            # --- INKUBATOR TKANKOWY ---
            screen.blit(font_lg.render("INKUBATOR TKANKOWY", True, COLOR_GOLD), (520, 410))
            pygame.draw.rect(screen, (20, 24, 30), (520, 440, 340, 110), border_radius=8)
            pygame.draw.rect(screen, (50, 60, 75), (520, 440, 340, 110), 1, border_radius=8)

            # Rysowanie wyhodowanych narządów w magazynie (tylko tych, które nie są jeszcze na człowieku)
            organs_render_list = [
                ("brain", "Mózg", (100, 180, 255)),
                ("heart", "Serce", COLOR_RED),
                ("lungs", "Płuca", COLOR_PURPLE),
                ("stomach", "Żołądek", COLOR_ORANGE)
            ]
            for key, name, color in organs_render_list:
                if getattr(game, f"organ_{key}") and not getattr(game, f"placed_{key}"):
                    pos = game.organ_pos[key]
                    pygame.draw.rect(screen, color, (pos[0], pos[1], 70, 50), border_radius=5)
                    pygame.draw.rect(screen, (255, 255, 255), (pos[0], pos[1], 70, 50), 1, border_radius=5)
                    text_surface = font_sm.render(name, True, (255, 255, 255))
                    screen.blit(text_surface, (pos[0] + (70 - text_surface.get_width()) // 2, pos[1] + 16))

        # ========================================================================
        # ETAP 5: BAZA DANYCH, LEKSYKON MEDYCZNY I STATYSTYKI
        # ========================================================================
        elif game.current_tab == 5:
            # Tło główne zakładki
            pygame.draw.rect(screen, (22, 26, 32), (40, 150, 820, 540), border_radius=8)
            pygame.draw.rect(screen, (55, 65, 80), (40, 150, 820, 540), 2, border_radius=8)

            # Nagłówek panelu
            screen.blit(font_title.render("CENTRUM BADAWCZE: LEKSYKON I STATYSTYKI", True, COLOR_GOLD), (60, 165))

            # LEWY PANEL: NAWIGACJA LEKSYKONU
            pygame.draw.rect(screen, (28, 33, 40), (50, 200, 180, 475), border_radius=4)
            pygame.draw.rect(screen, (45, 55, 65), (50, 200, 180, 475), 1)

            lex_buttons = [
                ("intro", "Wprowadzenie", game.btn_lex_intro),
                ("nerve", "Tk. Nerwowa", game.btn_lex_nerve),
                ("muscle", "Tk. Mięśniowa", game.btn_lex_muscle),
                ("epith", "Tk. Nabłonkowa", game.btn_lex_epith),
                ("bone", "Tk. Łączna/Kostna", game.btn_lex_bone),
                ("brain", "Narząd: Mózg", game.btn_lex_brain),
                ("heart", "Narząd: Serce", game.btn_lex_heart),
                ("lungs", "Narząd: Płuca", game.btn_lex_lungs),
                ("stomach", "Narząd: Żołądek", game.btn_lex_stomach)
            ]

            for key, label, rect in lex_buttons:
                is_sel = game.lexicon_selected == key
                pygame.draw.rect(screen, (40, 60, 90) if is_sel else (34, 40, 49), rect, border_radius=4)
                pygame.draw.rect(screen, (100, 150, 255) if is_sel else (60, 70, 80), rect, 1)
                screen.blit(font_sm.render(label, True, (255, 255, 255)), (rect.x + 10, rect.y + 6))

            # ŚRODKOWY PANEL: TREŚĆ ARTYKUŁÓW
            pygame.draw.rect(screen, (24, 28, 35), (240, 200, 360, 475), border_radius=4)
            pygame.draw.rect(screen, (45, 55, 65), (240, 200, 360, 475), 1)

            tx, ty = 255, 215
            if game.lexicon_selected == "intro":
                screen.blit(font_lg.render("Atlas Histologiczno-Anatomiczny", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("Witaj w bazie wiedzy bioinżynieryjnej.", True, COLOR_TEXT), (tx, ty + 40))
                screen.blit(font_sm.render("Wybierz interesującą Cię tkankę lub organ", True, COLOR_TEXT),
                            (tx, ty + 60))
                screen.blit(font_sm.render("z menu po lewej stronie, aby zapoznać się", True, COLOR_TEXT),
                            (tx, ty + 80))
                screen.blit(font_sm.render("z jej strukturą biologiczną, funkcją", True, COLOR_TEXT), (tx, ty + 100))
                screen.blit(font_sm.render("w organizmie oraz wymaganiami syntezy.", True, COLOR_TEXT), (tx, ty + 120))
                screen.blit(font_sm.render("Projekt realizuje założenia dydaktyczne", True, COLOR_TEXT_MUTED),
                            (tx, ty + 160))
                screen.blit(font_sm.render("z zakresu biologii komórki i anatomii.", True, COLOR_TEXT_MUTED),
                            (tx, ty + 180))

            elif game.lexicon_selected == "nerve":
                screen.blit(font_lg.render("Tkanka Nerwowa (Nervous Tissue)", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Skład: Neurony oraz komórki glejowe.", True, COLOR_TEXT), (tx, ty + 40))
                screen.blit(font_sm.render("• Funkcja: Przewodzenie impulsów", True, COLOR_TEXT), (tx, ty + 65))
                screen.blit(font_sm.render("  elektrochemicznych, odbieranie bodźców.", True, COLOR_TEXT),
                            (tx, ty + 85))
                screen.blit(font_sm.render("• Cechy: Neurony nie dzielą się", True, COLOR_TEXT), (tx, ty + 110))
                screen.blit(font_sm.render("  w dorosłym organizmie (baza postmitotyczna).", True, COLOR_TEXT),
                            (tx, ty + 130))
                screen.blit(font_sm.render("• Glej: Odżywia i chroni neurony,", True, COLOR_TEXT), (tx, ty + 155))
                screen.blit(font_sm.render("  tworzy osłonki mielinowe (izolacja).", True, COLOR_TEXT), (tx, ty + 175))
                screen.blit(font_sm.render("• Zastosowanie: Kluczowa do budowy Mózgu", True, (100, 180, 255)),
                            (tx, ty + 210))

            elif game.lexicon_selected == "muscle":
                screen.blit(font_lg.render("Tkanka Mięśniowa (Muscle Tissue)", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Rodzaje: Poprzecznie prążkowana szkieletowa,", True, COLOR_TEXT),
                            (tx, ty + 40))
                screen.blit(font_sm.render("  sercowa oraz gładka (narządowa).", True, COLOR_TEXT), (tx, ty + 60))
                screen.blit(font_sm.render("• Cechy: Zdolność do kurczenia się", True, COLOR_TEXT), (tx, ty + 85))
                screen.blit(font_sm.render("  dzięki obecności aktyny i miozyny.", True, COLOR_TEXT), (tx, ty + 105))
                screen.blit(font_sm.render("• Szkieletowa: Zależna od woli, wielojądrowa.", True, COLOR_TEXT),
                            (tx, ty + 130))
                screen.blit(font_sm.render("• Sercowa: Wstawki, skurcz automatyczny.", True, COLOR_TEXT),
                            (tx, ty + 155))
                screen.blit(font_sm.render("• Gładka: Niezależna, wyściela żołądek.", True, COLOR_TEXT), (tx, ty + 180))

            elif game.lexicon_selected == "epith":
                screen.blit(font_lg.render("Tkanka Nabłonkowa (Epithelial)", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Charakterystyka: Zwarty układ komórek,", True, COLOR_TEXT), (tx, ty + 40))
                screen.blit(font_sm.render("  minimalna ilość substancji międzykomórkowej.", True, COLOR_TEXT),
                            (tx, ty + 60))
                screen.blit(font_sm.render("• Podział: Jednowarstwowe (płaski, sześcienny,", True, COLOR_TEXT),
                            (tx, ty + 85))
                screen.blit(font_sm.render("  walcowaty) oraz wielowarstwowe.", True, COLOR_TEXT), (tx, ty + 105))
                screen.blit(font_sm.render("• Funkcja ochronna: Skóra, wyściółka.", True, COLOR_TEXT), (tx, ty + 130))
                screen.blit(font_sm.render("• Funkcja wydzielnicza: Gruczoły trawienne.", True, COLOR_TEXT),
                            (tx, ty + 155))

            elif game.lexicon_selected == "bone":
                screen.blit(font_lg.render("Tkanka Łączna / Kostna", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Cechy: Dużo substancji międzykomórkowej", True, COLOR_TEXT),
                            (tx, ty + 40))
                screen.blit(font_sm.render("  (macierzy) oraz włókien kolagenowych.", True, COLOR_TEXT), (tx, ty + 60))
                screen.blit(font_sm.render("• Tkanka Kostna: Wysycona solami mineralnymi", True, COLOR_TEXT),
                            (tx, ty + 85))
                screen.blit(font_sm.render("  (wapń, fosfor) – daje twardość i sztywność.", True, COLOR_TEXT),
                            (tx, ty + 105))
                screen.blit(font_sm.render("• Tkanka Chrzęstna: Elastyczna, brak naczyń", True, COLOR_TEXT),
                            (tx, ty + 130))
                screen.blit(font_sm.render("  krwionośnych (odżywianie przez dyfuzję).", True, COLOR_TEXT),
                            (tx, ty + 155))

            elif game.lexicon_selected == "brain":
                screen.blit(font_lg.render("Mózgowie (Encephalon)", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Główny narząd ośrodkowego układu", True, COLOR_TEXT), (tx, ty + 40))
                screen.blit(font_sm.render("  nerwowego. Kontroluje większość procesów.", True, COLOR_TEXT),
                            (tx, ty + 60))
                screen.blit(font_sm.render("• Zużycie energii: Pochłania około 20%", True, COLOR_TEXT), (tx, ty + 85))
                screen.blit(font_sm.render("  całego tlenu i glukozy organizmu.", True, COLOR_TEXT), (tx, ty + 105))
                screen.blit(font_sm.render("• Budowa histologiczna: Istota szara", True, COLOR_TEXT), (tx, ty + 130))
                screen.blit(font_sm.render("  (ciała neuronów) oraz istota biała (aksony).", True, COLOR_TEXT),
                            (tx, ty + 155))

            elif game.lexicon_selected == "heart":
                screen.blit(font_lg.render("Serce (Cor / Heart)", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Centralny narząd układu krwionośnego.", True, COLOR_TEXT), (tx, ty + 40))
                screen.blit(font_sm.render("  Działa jako ciśnieniowa pompa ssąco-tłocząca.", True, COLOR_TEXT),
                            (tx, ty + 60))
                screen.blit(font_sm.render("• Myokardium: Gruba warstwa unikalnej", True, COLOR_TEXT), (tx, ty + 85))
                screen.blit(font_sm.render("  tkanki mięśniowej poprzecznie prążkowanej.", True, COLOR_TEXT),
                            (tx, ty + 105))
                screen.blit(font_sm.render("• Automatyzm: Własny system generowania", True, COLOR_TEXT), (tx, ty + 130))
                screen.blit(font_sm.render("  impulsów (węzeł zatokowo-przedsionkowy).", True, COLOR_TEXT),
                            (tx, ty + 155))

            elif game.lexicon_selected == "lungs":
                screen.blit(font_lg.render("Płuca (Pulmones)", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Główny narząd wymiany gazowej.", True, COLOR_TEXT), (tx, ty + 40))
                screen.blit(font_sm.render("  Dostarcza tlen, usuwa dwutlenek węgla.", True, COLOR_TEXT), (tx, ty + 60))
                screen.blit(font_sm.render("• Dyfuzja: Zachodzi przez ekstremalnie cienki", True, COLOR_TEXT),
                            (tx, ty + 85))
                screen.blit(font_sm.render("  nabłonek jednowarstwowy płaski pęcherzyków.", True, COLOR_TEXT),
                            (tx, ty + 105))
                screen.blit(font_sm.render("• Rusztowanie: Drzewo oskrzelowe chronione", True, COLOR_TEXT),
                            (tx, ty + 130))
                screen.blit(font_sm.render("  jest przez chrzęstne pierścienie łącznotkankowe.", True, COLOR_TEXT),
                            (tx, ty + 155))

            elif game.lexicon_selected == "stomach":
                screen.blit(font_lg.render("Żołądek (Gaster / Stomach)", True, COLOR_GOLD), (tx, ty))
                screen.blit(font_sm.render("• Narząd muskularny układu pokarmowego.", True, COLOR_TEXT), (tx, ty + 40))
                screen.blit(font_sm.render("  Odpowiada za wstępne trawienie białek.", True, COLOR_TEXT), (tx, ty + 60))
                screen.blit(font_sm.render("• Sok żołądkowy: Zawiera kwas solny (HCl)", True, COLOR_TEXT),
                            (tx, ty + 85))
                screen.blit(font_sm.render("  o pH 1-2 oraz enzym pepsynę.", True, COLOR_TEXT), (tx, ty + 105))
                screen.blit(font_sm.render("• Ochrona: Gruba warstwa śluzu", True, COLOR_TEXT), (tx, ty + 130))
                screen.blit(font_sm.render("  zapobiega samostrawieniu ścian narządu.", True, COLOR_TEXT),
                            (tx, ty + 155))

            # PRAWY PANEL: STATYSTYKI GRY I OSIĄGNIĘCIA
            pygame.draw.rect(screen, (28, 33, 40), (615, 200, 230, 475), border_radius=4)
            pygame.draw.rect(screen, (45, 55, 65), (615, 200, 230, 475), 1)

            rx, ry = 625, 215
            screen.blit(font_lg.render("STATYSTYKI", True, COLOR_GOLD), (rx, ry))
            screen.blit(font_sm.render(f"Kliknięcia ogółem: {game.stats['total_clicks']}", True, (240, 240, 240)),
                        (rx, ry + 30))
            screen.blit(font_sm.render(f"Wygenerowane ATP: {game.stats['atp_generated']}", True, (240, 240, 240)),
                        (rx, ry + 50))
            screen.blit(font_sm.render(f"Wyhodowane tkanki: {game.stats['tissues_crafted']}", True, (240, 240, 240)),
                        (rx, ry + 70))
            screen.blit(font_sm.render(f"Zbudowane narządy: {game.stats['organs_built']}", True, (240, 240, 240)),
                        (rx, ry + 90))
            screen.blit(font_sm.render(f"Błędy laboratoryjne: {game.stats['failed_attempts']}", True, (240, 240, 240)),
                        (rx, ry + 110))

            pygame.draw.line(screen, (60, 70, 85), (620, 350), (835, 350), 1)
            screen.blit(font_lg.render("OSIĄGNIĘCIA", True, COLOR_GOLD), (rx, 360))

            ach_list = game.get_achievements_list()
            ay_offset = 390
            for title, desc, unlocked in ach_list[:5]:
                color_title = COLOR_GREEN if unlocked else (150, 150, 150)
                status_text = "[OK]" if unlocked else "[..]"
                screen.blit(font_sm.render(f"{status_text} {title}", True, color_title), (rx, ay_offset))
                screen.blit(font_sm.render(f"  {desc}", True, COLOR_TEXT_MUTED), (rx, ay_offset + 16))
                ay_offset += 36

        # --- PRZYCISK MENU GÓRNEGO "BAZA I STATY" ---
        # Rysuje się niezależnie od aktywnego tabu (na samym dole struktury warunków)
        is_active_5 = game.current_tab == 5
        pygame.draw.rect(screen, (40, 80, 130) if is_active_5 else (45, 50, 60), game.btn_tab5, border_radius=4)
        pygame.draw.rect(screen, (100, 180, 255) if is_active_5 else (80, 90, 100), game.btn_tab5, 1)
        screen.blit(font_sm.render("Baza i Staty", True, (255, 255, 255)), (game.btn_tab5.x + 18, game.btn_tab5.y + 10))

        game.draw_ui(screen)
    elif game.state == "GAME_OVER":
        screen.fill((35, 18, 18))
        screen.blit(font_title.render("KRACH METABOLICZNY. PROCES PRZERWANY.", True, COLOR_RED),
                    (WIDTH // 2 - 390, HEIGHT // 2 - 50))
        screen.blit(font_md.render("Poziom ATP spadł do zera. Zygota uległa degradacji.", True, COLOR_TEXT),
                    (WIDTH // 2 - 210, HEIGHT // 2 + 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
    elif game.state == "VICTORY":
        screen.fill((20, 40, 25))
        screen.blit(font_title.render("ORGANIZM UKOŃCZONY!", True, COLOR_GOLD), (WIDTH // 2 - 220, HEIGHT // 2 - 50))
        screen.blit(font_md.render("Ontogeneza zakończona pełnym sukcesem.", True, COLOR_TEXT),
                    (WIDTH // 2 - 180, HEIGHT // 2 + 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
    pygame.display.flip()
    clock.tick(60)