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