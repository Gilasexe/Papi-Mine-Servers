import streamlit as st
import requests
import sqlite3
import pandas as pd
from bd import *

# 1. Deixa a página mais larga para caberem as colunas
st.set_page_config(page_title="Radar Minecraft", layout="wide", page_icon="logo.png")

# Finge que são as horas do dia
historico_24h = [120, 135, 150, 180, 200, 210, 190, 160, 140, 130, 110, 100] 
# Finge que são os dias da semana
historico_7d = [1500, 1650, 1400, 1800, 2200, 2500, 1900]

meu_estilo_retro = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* Isso aqui muda o fundo da tela inteira (o app do Streamlit) */
    .stApp {
        background-color: #0a0a0a;
    }

    [data-testid="stAlertContentError"] [data-testid="stMarkdownContainer"] > p {
        color: #ffffff !important;}

    /* Substituímos o * por alvos específicos para não quebrar os ícones do Streamlit */
    h1, h2, h3, p, button, input, label, li {
        color: #00ff00 !important;
        font-family: 'VT323', monospace !important;
    }
</style>
"""

st.markdown(meu_estilo_retro, unsafe_allow_html=True)

st.title("📡 Central de Monitoramento", text_alignment="center")
if st.button("Criar DataBase local para servidores favoritos.", key=f"criardb"):
    if "radar.db" in locals():
        st.write("Voce ja tem o banco de dados local criado.")
    else:
        criar_banco()

st.markdown("---") # Cria uma linha divisória charmosa

# ==========================================
# SEÇÃO 1: SERVIDORES FIXOS (CARREGAM SOZINHOS)
# ==========================================
st.subheader("🌐 Servidores em Destaque")

# Uma lista com alguns IPs para testar
servidores_fixos = ["mc.hypixel.net", "jogar.mush.com.br", "org.mc-complex.com"]

# Criamos uma coluna para cada servidor da lista
colunas = st.columns(len(servidores_fixos))

# O loop 'for' passa por cada IP e usa a coluna certa (usando o enumerate)
for index, ip in enumerate(servidores_fixos):
    url = f"https://api.mcsrvstat.us/2/{ip}"
    
    # O comando 'with' diz para o Streamlit desenhar as coisas dentro daquela coluna específica
    with colunas[index]:
        st.markdown(f"### 🖥️ `{ip}`")
        st.button("Atualizar Status", icon="🔄", key=f"refresh_{ip}")
        
        
        # Fazemos o pedido. Adicionei um timeout para a página não travar se o servidor estiver lento
        try:
            resposta = requests.get(url, timeout=7)
            dados = resposta.json()
            
            if dados.get("online"):
                jogadores_online = dados["players"]["online"]
                jogadores_max = dados["players"]["max"]
                versao = dados.get("version", "Desconhecida")
                
                st.success("STATUS: ONLINE 🟢", width=200)
                # O st.metric cria um destaque visual bem legal para os números
                st.metric(label="Jogadores Ativos", value=jogadores_online, delta=f"Max: {jogadores_max}", delta_color="off")
                st.caption(f"🏷️ Versão: {versao}")
            else:
                st.error("STATUS: OFFLINE 🔴", width=200)
                st.caption("Servidor inacessível no momento.")
        except:
            st.error("Erro na conexão ⚠️", width=200)

st.markdown("---")

# ==========================================
# SEÇÃO 2: A SUA BUSCA MANUAL
# ==========================================
st.subheader("🔍 Investigar Outro Servidor")

ip_busca = st.text_input("Digite um IP para verificar:", "play.exemplo.com", width=350)

if st.button("Buscar Servidor"):
    url_busca = f"https://api.mcsrvstat.us/2/{ip_busca}"
    resposta_busca = requests.get(url_busca)
    
    # Em vez de desenhar a tela aqui, guardamos o JSON inteiro e o IP na mochila
    st.session_state['dados_da_busca'] = resposta_busca.json()
    st.session_state['ip_pesquisado'] = ip_busca

if 'dados_da_busca' in st.session_state:
    # "Tiramos" os dados da mochila para variáveis normais para facilitar
    dados_busca = st.session_state['dados_da_busca']
    ip_atual = st.session_state['ip_pesquisado']
    if dados_busca.get("online"):
        jogadores_online = dados_busca["players"]["online"]
        jogadores_max = dados_busca["players"]["max"]
        versao = dados_busca.get("version", "Desconhecida")
        motd = dados_busca["motd"]["clean"][0] if "motd" in dados_busca else "Sem mensagem"
        st.success("🟢 Este servidor está online!", width=200)
        st.write(f"🎮 Jogadores: {jogadores_online} / {jogadores_max}")
        st.write(f"🏷️ Versão: {versao}")
        st.write(f"📝 Mensagem: {motd}")

        escolha = st.radio("Selecione o período:", ["24 Horas", "7 Dias"])
        
        if escolha == "24 Horas":
            # Hackeando a ordem com 01, 02, 03...
            tabela_24h = pd.DataFrame(
                {"Jogadores Ativos": historico_24h},
                index=["01 - 12:00", "02 - 14:00", "03 - 16:00", "04 - 18:00", "05 - 20:00", "06 - 22:00", "07 - 00:00", "08 - 02:00", "09 - 04:00", "10 - 06:00", "11 - 08:00", "12 - 10:00"]
            )
            tabela_24h.index.name = "Horário"
            
            st.line_chart(tabela_24h)
            
        else:
            # Hackeando a ordem dos dias com 1, 2, 3...
            tabela_7d = pd.DataFrame(
                {"Jogadores Ativos": historico_7d},
                index=["1 - Seg", "2 - Ter", "3 - Qua", "4 - Qui", "5 - Sex", "6 - Sáb", "7 - Dom"]
            )
            tabela_7d.index.name = "Dia da Semana"
            
            st.line_chart(tabela_7d)

        st.write("este grafico é meramente ilustrativo, apenas para estudo.")
        if st.button("⭐ - Favoritar Servidor", key="salvar_historico"):
            try:
                conexaoFavoritar = sqlite3.connect("radar.db")
                cursorFavoritar = conexaoFavoritar.cursor()
                print("CONECTADO COM SUCESSO AO SQLITE!")

                cursorFavoritar.execute("""
                               insert into historico_servidores (enderecoServidor, qtdJogadores)
                               values (?,?)
                               """, (st.session_state['ip_pesquisado'], jogadores_online))
                conexaoFavoritar.commit()
                print("Servidor salvo no sistema.")

            except Exception as e:
                print(f"Erro ao salvar servidor: {e}")
            
            finally:
                if 'conexaoFavoritar' in locals() and conexaoFavoritar:
                    conexaoFavoritar.close()
                    print("conexao fechada.")
    else:
        st.error("🔴 Este servidor está offline!", width=200)
        st.write("O servidor está desligado ou o IP está incorreto.")

# ===================================
# SEÇÃO 3: A LISTA DE FAVORITOS
# ===================================

# aqui iremos fazer a parte da lista de favoritos

st.markdown("---")

st.title("⭐ Lista de Favoritos", text_alignment="left")

try:
    conexaoFavoritos = sqlite3.connect("radar.db")
    cursorFavoritos = conexaoFavoritos.cursor()
    print("CONECTADO COM SUCESSO AO SQLITE!")
    cursorFavoritos.execute("""
                            SELECT DISTINCT enderecoServidor
                            FROM historico_servidores""")
    resultado_sujo = cursorFavoritos.fetchall()
    print("Visualização de lista criada.")
except Exception as e:
    print(f"Ocorreu um erro ao visualizar favoritos: {e}")

finally:
    if 'conexaoFavoritos' in locals() and conexaoFavoritos:
        conexaoFavoritos.close()
        print("conexao fechada")

sua_lista_limpa = []

for ip_sujo in resultado_sujo:
    sua_lista_limpa.append(ip_sujo[0])

with st.expander("Clique aqui para abrir seus Favoritos", expanded=False):
    if len(sua_lista_limpa) > 0:
        for index, ip in enumerate(sua_lista_limpa):
            urlFavoritos = f"https://api.mcsrvstat.us/2/{ip}"
            st.markdown(f"### 🖥️ `{ip}`")
            st.button("Atualizar Status", icon="🔄", key=f"refresh_lista_limpa_{ip}")
            # O type="primary" deixa o botão em destaque (geralmente vermelho/cor principal dependendo do tema)
            if st.button("Remover Favorito", icon="❌", type="primary", key=f"del_{ip}"):
                try:
                    conDelFav = sqlite3.connect("radar.db")
                    curDelFav = conDelFav.cursor()
                    print("CONECTADO COM SUCESSO AO SQLITE!")
                    curDelFav.execute("""
                                DELETE FROM historico_servidores
                                WHERE enderecoServidor = ?
                                """, (ip,))
                    conDelFav.commit()
                    print("DELETE efetuado no sistema.")
                    st.rerun()
                    # 1. Abre a conexão
                    # 2. Executa o DELETE mirando no IP específico
                    # 3. Dá o commit e fecha
                except Exception as e:
                    print(f"DELETE não efetuado, erro: {e}")
                
                finally:
                    if 'conDelFav' in locals() and conDelFav:
                        conDelFav.close()
                        print("conexao fechada")

            # Fazemos o pedido. Adicionei um timeout para a página não travar se o servidor estiver lento
            try:
                resposta = requests.get(urlFavoritos, timeout=7)
                dados = resposta.json()
                
                if dados.get("online"):
                    jogadores_online = dados["players"]["online"]
                    jogadores_max = dados["players"]["max"]
                    versao = dados.get("version", "Desconhecida")
                    
                    st.success("STATUS: ONLINE 🟢", width=200)
                    # O st.metric cria um destaque visual bem legal para os números
                    st.metric(label="Jogadores Ativos", value=jogadores_online, delta=f"Max: {jogadores_max}", delta_color="off")
                    st.caption(f"🏷️ Versão: {versao}")
                else:
                    st.error("STATUS: OFFLINE 🔴", width=200)
                    st.caption("Servidor inacessível no momento.")
            except:
                st.error("Erro na conexão ⚠️", width=200)