import time
import shutil
import os
import sys
import logging
import threading
import customtkinter as ctk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from banco import DatabaseManager

# "C:\Users\Cesar.BLUETI\AppData\Local\Programs\Python\Python314\Scripts\pyinstaller.exe" --noconsole --onefile --icon="icone.ico" --add-data "icone.ico;." --name "Monitoramento" "monitor.py"

def resource_path(relative_path):
    """ Retorna o caminho absoluto para recursos, lidando com PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =========================
# CONFIGURAÇÕES GLOBAIS
# =========================
MOVER_ARQUIVOS = False  # False = Copia (mantém na origem) | True = Move (remove da origem)

# Configurações de Cores Adaptativas
COLORS = {
    "bg_main": ("#f8f9fa", "#1a1c1e"),
    "sidebar": ("#ffffff", "#212529"),
    "accent": ("#0062cc", "#007bff"),
    "text_primary": ("#212529", "#ffffff"),
    "text_secondary": ("#6c757d", "#adb5bd"),
    "card_bg": ("#ffffff", "#2b2f32"),
    "border": ("#dee2e6", "#3f4448"),
}

# =========================
# MONITORAMENTO
# =========================
class MonitorHandler(FileSystemEventHandler):
    def __init__(self, destino, logger_callback, db):
        self.destino = destino
        self.logger_callback = logger_callback
        self.db = db
        os.makedirs(destino, exist_ok=True)

    def processar_arquivo(self, origem_path):
        time.sleep(0.5) # Pequeno delay para garantir que o arquivo/pasta não está bloqueado
        if not os.path.exists(origem_path): return

        # Ignorar pasta infFolha
        if "infFolha" in origem_path:
            return

        nome = os.path.basename(origem_path)
        destino_path = os.path.join(self.destino, nome)
        is_dir = os.path.isdir(origem_path)
        tipo = "📁 PASTA" if is_dir else "📄 ARQUIVO"

        try:
            # Controle de envio via Banco de Dados (apenas para arquivos)
            if not is_dir:
                mtime = os.path.getmtime(origem_path)
                if not self.db.verificar_mudanca(origem_path, mtime):
                    # self.logger_callback(f"⏭ Ignorado (sem alterações): {nome}")
                    return

            # Sempre realizar a operação (Substituir se existir)
            if MOVER_ARQUIVOS:
                if os.path.exists(destino_path):
                    if os.path.isdir(destino_path):
                        shutil.rmtree(destino_path)
                    else:
                        os.remove(destino_path)
                shutil.move(origem_path, destino_path)
                self.logger_callback(f"🚚 Movido {tipo}: {nome}")
            else:
                if is_dir:
                    shutil.copytree(origem_path, destino_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(origem_path, destino_path)
                self.logger_callback(f"📋 Copia {tipo}: {nome}")
            
            # Atualizar banco de dados após sucesso (apenas para arquivos)
            if not is_dir:
                self.db.atualizar_tracking(origem_path, mtime)

        except Exception as e:
            self.logger_callback(f"❌ Erro ao processar {nome}: {str(e)}")

    def on_created(self, event):
        self.processar_arquivo(event.src_path)

    def on_moved(self, event):
        self.processar_arquivo(event.dest_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.processar_arquivo(event.src_path)

class Monitorador:
    def __init__(self, logger_callback):
        self.db = DatabaseManager()
        self.observer = Observer()
        self.logger_callback = logger_callback
        self.running = True

    def iniciar(self):
        self.running = True
        empresas = self.db.listar()
        
        if not empresas:
            self.logger_callback("⚠ Nenhuma empresa encontrada no banco de dados.")
            return

        modo = "MOVIMENTAÇÃO (Recorta da origem)" if MOVER_ARQUIVOS else "CÓPIA (Mantém na origem)"
        self.logger_callback(f"⚙ MODO OPERACIONAL: {modo}")
        self.logger_callback("🔄 Iniciando sincronização inicial...")
        
        for _, nome, origem, destino in empresas:
            if os.path.exists(origem):
                handler = MonitorHandler(destino, self.logger_callback, self.db)
                
                # Sincronização Inicial (Arquivos e Pastas que já existem)
                try:
                    if os.path.exists(origem):
                        itens = os.listdir(origem)
                        for item in itens:
                            handler.processar_arquivo(os.path.join(origem, item))
                except Exception as e:
                    self.logger_callback(f"❌ Erro na varredura de {nome}: {e}")

                # Configurar Observador em tempo real
                self.observer.schedule(handler, origem, recursive=False)
                self.logger_callback(f"🔍 Monitorando em tempo real: {nome}")
            else:
                self.logger_callback(f"⚠ Caminho não encontrado: {origem}")

        self.observer.start()
        self.logger_callback("🚀 SERVIÇO ATIVO E OPERANTE")

        try:
            while self.running:
                time.sleep(1)
        except:
            self.stop()

    def stop(self):
        self.running = False
        self.observer.stop()
        self.observer.join()
        self.logger_callback("🛑 SERVIÇO PARALISADO")

# =========================
# INTERFACE
# =========================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup Janela
        self.title("Monitoramento")
        self.geometry("800x600")
        ctk.set_appearance_mode("system")
        
        self.configure(fg_color=COLORS["bg_main"])
        
        self.monitor = None
        self.running = False

        # Título e Status
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=30, padx=40, fill="x")
        
        self.lbl_title = ctk.CTkLabel(
            self.header, 
            text="MONITORAMENTO", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["accent"]
        )
        self.lbl_title.pack(side="left")
        
        self.status_ball = ctk.CTkLabel(self.header, text="● OFF", text_color="#6c757d", font=ctk.CTkFont(weight="bold"))
        self.status_ball.pack(side="right")

        # Console / Terminal
        self.console_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], border_width=1, border_color=COLORS["border"], corner_radius=15)
        self.console_frame.pack(pady=(0, 20), padx=40, fill="both", expand=True)
        
        self.txt_console = ctk.CTkTextbox(
            self.console_frame, 
            fg_color="transparent", 
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Consolas", size=13),
            padx=20,
            pady=20
        )
        self.txt_console.pack(fill="both", expand=True)
        self.txt_console.configure(state="disabled")

        # Botões de Controle
        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.pack(pady=20, padx=40, fill="x")

        self.btn_run = ctk.CTkButton(
            self.controls, 
            text="INICIAR MONITORAMENTO", 
            height=45, 
            corner_radius=10,
            fg_color=COLORS["accent"],
            font=ctk.CTkFont(weight="bold"),
            command=self.toggle_monitor
        )
        self.btn_run.pack(fill="x")

        self.log_message("Sistema pronto. Clique em 'Iniciar' para monitorar as pastas.")

        # Carregar Ícone
        icon_path = resource_path("icone.ico")
        if os.path.exists(icon_path):
            self.after(200, lambda: self.iconbitmap(icon_path))

    def log_message(self, message):
        self.txt_console.configure(state="normal")
        timestamp = time.strftime("[%H:%M:%S]")
        self.txt_console.insert("end", f"{timestamp} {message}\n")
        self.txt_console.see("end")
        self.txt_console.configure(state="disabled")

    def toggle_monitor(self):
        if not self.running:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        self.running = True
        self.monitor = Monitorador(self.log_message)
        self.thread = threading.Thread(target=self.monitor.iniciar, daemon=True)
        self.thread.start()
        
        self.btn_run.configure(text="PARAR MONITORAMENTO", fg_color="#dc3545", hover_color="#c82333")
        self.status_ball.configure(text="● ACTIVE", text_color="#28a745")
        self.log_message("Preparando observadores...")

    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop()
        self.running = False
        self.btn_run.configure(text="INICIAR MONITORAMENTO", fg_color=COLORS["accent"], hover_color="#0056b3")
        self.status_ball.configure(text="● OFF", text_color="#6c757d")

if __name__ == "__main__":
    app = App()
    app.mainloop()

