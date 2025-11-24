import pygame
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO
from utils.constants import *
from utils.helpers import load_game_history

# Kelas jendela riwayat permainan
class HistoryWindow:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.history = load_game_history()
        
        # Tombol
        button_width, button_height = 120, 40
        self.back_button = pygame.Rect(20, 20, button_width, button_height)
        self.graph_button = pygame.Rect(self.screen.get_width() - button_width - 20, 20, button_width, button_height)
        
        self.show_graph = False
    
    # Jalankan loop utama jendela riwayat
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.collidepoint(mouse_pos):
                        running = False
                    
                    if self.graph_button.collidepoint(mouse_pos):
                        self.show_graph = not self.show_graph
            
            self.draw()
            self.clock.tick(60)
    
    # Gambar antarmuka
    def draw(self):
        self.screen.fill(GREEN)
        
        # Gambar tombol
        pygame.draw.rect(self.screen, DARK_GREEN, self.back_button, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, self.back_button, 2, border_radius=5)
        back_text = self.font.render("Kembali", True, WHITE)
        back_text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        pygame.draw.rect(self.screen, DARK_GREEN, self.graph_button, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, self.graph_button, 2, border_radius=5)
        graph_text = self.font.render("Grafik" if not self.show_graph else "Daftar", True, WHITE)
        graph_text_rect = graph_text.get_rect(center=self.graph_button.center)
        self.screen.blit(graph_text, graph_text_rect)
        
        # Judul
        title = self.title_font.render("Riwayat Permainan", True, WHITE)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 40))
        self.screen.blit(title, title_rect)
        
        if self.show_graph:
            self.draw_graph()
        else:
            self.draw_history_list()
        
        pygame.display.flip()
    
    # Gambar daftar riwayat permainan
    def draw_history_list(self):
        if not self.history:
            no_data_text = self.font.render("Tidak ada riwayat permainan", True, WHITE)
            no_data_rect = no_data_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(no_data_text, no_data_rect)
            return
        
        # Header
        headers = ["Mode", "Kesulitan", "Skor", "Pemenang", "Waktu"]
        header_y = 100
        
        for i, header in enumerate(headers):
            header_text = self.font.render(header, True, WHITE)
            header_x = 50 + i * 150
            self.screen.blit(header_text, (header_x, header_y))
        
        # Garis pemisah
        pygame.draw.line(self.screen, WHITE, (50, header_y + 30), 
                         (self.screen.get_width() - 50, header_y + 30), 2)
        
        # Data riwayat (maksimal 10 terbaru)
        recent_history = self.history[-10:]
        
        for i, game in enumerate(recent_history):
            y_pos = header_y + 50 + i * 40
            
            # Mode
            mode_text = self.font.render(game['mode'].upper(), True, WHITE)
            self.screen.blit(mode_text, (50, y_pos))
            
            # Kesulitan
            difficulty = game.get('difficulty', '-')
            if difficulty:
                difficulty_text = self.font.render(difficulty.capitalize(), True, WHITE)
            else:
                difficulty_text = self.font.render('-', True, WHITE)
            self.screen.blit(difficulty_text, (200, y_pos))
            
            # Skor
            score_text = self.font.render(f"{game['black_score']}-{game['white_score']}", True, WHITE)
            self.screen.blit(score_text, (350, y_pos))
            
            # Pemenang
            winner = game['winner']
            if winner == 'B':
                winner_text = "Black"
            elif winner == 'W':
                winner_text = "White"
            else:
                winner_text = "Seri"
            
            winner_surface = self.font.render(winner_text, True, WHITE)
            self.screen.blit(winner_surface, (500, y_pos))
            
            # Waktu
            timestamp = game.get('timestamp', '')
            if timestamp:
                try:
                    # Format: DD/MM HH:MM
                    date_part = timestamp.split('T')[0]
                    time_part = timestamp.split('T')[1][:5]
                    formatted_time = f"{date_part} {time_part}"
                except:
                    formatted_time = "-"
            else:
                formatted_time = "-"
            
            time_text = self.font.render(formatted_time, True, WHITE)
            self.screen.blit(time_text, (650, y_pos))
    
    # Konversi matplotlib figure ke pygame surface
    def matplotlib_to_pygame(self, fig):
        # Simpan figure ke buffer BytesIO sebagai PNG
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Load dari buffer ke pygame surface
        surf = pygame.image.load(buf)
        buf.close()
        
        return surf
    
    # Gambar grafik statistik bot vs bot
    def draw_graph(self):
        # Filter hanya game bot vs bot
        bvb_games = [game for game in self.history if game['mode'] == 'bvb']
        
        if not bvb_games:
            no_data_text = self.font.render("Tidak ada data Bot vs Bot", True, WHITE)
            no_data_rect = no_data_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(no_data_text, no_data_rect)
            return
        
        # Hitung statistik
        black_wins = sum(1 for game in bvb_games if game['winner'] == 'B')
        white_wins = sum(1 for game in bvb_games if game['winner'] == 'W')
        draws = sum(1 for game in bvb_games if game['winner'] == 'D')
        total_games = len(bvb_games)
        
        # Buat grafik pie
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        
        # Data untuk pie chart
        labels = ['Black Menang', 'While Menang', 'Seri']
        sizes = [black_wins, white_wins, draws]
        colors = ['#000000', '#FFFFFF', '#808080']  # Hitam, Putih, Abu-abu
        
        # Hapus bagian yang 0
        non_zero_sizes = []
        non_zero_labels = []
        non_zero_colors = []
        
        for i, size in enumerate(sizes):
            if size > 0:
                non_zero_sizes.append(size)
                non_zero_labels.append(labels[i])
                non_zero_colors.append(colors[i])
        
        if not non_zero_sizes:
            # Jika semua 0, tampilkan pesan
            ax.text(0.5, 0.5, 'Tidak ada data\nkemenangan', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='black')
            ax.set_facecolor('#90EE90')  # Light green
        else:
            # Buat grafik pie dengan outline
            wedges, texts, autotexts = ax.pie(
                non_zero_sizes, 
                labels=non_zero_labels, 
                colors=non_zero_colors, 
                autopct='%1.1f%%', 
                startangle=90, 
                wedgeprops={'edgecolor': 'black', 'linewidth': 1}
            )
            
            # Styling untuk teks
            for text in texts:
                text.set_color('black')
                text.set_fontsize(10)
                text.set_fontweight('bold')
            
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
        
        # Styling plot - HAPUS facecolor dari savefig, gunakan set_facecolor saja
        ax.set_title('Statistik Bot vs Bot', color='black', fontsize=14, fontweight='bold', pad=20)
        fig.patch.set_facecolor('#90EE90')  # Light green background
        ax.set_facecolor('#90EE90')  # Light green background
        
        # Konversi ke pygame surface
        surf = self.matplotlib_to_pygame(fig)
        
        # Buat background hijau untuk grafik
        graph_bg_rect = pygame.Rect(
            self.screen.get_width() // 2 - surf.get_width() // 2 - 10,
            self.screen.get_height() // 2 - surf.get_height() // 2 - 60,
            surf.get_width() + 20,
            surf.get_height() + 20
        )
        pygame.draw.rect(self.screen, DARK_GREEN, graph_bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, graph_bg_rect, 2, border_radius=10)
        
        # Gambar grafik di tengah layar
        graph_rect = surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(surf, graph_rect)
        
        # Informasi statistik detail
        stats_text = [
            f"Total Permainan: {total_games}",
            f"Black Menang: {black_wins} ({black_wins/total_games*100:.1f}%)",
            f"While Menang: {white_wins} ({white_wins/total_games*100:.1f}%)", 
            f"Seri: {draws} ({draws/total_games*100:.1f}%)"
        ]
        
        stats_y = graph_bg_rect.bottom + 20
        for i, text in enumerate(stats_text):
            stat_surface = self.font.render(text, True, WHITE)
            stat_rect = stat_surface.get_rect(center=(self.screen.get_width() // 2, stats_y + i * 25))
            self.screen.blit(stat_surface, stat_rect)
        
        plt.close(fig)  # Tutup figure untuk menghindari memory leak