import base64
from pathlib import Path
import streamlit as st
  

def render_header(nome_usuario, titulo="Conciliação Retroativa", logo_path="img/sc-semfundo.png"):
    st.markdown("""
      <style>
      .block-container { padding-top: 0.5rem; }
      .app-header-wrap {
        position: sticky; top: 0; z-index: 1000;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        background: #F5F9F1;
        border-bottom: 2px solid #C4D79B;
        margin-bottom: 50px;
        margin-top: -4.6%;
      }
      .app-header { display:flex; align-items:center; gap:14px; padding:10px 20px; }
      .app-header__logo { height: 42px; display:block; }
      .app-header__title { font:700 20px/1.2 Helvetica, Arial, sans-serif; color:#375623; text-align:center; flex:1; }
      .app-header__link {
      display: inline-flex; align-items: center; justify-content: center;
      background: #E3EAD7; border: 1px solid #C4D79B;
      padding: 6px; border-radius: 8px; text-decoration: none;
      }
      .app-header__icon { height: 18px; width: 18px; }
      .app-header__user {
        font:600 13px Helvetica, Arial, sans-serif; color:#375623;
        background:#E9F2E1; padding:6px 10px; border-radius:8px;
      }
      </style>
    """, unsafe_allow_html=True)

    # 2) Logo em Base64 com MIME correto
    p = Path(logo_path)
    mime = "image/png" if p.suffix.lower() in {".png"} else "image/jpeg"
    logo_b64 = base64.b64encode(p.read_bytes()).decode("ascii")

    icon_path = Path("img/configuracao.png")
    icon_mime = "image/png" if icon_path.suffix.lower() == ".png" else "image/jpeg"
    icon_b64 = base64.b64encode(icon_path.read_bytes()).decode("ascii")

    st.markdown(f"""
    <div class="app-header-wrap">
      <div class="app-header">
        <a href="/" target="_self">
          <img class="app-header__logo" src="data:{mime};base64,{logo_b64}" alt="logo">
        </a>
        <div class="app-header__title">{titulo}</div>
        <a class="app-header__link" href="/empresas" target="_self">
          <img class="app-header__icon" src="data:{icon_mime};base64,{icon_b64}" alt="Gerenciar empresas">
        </a>
        <div class="app-header__user">{nome_usuario}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)