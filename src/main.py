import pygame
import sys
from gui.main_menu import MainMenu

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Othello Game")
    
    main_menu = MainMenu(screen)
    main_menu.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()