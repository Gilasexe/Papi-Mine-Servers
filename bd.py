import sqlite3

def criar_banco():
    try:
        conexao = sqlite3.connect("radar.db")
        cursor = conexao.cursor()
        print("🟢 CONECTADO COM SUCESSO AO SQLITE!")
        
        # A sua query perfeita entra aqui:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_servidores (
                idServidor INTEGER PRIMARY KEY AUTOINCREMENT,
                enderecoServidor TEXT,
                qtdJogadores INT,
                logBotao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conexao.commit()
        print("💾 Tabela verificada/criada com sucesso.")
        
    except Exception as e:
        print(f"🔴 ERRO AO CONECTAR/CRIAR TABELA: {e}")
        
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()
            print("🚪 Conexão fechada.")

if __name__ == "__main__":
    criar_banco()