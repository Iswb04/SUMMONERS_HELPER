import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sqlite3
from pathlib import Path

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

class LeagueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Informações de Campeões")
        self.geometry("850x550")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        print(f"[DEBUG] Banco de dados procurado em: {DB_FILE}")

        self.create_widgets()
        self.load_all()

    def create_widgets(self):
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text="SUMMONERS HELPER",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10))

        # Frame de Busca
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)

        self.search_label = ctk.CTkLabel(self.search_frame, text="Buscar Campeão:")
        self.search_label.grid(row=0, column=0, padx=(15, 5), pady=10)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Digite o nome...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.search_champion())

        self.search_button = ctk.CTkButton(self.search_frame, text="Buscar", command=self.search_champion)
        self.search_button.grid(row=0, column=2, padx=(5, 15), pady=10)

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
        
        # Esconder COMPLETAMENTE os cabeçalhos originais da Treeview para não ocuparem espaço
        style.layout("Treeview.Heading", []) 

        # Frame para os Cabeçalhos Customizados
        self.header_frame = ctk.CTkFrame(self, fg_color="#333333", height=30, corner_radius=0)
        self.header_frame.grid(row=2, column=0, padx=(20, 36), pady=(10, 0), sticky="ew") 
        
        # Definição das larguras das colunas
        col_widths = [90, 180, 120, 210, 210]
        
        # Nome
        ctk.CTkLabel(self.header_frame, text="Nome", width=90, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(5,0))
        # Título
        ctk.CTkLabel(self.header_frame, text="Título", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
        # Categorias
        ctk.CTkLabel(self.header_frame, text="Categorias", width=120, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)
        # Desvantagem (Vermelho)
        ctk.CTkLabel(self.header_frame, text="■ Desvantagem", width=210, anchor="w", 
                     text_color="#ff4d4d", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3)
        # Vantagem (Verde)
        ctk.CTkLabel(self.header_frame, text="■ Vantagem", width=210, anchor="w", 
                     text_color="#2ecc71", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4)

        # Container para Treeview e Scrollbar
        self.tree_frame = ctk.CTkFrame(self, corner_radius=0)
        self.tree_frame.grid(row=3, column=0, padx=(20, 20), pady=(0, 10), sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("name", "title", "tags", "counters", "advantages"),
            show="headings", # Mantemos headings mas o estilo remove o desenho deles
            style="Treeview"
        )

        # Cabeçalhos invisíveis (apenas para definir colunas)
        for col in ("name", "title", "tags", "counters", "advantages"):
            self.tree.heading(col, text="")

        self.tree.column("name", width=90, anchor="w")
        self.tree.column("title", width=180, anchor="w")
        self.tree.column("tags", width=120, anchor="w")
        self.tree.column("counters", width=210, anchor="w")
        self.tree.column("advantages", width=210, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ctk.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Botão Listar Todos
        self.list_all_button = ctk.CTkButton(self, text="Voltar", command=self.load_all)
        self.list_all_button.grid(row=4, column=0, pady=(10, 20))

    def search_champion(self):
        name = self.search_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Digite o nome de um campeão para buscar.")
            return

        if not DB_FILE.exists():
            messagebox.showerror("Erro", f"Banco de dados não encontrado em:\n{DB_FILE}")
            return

        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        try:
            cursor.execute(
                f"SELECT name, title, tags, counters, advantages FROM {TABLE_NAME} WHERE name LIKE ?",
                (f"%{name}%",)
            )
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Erro no Banco", f"Ocorreu um erro:\n{e}")
            connection.close()
            return

        connection.close()
        self.tree.delete(*self.tree.get_children())

        if rows:
            for r in rows:
                self.tree.insert("", tk.END, values=r)
        else:
            messagebox.showinfo("Resultado", "Nenhum campeão encontrado.")

    def load_all(self):
        if not DB_FILE.exists():
            messagebox.showerror("Erro", f"Banco de dados não encontrado em:\n{DB_FILE}")
            return

        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT name, title, tags, counters, advantages FROM {TABLE_NAME}")
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Erro no Banco", f"Ocorreu um erro:\n{e}")
            connection.close()
            return

        connection.close()
        self.tree.delete(*self.tree.get_children())

        for r in rows:
            self.tree.insert("", tk.END, values=r)

if __name__ == "__main__":
    app = LeagueApp()
    app.mainloop()
