import pygame
import time
from utils.constants import *
from game.game_logic import GameLogic
from utils.helpers import save_game_history
from gui.game_renderer import GameRenderer

class GameWindow:
    # --- UPDATE DI SINI: Tambahkan parameter mcts_iterations=1000 ---
    def __init__(self, screen, game_mode='pvp', ai_difficulty='medium', num_games=1, ai_depth=3, ai_time_limit=None, bot_config=None, mcts_iterations=1000):
        self.screen = screen
        # Pass parameter mcts_iterations ke GameLogic
        self.game_logic = GameLogic(game_mode, ai_difficulty, num_games, ai_depth, ai_time_limit, bot_config, mcts_iterations)
        self.clock = pygame.time.Clock()
        
        self.renderer = GameRenderer(screen, self.game_logic)
        
        self.game_over = False
        self.waiting_for_click = False 
        self.game_over_time = 0 
        self.history_saved = False 

    def run(self):
        running = True
        # ... (sisa kode di bawah ini SAMA PERSIS dengan sebelumnya, tidak perlu diubah)
        ai_move_delay = 0.5 if self.game_logic.game_mode != 'bvb_compare' else 0.1
        last_ai_move_time = 0
        
        self.renderer.draw()
        self.handle_pass_condition()

        while running:
            current_time = time.time()
            
            # Auto Next Game Logic
            if self.game_over and self.waiting_for_click and self.game_logic.game_mode in ['bvb', 'bvb_compare']:
                if current_time - self.game_over_time > 2.0:
                    if self.game_logic.current_game < self.game_logic.num_games:
                        if self.game_logic.next_game():
                            self._reset_state()
                            last_ai_move_time = time.time()
                            self.handle_pass_condition()

            # Save History Logic
            if self.game_over and self.game_logic.current_game == self.game_logic.num_games:
                if not self.history_saved: # Logic baru (simpan semua mode)
                    self.save_bvb_history()
                    self.history_saved = True

            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.renderer.back_button_rect.collidepoint(mouse_pos): running = False
                    
                    if self.game_over and self.waiting_for_click:
                        if self.game_logic.current_game < self.game_logic.num_games:
                            if self.game_logic.next_game():
                                self._reset_state()
                                last_ai_move_time = 0
                                self.handle_pass_condition()
                        else:
                            running = False 
                        continue
                    
                    if not self.game_over and (self.game_logic.game_mode == 'pvp' or (self.game_logic.game_mode == 'pvb' and self.game_logic.board.current_player == 'B')):
                        board_x, board_y = self.get_board_position(mouse_pos)
                        if board_x is not None and board_y is not None:
                            if self.game_logic.make_move(board_x, board_y):
                                self.renderer.draw(self.game_over, self.game_over_time)
                                if self.game_logic.check_game_over():
                                    self._set_game_over()
                                else: self.handle_pass_condition()

            if (not self.game_over and self.game_logic.game_mode in ['pvb', 'bvb', 'bvb_compare'] and current_time - last_ai_move_time > ai_move_delay):
                cp = self.game_logic.board.current_player
                is_ai = (self.game_logic.game_mode == 'pvb' and cp == 'W') or (self.game_logic.game_mode in ['bvb', 'bvb_compare'])
                if is_ai:
                    if self.game_logic.ai_move():
                        last_ai_move_time = current_time
                        self.renderer.draw(self.game_over, self.game_over_time)
                        if self.game_logic.check_game_over():
                            self._set_game_over()
                        else: self.handle_pass_condition()
            
            self.renderer.draw(self.game_over, self.game_over_time)
            self.clock.tick(60)

    def _set_game_over(self):
        self.game_logic.record_game_result()
        self.game_over = True
        self.waiting_for_click = True
        self.game_over_time = time.time()

    def _reset_state(self):
        self.game_over = False
        self.waiting_for_click = False

    def save_bvb_history(self):
        # ... (Gunakan kode save_bvb_history TERBARU yang sudah kita buat sebelumnya untuk menyimpan data detail JSON)
        # Hitung total kemenangan
        b_wins = sum(1 for res in self.game_logic.game_results if res['winner'] == 'B')
        w_wins = sum(1 for res in self.game_logic.game_results if res['winner'] == 'W')
        draws = sum(1 for res in self.game_logic.game_results if res['winner'] == 'D')
        
        # Nama Bot
        b_name_raw = self.game_logic.black_algo_name
        w_name_raw = self.game_logic.white_algo_name
        
        black_n = f"{b_name_raw} (D={self.game_logic.ai_depth})"
        white_n = f"{w_name_raw} (D={self.game_logic.ai_depth})"

        # --- DATA DETAIL PER GAME ---
        detailed_games = []
        for res in self.game_logic.game_results:
            game_detail = {
                "no": res['game_no'],
                "winner": "Black" if res['winner'] == 'B' else ("White" if res['winner'] == 'W' else "Draw"),
                "score_black": res['b_score'],
                "score_white": res['w_score'],
                "black_stats": {
                    "avg_depth": round(res['b_stats']['avg_depth'], 2),
                    "avg_time": round(res['b_stats']['avg_time'], 4),
                    "max_depth": res['b_stats']['max_depth']
                },
                "white_stats": {
                    "avg_depth": round(res['w_stats']['avg_depth'], 2),
                    "avg_time": round(res['w_stats']['avg_time'], 4),
                    "max_depth": res['w_stats']['max_depth']
                }
            }
            detailed_games.append(game_detail)

        # Struktur Data Akhir untuk JSON
        data = {
            "mode": "Bot vs Bot",
            "timestamp": None, 
            "total_games": self.game_logic.num_games,
            "result_summary": f"Menang: Black ({b_wins}) - White ({w_wins}) | Seri: {draws}",
            "ai_config": {
                "black": black_n, 
                "white": white_n, 
                "time_limit": self.game_logic.ai_time_limit
            },
            "winner": "Black" if b_wins > w_wins else ("White" if w_wins > b_wins else "Seri"),
            "games": detailed_games 
        }
        save_game_history(data)
        
    def get_board_position(self, mouse_pos):
        bx, by = self.renderer.board_x, self.renderer.board_y
        mx, my = mouse_pos
        if bx <= mx < bx + BOARD_SIZE * CELL_SIZE and by <= my < by + BOARD_SIZE * CELL_SIZE:
            return (my - by) // CELL_SIZE, (mx - bx) // CELL_SIZE
        return None, None

    def handle_pass_condition(self):
        cp = self.game_logic.board.current_player
        if not self.game_logic.board.get_valid_moves(cp) and not self.game_logic.board.is_game_over():
            self.renderer.draw(self.game_over, self.game_over_time)
            self.renderer.draw_pass_message(cp) # Panggil pesan PASS
            pygame.display.flip()
            time.sleep(1.5)
            self.game_logic.board.current_player = 'W' if cp == 'B' else 'B'