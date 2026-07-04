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