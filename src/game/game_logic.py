import random
import time
from game.board import Board
from utils.helpers import save_game_history
from game.minmaxAI import MinimaxAI
from game.alphabetaAI import AlphaBetaAI
from game.mctsAI import MonteCarloAI  # <--- TAMBAHAN BARU

class GameLogic:
    def __init__(self, game_mode='pvp', ai_difficulty='alphabeta', num_games=1, ai_depth=3, ai_time_limit=None, bot_config=None , mcts_iterations=1000):
        self.board = Board()
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty
        self.num_games = num_games
        self.current_game = 1
        
        self.game_results = [] 
        
        self.ai_depth = ai_depth
        self.ai_time_limit = ai_time_limit
        self.mcts_iterations = mcts_iterations
        self.stats_history = {'B': [], 'W': []}
        self.bot_config = bot_config 
        
        self.black_algo_name = "Player"
        self.white_algo_name = "Player"
        self.ai_black = None
        self.ai_white = None

        if game_mode in ['pvb', 'bvb', 'bvb_compare']:
            seed = int(time.time() * 1000) % 1000000
            
            if game_mode == 'bvb_compare':
                if self.bot_config:
                    # SETUP BLACK BOT
                    if self.bot_config['black'] == 'minimax':
                        self.ai_black = MinimaxAI(depth=self.ai_depth, time_limit=self.ai_time_limit)
                        self.black_algo_name = "Minimax"
                    elif self.bot_config['black'] == 'mcts':
                        # PASSING ITERASI KE MCTS
                        self.ai_black = MonteCarloAI(time_limit=self.ai_time_limit, iterations=self.mcts_iterations)
                        self.black_algo_name = "MCTS"
                    else:
                        self.ai_black = AlphaBetaAI(depth=self.ai_depth, time_limit=self.ai_time_limit)
                        self.black_algo_name = "AlphaBeta"
                        
                    # SETUP WHITE BOT
                    if self.bot_config['white'] == 'minimax':
                        self.ai_white = MinimaxAI(depth=self.ai_depth, time_limit=self.ai_time_limit)
                        self.white_algo_name = "Minimax"
                    elif self.bot_config['white'] == 'mcts':
                        # PASSING ITERASI KE MCTS
                        self.ai_white = MonteCarloAI(time_limit=self.ai_time_limit, iterations=self.mcts_iterations)
                        self.white_algo_name = "MCTS"
                    else:
                        self.ai_white = AlphaBetaAI(depth=self.ai_depth, time_limit=self.ai_time_limit)
                        self.white_algo_name = "AlphaBeta"
                
                else:
                    # Fallback random jika config kosong
                    pass 
                
                self.ai_difficulty = 'custom_matchup'
                
            else:
                # Logika PvB Biasa
                if self.ai_difficulty == 'minimax': 
                    AIClass = MinimaxAI
                    name = "Minimax"
                elif self.ai_difficulty == 'mcts': # Tambahan jika ingin PvB lawan MCTS
                    AIClass = MonteCarloAI
                    name = "MCTS"
                else: 
                    AIClass = AlphaBetaAI
                    name = "AlphaBeta"

                random.seed(seed + 1)
                # MCTS menggunakan time_limit, Minimax/AlphaBeta menggunakan depth & time_limit
                if name == 'MCTS':
                    self.ai_black = AIClass(time_limit=self.ai_time_limit)
                    random.seed(seed + 2)
                    self.ai_white = AIClass(time_limit=self.ai_time_limit)
                else:
                    self.ai_black = AIClass(depth=self.ai_depth, time_limit=self.ai_time_limit)
                    random.seed(seed + 2)
                    self.ai_white = AIClass(depth=self.ai_depth, time_limit=self.ai_time_limit)
                
                random.seed()
                self.black_algo_name = name
                self.white_algo_name = name

    def record_game_result(self):
        stats = self.get_match_stats()
        winner = self.board.get_winner()
        b_score, w_score = self.board.get_score()
        
        result_data = {
            'game_no': self.current_game,
            'winner': winner,
            'b_score': b_score,
            'w_score': w_score,
            'b_stats': stats['B'],
            'w_stats': stats['W'],
            'b_name': self.black_algo_name, 
            'w_name': self.white_algo_name
        }
        self.game_results.append(result_data)

    def ai_move(self):
        if self.board.is_game_over(): return False

        current_player = self.board.current_player
        move = None
        active_ai = None 

        try:
            if current_player == 'B' and self.game_mode in ['pvb', 'bvb', 'bvb_compare']:
                move = self.ai_black.get_move(self.board, 'B')
                active_ai = self.ai_black
            elif current_player == 'W' and self.game_mode in ['pvb', 'bvb', 'bvb_compare']:
                move = self.ai_white.get_move(self.board, 'W')
                active_ai = self.ai_white
            else:
                return False

            if move:
                # Simpan statistik langkah (Depth/Simulations & Time)
                if active_ai and hasattr(active_ai, 'last_stats'):
                    self.stats_history[current_player].append(active_ai.last_stats)
                
                if self.board.make_move(move[0], move[1], current_player):
                    self.board.current_player = 'W' if current_player == 'B' else 'B'
                    return True

            if not move:
                # Pass giliran
                self.board.current_player = 'W' if current_player == 'B' else 'B'
                return True

        except Exception as e:
            print(f"Error AI: {e}")
            self.board.current_player = 'W' if current_player == 'B' else 'B'
            return True

        return False
             
    def make_move(self, row, col):
        if self.board.is_game_over(): return False
        current_player = self.board.current_player
        
        if self.game_mode == 'pvp':
            if self.board.make_move(row, col, current_player):
                self.board.current_player = 'W' if current_player == 'B' else 'B'
                return True
        elif self.game_mode == 'pvb':
            if current_player == 'B' and self.board.make_move(row, col, 'B'):
                self.board.current_player = 'W'
                return True
        return False
    
    def next_game(self):
        if self.current_game < self.num_games:
            self.current_game += 1
            self.board.reset()
            self.stats_history = {'B': [], 'W': []}
            return True
        return False
    
    def check_game_over(self):
        return self.board.is_game_over()
    
    def get_match_stats(self):
        summary = {}
        for p in ['B', 'W']:
            moves = self.stats_history[p]
            if not moves:
                summary[p] = {'avg_depth': 0, 'avg_time': 0, 'max_depth': 0}
                continue
            
            valid_depths = [m['depth'] for m in moves if m['depth'] > 0]
            avg_depth = sum(valid_depths) / len(valid_depths) if valid_depths else 0
            max_depth = max([m['depth'] for m in moves]) if moves else 0
            avg_time = sum([m['time'] for m in moves]) / len(moves)
            
            summary[p] = {
                'avg_depth': avg_depth,
                'avg_time': avg_time,
                'max_depth': max_depth
            }
        return summary