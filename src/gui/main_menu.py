import pygame
from utils.constants import *
from gui.game_window import GameWindow
from gui.history_window import HistoryWindow
from gui.ui_components import Button, InputBox

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 36)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 20)
        
        self.selected_depth = 3
        self.selected_time = None
        self.temp_game_mode = None
        self.temp_ai_difficulty = None
        
        # Pilihan Algoritma Default
        self.black_choice = 'minimax'
        self.white_choice = 'alphabeta'
        
        button_width, button_height = 250, 50
        center_x = screen.get_width() // 2 - button_width // 2
        
        start_y = 140
        gap = 60
        self.buttons = [
            Button(center_x, start_y, button_width, button_height, "Player vs Player"),
            Button(center_x, start_y + gap, button_width, button_height, "Player vs Bot"),
            Button(center_x, start_y + gap*2, button_width, button_height, "Bot vs Bot (Custom)"),
            Button(center_x, start_y + gap*3, button_width, button_height, "Riwayat BvB"),
            Button(center_x, start_y + gap*4, button_width, button_height, "Keluar Game")
        ]
        
        self.difficulty_buttons = [
            Button(center_x, 220, button_width, button_height, "Minimax"),
            Button(center_x, 290, button_width, button_height, "Alpha-Beta"),
            Button(center_x, 360, button_width, button_height, "Kembali")
        ]
        
        # layout pengaturan T_T
        center_w = screen.get_width() // 2
        
        # Tombol Depth
        self.btn_depth_minus = Button(center_w - 120, 190, 50, 50, "-")
        self.btn_depth_plus = Button(center_w + 70, 190, 50, 50, "+")
        
        # Input Box Waktu
        self.time_input = InputBox(center_w - 70, 290, 140, 40, text='2.0') 
        
        # Input Box Iterasi 
        self.iter_input = InputBox(center_w - 70, 370, 140, 40, text='1000')
        
        # Tombol Pilihan Algoritma 
        self.btn_black_algo = Button(center_w - 260, 450, 250, 40, f"Black: {self.black_choice.title()}", color=BLUE)
        self.btn_white_algo = Button(center_w + 10, 450, 250, 40, f"White: {self.white_choice.title()}", color=RED)
        
        self.btn_start_game = Button(center_x, 520, button_width, button_height, "MULAI GAME", color=RED)
        self.btn_settings_back = Button(center_x, 590, button_width, button_height, "Kembali")

        self.current_menu = "main"  
    
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                
                if self.current_menu == "main":
                    self.handle_main_menu(event, mouse_pos)
                    if self.current_menu == "exit": return 
                elif self.current_menu == "pvb_difficulty":
                    self.handle_pvb_difficulty_menu(event, mouse_pos)
                elif self.current_menu == "settings":
                    self.handle_settings_menu(event, mouse_pos)
            
            self.draw()
            self.clock.tick(60)
    
    def handle_main_menu(self, event, mouse_pos):
        for i, button in enumerate(self.buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, event):
                if i == 0: GameWindow(self.screen, 'pvp').run()
                elif i == 1: self.temp_game_mode = 'pvb'; self.current_menu = "pvb_difficulty"
                elif i == 2: 
                    self.temp_game_mode = 'bvb_compare'
                    self.temp_ai_difficulty = 'custom'
                    self.black_choice = 'minimax'
                    self.white_choice = 'alphabeta'
                    self.btn_black_algo.text = "Black: Minimax"
                    self.btn_white_algo.text = "White: AlphaBeta"
                    self.current_menu = "settings"
                elif i == 3: HistoryWindow(self.screen).run()
                elif i == 4: self.current_menu = "exit"

    def handle_pvb_difficulty_menu(self, event, mouse_pos):
        for i, button in enumerate(self.difficulty_buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, event):
                if i == 0: self.temp_ai_difficulty = 'minimax'; self.current_menu = "settings"
                elif i == 1: self.temp_ai_difficulty = 'alphabeta'; self.current_menu = "settings"
                elif i == 2: self.current_menu = "main"

    def handle_settings_menu(self, event, mouse_pos):
        self.btn_depth_minus.check_hover(mouse_pos); self.btn_depth_plus.check_hover(mouse_pos)
        self.btn_start_game.check_hover(mouse_pos); self.btn_settings_back.check_hover(mouse_pos)
        self.time_input.handle_event(event)
        self.iter_input.handle_event(event) 

        if self.btn_depth_minus.is_clicked(mouse_pos, event) and self.selected_depth > 1: self.selected_depth -= 1
        if self.btn_depth_plus.is_clicked(mouse_pos, event) and self.selected_depth < 20: self.selected_depth += 1
        
        # Logic Siklus Algoritma
        if self.temp_game_mode == 'bvb_compare':
            algos = ['minimax', 'alphabeta', 'mcts']
            
            self.btn_black_algo.check_hover(mouse_pos)
            if self.btn_black_algo.is_clicked(mouse_pos, event):
                curr_idx = algos.index(self.black_choice)
                self.black_choice = algos[(curr_idx + 1) % len(algos)]
                self.btn_black_algo.text = f"Black: {self.black_choice.title()}"
                
            self.btn_white_algo.check_hover(mouse_pos)
            if self.btn_white_algo.is_clicked(mouse_pos, event):
                curr_idx = algos.index(self.white_choice)
                self.white_choice = algos[(curr_idx + 1) % len(algos)]
                self.btn_white_algo.text = f"White: {self.white_choice.title()}"
        
        if self.btn_start_game.is_clicked(mouse_pos, event):
            final_time = self.time_input.get_value()

            try:
                final_iter = int(self.iter_input.get_value())
            except:
                final_iter = 1000 

            num = 10 if self.temp_game_mode == 'bvb_compare' else 1
            
            bot_config = None
            if self.temp_game_mode == 'bvb_compare':
                bot_config = {
                    'black': self.black_choice,
                    'white': self.white_choice
                }
            
            GameWindow(self.screen, self.temp_game_mode, self.temp_ai_difficulty, num, self.selected_depth, final_time, bot_config, final_iter).run()
            self.current_menu = "main"
            
        if self.btn_settings_back.is_clicked(mouse_pos, event):
            self.current_menu = "pvb_difficulty" if self.temp_game_mode == 'pvb' else "main"

    def draw(self):
        self.screen.fill(GREEN)
        title_text = "PENGATURAN BOT" if self.current_menu == "settings" else "OTHELLO GAME"
        title = self.title_font.render(title_text, True, WHITE)
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 80)))
        
        if self.current_menu == "main":
            for button in self.buttons: button.draw(self.screen)
        elif self.current_menu == "pvb_difficulty":
            sub = self.font.render("Pilih Bot Lawan", True, WHITE)
            self.screen.blit(sub, sub.get_rect(center=(self.screen.get_width()//2, 150)))
            for button in self.difficulty_buttons: button.draw(self.screen)
        elif self.current_menu == "settings":
            center_x = self.screen.get_width() // 2
            
            # 1. Depth (Minimax/AB)
            d_lbl = self.font.render("Depth (Minimax/AlphaBeta Only):", True, WHITE)
            self.screen.blit(d_lbl, d_lbl.get_rect(center=(center_x, 150)))
            self.btn_depth_minus.draw(self.screen); self.btn_depth_plus.draw(self.screen)
            d_val = self.title_font.render(str(self.selected_depth), True, WHITE)
            self.screen.blit(d_val, d_val.get_rect(center=(center_x, 215)))
            
            # 2. Time Limit
            t_lbl = self.font.render("Waktu (Detik) - *Kosongkan untuk MCTS Infinity:", True, WHITE)
            self.screen.blit(t_lbl, t_lbl.get_rect(center=(center_x, 260)))
            self.time_input.draw(self.screen)
            
            # 3. Iterations (MCTS) - --- BARU ---
            i_lbl = self.font.render("Max Iterasi (MCTS Only):", True, WHITE)
            self.screen.blit(i_lbl, i_lbl.get_rect(center=(center_x, 340)))
            self.iter_input.draw(self.screen)
            
            if self.temp_game_mode == 'bvb_compare':
                self.btn_black_algo.draw(self.screen)
                self.btn_white_algo.draw(self.screen)
            
            self.btn_start_game.draw(self.screen); self.btn_settings_back.draw(self.screen)
        
        pygame.display.flip()