import sqlite3
import time
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_name: str = "empresas.db"):
        self.db_name = db_name
        self.criar_tabela()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def criar_tabela(self) -> None:
        """Cria a tabela de empresas se não existir."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                origem TEXT NOT NULL,
                destino TEXT NOT NULL
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS arquivo_tracking (
                caminho_arquivo TEXT PRIMARY KEY,
                last_modified TEXT NOT NULL,
                data_processamento TEXT
            )
            """)
            
            # Migração: Adicionar coluna data_processamento se não existir
            cursor.execute("PRAGMA table_info(arquivo_tracking)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'data_processamento' not in columns:
                cursor.execute("ALTER TABLE arquivo_tracking ADD COLUMN data_processamento TEXT")
                
            conn.commit()

    def inserir(self, nome: str, origem: str, destino: str) -> None:
        """Insere uma nova empresa no banco de dados."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO empresas (nome, origem, destino) VALUES (?, ?, ?)",
                (nome, origem, destino)
            )
            conn.commit()

    def listar(self) -> List[Tuple]:
        """Retorna todas as empresas cadastradas."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empresas")
            return cursor.fetchall()

    def atualizar(self, id_empresa: int, nome: str, origem: str, destino: str) -> None:
        """Atualiza os dados de uma empresa existente."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE empresas 
                SET nome=?, origem=?, destino=? 
                WHERE id=?
            """, (nome, origem, destino, id_empresa))
            conn.commit()

    def excluir(self, id_empresa: int) -> None:
        """Exclui uma empresa do banco de dados."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM empresas WHERE id=?", (id_empresa,))
            conn.commit()

    def verificar_mudanca(self, caminho_arquivo: str, current_mtime: float) -> bool:
        """Verifica se o arquivo foi alterado desde o último envio."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT last_modified FROM arquivo_tracking WHERE caminho_arquivo = ?",
                (caminho_arquivo,)
            )
            result = cursor.fetchone()
            if result is None:
                return True  # Novo arquivo
            
            stored_mtime_str = result[0]
            current_mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_mtime))
            
            # Comparação de strings funciona bem se o formato for YYYY-MM-DD HH:MM:SS
            return current_mtime_str > stored_mtime_str

    def atualizar_tracking(self, caminho_arquivo: str, current_mtime: float) -> None:
        """Atualiza a data de modificação e processamento de um arquivo no banco de dados."""
        mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_mtime))
        # Data e hora atual da sincronização
        processamento_str = time.strftime('%Y-%m-%d %H:%M:%S')
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO arquivo_tracking (caminho_arquivo, last_modified, data_processamento)
                VALUES (?, ?, ?)
                ON CONFLICT(caminho_arquivo) DO UPDATE SET 
                    last_modified = excluded.last_modified,
                    data_processamento = excluded.data_processamento
            """, (caminho_arquivo, mtime_str, processamento_str))
            conn.commit()

    def listar_tracking(self) -> List[Tuple]:
        """Retorna todos os registros de tracking."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT caminho_arquivo, last_modified, data_processamento FROM arquivo_tracking ORDER BY data_processamento DESC")
            return cursor.fetchall()

    def excluir_tracking_multiplo(self, caminhos: List[str]) -> None:
        """Exclui múltiplos registros de tracking."""
        if not caminhos:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # SQLite handles lists via IN (...)
            placeholders = ', '.join(['?'] * len(caminhos))
            cursor.execute(f"DELETE FROM arquivo_tracking WHERE caminho_arquivo IN ({placeholders})", caminhos)
            conn.commit()

