from pathlib import Path
import sys
import streamlit as st
import os

# Configuração da página principal
st.set_page_config(
    page_title="HDF5 Viewer Suite",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Adiciona o diretório raiz do projeto ao PATH
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# (Opcional) Carregar CSS centralizado, se existir
css_path = os.path.join(project_root, "static", "css", "material_styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Definição das páginas do app
pages = {
    "Visualização e Análise": [
        st.Page("streamlit_app.py", title="Visão Geral HDF5", icon="📂"),
        st.Page("pages/01_Temporais.py", title="Séries Temporais (Tempo + Dados)", icon="⏱️"),
    ],
    # "Utilitários": [
    #     st.Page("create_sample_multichannel.py", title="Gerar Dados de Exemplo", icon="🧪"),
    #     # Adicione outras páginas utilitárias aqui
    # ]
}

# Navegação entre páginas
pg = st.navigation(pages, expanded=True)
pg.run()
