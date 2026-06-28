import streamlit as st
import requests
import pandas as pd
from bd import *

# 1. Deixa a página mais larga para caberem as colunas
st.set_page_config(page_title="Papi Mine", layout="wide", page_icon="logo.png")

# Finge que são as horas do dia
historico_24h = [120, 135, 150, 180, 200, 210, 190, 160, 140, 130, 110, 100] 
# Finge que são os dias da semana
historico_7d = [1500, 1650, 1400, 1800, 2200, 2500, 1900]

meu_estilo_retro = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,opsz,wght@0,18..144,300..900;1,18..144,300..900&display=swap');

    .stApp {
        background-color: #0a0a0a;
    }

    [data-testid="stAlertContentError"] [data-testid="stMarkdownContainer"] > p {
        color: #ffffff !important;}

    h1, h2, h3, p, button, input, label, li {
        color: #18FF00 !important;
        font-family: 'Merriweather', serif !important;
    }
</style>
"""

st.markdown(meu_estilo_retro, unsafe_allow_html=True)

# 1. Verifica se a gaveta do crachá existe na memória. Se não, cria vazia.
if 'usuario_id' not in st.session_state:
    st.session_state['usuario_id'] = None
    st.session_state['usuario_nome'] = None

# 2. Se o crachá estiver vazio, mostra a tela de Login/Registro
# 2. Se o crachá estiver vazio, mostra a tela de Login/Registro
if st.session_state['usuario_id'] is None:
    
    # Criamos 3 colunas: as da ponta (1.5) são mais largas para "espremer" a do meio (1)
    col_vazia_esq, col_login, col_vazia_dir = st.columns([1.5, 1, 1.5])
    
    # TUDO do login vai aqui dentro agora!
    with col_login:
        st.title("Terminal de Acesso", anchor=False) # anchor=False tira o ícone de link chato
        
        # Cria duas abas pra ficar organizado
        aba_login, aba_registro = st.tabs(["🔑 Entrar", "📝 Nova Conta"])
        
        with aba_login:
            # Como a coluna é estreita, a caixa e o texto ficam centralizados na tela
            login_user = st.text_input("Usuário", key="log_user")
            login_senha = st.text_input("Senha", type="password", key="log_pass")
            
            # O botão estica pra preencher o bloquinho certinho
            if st.button("Acessar", use_container_width=True):
                user_id = verificar_login(login_user, login_senha)
                if user_id:
                    st.session_state['usuario_id'] = user_id
                    st.session_state['usuario_nome'] = login_user
                    st.rerun() 
                else:
                    st.error("Usuário ou senha incorretos!")

        with aba_registro:
            reg_user = st.text_input("Novo Usuário", key="reg_user")
            reg_senha = st.text_input("Nova Senha", type="password", key="reg_pass")
            
            if st.button("Criar Conta", use_container_width=True):
                if criar_usuario(reg_user, reg_senha):
                    st.success("Conta criada com sucesso! Vá na aba de Entrar.")
                else:
                    st.error("Esse nome de usuário já está em uso!")

# 3. Se ele tiver o crachá (logado), mostra o sistema inteiro!
else:
    # Um cabeçalho legal pra mostrar quem está logado
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.write(f"Conectado como: **{st.session_state['usuario_nome']}**")
    with col2:
        if st.button("Sair"):
            st.session_state['usuario_id'] = None
            st.session_state['usuario_nome'] = None
            st.rerun()

    st.divider() # Uma linha separadora

    st.title("📡 Central de Monitoramento", text_alignment="center")

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
                    conexao = conectar()
                    cursor = conexao.cursor()
                    
                    # Mudamos de ? para %s, e agora inserimos o usuario_id junto!
                    cursor.execute("""
                        INSERT INTO historico_servidores (usuario_id, enderecoServidor, qtdJogadores)
                        VALUES (%s, %s, %s)
                    """, (st.session_state['usuario_id'], st.session_state['ip_pesquisado'], jogadores_online))
                    
                    conexao.commit()
                    st.toast("Servidor salvo com sucesso! ⭐") # Um balãozinho de aviso chique

                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
                finally:
                    if 'conexao' in locals() and conexao:
                        conexao.close()
        else:
            st.error("🔴 Este servidor está offline!", width=200)
            st.write("O servidor está desligado ou o IP está incorreto.")

    # ===================================
    # SEÇÃO 3: A LISTA DE FAVORITOS
    # ===================================

    st.markdown("---")

    st.title("⭐ Lista de Favoritos", text_alignment="left")

    criar_banco()

    try:
        conexao = conectar()
        cursor = conexao.cursor()
        
        # O WHERE filtra para trazer só os favoritos do seu crachá
        cursor.execute("""
            SELECT DISTINCT enderecoServidor
            FROM historico_servidores
            WHERE usuario_id = %s
        """, (st.session_state['usuario_id'],)) 
        
        resultado_sujo = cursor.fetchall()
    except Exception as e:
        st.error(f"Erro ao visualizar favoritos: {e}")
        resultado_sujo = [] # Previne erro se o fetch falhar
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()
            print("Conexão fechada")

    sua_lista_limpa = []

    try:
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
                            conexao = conectar()
                            cursor = conexao.cursor()
                            
                            # Deleta o IP, MAS só se for do seu usuário!
                            cursor.execute("""
                                DELETE FROM historico_servidores
                                WHERE enderecoServidor = %s AND usuario_id = %s
                            """, (ip, st.session_state['usuario_id']))
                            
                            conexao.commit()
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Erro ao deletar: {e}")
                        finally:
                            if 'conexao' in locals() and conexao:
                                conexao.close()

                    try:
                        resposta = requests.get(urlFavoritos, timeout=7)
                        dados = resposta.json()
                        
                        if dados.get("online"):
                            jogadores_online = dados["players"]["online"]
                            jogadores_max = dados["players"]["max"]
                            versao = dados.get("version", "Desconhecida")
                            
                            st.success("STATUS: ONLINE 🟢", width=200)
                            st.metric(label="Jogadores Ativos", value=jogadores_online, delta=f"Max: {jogadores_max}", delta_color="off")
                            st.caption(f"🏷️ Versão: {versao}")
                        else:
                            st.error("STATUS: OFFLINE 🔴", width=200)
                            st.caption("Servidor inacessível no momento.")
                    except:
                        st.error("Erro na conexão ⚠️", width=200)
    except Exception as e:
        st.write("Erro na hora de carregar favoritos, por favor, tente mais tarde.")