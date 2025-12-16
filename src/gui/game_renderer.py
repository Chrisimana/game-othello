import pygame
import time
from utils.constants import *

class GameRenderer:
    def __init__(self, screen, game_logic):
        self.screen = screen
        self.game_logic = game_logic
        
        # Inisialisasi Font
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.table_font = pygame.font.SysFont('Consolas', 16)
        self.summary_font = pygame.font.SysFont("Arial", 20, bold=True)
        
        # Hitung posisi papan agar di tengah
        board_pixel_size = BOARD_SIZE * CELL_SIZE
        self.board_x = (screen.get_width() - board_pixel_size) // 2
        self.board_y = (screen.get_height() - board_pixel_size) // 2

        # Tombol Kembali (Visual)
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)

    def draw(self, game_over=False, game_over_time=0):
        self.screen.fill(GREEN)
        
        # Gambar Tombol Kembali
        pygame.draw.rect(self.screen, DARK_GREEN, self.back_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, self.back_button_rect, 2, border_radius=5)
        back_text = self.font.render("Kembali", True, WHITE)
        self.screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))
        
        # Judul
        if self.game_logic.game_mode == 'pvp': title = "Player vs Player"
        elif self.game_logic.game_mode == 'pvb': 
            t_str = f"{self.game_logic.ai_time_limit}s" if self.game_logic.ai_time_limit else "∞"
            title = f"PvB ({self.game_logic.ai_difficulty} | D:{self.game_logic.ai_depth} T:{t_str})"
        else: title = f"Bot vs Bot - Game {self.game_logic.current_game}/{self.game_logic.num_games}"
        
        title_s = self.title_font.render(title, True, WHITE)
        self.screen.blit(title_s, title_s.get_rect(center=(self.screen.get_width()//2, 40)))
        
        self.draw_board(game_over)
        self.draw_player_info()
        
        if game_over:
            self.draw_game_over(game_over_time)
        
        pygame.display.flip()

    def draw_board(self, game_over):
        pygame.draw.rect(self.screen, DARK_GREEN, (self.board_x - 5, self.board_y - 5, BOARD_SIZE * CELL_SIZE + 10, BOARD_SIZE * CELL_SIZE + 10))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell_rect = pygame.Rect(self.board_x + col * CELL_SIZE, self.board_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GREEN, cell_rect)
                pygame.draw.rect(self.screen, BLACK, cell_rect, 1)
                
                piece = self.game_logic.board.board[row][col]
                if piece:
                    color = BLACK if piece == 'B' else WHITE
                    pygame.draw.circle(self.screen, color, (cell_rect.centerx, cell_rect.centery), CELL_SIZE // 2 - 5)
                
                # Highlight langkah valid (Hints)
                if not game_over and (self.game_logic.game_mode == 'pvp' or (self.game_logic.game_mode == 'pvb' and self.game_logic.board.current_player == 'B')):
                    if self.game_logic.board.is_valid_move(row, col, self.game_logic.board.current_player):
                        pygame.draw.circle(self.screen, RED, (cell_rect.centerx, cell_rect.centery), 5)

    def draw_player_info(self):
        cp = "Black (B)" if self.game_logic.board.current_player == 'B' else "White (W)"
        bs, ws = self.game_logic.board.get_score()
        info_y = self.board_y + BOARD_SIZE * CELL_SIZE + 20
        
        self.screen.blit(self.font.render(f"Giliran: {cp}", True, WHITE), (self.board_x, info_y))
        self.screen.blit(self.font.render(f"Black: {bs}  -  White: {ws}", True, WHITE), (self.board_x, info_y + 30))
        
        if self.game_logic.game_mode == 'bvb_compare': 
            # --- GUNAKAN NAMA DINAMIS DARI LOGIC ---
            b_name = self.game_logic.black_algo_name
            w_name = self.game_logic.white_algo_name
            text_str = f"Black: {b_name} | White: {w_name}"
            # ---------------------------------------
            self.screen.blit(self.font.render(text_str, True, WHITE), (self.board_x, info_y + 60))

    def draw_game_over(self, game_over_time):
        if self.game_logic.current_game == self.game_logic.num_games and self.game_logic.num_games > 1:
            self.draw_tournament_summary()
        else:
            self.draw_single_game_result(game_over_time)

    def draw_single_game_result(self, game_over_time):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        w, h = 600, 400 
        message_rect = pygame.Rect((self.screen.get_width() - w) // 2, (self.screen.get_height() - h) // 2, w, h)
        pygame.draw.rect(self.screen, DARK_GREEN, message_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, message_rect, 2, border_radius=10)
        
        winner = self.game_logic.board.get_winner()
        black_score, white_score = self.game_logic.board.get_score()
        
        if winner == 'B': result_text = "Black Menang!"
        elif winner == 'W': result_text = "White Menang!"
        else: result_text = "Permainan Seri!"
        
        cx = message_rect.centerx
        self.screen.blit(self.title_font.render(result_text, True, WHITE), (cx - 100, message_rect.top + 50))
        self.screen.blit(self.title_font.render(f"Black {black_score} - {white_score} White", True, WHITE), (cx - 120, message_rect.top + 100))

        # Statistik
        stats = self.game_logic.get_match_stats()
        b_stat = f"Black (Minimax): Avg Depth {stats['B']['avg_depth']:.2f}, Time {stats['B']['avg_time']:.2f}s"
        w_stat = f"White (AlphaBeta): Avg Depth {stats['W']['avg_depth']:.2f}, Time {stats['W']['avg_time']:.2f}s"
        self.screen.blit(self.font.render(b_stat, True, (144, 238, 144)), (message_rect.left + 50, message_rect.top + 160))
        self.screen.blit(self.font.render(w_stat, True, (255, 182, 193)), (message_rect.left + 50, message_rect.top + 200))
        
        # Tombol Auto Next Text
        if self.game_logic.game_mode in ['bvb', 'bvb_compare'] and self.game_logic.current_game < self.game_logic.num_games:
             elapsed = time.time() - game_over_time
             remaining = max(0, 2.0 - elapsed)
             btn_text = f"Lanjut Otomatis dalam {remaining:.1f}s..."
        else:
             btn_text = "Lanjut ke Game Berikutnya" if self.game_logic.current_game < self.game_logic.num_games else "Selesai"
        
        close_button = pygame.Rect(cx - 150, message_rect.bottom - 80, 300, 50)
        pygame.draw.rect(self.screen, GREEN, close_button, border_radius=5)
        text_surf = self.font.render(btn_text, True, WHITE)
        self.screen.blit(text_surf, text_surf.get_rect(center=close_button.center))

    def draw_tournament_summary(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        w, h = 800, 600
        rect = pygame.Rect((self.screen.get_width() - w) // 2, (self.screen.get_height() - h) // 2, w, h)
        pygame.draw.rect(self.screen, DARK_GREEN, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
        
        title = self.title_font.render(f"HASIL AKHIR ({self.game_logic.num_games} PERTANDINGAN)", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(rect.centerx, rect.top + 40)))
        
        header_y = rect.top + 90
        headers = ["No", "Pemenang", "Skor (B-W)", "Hitam (D/T)", "Putih (D/T)"]
        col_x = [rect.left + 40, rect.left + 100, rect.left + 220, rect.left + 380, rect.left + 600]
        
        for i, h_text in enumerate(headers):
            self.screen.blit(self.font.render(h_text, True, (255, 255, 100)), (col_x[i], header_y))
        
        pygame.draw.line(self.screen, WHITE, (rect.left + 20, header_y + 30), (rect.right - 20, header_y + 30), 2)
        
        start_y = header_y + 45
        line_height = 30
        
        b_wins, w_wins, draws = 0, 0, 0
        for i, res in enumerate(self.game_logic.game_results):
            y_pos = start_y + i * line_height
            if res['winner'] == 'B': b_wins += 1
            elif res['winner'] == 'W': w_wins += 1
            else: draws += 1
            
            color = (144, 238, 144) if res['winner'] == 'B' else ((255, 182, 193) if res['winner'] == 'W' else WHITE)
            
            row_data = [
                str(res['game_no']),
                "Black" if res['winner'] == 'B' else ("White" if res['winner'] == 'W' else "Draw"),
                f"{res['b_score']} - {res['w_score']}",
                f"D:{res['b_stats']['avg_depth']:.1f} / {res['b_stats']['avg_time']:.2f}s",
                f"D:{res['w_stats']['avg_depth']:.1f} / {res['w_stats']['avg_time']:.2f}s"
            ]
            
            for j, text in enumerate(row_data):
                self.screen.blit(self.table_font.render(text, True, color), (col_x[j], y_pos))

        pygame.draw.line(self.screen, WHITE, (rect.left + 20, rect.bottom - 100), (rect.right - 20, rect.bottom - 100), 2)
        summary_text = f"TOTAL: Black Menang: {b_wins}  |  White Menang: {w_wins}  |  Seri: {draws}"
        text_surface = self.summary_font.render(summary_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(rect.centerx, rect.bottom - 60))
        self.screen.blit(text_surface, text_rect)

    def draw_pass_message(self, pc):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0,0,0,100))
        self.screen.blit(overlay, (0,0))
        mr = pygame.Rect(0,0,300,100)
        mr.center = (self.screen.get_width()//2, self.screen.get_height()//2)
        pygame.draw.rect(self.screen, WHITE, mr, border_radius=10)
        pygame.draw.rect(self.screen, RED, mr, 3, border_radius=10)
        
        pn = "BLACK" if pc == 'B' else "WHITE"
        self.screen.blit(self.font.render(f"{pn} Tidak Ada Jalan!", True, BLACK), (mr.centerx - 80, mr.centery - 20))
        self.screen.blit(self.title_font.render("PASS", True, RED), (mr.centerx - 40, mr.centery + 10))