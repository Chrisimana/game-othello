import random
import math
from game.board import Board

# Kelas AI untuk Othello dengan berbagai tingkat kesulitan
class OthelloAI:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.random_factor = {
            'easy': 0.8,    # 80% random
            'medium': 0.3,  # 30% random  
            'hard': 0.1     # 10% random
        }
    # Dapatkan gerakan AI berdasarkan tingkat kesulitan
    def get_move(self, board, player):
        valid_moves = board.get_valid_moves(player)
        
        if not valid_moves:
            return None
        
        # Kadang-kadang pilih random untuk variasi
        if random.random() < self.random_factor[self.difficulty]:
            return random.choice(valid_moves)
        
        if self.difficulty == 'easy':
            return self._easy_move(valid_moves, board, player)
        elif self.difficulty == 'medium':
            return self._medium_move(valid_moves, board, player)
        else:  # hard
            return self._hard_move(valid_moves, board, player)
    
    # Gerakan mudah: prioritaskan sudut, hindari samping sudut
    def _easy_move(self, valid_moves, board, player):
        scored_moves = []
        
        for move in valid_moves:
            score = self._evaluate_simple(move, board, player)
            scored_moves.append((score, move))
        
        if scored_moves:
            scored_moves.sort(reverse=True)
            # Pilih dari 3 terbaik secara random
            top_moves = scored_moves[:min(3, len(scored_moves))]
            return random.choice(top_moves)[1]
        return random.choice(valid_moves)
    
    # Gerakan sedang: pertimbangkan posisi dan jumlah bidak yang dibalik
    def _medium_move(self, valid_moves, board, player):
        scored_moves = []
        
        for move in valid_moves:
            score = self._evaluate_medium(move, board, player)
            scored_moves.append((score, move))
        
        if scored_moves:
            scored_moves.sort(reverse=True)
            # Pilih dari 2 terbaik secara random
            top_moves = scored_moves[:min(2, len(scored_moves))]
            return random.choice(top_moves)[1]
        return random.choice(valid_moves)
    
    # Gerakan sulit: menggunakan minimax dengan depth terbatas
    def _hard_move(self, valid_moves, board, player):
        if not valid_moves:
            return None
            
        # Untuk early game, gunakan evaluasi posisi
        if self._get_game_phase(board) == 'early':
            return self._medium_move(valid_moves, board, player)
        
        best_score = float('-inf')
        best_moves = []
        
        for move in valid_moves:
            # Buat salinan papan untuk simulasi
            test_board = self._copy_board(board)
            
            # Lakukan gerakan
            if test_board.make_move(move[0], move[1], player):
                # Evaluasi posisi dengan minimax
                score = self._minimax(test_board, 2, False, player)
                
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)
        
        return random.choice(best_moves) if best_moves else valid_moves[0]
    
    # Algoritma minimax sederhana
    def _minimax(self, board, depth, is_maximizing, player):
        if depth == 0 or board.is_game_over():
            return self._evaluate_board_advanced(board, player)
        
        opponent = 'W' if player == 'B' else 'B'
        current_player = player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)
        
        if not valid_moves:
            # Jika tidak ada gerakan valid, lewati giliran
            return self._minimax(board, depth - 1, not is_maximizing, player)
        
        if is_maximizing:
            best_score = float('-inf')
            for move in valid_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._minimax(test_board, depth - 1, False, player)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for move in valid_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._minimax(test_board, depth - 1, True, player)
                best_score = min(best_score, score)
            return best_score
    
    # Evaluasi sederhana untuk easy mode
    def _evaluate_simple(self, move, board, player):
        row, col = move
        score = 0
        
        # Prioritas sudut
        if (row, col) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            score += 100
        
        # Hindari posisi di samping sudut
        if (row, col) in [(0, 1), (1, 0), (1, 1), (0, 6), (1, 6), (1, 7),
                          (6, 0), (6, 1), (7, 1), (6, 6), (6, 7), (7, 6)]:
            score -= 50
        
        # Prioritas tepi
        if row == 0 or row == 7 or col == 0 or col == 7:
            score += 10
        
        return score
    
    # Evaluasi untuk medium mode
    def _evaluate_medium(self, move, board, player):
        row, col = move
        score = self._evaluate_simple(move, board, player)
        
        # Tambahkan evaluasi berdasarkan jumlah bidak yang dibalik
        try:
            test_board = self._copy_board(board)
            before_black, before_white = test_board.get_score()
            
            if test_board.make_move(row, col, player):
                after_black, after_white = test_board.get_score()
                
                if player == 'B':
                    pieces_flipped = after_black - before_black - 1
                else:
                    pieces_flipped = after_white - before_white - 1
                
                score += pieces_flipped * 3
        except:
            pass
        
        # Pertimbangkan mobilitas (jumlah gerakan lawan setelah move ini)
        try:
            test_board = self._copy_board(board)
            test_board.make_move(row, col, player)
            opponent = 'W' if player == 'B' else 'B'
            opponent_moves = len(test_board.get_valid_moves(opponent))
            score -= opponent_moves * 2  # Kurangi score jika memberi banyak gerakan ke lawan
        except:
            pass
        
        return score
    
    # Evaluasi posisi papan yang lebih advanced
    def _evaluate_board_advanced(self, board, player):
        black, white = board.get_score()
        
        if player == 'B':
            score = black - white
        else:
            score = white - black
        
        # Phase game adjustment
        game_phase = self._get_game_phase(board)
        
        # Bonus untuk sudut
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for r, c in corners:
            if board.board[r][c] == player:
                score += 25
            elif board.board[r][c] is not None:
                score -= 25
        
        # Bonus untuk stabil pieces (pieces yang tidak bisa dibalik)
        stable_score = self._count_stable_pieces(board, player)
        score += stable_score * 2
        
        # Mobility bonus
        player_moves = len(board.get_valid_moves(player))
        opponent = 'W' if player == 'B' else 'B'
        opponent_moves = len(board.get_valid_moves(opponent))
        
        if game_phase == 'early':
            score += player_moves * 3 - opponent_moves * 2
        else:  # late game
            score += player_moves - opponent_moves * 2
        
        return score
    
    # Tentukan fase permainan
    def _get_game_phase(self, board):
        total_pieces = sum(1 for row in board.board for cell in row if cell is not None)
        if total_pieces < 20:
            return 'early'
        elif total_pieces < 45:
            return 'mid'
        else:
            return 'late'
    
    # Hitung jumlah bidak stabil
    def _count_stable_pieces(self, board, player):
        stable = 0
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        
        for corner in corners:
            if board.board[corner[0]][corner[1]] == player:
                stable += 1
                # Hitung pieces di baris dan kolom dari corner
                for i in range(1, 8):
                    if board.board[corner[0]][i] == player:
                        stable += 0.5
                    if board.board[i][corner[1]] == player:
                        stable += 0.5
        
        return stable
    
    # Buat salinan papan
    def _copy_board(self, board):
        new_board = Board()
        new_board.board = [row[:] for row in board.board]
        new_board.current_player = board.current_player
        return new_board