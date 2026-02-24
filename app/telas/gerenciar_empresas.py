import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path
import yaml

from app import ui
from core import empresas


def requerer_login():
    config_path = Path('config/users.yaml')
    with open(config_path) as arquivo:
        config = yaml.load(arquivo, Loader=yaml.loader.SafeLoader)

    autenticador = stauth.Authenticate(
        credentials=config['credentials'],
        cookie_name=config['cookie']['name'],
        cookie_key=config['cookie']['key'],
        cookie_expiry_days=config['cookie']['expiry_days']
    )
    autenticador.login(fields={"Username": "Usuario", "Password": "Senha", "Login": "Entrar"})

    # Verificar se está logado
    if not st.session_state.get('authentication_status'):
        st.switch_page('main.py')
        return
    
    usuario = st.session_state.get('username')
    role = config['credentials']['usernames'][usuario].get('role')

    return role

def run():
    user_role = requerer_login()

    # Configurações gerais da página
    st.set_page_config(page_title='Gerenciar Empresas', page_icon='img/sc-quadrada.png', layout='wide')
    st.markdown("""<style>[data-testid="InputInstructions"] { display: none !important; }</style>""", unsafe_allow_html=True)
    ui.header.render_header(titulo='Gerenciador de Empresas', nome_usuario=st.session_state.get('name'))

    catalogo_empresas = empresas.listar_empresas()
    ui.gerenciador_empresas.render_gerenciador_empresas(catalogo_empresas, (user_role == 'admin'))

    # Parte exclusiva para admins
    if user_role == 'admin':
        ui.gerenciador_arquivos.render_gerenciador_arquivos()