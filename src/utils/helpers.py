import json
import os
from datetime import datetime

# Menyimpan riwayat permainan ke file JSON
def save_game_history(game_data):
    history_file = "data/game_history.json"
    
    # Buat folder data jika belum ada
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    # Load data yang sudah ada
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []
    
    # Tambahkan data baru dengan timestamp
    game_data['timestamp'] = datetime.now().isoformat()
    history.append(game_data)
    
    # Simpan kembali
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

# Memuat riwayat permainan dari file JSON
def load_game_history():
    history_file = "data/game_history.json"
    
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []