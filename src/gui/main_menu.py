import pygame
import sys
from utils.constants import *

# Kelas untuk tombol
class Button:
    def __init__(self, x, y, width, height, text, color=GREEN, hover_color=DARK_GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 24)
    
    # Menggambar tombol
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    # Memeriksa apakah mouse berada di atas tombol
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
    
    # Memeriksa apakah tombol diklik
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Kelas untuk menu utama
class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 36)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        # Buat tombol
        button_width, button_height = 250, 50
        center_x = screen.get_width() // 2 - button_width // 2
        
        # Tombol menu utama
        # Tombol menu utama
        self.buttons = [
            Button(center_x, 150, button_width, button_height, "Player vs Player"),
            Button(center_x, 220, button_width, button_height, "Player vs Bot"),
            Button(center_x, 290, button_width, button_height, "Bot Minimax vs Alpha-Beta"),
            Button(center_x, 360, button_width, button_height, "Keluar Game")
        ]
        
        # Tombol menu tingkat kesulitan Player vs Bot
        self.difficulty_buttons = [
            Button(center_x, 220, button_width, button_height, "Minimax"),
            Button(center_x, 290, button_width, button_height, "Alpha-Beta"),
            Button(center_x, 360, button_width, button_height, "Kembali")
        ]

        
        # Status menu saat ini
        self.current_menu = "main"  # "main", "pvb_difficulty", "bvb_games"
    
    # Menjalankan loop utama menu
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.current_menu == "main":
                    running = self.handle_main_menu(event, mouse_pos)
                elif self.current_menu == "pvb_difficulty":
                    self.handle_pvb_difficulty_menu(event, mouse_pos)
                elif self.current_menu == "bvb_games":
                    self.handle_bvb_games_menu(event, mouse_pos)
            
            self.draw()
            self.clock.tick(60)
    
    # Menangani menu utama
    # Menangani menu utama
    def handle_main_menu(self, event, mouse_pos):
        for i, button in enumerate(self.buttons):
            button.check_hover(mouse_pos)
        
            if button.is_clicked(mouse_pos, event):
                if i == 0:  # Player vs Player
                    from gui.game_window import GameWindow
                    game_window = GameWindow(self.screen, 'pvp')
                    game_window.run()
                elif i == 1:  # Player vs Bot
                    self.current_menu = "pvb_difficulty"
                elif i == 2:  # Bot Minimax vs Alpha-Beta (sekarang index ke-2)
                    from gui.game_window import GameWindow
                    # misal jalankan 10 game perbandingan
                    game_window = GameWindow(self.screen, 'bvb_compare', 'minimax_vs_alphabeta', 10)
                    game_window.run()
                elif i == 3:  # Keluar Game (sekarang index ke-3)
                    return False
        return True

    
    # Menangani menu Player vs Bot - Tingkat Kesulitan
    def handle_pvb_difficulty_menu(self, event, mouse_pos):
        for i, button in enumerate(self.difficulty_buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, event):
                from gui.game_window import GameWindow
                if i == 0:  # Minimax
                    game_window = GameWindow(self.screen, 'pvb', 'minimax')
                    game_window.run()
                    self.current_menu = "main"
                elif i == 1:  # Alpha-Beta
                    game_window = GameWindow(self.screen, 'pvb', 'alphabeta')
                    game_window.run()
                    self.current_menu = "main"
                elif i == 2:  # Kembali
                    self.current_menu = "main"

    # Menggambar menu
    def draw(self):
        self.screen.fill(GREEN)
        
        # Judul
        title = self.title_font.render("OTHELLO GAME", True, WHITE)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Gambar tombol sesuai menu saat ini
        if self.current_menu == "main":
            for button in self.buttons:
                button.draw(self.screen)
        elif self.current_menu == "pvb_difficulty":
            subtitle = self.font.render("Pilih Bot yang akan dilawan", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 150))
            self.screen.blit(subtitle, subtitle_rect)
            
            for button in self.difficulty_buttons:
                button.draw(self.screen)
        elif self.current_menu == "bvb_games":
            subtitle = self.font.render("Pilih Jumlah Permainan", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 150))
            self.screen.blit(subtitle, subtitle_rect)
            
            for button in self.bot_game_buttons:
                button.draw(self.screen)
        
        pygame.display.flip()