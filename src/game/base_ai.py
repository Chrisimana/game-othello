from game.board import Board

class BaseAI:
    """
    Kelas dasar untuk semua algoritma AI Othello.
    Berisi logika evaluasi heuristik dan fungsi bantuan umum.
    """
    
    def _copy_board(self, board):
        """Membuat salinan deep copy dari papan untuk simulasi."""
        new_board = Board()
        # List comprehension lebih cepat daripada deepcopy untuk kasus ini
        new_board.board = [row[:] for row in board.board]
        new_board.current_player = board.current_player
        return new_board

    def _get_game_phase(self, board):
        """Menentukan fase permainan berdasarkan jumlah bidak."""
        total_pieces = sum(1 for row in board.board for cell in row if cell is not None)
        if total_pieces < 20:
            return 'early'
        elif total_pieces < 45:
            return 'mid'
        else:
            return 'late'

    def _count_stable_pieces(self, board, player):
        """
        Menghitung bidak stabil (tidak bisa dibalik lagi).
        PERBAIKAN: Logika sebelumnya kurang akurat. 
        Di sini kita fokus pada sudut dan sisi yang terhubung ke sudut.
        """
        stable = 0
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        
        for r, c in corners:
            if board.board[r][c] == player:
                stable += 1
                
                # Cek sisi horizontal dari sudut ini
                dx = 1 if c == 0 else -1
                for i in range(1, 7):
                    if 0 <= c + i*dx < 8 and board.board[r][c + i*dx] == player:
                        stable += 1
                    else:
                        break # Putus, tidak stabil lagi
                
                # Cek sisi vertikal dari sudut ini
                dy = 1 if r == 0 else -1
                for i in range(1, 7):
                    if 0 <= r + i*dy < 8 and board.board[r + i*dy][c] == player:
                        stable += 1
                    else:
                        break
        return stable

    def _evaluate_board_advanced(self, board, player):
        """
        Evaluasi menggunakan Positional Weight Matrix.
        Ini lebih stabil daripada logika if-else manual.
        """
        black_len, white_len = board.get_score()
        
        # 1. Matriks Bobot Standar Othello
        # Sudut = 100 (Sangat bagus)
        # X-square = -20 (Bahaya)
        # C-square = -10 (Kurang bagus)
        # Pinggir aman = 10
        # Pusat = 1 sampai 5
        weights = [
            [100, -25,  10,   5,   5,  10, -25, 100],
            [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
            [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
            [  5,  -2,  -1,  -1,  -1,  -1,  -2,   5],
            [  5,  -2,  -1,  -1,  -1,  -1,  -2,   5],
            [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
            [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
            [100, -25,  10,   5,   5,  10, -25, 100],
        ]

        position_score = 0
        for r in range(8):
            for c in range(8):
                if board.board[r][c] == player:
                    position_score += weights[r][c]
                elif board.board[r][c] is not None: # Lawan
                    position_score -= weights[r][c]

        # 2. Mobility (Kebebasan Melangkah)
        # Sangat penting agar tidak terkena 'Zugzwang' (kehabisan langkah)
        my_moves = len(board.get_valid_moves(player))
        opponent = 'W' if player == 'B' else 'B'
        op_moves = len(board.get_valid_moves(opponent))
        mobility_score = (my_moves - op_moves) * 10 

        # 3. Coin Parity (Jumlah Bidak)
        # Hati-hati! Di awal game, punya sedikit bidak justru taktis (evaporation strategy).
        # Jadi kita hanya hitung selisih bidak di fase AKHIR game.
        game_phase = self._get_game_phase(board)
        coin_score = 0
        if game_phase == 'late':
            if player == 'B':
                coin_score = (black_len - white_len)
            else:
                coin_score = (white_len - black_len)
        else:
            # Di early/mid, punya lebih sedikit bidak kadang lebih baik (untuk mobilitas)
            # Kita beri sedikit penalti jika terlalu banyak bidak di awal
            coin_score = - (black_len - white_len) if player == 'B' else - (white_len - black_len)

        # Total Score
        return position_score + mobility_score + coin_score