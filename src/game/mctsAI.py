import time
import math
import random
from game.base_ai import BaseAI
from utils.constants import BOARD_WEIGHTS

class MCTSNode:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = board.get_valid_moves(board.current_player)
        self.player_just_moved = parent.board.current_player if parent else None
        
        # --- [MODIFIKASI 1] Hitung Heuristic Score saat Node dibuat ---
        self.heuristic_val = 0
        if move:
            r, c = move
            # Ambil bobot dari konstanta (misal range -50 s.d 100)
            weight = BOARD_WEIGHTS[r][c]
            
            # Normalisasi sederhana agar nilainya tidak terlalu ekstrem dibanding Win Rate (0-1)
            # Kita bagi 100 agar range-nya sekitar -0.5 sampai 1.0
            self.heuristic_val = weight / 100.0

    def get_bias_weight(board):
        total = sum(1 for r in board.board for c in r if c is not None)
        if total < 20:
            return 3.0   # early
        elif total < 45:
            return 1.5   # mid
        else:
            return 0.5   # late
        

    def uct_score(self, parent_visits):
        if self.visits == 0:
            return float('inf')
            
        # --- [MODIFIKASI 2] Tambahkan Progressive Bias ---
        
        # 1. Exploitation (Statistik Menang Murni)
        exploitation = self.wins / self.visits
        
        # 2. Exploration (Mencari yang jarang dikunjungi)
        exploration = 1.41 * math.sqrt(math.log(parent_visits) / self.visits)
        
        # 3. Progressive Bias (Memanfaatkan Heuristic Value) dan adaptive weight implementasi dari adaptive bias pada mcts
        adaptive_weight = MCTSNode.get_bias_weight(self.board)
        bias = (self.heuristic_val * adaptive_weight) / (self.visits + 1)
        
        return exploitation + exploration + bias

    def best_child(self):
        # Tidak perlu diubah, dia akan otomatis pakai uct_score yang baru
        return max(self.children, key=lambda c: c.uct_score(self.visits))

class MonteCarloAI(BaseAI):
    def __init__(self, time_limit=2.0, iterations=1000):
        self.time_limit = time_limit
        self.iterations = iterations
        self.start_time = 0
        self.last_stats = {'depth': 0, 'time': 0}

    def get_move(self, board, player):
        self.start_time = time.time()
        
        # Menggunakan _copy_board yang sudah dioptimasi di BaseAI
        root = MCTSNode(self._copy_board(board))
        
        simulations = 0
        
        while True:
            # Cek Time Limit
            if self.time_limit and (time.time() - self.start_time >= self.time_limit):
                break
            
            node = root
            
            # 1. SELECTION
            while not node.untried_moves and node.children:
                node = node.best_child()
            
            # 2. EXPANSION
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                temp_board = self._copy_board(node.board) # Fast copy
                temp_board.make_move(move[0], move[1], temp_board.current_player)
                
                # Manual swap turn karena make_move di copy object tidak auto-swap logika game logic utama
                temp_board.current_player = 'W' if temp_board.current_player == 'B' else 'B'
                
                child = MCTSNode(temp_board, parent=node, move=move)
                node.untried_moves.remove(move)
                node.children.append(child)
                node = child
            
            # 3. SIMULATION (HEURISTIC ROLLOUT)
            # Menggunakan BOARD_WEIGHTS dari constants.py untuk arah yang lebih pintar
            rollout_board = self._copy_board(node.board)
            while not rollout_board.is_game_over():
                p = rollout_board.current_player
                moves = rollout_board.get_valid_moves(p)
                
                if not moves:
                    rollout_board.current_player = 'W' if p == 'B' else 'B'
                else:
                    # Epsilon-Greedy: 30% Random, 70% Pilih posisi strategis (Pojok/Pinggir aman)
                    if random.random() < 0.3:
                        m = random.choice(moves)
                    else:
                        # Lookup nilai bobot langsung (sangat cepat O(1))
                        m = max(moves, key=lambda mv: BOARD_WEIGHTS[mv[0]][mv[1]])
                        
                    rollout_board.make_move(m[0], m[1], p)
                    rollout_board.current_player = 'W' if p == 'B' else 'B'
            
            # 4. BACKPROPAGATION
            winner = rollout_board.get_winner()
            while node is not None:
                node.visits += 1
                if node.player_just_moved:
                    if node.player_just_moved == winner:
                        node.wins += 1
                    elif winner == 'D':
                        node.wins += 0.5
                node = node.parent
            
            simulations += 1
            # Cek Iteration Limit jika Time Limit tidak aktif
            if not self.time_limit and simulations >= self.iterations:
                break
        
        elapsed_time = time.time() - self.start_time
        self.last_stats = {'depth': simulations, 'time': elapsed_time}
        
        if not root.children:
            return None
            
        # Pilih langkah yang paling robust (paling banyak dikunjungi)
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move