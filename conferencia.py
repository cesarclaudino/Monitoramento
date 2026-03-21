import os
import sys
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from banco import DatabaseManager

# "C:\Users\Cesar.BLUETI\AppData\Local\Programs\Python\Python314\Scripts\pyinstaller.exe" --noconsole --onefile --icon="icone.ico" --add-data "icone.ico;." --name "Conferencia" "conferencia.py"

def resource_path(relative_path):
    """ Retorna o caminho absoluto para recursos, lidando com PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configurações de Cores Premium (Consistente com os outros apps)
COLORS = {
    "bg_main": ("#f1f5f9", "#111111"),
    "sidebar": ("#ffffff", "#1e1e1e"),
    "accent": ("#0061ff", "#0ea5e9"),
    "danger": ("#ef4444", "#f43f5e"),
    "text_primary": ("#0f172a", "#f8fafc"),
    "text_secondary": ("#64748b", "#94a3b8"),
    "card_bg": ("#ffffff", "#1e1e1e"),
    "border": ("#e2e8f0", "#2d3748"),
    "hover": ("#f8fafc", "#2d3748")
}

class TrackingCard(ctk.CTkFrame):
    def __init__(self, master, caminho, modificado, processado, on_select_change, **kwargs):
        super().__init__(master, fg_color=COLORS["card_bg"], corner_radius=12, border_width=1, border_color=COLORS["border"], **kwargs)
        
        self.caminho = caminho
        self.on_select_change = on_select_change
        
        # Checkbox para seleção
        self.check_var = ctk.StringVar(value="off")
        self.checkbox = ctk.CTkCheckBox(
            self, 
            text="", 
            variable=self.check_var, 
            onvalue="on", 
            offvalue="off",
            width=20,
            command=self.on_select_change
        )
        self.checkbox.pack(side="left", padx=(15, 5))
        
        # Informações
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        nome_arquivo = os.path.basename(caminho)
        pasta_pai = os.path.dirname(caminho)
        
        self.lbl_nome = ctk.CTkLabel(info_frame, text=nome_arquivo, font=ctk.CTkFont(weight="bold", size=14), text_color=COLORS["text_primary"])
        self.lbl_nome.pack(anchor="w")
        
        self.lbl_path = ctk.CTkLabel(info_frame, text=pasta_pai, font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"])
        self.lbl_path.pack(anchor="w")
        
        # Datas (Direita)
        dates_frame = ctk.CTkFrame(self, fg_color="transparent")
        dates_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(dates_frame, text=f"Modificado: {modificado}", font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"]).pack(anchor="e")
        ctk.CTkLabel(dates_frame, text=f"Sincronizado: {processado}", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["accent"]).pack(anchor="e")

    def is_selected(self):
        return self.check_var.get() == "on"
    
    def set_selected(self, selected):
        self.check_var.set("on" if selected else "off")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.cards = []

        # Configurações da Janela
        self.title("Conferência de Sincronização")
        self.geometry("900x700")
        ctk.set_appearance_mode("system")
        self.configure(fg_color=COLORS["bg_main"])

        # Layout Principal
        self.setup_ui()
        self.after(200, self.carregar_dados)
        
        # Carregar Ícone
        icon_path = resource_path("icone.ico")
        if os.path.exists(icon_path):
            self.after(200, lambda: self.iconbitmap(icon_path))

    def setup_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=(40, 20), padx=40, fill="x")
        
        self.lbl_title = ctk.CTkLabel(
            self.header, 
            text="CONFERÊNCIA", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent"]
        )
        self.lbl_title.pack(side="left")

        # Filtros (Lado Direito)
        filter_container = ctk.CTkFrame(self.header, fg_color="transparent")
        filter_container.pack(side="right")

        # Período (Data Inicial e Final)
        ctk.CTkLabel(filter_container, text="De:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(10, 2))
        self.entry_dt_ini = DateEntry(filter_container, width=15, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 12))
        self.entry_dt_ini.pack(side="left", padx=10, pady=10)
        self.entry_dt_ini.bind("<<DateEntrySelected>>", lambda e: self.filtrar())

        ctk.CTkLabel(filter_container, text="Até:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(10, 2))
        self.entry_dt_fim = DateEntry(filter_container, width=15, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Segoe UI", 12))
        self.entry_dt_fim.pack(side="left", padx=10, pady=10)
        self.entry_dt_fim.bind("<<DateEntrySelected>>", lambda e: self.filtrar())

        # Busca por Nome
        self.entry_busca = ctk.CTkEntry(
            filter_container, 
            placeholder_text="Pesquisar por nome...", 
            width=230, 
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        self.entry_busca.pack(side="left", padx=(25, 5))
        self.entry_busca.bind("<KeyRelease>", lambda e: self.filtrar())

        # Container da Lista
        self.list_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            label_text=None
        )
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Barra de Ações (Inferior)
        self.actions_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], height=80, corner_radius=0)
        self.actions_bar.pack(fill="x", side="bottom")
        
        self.btn_select_all = ctk.CTkCheckBox(
            self.actions_bar, 
            text="Selecionar Todos", 
            command=self.toggle_select_all,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_select_all.pack(side="left", padx=40, pady=25)
        
        self.btn_delete = ctk.CTkButton(
            self.actions_bar, 
            text="EXCLUIR SELECIONADOS", 
            fg_color=COLORS["danger"],
            hover_color=("#dc2626", "#991b1b"),
            font=ctk.CTkFont(weight="bold"),
            height=40,
            command=self.confirmar_exclusao
        )
        self.btn_delete.pack(side="right", padx=40, pady=20)
        
        self.lbl_count = ctk.CTkLabel(self.actions_bar, text="0 arquivos selecionados", text_color=COLORS["text_secondary"])
        self.lbl_count.pack(side="right", padx=20)

    def carregar_dados(self):
        # Limpar cards atuais
        for card in self.cards:
            card.destroy()
        self.cards = []
        
        tracking = self.db.listar_tracking()
        for caminho, modif, proc in tracking:
            card = TrackingCard(self.list_frame, caminho, modif, proc, self.update_count)
            card.processado = proc # Armazenar para filtro fácil
            card.pack(fill="x", pady=5, padx=10)
            self.cards.append(card)
        
        self.update_count()

    def filtrar(self):
        termo_nome = self.entry_busca.get().lower()
        dt_ini = self.entry_dt_ini.get_date() # Retorna objeto datetime.date
        dt_fim = self.entry_dt_fim.get_date() # Retorna objeto datetime.date
        
        # Formatar para string YYYY-MM-DD para comparação com o banco
        str_ini = dt_ini.strftime("%Y-%m-%d")
        str_fim = dt_fim.strftime("%Y-%m-%d")
        
        for card in self.cards:
            match_nome = termo_nome in card.caminho.lower()
            
            # Data do arquivo: YYYY-MM-DD (prefixo do processado)
            data_file = card.processado.split(" ")[0]
            
            # Filtro por Período
            match_data = (str_ini <= data_file <= str_fim)
            
            if match_nome and match_data:
                card.pack(fill="x", pady=5, padx=10)
            else:
                card.pack_forget()

    def update_count(self):
        selecionados = [c for c in self.cards if c.is_selected()]
        count = len(selecionados)
        self.lbl_count.configure(text=f"{count} arquivos selecionados")
        
        if count > 0:
            self.btn_delete.configure(state="normal")
        else:
            self.btn_delete.configure(state="disabled")

    def toggle_select_all(self):
        val = self.btn_select_all.get()
        for card in self.cards:
            # Apenas aplicar aos visíveis (filtrados)
            if card.winfo_ismapped():
                card.set_selected(val)
        self.update_count()

    def confirmar_exclusao(self):
        selecionados = [c for c in self.cards if c.is_selected() and c.winfo_ismapped()]
        if not selecionados:
            return
            
        count = len(selecionados)
        msg = f"Você tem certeza que deseja excluir o registro de {count} arquivo(s)?\n\nIsso fará com que o monitor envie esses arquivos novamente se eles ainda existirem na origem."
        
        if messagebox.askyesno("Confirmar Exclusão", msg):
            caminhos = [c.caminho for c in selecionados]
            try:
                self.db.excluir_tracking_multiplo(caminhos)
                messagebox.showinfo("Sucesso", f"{count} registros excluídos com sucesso.")
                self.carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir registros: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
