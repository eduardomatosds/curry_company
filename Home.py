import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon=''
)
#image_path='/home/eduardo_matos/venv_jupyter/'
image=Image.open( 'logo.png')

st.sidebar.image(image,width=120)

st.sidebar.markdown('# Curry Cumpany')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry company growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construido para acmponhar as metricas de crescimentos dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão empresa:
       - Visão Gerencial: Metricas gerais de comportamentos.
       - Visão Tatica: Indicadores semanais de crescimentos.
       - Visão geografica: Insigights de geolocalização .
    - Visão entregadores:
       - Acompanhemento dos indicadores semanais de crescimentos.
    - Visão Restaurantes:
       - Indicadores semanais dos crescimentos dos restarurantes.
    ### Ask for help
    - Time de Data Science no Discord 
       -@ Eduardo
""")
