import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sqlite3
from pathlib import Path
from PIL import Image, ImageTk
import requests
import io
import threading

# Configuração do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Detecta se está rodando como .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys._MEIPASS)
    EXEC_DIR = Path(os.path.dirname(sys.executable))
else:
    ROOT_DIR = Path(__file__).resolve().parent
    EXEC_DIR = ROOT_DIR

DB_FILE = EXEC_DIR / 'db.sqleague'
TABLE_NAME = 'Champions'
# Versão atualizada para 15.9.1 conforme pedido
IMG_URL_BASE = "https://ddragon.leagueoflegends.com/cdn/15.9.1/img/champion/"
LOADING_URL_BASE = "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/"

# Caminho do Logo
LOGO_PATH = ROOT_DIR / "dist" / "images" / "logo4.png"

class ChampionTooltip:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.cache = {}

    def show(self, x, y, data):
        if self.window:
            self.window.destroy()

        # Verifica se os dados necessários existem
        if 'image_full' not in data:
            self.window = tk.Toplevel(self.parent)
            self.window.wm_overrideredirect(True)
            self.window.geometry(f"+{x+20}+{y+20}")
            f = ctk.CTkFrame(self.window, fg_color="#1a1a1a", border_color="red", border_width=1)
            f.pack()
            ctk.CTkLabel(f, text="Dados incompletos.\nPor favor, rode o league_main.py\ncom a API ligada.", font=("Arial", 10)).pack(padx=10, pady=10)
            return

        self.window = tk.Toplevel(self.parent)
        self.window.wm_overrideredirect(True)
        self.window.attributes("-topmost", True)
        
        # Frame Principal (Horizontal) - Borda Cinza
        main_frame = ctk.CTkFrame(self.window, fg_color="#1a1a1a", border_color="#555555", border_width=2)
        main_frame.pack()

        # Lado Esquerdo: Imagem (Ainda mais reduzido)
        self.img_label = tk.Label(main_frame, text="Carregando...", fg="white", bg="#1a1a1a", width=16, height=12)
        self.img_label.pack(side="left", padx=(10, 5), pady=10)

        # Lado Direito: Informações (Bem compacto)
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

        name_label = ctk.CTkLabel(info_frame, text=data.get('name', "Desconhecido").upper(), font=ctk.CTkFont(size=18, weight="bold"), anchor="w")
        name_label.pack(fill="x", pady=(0, 0))

        title_label = ctk.CTkLabel(info_frame, text=data.get('title', "").capitalize(), font=ctk.CTkFont(size=14, slant="italic"), text_color="#aaaaaa", anchor="w")
        title_label.pack(fill="x", pady=(0, 5))


        tags_label = ctk.CTkLabel(info_frame, text=f"Tags: {data.get('tags', '')}", font=ctk.CTkFont(size=11), text_color="#aaaaaa", anchor="w")
        tags_label.pack(fill="x", pady=(0, 5))

        # Divisor simples
        line = tk.Frame(info_frame, height=1, bg="#333333")
        line.pack(fill="x", pady=(0, 5))

        blurb_label = ctk.CTkLabel(info_frame, text=data.get('blurb', ""), font=ctk.CTkFont(size=11), wraplength=200, justify="left", anchor="nw")
        blurb_label.pack(fill="both", expand=True)

        # Ajuste de Posição (Garante que não saia da tela)
        self.window.update_idletasks()
        win_w = self.window.winfo_width()
        win_h = self.window.winfo_height()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()

        pos_x = x + 25
        pos_y = y - (win_h // 2)

        # Se ultrapassar a largura da tela, inverte para o lado esquerdo do mouse
        if pos_x + win_w > screen_w:
            pos_x = x - win_w - 25
        
        # Se ultrapassar a altura da tela (topo ou fundo)
        if pos_y + win_h > screen_h:
            pos_y = screen_h - win_h - 10
        if pos_y < 10:
            pos_y = 10

        self.window.geometry(f"+{pos_x}+{pos_y}")

        # Carregar Imagem de Loading (High Res Portrait)
        img_full = data.get('image_full', "")
        champ_id = img_full.split('.')[0]
        img_url = f"{LOADING_URL_BASE}{champ_id}_0.jpg"
        
        if img_url in self.cache:
            self.update_image(self.cache[img_url])
        else:
            threading.Thread(target=self.fetch_image, args=(img_url,), daemon=True).start()

    def fetch_image(self, url):
        try:
            response = requests.get(url, timeout=5)
            image = Image.open(io.BytesIO(response.content))
            # Formato Loading Art (Portrait) - Agora bem compacto
            image = image.resize((140, 250), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(image)
            self.cache[url] = tk_img
            
            if self.window and self.window.winfo_exists():
                self.parent.after(0, lambda: self.update_image(tk_img))
        except Exception as e:
            print(f"Erro ao baixar imagem: {e}")
            if self.window and self.window.winfo_exists():
                self.parent.after(0, lambda: self.img_label.configure(text="Erro ao carregar"))

    def update_image(self, tk_img):
        if self.window and self.window.winfo_exists() and self.img_label.winfo_exists():
            self.img_label.configure(image=tk_img, text="", width=140, height=250)
            self.img_label.image = tk_img

    def hide(self):
        if self.window:
            self.window.destroy()
            self.window = None

class LeagueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("League of Legends - Informações de Campeões")
        self.geometry("850x550")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        print(f"[DEBUG] Banco de dados procurado em: {DB_FILE}")

        self.tooltip = ChampionTooltip(self)
        self.champion_data = {} # Cache local de dados dos campeões
        self.last_clicked_row = None
        self.mouse_start_pos = (0, 0) # Armazena onde o mouse estava no clique

        self.create_widgets()
        self.load_all()

    def create_widgets(self):
        # Título com Logo
        try:
            logo_img = Image.open(LOGO_PATH)
            # Redimensiona mantendo a proporção (ex: altura 60)
            w, h = logo_img.size
            new_h = 60
            new_w = int((new_h / h) * w)
            self.logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(new_w, new_h))
            
            self.logo_label = ctk.CTkLabel(self, image=self.logo_ctk, text="")
            self.logo_label.grid(row=0, column=0, pady=(15, 5))
        except Exception as e:
            print(f"[AVISO] Não foi possível carregar o logo: {e}")
            self.title_label = ctk.CTkLabel(
                self,
                text="SUMMONERS HELPER",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            self.title_label.grid(row=0, column=0, pady=(15, 5))

        # Frame de Busca
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=(5, 5), sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)

        self.search_label = ctk.CTkLabel(self.search_frame, text="Buscar Campeão:")
        self.search_label.grid(row=0, column=0, padx=(15, 5), pady=8)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Digite o nome...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.search_champion())

        self.search_button = ctk.CTkButton(self.search_frame, text="Buscar", command=self.search_champion, fg_color="#555555", hover_color="#444444", width=80)
        self.search_button.grid(row=0, column=2, padx=5, pady=8)

        # Botão Listar Todos (Movido para cima ao lado do buscar)
        self.list_all_button = ctk.CTkButton(self.search_frame, text="Listar Todos", command=self.load_all, fg_color="#555555", hover_color="#444444", width=100)
        self.list_all_button.grid(row=0, column=3, padx=(5, 15), pady=8)

        # Estilização da Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2b2b2b",
                        bordercolor="#2b2b2b",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#4a4a4a')])
        
        style.layout("Treeview.Heading", []) 

        # Frame para os Cabeçalhos Customizados
        self.header_frame = ctk.CTkFrame(self, fg_color="#333333", height=30, corner_radius=0)
        self.header_frame.grid(row=2, column=0, padx=(20, 36), pady=(5, 0), sticky="ew") 
        
        # Colunas
        ctk.CTkLabel(self.header_frame, text="Nome", width=150, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(5,0))
        ctk.CTkLabel(self.header_frame, text="■ Desvantagem", width=320, anchor="w", 
                     text_color="#ff4d4d", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
        ctk.CTkLabel(self.header_frame, text="■ Vantagem", width=320, anchor="w", 
                     text_color="#2ecc71", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)

        # Container para Treeview e Scrollbar
        self.tree_frame = ctk.CTkFrame(self, corner_radius=0)
        self.tree_frame.grid(row=3, column=0, padx=(20, 20), pady=(0, 15), sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("name", "counters", "advantages"),
            show="headings",
            style="Treeview"
        )

        for col in ("name", "counters", "advantages"):
            self.tree.heading(col, text="")

        self.tree.column("name", width=150, anchor="w")
        self.tree.column("counters", width=320, anchor="w")
        self.tree.column("advantages", width=320, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ctk.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Binds para o Tooltip e Seleção
        self.tree.bind("<Button-1>", self.on_item_click)
        self.tree.bind("<Motion>", self.on_mouse_move)

    def on_item_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            item = self.tree.item(row_id)
            name = item['values'][0]
            if name in self.champion_data:
                data = self.champion_data[name]
                x = self.winfo_pointerx()
                y = self.winfo_pointery()
                self.tooltip.show(x, y, data)
                self.last_clicked_row = row_id
                self.mouse_start_pos = (x, y) # Define a posição inicial
                # Garante que a linha fique selecionada (cinza) ao clicar
                self.tree.selection_set(row_id)
            else:
                self.tooltip.hide()
                self.last_clicked_row = None
        else:
            self.tooltip.hide()
            self.last_clicked_row = None

    def on_mouse_move(self, event):
        # Só verifica se houver um card aberto
        if self.last_clicked_row:
            curr_x = self.winfo_pointerx()
            curr_y = self.winfo_pointery()
            start_x, start_y = self.mouse_start_pos
            
            # Calcula a distância percorrida (Pitágoras simples para o range de erro)
            distance = ((curr_x - start_x)**2 + (curr_y - start_y)**2)**0.5
            
            # Margem de erro: o card só fecha se o mouse se mover mais de 20 pixels
            if distance > 20:
                self.tooltip.hide()
                self.tree.selection_remove(self.last_clicked_row)
                self.last_clicked_row = None

    def search_champion(self):
        name = self.search_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Digite o nome de um campeão para buscar.")
            return

        if not DB_FILE.exists():
            messagebox.showerror("Erro", f"Banco de dados não encontrado em:\n{DB_FILE}")
            return

        connection = sqlite3.connect(DB_FILE)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        try:
            cursor.execute(
                f"SELECT * FROM {TABLE_NAME} WHERE name LIKE ?",
                (f"%{name}%",)
            )
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Erro no Banco", f"Ocorreu um erro:\n{e}")
            connection.close()
            return

        connection.close()
        self.tree.delete(*self.tree.get_children())
        self.champion_data = {}

        if rows:
            for r in rows:
                self.tree.insert("", tk.END, values=(r['name'], r['counters'], r['advantages']))
                self.champion_data[r['name']] = dict(r)
        else:
            messagebox.showinfo("Resultado", "Nenhum campeão encontrado.")

    def load_all(self):
        # Limpa o campo de busca
        self.search_entry.delete(0, tk.END)

        if not DB_FILE.exists():
            messagebox.showerror("Erro", f"Banco de dados não encontrado em:\n{DB_FILE}")
            return

        connection = sqlite3.connect(DB_FILE)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT * FROM {TABLE_NAME}")
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Erro no Banco", f"Ocorreu um erro:\n{e}")
            connection.close()
            return

        connection.close()
        self.tree.delete(*self.tree.get_children())
        self.champion_data = {}

        for r in rows:
            self.tree.insert("", tk.END, values=(r['name'], r['counters'], r['advantages']))
            self.champion_data[r['name']] = dict(r)

if __name__ == "__main__":
    app = LeagueApp()
    app.mainloop()
