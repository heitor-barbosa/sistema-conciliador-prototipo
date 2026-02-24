import yaml
from pathlib import Path
import streamlit as st
import streamlit_authenticator as stauth
from app.telas.conciliacao import run


# Configuracao da pagina
st.set_page_config(page_title='Conciliação Retroativa', page_icon='img/sc-quadrada.png', layout='wide')
st.markdown("""<style>[data-testid="InputInstructions"] { display: none !important; }</style>""", unsafe_allow_html=True)

# Pegar credenciais no arquivo yaml
config_path = Path('config/users.yaml')
with open(config_path) as arquivo:
    config = yaml.load(arquivo, Loader=yaml.loader.SafeLoader)

autenticador = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

# Exibir formulario de login (traduzido e estilizado)  
auth_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')

if auth_status:
    run(nome_usuario=name)
    st.stop()

_, centro, _ = st.columns([0.2, 0.6, 0.2])
with centro:
    autenticador.login(fields={'Username': 'Usuario', 'Password': 'Senha', 'Login': 'Entrar'})

if auth_status is False:
    st.error('Usuario ou senha errado')
