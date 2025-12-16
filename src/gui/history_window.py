import pygame
from utils.constants import *
from utils.helpers import load_game_history
from gui.ui_components import Button

class HistoryWindow:
    def __init__(self, screen):
        self.screen = screen
        # Font
        self.font_title = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_header = pygame.font.SysFont('Arial', 20, bold=True)
        self.font_content = pygame.font.SysFont('Arial', 18)
        self.font_small = pygame.font.SysFont('Arial', 16, italic=True)
        self.table_font = pygame.font.SysFont('Consolas', 16) # Font monospace untuk tabel
        
        self.back_button = Button(20, 20, 100, 40, "Kembali")
        
        self.history_data = load_game_history()
        self.history_data.reverse() 
        
        # State untuk Detail View
        self.selected_history = None # Akan berisi data dict jika ada yang diklik
        self.scroll_offset = 0

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Jika sedang membuka Detail View
                if self.selected_history:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Klik di mana saja untuk menutup detail (atau bisa buat tombol close khusus)
                        self.selected_history = None
                
                # Jika sedang di List View
                else:
                    self.back_button.check_hover(mouse_pos)
                    if self.back_button.is_clicked(mouse_pos, event):
                        running = False
                    
                    # Cek klik pada kartu history
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.check_card_click(mouse_pos)

            self.draw()
            pygame.display.flip()

    def check_card_click(self, mouse_pos):
        start_y = 100
        card_height = 110
        padding = 15
        
        for i, data in enumerate(self.history_data[:10]): # Batasi 10 terakhir
            y = start_y + i * (card_height + padding)
            card_rect = pygame.Rect(50, y, self.screen.get_width() - 100, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                self.selected_history = data # Buka detail view
                break

    def draw(self):
        self.screen.fill(GREEN)
        
        # Jika ada history yang dipilih, gambar Detail View (Overlay)
        if self.selected_history:
            self.draw_list_view() # Gambar background redup
            self.draw_detail_view(self.selected_history)
        else:
            self.draw_list_view()

    def draw_list_view(self):
        # Header
        title = self.font_title.render("RIWAYAT PERTANDINGAN", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width()//2, 50)))
        
        self.back_button.draw(self.screen)
        
        # Layout List
        start_y = 100
        card_height = 110 
        padding = 15
        
        if not self.history_data:
            empty_text = self.font_content.render("Belum ada riwayat pertandingan.", True, WHITE)
            self.screen.blit(empty_text, empty_text.get_rect(center=(self.screen.get_width()//2, 300)))
            return

        for i, data in enumerate(self.history_data[:10]): 
            y = start_y + i * (card_height + padding)
            
            # Background Kartu
            card_rect = pygame.Rect(50, y, self.screen.get_width() - 100, card_height)
            
            # Efek hover sederhana (jika tidak sedang popup)
            color = DARK_GREEN
            if not self.selected_history and card_rect.collidepoint(pygame.mouse.get_pos()):
                color = (0, 120, 0) # Sedikit lebih terang
                
            pygame.draw.rect(self.screen, color, card_rect, border_radius=12)
            pygame.draw.rect(self.screen, (200, 255, 200), card_rect, 2, border_radius=12)
            
            # Parsing Waktu
            ts = data.get('timestamp', '')[:16].replace('T', ' ')
            
            # Info Kiri
            date_surf = self.font_header.render(ts, True, (255, 255, 200))
            self.screen.blit(date_surf, (card_rect.left + 20, card_rect.top + 15))
            
            # Nama / Mode
            mode = data.get('mode', 'Unknown')
            if mode == "Bot vs Bot":
                b_name = data.get('ai_config', {}).get('black', '?')
                w_name = data.get('ai_config', {}).get('white', '?')
                match_text = f"{b_name} vs {w_name}"
            else:
                match_text = mode # PvP atau PvB
                
            match_surf = self.font_content.render(match_text, True, WHITE)
            self.screen.blit(match_surf, (card_rect.left + 20, card_rect.top + 45))
            
            # Hint Klik
            hint_surf = self.font_small.render("(Klik untuk detail)", True, (150, 150, 150))
            self.screen.blit(hint_surf, (card_rect.left + 20, card_rect.bottom - 25))

            # Info Kanan (Hasil)
            res_text = data.get('result_summary', 'N/A').replace("Menang: ", "")
            winner = data.get('winner', '')
            res_color = WHITE
            if winner == 'Black': res_color = (100, 255, 100)
            elif winner == 'White': res_color = (255, 150, 150)
            elif winner == 'Seri': res_color = (255, 255, 100)
            
            res_surf = self.font_title.render(res_text, True, res_color)
            res_rect = res_surf.get_rect(midright=(card_rect.right - 30, card_rect.centery))
            self.screen.blit(res_surf, res_rect)

    def draw_detail_view(self, data):
        # Overlay Gelap
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) # Lebih gelap agar fokus
        self.screen.blit(overlay, (0, 0))
        
        # Kotak Panel
        w, h = 850, 600
        rect = pygame.Rect((self.screen.get_width() - w) // 2, (self.screen.get_height() - h) // 2, w, h)
        pygame.draw.rect(self.screen, DARK_GREEN, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
        
        # Judul Detail
        header_text = f"DETAIL PERTANDINGAN - {data.get('timestamp', '')[:16].replace('T', ' ')}"
        title = self.font_header.render(header_text, True, WHITE)
        self.screen.blit(title, title.get_rect(center=(rect.centerx, rect.top + 30)))
        
        # Cek apakah ada data detail 'games' (dari update JSON baru)
        games_data = data.get('games', [])
        
        if not games_data:
            # Fallback untuk data lama atau mode selain BvB
            msg = self.font_content.render("Data detail per-game tidak tersedia untuk riwayat ini.", True, (200, 200, 200))
            self.screen.blit(msg, msg.get_rect(center=rect.center))
        else:
            # --- GAMBAR TABEL ---
            header_y = rect.top + 80
            headers = ["No", "Pemenang", "Skor (B-W)", "Hitam (Depth/Time)", "Putih (Depth/Time)"]
            # Posisi Kolom
            col_x = [rect.left + 30, rect.left + 80, rect.left + 200, rect.left + 350, rect.left + 600]
            
            # Gambar Header
            for i, h_text in enumerate(headers):
                self.screen.blit(self.font_header.render(h_text, True, (255, 255, 100)), (col_x[i], header_y))
            
            pygame.draw.line(self.screen, WHITE, (rect.left + 20, header_y + 30), (rect.right - 20, header_y + 30), 2)
            
            # Gambar Baris Data
            start_y = header_y + 45
            line_height = 35 # Jarak antar baris
            
            for g in games_data:
                y_pos = start_y + (int(g['no']) - 1) * line_height
                
                # Warna teks berdasarkan pemenang per game
                color = WHITE
                if g['winner'] == 'Black': color = (144, 238, 144)
                elif g['winner'] == 'White': color = (255, 182, 193)
                
                # Format Data Baris
                row_items = [
                    str(g['no']),
                    g['winner'],
                    f"{g['score_black']} - {g['score_white']}",
                    f"D:{g['black_stats']['avg_depth']} / {g['black_stats']['avg_time']}s",
                    f"D:{g['white_stats']['avg_depth']} / {g['white_stats']['avg_time']}s"
                ]
                
                for j, text in enumerate(row_items):
                    self.screen.blit(self.table_font.render(text, True, color), (col_x[j], y_pos))

        # Footer / Info Klik
        close_hint = self.font_content.render("Klik di mana saja untuk menutup", True, (200, 200, 200))
        self.screen.blit(close_hint, close_hint.get_rect(center=(rect.centerx, rect.bottom - 30)))