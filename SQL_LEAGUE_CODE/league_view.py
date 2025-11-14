import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path


# Detecta se está rodando como .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys._MEIPASS)
    EXEC_DIR = Path(os.path.dirname(sys.executable))
else:
    ROOT_DIR = Path(__file__).resolve().parent
    EXEC_DIR = ROOT_DIR

DB_FILE = EXEC_DIR / 'db.sqleague'
TABLE_NAME = 'Champions'


class LeagueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("League of Legends - Champions Infos")
        self.geometry("850x500")
        self.configure(bg="#18293B")

        print(f"[DEBUG] Banco de dados procurado em: {DB_FILE}")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self,
            text="Banco de Campeões",
            font=("Arial", 18, "bold"),
            fg="#F2AA4C",
            bg="#18293B"
        )
        title_label.pack(pady=15)

        search_frame = tk.Frame(self, bg="#101820")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Buscar Campeão:", fg="white", bg="#101820").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.search_champion).pack(side=tk.LEFT)

        self.search_entry.bind("<Return>", lambda event: self.search_champion())

        # Criação da Treeview
        self.tree = ttk.Treeview(
            self,
            columns=("name", "title", "tags", "counters", "advantages"),
            show="headings"
        )

        # Cabeçalhos normais
        self.tree.heading("name", text="Nome")
        self.tree.heading("title", text="Título")
        self.tree.heading("tags", text="Funções")

        # Criar quadradinhos coloridos para as colunas
        # Vermelho (counter)
        red_square = tk.PhotoImage(width=10, height=10)
        red_square.put(("red",), to=(0, 0, 10, 10))

        # Verde (advantage)
        green_square = tk.PhotoImage(width=10, height=10)
        green_square.put(("green",), to=(0, 0, 10, 10))

        # Armazena imagens para não perder referência
        self.red_square = red_square
        self.green_square = green_square

        # Cabeçalhos com ícones coloridos
        self.tree.heading("counters", text="  Counters", image=self.red_square, anchor="w")
        self.tree.heading("advantages", text="  Advantages", image=self.green_square, anchor="w")

        # Largura das colunas
        self.tree.column("name", width=90, anchor="w")
        self.tree.column("title", width=180, anchor="w")
        self.tree.column("tags", width=150, anchor="w")
        self.tree.column("counters", width=200, anchor="w")
        self.tree.column("advantages", width=200, anchor="w")

        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        ttk.Button(self, text="Listar Todos", command=self.load_all).pack(pady=5)

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
