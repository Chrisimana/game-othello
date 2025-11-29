import random
from game.base_ai import BaseAI # Import kelas base baru

class MinimaxAI(BaseAI): # Warisi BaseAI
    def __init__(self, depth=3):
        # Default depth dinaikkan ke 3 (sebelumnya hardcoded 2)
        self.depth = depth

    def get_move(self, board, player):
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            return None

        best_score = float('-inf')
        best_moves = []

        # Gunakan depth dari init
        for move in valid_moves:
            test_board = self._copy_board(board)
            if test_board.make_move(move[0], move[1], player):
                # Panggil rekursi
                score = self._minimax(test_board, self.depth - 1, False, player)
                
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

        return random.choice(best_moves) if best_moves else valid_moves[0]

    def _minimax(self, board, depth, is_maximizing, player):
        # Base case: depth habis atau game over
        if depth == 0 or board.is_game_over():
            return self._evaluate_board_advanced(board, player)

        opponent = 'W' if player == 'B' else 'B'
        current_player = player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)

        # Handle PASS: Jika tidak ada langkah, lempar giliran tapi jangan kurangi depth (opsional)
        # atau kurangi depth dan lanjut
        if not valid_moves:
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