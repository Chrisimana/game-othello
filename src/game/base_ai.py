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
        """Fungsi evaluasi skor heuristik."""
        black, white = board.get_score()
        
        if player == 'B':
            score = black - white
        else:
            score = white - black
        
        game_phase = self._get_game_phase(board)
        
        # 1. Evaluasi Posisi (Corner & Edge)
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for r, c in corners:
            if board.board[r][c] == player:
                score += 25
            elif board.board[r][c] is not None:
                score -= 25
                
            # Hindari area berbahaya di samping sudut (X-squares/C-squares) jika sudut kosong
            if board.board[r][c] is None:
                adjacent_danger = []
                if r == 0: adjacent_danger.extend([(0, 1), (1, 1), (1, 0)]) # Top-Left
                elif r == 7: adjacent_danger.extend([(7, 1), (6, 1), (6, 0)]) # Bottom-Left
                # ... (logika serupa untuk sudut kanan)
                
                # (Sederhana) Hukum gerakan ke area dekat sudut jika sudut kosong
                # Implementasi detail bisa ditambahkan di sini
        
        # 2. Stable Pieces
        stable_score = self._count_stable_pieces(board, player)
        score += stable_score * 5  # Bobot ditingkatkan karena sangat penting
        
        # 3. Mobility (Jumlah langkah legal)
        my_moves = len(board.get_valid_moves(player))
        opponent = 'W' if player == 'B' else 'B'
        op_moves = len(board.get_valid_moves(opponent))
        
        if game_phase == 'early':
            # Di awal, jangan terlalu rakus makan bidak, fokus mobilitas
            score += (my_moves - op_moves) * 2
        elif game_phase == 'mid':
            score += (my_moves - op_moves) * 3
        else:
            # Late game: jumlah bidak mulai jadi prioritas utama
            pass 
            
        return score