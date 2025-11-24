import pygame
from utils.constants import *

class Board:
    def __init__(self):
        self.reset()
    
    # Reset papan ke kondisi awal
    def reset(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Posisi awal
        mid = BOARD_SIZE // 2
        self.board[mid-1][mid-1] = 'W'
        self.board[mid][mid] = 'W'
        self.board[mid-1][mid] = 'B'
        self.board[mid][mid-1] = 'B'
        
        self.current_player = 'B'  # Black starts
    
    # Cek apakah gerakan valid
    def is_valid_move(self, row, col, player):
        # Cek jika posisi sudah terisi
        if self.board[row][col] is not None:
            return False
        
        opponent = 'W' if player == 'B' else 'B'
        valid = False
        
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            found_opponent = False
            
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if self.board[r][c] == opponent:
                    found_opponent = True
                elif self.board[r][c] == player:
                    if found_opponent:
                        valid = True
                    break
                else:  # Kosong atau None
                    break
                r += dr
                c += dc
        
        return valid
    
    # Lakukan gerakan jika valid
    def make_move(self, row, col, player):
        if not self.is_valid_move(row, col, player):
            return False
        
        self.board[row][col] = player
        opponent = 'W' if player == 'B' else 'B'
        pieces_flipped = 0
        
        # Balikkan bidak lawan
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            to_flip = []
            
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if self.board[r][c] == opponent:
                    to_flip.append((r, c))
                elif self.board[r][c] == player:
                    # Balikkan semua bidak di antara
                    for flip_r, flip_c in to_flip:
                        self.board[flip_r][flip_c] = player
                        pieces_flipped += 1
                    break
                else:  # Kosong
                    break
                r += dr
                c += dc
        
        return True
    
    # Dapatkan semua gerakan valid untuk pemain
    def get_valid_moves(self, player):
        moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col, player):
                    moves.append((row, col))
        return moves
    
    # Hitung skor untuk kedua pemain
    def get_score(self):
        black_count = 0
        white_count = 0
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 'B':
                    black_count += 1
                elif self.board[row][col] == 'W':
                    white_count += 1
        
        return black_count, white_count
    
    # Cek apakah permainan sudah selesai
    def is_game_over(self):
        # Jika tidak ada gerakan valid untuk kedua pemain
        if not self.get_valid_moves('B') and not self.get_valid_moves('W'):
            return True
        
        # Jika papan penuh
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] is None:
                    return False
        return True
    
    # Tentukan pemenang permainan
    def get_winner(self):
        if not self.is_game_over():
            return None
        
        black, white = self.get_score()
        if black > white:
            return 'B'
        elif white > black:
            return 'W'
        else:
            return 'D'  # Draw