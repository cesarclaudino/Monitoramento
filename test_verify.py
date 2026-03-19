import sys
import os
import time
import shutil
from banco import DatabaseManager
from monitor import MonitorHandler

# Configurar saída para suportar emojis
sys.stdout.reconfigure(encoding='utf-8')

def test_monitoring():
    db = DatabaseManager("test_empresas.db")
    
    try:
        # Setup test folders
        test_origem = "test_origem"
        test_destino = "test_destino"
        os.makedirs(test_origem, exist_ok=True)
        os.makedirs(test_destino, exist_ok=True)
        
        # Test folder infFolha (should be ignored)
        inf_folha_path = os.path.join(test_origem, "infFolha")
        os.makedirs(inf_folha_path, exist_ok=True)
        with open(os.path.join(inf_folha_path, "test.txt"), "w") as f:
            f.write("test")
            
        # Test normal file
        normal_file = os.path.abspath(os.path.join(test_origem, "normal.txt"))
        with open(normal_file, "w") as f:
            f.write("content v1")
            
        def mock_logger(msg):
            print(f"LOG: {msg}")
            
        handler = MonitorHandler(test_destino, mock_logger, db)
        
        print(f"--- First process (new file: {os.path.basename(normal_file)}) ---")
        handler.processar_arquivo(normal_file)
        
        print("--- Process again (no change) ---")
        # Should NOT log anything if skipped
        handler.processar_arquivo(normal_file)
        
        print("--- Modify file and process ---")
        time.sleep(1.1) # Ensure mtime changes
        with open(normal_file, "w") as f:
            f.write("content v2")
        handler.processar_arquivo(normal_file)
        
        print("--- Process folder infFolha (should be ignored silently) ---")
        handler.processar_arquivo(inf_folha_path)
        
    finally:
        # Cleanup
        if os.path.exists(test_origem):
            shutil.rmtree(test_origem)
        if os.path.exists(test_destino):
            shutil.rmtree(test_destino)
        # We don't have a close method on DatabaseManager, but the connections are closed after each 'with self._get_connection()'
        # However, sqlite might still hold the file for a bit.
        time.sleep(1)
        if os.path.exists("test_empresas.db"):
            try:
                os.remove("test_empresas.db")
            except:
                print("Note: Could not delete test_empresas.db")

if __name__ == "__main__":
    test_monitoring()

if __name__ == "__main__":
    test_monitoring()
