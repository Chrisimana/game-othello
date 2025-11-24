import pygame
import time
from utils.constants import *
from game.game_logic import GameLogic

# Kelas utama untuk jendela permainan
class GameWindow:
    def __init__(self, screen, game_mode='pvp', ai_difficulty='medium', num_games=1):
        self.screen = screen
        self.game_logic = GameLogic(game_mode, ai_difficulty, num_games)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        
        # Hitung posisi papan
        board_pixel_size = BOARD_SIZE * CELL_SIZE
        self.board_x = (screen.get_width() - board_pixel_size) // 2
        self.board_y = (screen.get_height() - board_pixel_size) // 2
        
        # Tombol
        button_width, button_height = 120, 40
        self.back_button = pygame.Rect(20, 20, button_width, button_height)
        
        self.game_over = False
        self.waiting_for_click = False  # Untuk menunggu klik setelah game over
    
    # Jalankan loop utama permainan
    def run(self):
        running = True
        ai_move_delay = 0.5  # Delay untuk gerakan AI (detik)
        last_ai_move_time = 0
        
        while running:
            current_time = time.time()
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.collidepoint(mouse_pos):
                        running = False
                    
                    # Handle klik untuk menutup pesan game over
                    if self.game_over and self.waiting_for_click:
                        if self.game_logic.game_mode == 'bvb' and self.game_logic.next_game():
                            # Lanjut ke game berikutnya untuk BvB
                            self.game_over = False
                            self.waiting_for_click = False
                            last_ai_move_time = 0
                        else:
                            # Untuk mode lain, kembali ke menu
                            running = False
                        continue
                    
                    # Handle klik papan untuk pemain manusia
                    if not self.game_over and (self.game_logic.game_mode == 'pvp' or 
                        (self.game_logic.game_mode == 'pvb' and 
                         self.game_logic.board.current_player == 'B')):
                        
                        board_x, board_y = self.get_board_position(mouse_pos)
                        if board_x is not None and board_y is not None:
                            if self.game_logic.make_move(board_x, board_y):
                                # Cek apakah game selesai setelah move
                                if self.game_logic.check_game_over():
                                    self.game_over = True
                                    self.waiting_for_click = True
            
            # Handle gerakan AI
            if (not self.game_over and 
                self.game_logic.game_mode in ['pvb', 'bvb'] and
                current_time - last_ai_move_time > ai_move_delay):
                
                current_player = self.game_logic.board.current_player
                
                # Untuk BvB, kedua pemain adalah AI
                if (self.game_logic.game_mode == 'pvb' and current_player == 'W') or \
                   (self.game_logic.game_mode == 'bvb'):
                    
                    if self.game_logic.ai_move():
                        last_ai_move_time = current_time
                        
                        # Cek apakah game selesai setelah AI move
                        if self.game_logic.check_game_over():
                            self.game_over = True
                            self.waiting_for_click = True
            
            self.draw()
            self.clock.tick(60)
    

    # Konversi posisi mouse ke posisi papan
    def get_board_position(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        
        # Cek apakah klik di dalam papan
        if (self.board_x <= mouse_x < self.board_x + BOARD_SIZE * CELL_SIZE and
            self.board_y <= mouse_y < self.board_y + BOARD_SIZE * CELL_SIZE):
            
            # Hitung posisi sel
            board_x = (mouse_x - self.board_x) // CELL_SIZE
            board_y = (mouse_y - self.board_y) // CELL_SIZE
            
            # Validasi posisi
            if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
                return board_x, board_y
        
        return None, None
    
    # Gambar seluruh jendela permainan
    def draw(self):
        self.screen.fill(GREEN)
        
        # Gambar tombol kembali
        pygame.draw.rect(self.screen, DARK_GREEN, self.back_button, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, self.back_button, 2, border_radius=5)
        back_text = self.font.render("Kembali", True, WHITE)
        back_text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Gambar judul
        if self.game_logic.game_mode == 'pvp':
            title = "Player vs Player"
        elif self.game_logic.game_mode == 'pvb':
            title = f"Player vs Bot ({self.game_logic.ai_difficulty})"
        else:  # bvb
            title = f"Bot vs Bot - Game {self.game_logic.current_game}/{self.game_logic.num_games}"
        
        title_surface = self.title_font.render(title, True, WHITE)
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Gambar papan
        self.draw_board()
        
        # Gambar informasi pemain
        self.draw_player_info()
        
        # Gambar game over message
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    # Gambar papan permainan
    def draw_board(self):
        # Gambar latar papan
        pygame.draw.rect(self.screen, DARK_GREEN, 
                        (self.board_x - 5, self.board_y - 5, 
                         BOARD_SIZE * CELL_SIZE + 10, BOARD_SIZE * CELL_SIZE + 10))
        
        # Gambar grid dan bidak
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Gambar sel
                cell_rect = pygame.Rect(
                    self.board_x + col * CELL_SIZE,
                    self.board_y + row * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, GREEN, cell_rect)
                pygame.draw.rect(self.screen, BLACK, cell_rect, 1)
                
                # Gambar bidak
                piece = self.game_logic.board.board[row][col]
                if piece is not None:
                    color = BLACK if piece == 'B' else WHITE
                    pygame.draw.circle(
                        self.screen, color,
                        (self.board_x + col * CELL_SIZE + CELL_SIZE // 2,
                         self.board_y + row * CELL_SIZE + CELL_SIZE // 2),
                        CELL_SIZE // 2 - 5
                    )
                
                # Tandai gerakan valid untuk pemain saat ini
                if not self.game_over and (self.game_logic.game_mode == 'pvp' or 
                    (self.game_logic.game_mode == 'pvb' and 
                     self.game_logic.board.current_player == 'B')):
                    
                    current_player = self.game_logic.board.current_player
                    if self.game_logic.board.is_valid_move(row, col, current_player):
                        pygame.draw.circle(
                            self.screen, RED,
                            (self.board_x + col * CELL_SIZE + CELL_SIZE // 2,
                             self.board_y + row * CELL_SIZE + CELL_SIZE // 2),
                            5
                        )
    
    # Gambar informasi pemain
    def draw_player_info(self):
        # Informasi pemain saat ini
        if self.game_logic.board.current_player == 'B':
            current_player = "Black (B)"
        else:
            current_player = "While (W)"
            
        current_text = f"Giliran: {current_player}"
        
        # Skor
        black_score, white_score = self.game_logic.board.get_score()
        score_text = f"Black: {black_score}  -  While: {white_score}"
        
        # Mode info
        if self.game_logic.game_mode == 'pvb':
            mode_info = "Anda: Black | Bot: While"
        else:
            mode_info = ""
        
        # Render teks
        current_surface = self.font.render(current_text, True, WHITE)
        score_surface = self.font.render(score_text, True, WHITE)
        mode_surface = self.font.render(mode_info, True, WHITE)
        
        # Posisi teks
        info_y = self.board_y + BOARD_SIZE * CELL_SIZE + 20
        self.screen.blit(current_surface, (self.board_x, info_y))
        self.screen.blit(score_surface, (self.board_x, info_y + 30))
        if mode_info:
            self.screen.blit(mode_surface, (self.board_x, info_y + 60))
    
    # Gambar pesan game over
    def draw_game_over(self):
        # Overlay semi-transparan
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Kotak pesan
        message_rect = pygame.Rect(
            self.screen.get_width() // 2 - 200,
            self.screen.get_height() // 2 - 100,
            400, 200
        )
        pygame.draw.rect(self.screen, GREEN, message_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, message_rect, 2, border_radius=10)
        
        # Teks hasil
        winner = self.game_logic.board.get_winner()
        black_score, white_score = self.game_logic.board.get_score()
        
        if winner == 'B':
            result_text = "Black Menang!"
        elif winner == 'W':
            result_text = "While Menang!"
        else:
            result_text = "Permainan Seri!"
        
        score_text = f"Black {black_score} - {white_score} While"
        
        # Render teks
        result_surface = self.title_font.render(result_text, True, BLACK)
        score_surface = self.font.render(score_text, True, BLACK)
        
        # Posisi teks
        result_rect = result_surface.get_rect(center=(message_rect.centerx, message_rect.centery - 30))
        score_rect = score_surface.get_rect(center=(message_rect.centerx, message_rect.centery + 10))
        
        self.screen.blit(result_surface, result_rect)
        self.screen.blit(score_surface, score_rect)
        
        # Tombol berdasarkan mode
        if self.game_logic.game_mode == 'bvb' and self.game_logic.current_game < self.game_logic.num_games:
            button_text = "Lanjut"
        else:
            button_text = "Tutup"
            
        close_button = pygame.Rect(
            message_rect.centerx - 60,
            message_rect.centery + 50,
            120, 40
        )
        pygame.draw.rect(self.screen, DARK_GREEN, close_button, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, close_button, 2, border_radius=5)
        close_text = self.font.render(button_text, True, WHITE)
        close_text_rect = close_text.get_rect(center=close_button.center)
        self.screen.blit(close_text, close_text_rect)