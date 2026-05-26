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
        self.window.geometry(f"+{x+20}+{y+20}")
        
        frame = ctk.CTkFrame(self.window, fg_color="#1a1a1a", border_color="#333333", border_width=2)
        frame.pack()

        # Carregar Imagem Full
        img_name = data.get('image_full', "")
        img_url = f"{IMG_URL_BASE}{img_name}"
        
        try:
            if img_url in self.cache:
                tk_img = self.cache[img_url]
            else:
                response = requests.get(img_url, timeout=2)
                image = Image.open(io.BytesIO(response.content))
                image = image.resize((120, 120))
                tk_img = ImageTk.PhotoImage(image)
                self.cache[img_url] = tk_img
            
            img_label = tk.Label(frame, image=tk_img, bg="#1a1a1a")
            img_label.image = tk_img 
            img_label.pack(pady=(10, 5), padx=10)
        except:
            pass

        name_label = ctk.CTkLabel(frame, text=data.get('name', "Desconhecido"), font=ctk.CTkFont(size=18, weight="bold"))
        name_label.pack(padx=10)

        title_label = ctk.CTkLabel(frame, text=data.get('title', ""), font=ctk.CTkFont(size=14, slant="italic"), text_color="#ffd700")
        title_label.pack(padx=10)

        tags_label = ctk.CTkLabel(frame, text=f"Tags: {data.get('tags', '')}", font=ctk.CTkFont(size=11), text_color="#aaaaaa")
        tags_label.pack(padx=10, pady=5)

        blurb_label = ctk.CTkLabel(frame, text=data.get('blurb', ""), font=ctk.CTkFont(size=11), wraplength=250, justify="left")
        blurb_label.pack(padx=15, pady=(0, 15))

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
        self.champion_data = {} # Cache local de dados dos campeões para o hover

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
        style.map('Treeview', background=[('selected', '#1f538d')])
        
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

        # Binds para o Tooltip
        self.tree.bind("<Motion>", self.on_mouse_move)
        self.tree.bind("<Leave>", lambda e: self.tooltip.hide())

    def on_mouse_move(self, event):
        row_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        # Só mostra se estiver sobre a coluna "Nome" (#1)
        if row_id and column == "#1":
            item = self.tree.item(row_id)
            name = item['values'][0]
            if name in self.champion_data:
                data = self.champion_data[name]
                x = self.winfo_pointerx()
                y = self.winfo_pointery()
                self.tooltip.show(x, y, data)
            else:
                self.tooltip.hide()
        else:
            self.tooltip.hide()

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
