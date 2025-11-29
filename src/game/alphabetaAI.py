import random
from game.base_ai import BaseAI

class AlphaBetaAI(BaseAI):
    def __init__(self, depth=5):
        # Alpha-Beta lebih efisien, jadi bisa pakai depth lebih tinggi (5)
        self.depth = depth

    def get_move(self, board, player):
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            return None

        best_score = float('-inf')
        best_moves = []
        alpha = float('-inf')
        beta = float('inf')

        for move in valid_moves:
            test_board = self._copy_board(board)
            if test_board.make_move(move[0], move[1], player):
                score = self._alphabeta(test_board, self.depth - 1, alpha, beta, False, player)
                
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)
                
                # Update alpha untuk root level
                alpha = max(alpha, best_score)

        return random.choice(best_moves) if best_moves else valid_moves[0]

    def _alphabeta(self, board, depth, alpha, beta, is_maximizing, player):
        if depth == 0 or board.is_game_over():
            return self._evaluate_board_advanced(board, player)

        opponent = 'W' if player == 'B' else 'B'
        current_player = player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)

        if not valid_moves:
            return self._alphabeta(board, depth - 1, alpha, beta, not is_maximizing, player)

        if is_maximizing:
            value = float('-inf')
            for move in valid_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._alphabeta(test_board, depth - 1, alpha, beta, False, player)
                value = max(value, score)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break # Pruning
            return value
        else:
            value = float('inf')
            for move in valid_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._alphabeta(test_board, depth - 1, alpha, beta, True, player)
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha:
                    break # Pruning
            return value
    

