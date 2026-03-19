import os
import sys
import customtkinter as ctk
from tkinter import messagebox, filedialog
from banco import DatabaseManager

# "C:\Users\Cesar.BLUETI\AppData\Local\Programs\Python\Python314\Scripts\pyinstaller.exe" --noconsole --onefile --icon="icone.ico" --add-data "icone.ico;." --name "Cadastro" "Cadastro.py"

def resource_path(relative_path):
    """ Retorna o caminho absoluto para recursos, lidando com PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configurações de Cores Premium (Adaptativas)
COLORS = {
    "bg_main": ("#f1f5f9", "#111111"),      # Fundo levemente acinzentado para destacar cards
    "sidebar": ("#ffffff", "#1e1e1e"),      # Sidebar sólida
    "accent": ("#0061ff", "#0ea5e9"),       # Azul moderno vívido
    "success": ("#10b981", "#22c55e"),      # Esmeralda / Verde
    "danger": ("#ef4444", "#f43f5e"),       # Rose / Vermelho
    "text_primary": ("#0f172a", "#f8fafc"), # Azul escuro profundo / Branco suave
    "text_secondary": ("#64748b", "#94a3b8"),# Cinza médio sofisticado
    "card_bg": ("#ffffff", "#1e1e1e"),      # Branco puro / Preto suave
    "border": ("#e2e8f0", "#2d3748"),       # Bordas sutis
    "hover": ("#f8fafc", "#2d3748")         # Hover delicado
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.selected_id = None

        # Configurações da Janela
        self.title("Cadastro")
        self.geometry("1050x650")
        ctk.set_appearance_mode("system")
        
        # Grid System
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # BARRA LATERAL (Sidebar)
        self.sidebar = ctk.CTkFrame(
            self, 
            width=320, 
            corner_radius=0, 
            fg_color=COLORS["sidebar"], 
            border_width=1, 
            border_color=COLORS["border"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.setup_sidebar()

        # CONTEÚDO PRINCIPAL (Main Content)
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_main"])
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        self.setup_main_content()
        self.carregar_lista()
        
        # Carregar Ícone
        icon_path = resource_path("icone.ico")
        if os.path.exists(icon_path):
            self.after(200, lambda: self.iconbitmap(icon_path))

    def setup_sidebar(self):
        # Logo / Título
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(60, 40), padx=30, fill="x")

        self.title_label = ctk.CTkLabel(
            logo_frame, 
            text="CADASTRO", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=COLORS["accent"]
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.subtitle_label = ctk.CTkLabel(
            logo_frame, 
            text="Gestão de Sincronização", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w")

        # Formulário (Agrupado em um frame)
        form_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        form_frame.pack(fill="x", padx=10)

        self.create_input_field(form_frame, "ENTIDADE / EMPRESA", "entry_nome", "Ex: Nome Fantasia")
        self.create_input_with_picker(form_frame, "DIRETÓRIO ORIGEM", "entry_origem")
        self.create_input_with_picker(form_frame, "DIRETÓRIO DESTINO", "entry_destino")

        # Botões de Ação
        self.btn_salvar = ctk.CTkButton(
            self.sidebar, 
            text="SALVAR", 
            command=self.salvar, 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLORS["accent"], 
            hover_color=("#0051d4", "#0284c7"),
            height=50,
            corner_radius=12
        )
        self.btn_salvar.pack(pady=(50, 10), padx=30, fill="x")

        self.btn_limpar = ctk.CTkButton(
            self.sidebar, 
            text="+ Nova Empresa", 
            command=self.limpar, 
            fg_color="transparent", 
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["hover"],
            height=42,
            corner_radius=12
        )
        self.btn_limpar.pack(pady=5, padx=30, fill="x")

    def create_input_field(self, parent, label, attr_name, placeholder):
        lbl = ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"])
        lbl.pack(anchor="w", padx=30, pady=(20, 0))
        entry = ctk.CTkEntry(
            parent, 
            placeholder_text=placeholder, 
            height=42, 
            fg_color=COLORS["bg_main"], 
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        entry.pack(fill="x", padx=20, pady=(5, 5))
        setattr(self, attr_name, entry)

    def create_input_with_picker(self, parent, label, attr_name):
        lbl = ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["text_secondary"])
        lbl.pack(anchor="w", padx=30, pady=(20, 0))
        
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(5, 5))
        
        entry = ctk.CTkEntry(
            frame, 
            placeholder_text="Selecione o caminho...", 
            height=42, 
            fg_color=COLORS["bg_main"], 
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=10,
            font=ctk.CTkFont(size=12)
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn = ctk.CTkButton(
            frame, 
            text="📁", 
            width=45, 
            height=42, 
            fg_color=COLORS["bg_main"], 
            text_color=COLORS["accent"], 
            border_width=1, 
            border_color=COLORS["border"], 
            hover_color=COLORS["hover"], 
            corner_radius=10,
            command=lambda: self.browse_folder(entry)
        )
        btn.pack(side="right")
        setattr(self, attr_name, entry)

    def setup_main_content(self):
        # Header Lado Direito (Navegação/Busca)
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=50, pady=(50, 30), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(
            header_frame, 
            text="Pastas Monitoradas", 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.header_label.grid(row=0, column=0, sticky="w")

        # Filtro de Busca Premium
        search_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_container.grid(row=0, column=1, sticky="e")

        self.entry_busca = ctk.CTkEntry(
            search_container, 
            placeholder_text="Pesquisar por nome...", 
            width=320, 
            height=45,
            fg_color=COLORS["sidebar"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=22,
            font=ctk.CTkFont(size=13)
        )
        self.entry_busca.pack(side="right")
        self.entry_busca.bind("<KeyRelease>", lambda e: self.carregar_lista())

        # Container da Lista (Scrollable)
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.main_container, 
            fg_color="transparent",
            label_text=None,
            scrollbar_button_color=COLORS["border"]
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=35, pady=(0, 40))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def browse_folder(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, 'end')
            entry.insert(0, folder)

    def carregar_lista(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        filtro = self.entry_busca.get().lower()
        empresas = self.db.listar()
        
        if not empresas:
            ctk.CTkLabel(self.scrollable_frame, text="Nenhuma empresa cadastrada.", font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"]).pack(pady=50)
            return

        for emp in empresas:
            if filtro in emp[1].lower():
                self.create_card(emp)

    def create_card(self, emp):
        # Card Elevado
        card = ctk.CTkFrame(
            self.scrollable_frame, 
            fg_color=COLORS["card_bg"], 
            height=130, 
            corner_radius=18,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=12, padx=15)
        card.grid_columnconfigure(0, weight=1)

        # Informações (Esquerda)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, padx=30, pady=25)

        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(anchor="w", fill="x")

        nome_lbl = ctk.CTkLabel(
            title_frame, 
            text=emp[1].upper(), 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
            text_color=COLORS["text_primary"]
        )
        nome_lbl.pack(side="left")

        # Badge de ID ou Status (Opcional)
        id_badge = ctk.CTkLabel(
            title_frame, 
            text=f" #ID {emp[0]} ", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["bg_main"],
            corner_radius=6
        )
        id_badge.pack(side="left", padx=15)

        # Caminhos com design melhor
        paths_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        paths_frame.pack(anchor="w", pady=(12, 0))

        origem_lbl = ctk.CTkLabel(
            paths_frame, 
            text=f"ORIGEM: {emp[2]}", 
            font=ctk.CTkFont(size=12), 
            text_color=COLORS["text_secondary"]
        )
        origem_lbl.pack(anchor="w")

        destino_lbl = ctk.CTkLabel(
            paths_frame, 
            text=f"DESTINO: {emp[3]}", 
            font=ctk.CTkFont(size=12), 
            text_color=COLORS["text_secondary"]
        )
        destino_lbl.pack(anchor="w")

        # Ações (Direita)
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=30)

        btn_edit = ctk.CTkButton(
            actions_frame, 
            text="Alterar", 
            width=110, 
            height=34, 
            fg_color=COLORS["bg_main"], 
            border_width=1, 
            border_color=COLORS["accent"],
            text_color=COLORS["accent"],
            hover_color=COLORS["hover"],
            corner_radius=10,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda e=emp: self.selecionar(e)
        )
        btn_edit.pack(pady=4)

        btn_del = ctk.CTkButton(
            actions_frame, 
            text="Excluir", 
            width=110, 
            height=34, 
            fg_color="transparent", 
            text_color=COLORS["danger"],
            hover_color=("#fff1f2", "#4c0519"), # Vermelho ultra suave no hover
            corner_radius=10,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda id_emp=emp[0]: self.deletar(id_emp)
        )
        btn_del.pack(pady=4)

    def salvar(self):
        nome = self.entry_nome.get().strip()
        origem = self.entry_origem.get().strip()
        destino = self.entry_destino.get().strip()

        if not nome or not origem or not destino:
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.")
            return

        if self.selected_id:
            self.db.atualizar(self.selected_id, nome, origem, destino)
            messagebox.showinfo("Dashboard", f"Configuração de '{nome}' atualizada.")
        else:
            self.db.inserir(nome, origem, destino)
            messagebox.showinfo("Dashboard", f"'{nome}' agora está integrada ao sistema.")

        self.limpar()
        self.carregar_lista()

    def selecionar(self, emp):
        self.selected_id = emp[0]
        self.entry_nome.delete(0, 'end')
        self.entry_nome.insert(0, emp[1])
        self.entry_origem.delete(0, 'end')
        self.entry_origem.insert(0, emp[2])
        self.entry_destino.delete(0, 'end')
        self.entry_destino.insert(0, emp[3])
        self.btn_salvar.configure(text="ATUALIZAR CONFIGURAÇÃO", fg_color=COLORS["success"])

    def limpar(self):
        self.selected_id = None
        self.entry_nome.delete(0, 'end')
        self.entry_origem.delete(0, 'end')
        self.entry_destino.delete(0, 'end')
        self.btn_salvar.configure(text="SALVAR CONFIGURAÇÃO", fg_color=COLORS["accent"])

    def deletar(self, id_empresa=None):
        target_id = id_empresa if id_empresa else self.selected_id
        if not target_id: return

        if messagebox.askyesno("Confirmar Exclusão", "Deseja remover esta empresa do monitoramento permanentemente?"):
            self.db.excluir(target_id)
            if target_id == self.selected_id: self.limpar()
            self.carregar_lista()

if __name__ == "__main__":
    app = App()
    app.mainloop()




