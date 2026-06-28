import psycopg2
import streamlit as st
import hashlib

# 1. CRIAMOS UMA PONTE (Função construtora)
def conectar():
    return psycopg2.connect(st.secrets["DATABASE_URL"])


def criar_banco():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        print("🟢 CONECTADO COM SUCESSO AO POSTGRESQL (SUPABASE)!")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE historico_servidores (
                idServidor SERIAL PRIMARY KEY,
                usuario_id INT REFERENCES usuarios(id),
                enderecoServidor TEXT,
                qtdJogadores INT,
                logBotao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conexao.commit()
        print("💾 Tabelas de usuários e servidores criadas e amarradas com sucesso!")

    except Exception as e:
        print(f"🔴 ERRO NO SUPABASE: {e}")

    finally:
        if "conexao" in locals() and conexao:
            conexao.close()
            print("🚪 Conexão fechada.")


def criar_usuario(usuario, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    # Transforma a senha "123" em um código maluco e indecifrável
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)", (usuario, senha_hash))
        conexao.commit()
        return True # Deu certo, conta criada
    except psycopg2.errors.UniqueViolation:
        return False # Deu erro, o usuário já existe
    finally:
        conexao.close()

def verificar_login(usuario, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    cursor.execute("SELECT id FROM usuarios WHERE usuario = %s AND senha = %s", (usuario, senha_hash))
    resultado = cursor.fetchone()
    conexao.close()
    
    if resultado:
        return resultado[0] # Retorna o ID numérico do usuário
    return None # Login falhou


if __name__ == "__main__":
    criar_banco()