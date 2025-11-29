import random
from game.board import Board
from utils.helpers import save_game_history
from game.minmaxAI import MinimaxAI
from game.alphabetaAI import AlphaBetaAI

# Logika utama permainan Othello
class GameLogic:
    def __init__(self, game_mode='pvp', ai_difficulty='alphabeta', num_games=1):
        self.board = Board()
        self.game_mode = game_mode
        # ai_difficulty dipakai untuk pvb dan bvb biasa
        self.ai_difficulty = ai_difficulty
        self.num_games = num_games
        self.current_game = 1
        self.game_results = []

        if game_mode in ['pvb', 'bvb', 'bvb_compare']:
            import time
            seed = int(time.time() * 1000) % 1000000

            if game_mode == 'bvb_compare':
                # Hitam = Minimax, Putih = Alpha-Beta
                random.seed(seed + 1)
                self.ai_black = MinimaxAI()
                random.seed(seed + 2)
                self.ai_white = AlphaBetaAI()
                random.seed()
                # Supaya di history kelihatan jelas
                self.ai_difficulty = 'minimax_vs_alphabeta'
            else:
                # mode pvb / bvb biasa: satu jenis algoritma untuk kedua bot
                if self.ai_difficulty == 'minimax':
                    AIClass = MinimaxAI
                else:
                    AIClass = AlphaBetaAI

                random.seed(seed + 1)
                self.ai_black = AIClass()
                random.seed(seed + 2)
                self.ai_white = AIClass()
                random.seed()

    def ai_move(self):
        if self.board.is_game_over():
            return False

        current_player = self.board.current_player

        try:
            if current_player == 'B' and self.game_mode in ['pvb', 'bvb', 'bvb_compare']:
                move = self.ai_black.get_move(self.board, 'B')
            elif current_player == 'W' and self.game_mode in ['pvb', 'bvb', 'bvb_compare']:
                move = self.ai_white.get_move(self.board, 'W')
            else:
                return False

            if move and self.board.make_move(move[0], move[1], current_player):
                self.board.current_player = 'W' if current_player == 'B' else 'B'
                return True

            # Jika tidak ada gerakan valid, lewati giliran
            if not move:
                self.board.current_player = 'W' if current_player == 'B' else 'B'
                return True

        except Exception as e:
            print(f"Error in AI move: {e}")
            self.board.current_player = 'W' if current_player == 'B' else 'B'
            return True

        return False
             
    
    # Lakukan gerakan untuk pemain manusia
    def make_move(self, row, col):
        # Pastikan game belum selesai
        if self.board.is_game_over():
            return False
            
        current_player = self.board.current_player
        
        # Validasi berdasarkan mode permainan
        if self.game_mode == 'pvp':
            # Player vs Player - siapa saja bisa main
            if self.board.make_move(row, col, current_player):
                self.board.current_player = 'W' if current_player == 'B' else 'B'
                return True
                
        elif self.game_mode == 'pvb':
            # Player vs Bot - player selalu hitam
            if current_player == 'B' and self.board.make_move(row, col, 'B'):
                self.board.current_player = 'W'
                return True
                
        return False
    
    # Simpan hasil permainan
    def save_game_result(self):
        black_score, white_score = self.board.get_score()
        winner = self.board.get_winner()
        
        game_data = {
            'mode': self.game_mode,
            'difficulty': self.ai_difficulty if self.game_mode != 'pvp' else None,
            'black_score': black_score,
            'white_score': white_score,
            'winner': winner,
            'game_number': self.current_game if self.game_mode == 'bvb' else 1
        }
        
        self.game_results.append(game_data)
        
        if self.game_mode != 'bvb' or self.current_game == self.num_games:
            # Untuk bvb, simpan semua hasil sekaligus di akhir
            if self.game_mode == 'bvb' and self.current_game == self.num_games:
                for result in self.game_results:
                    save_game_history(result)
            else:
                save_game_history(game_data)
    
    # Lanjutkan ke permainan berikutnya (bot vs bot)
    def next_game(self):
        if self.current_game < self.num_games:
            self.current_game += 1
            self.board.reset()
            return True
        return False
    
    # Cek apakah permainan selesai dan handle hasil
    def check_game_over(self):
        if self.board.is_game_over():
            self.save_game_result()
            return True
        return False