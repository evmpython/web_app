# https://streamlit.io/ e https://docs.streamlit.io/get-started/tutorials/create-an-app
import streamlit as st
import pandas as pd

st.set_page_config(page_title='Meu site Stramlit')

with st.container():
    st.subheader('Meu primeiro site com o streamlit')
    st.title('Dasboard de Contratos')
    st.write('Informações sobre o contrato ao longo de maio')
    st.write('Quer aprender python? [Clique aqui](https://www.hashtagtreinamentos.com/)')

@st.cache_data
def carregar_dados():
    tabela = pd.read_csv('resultados.csv')
    return tabela

with st.container():
    st.write('----')    

    qte_dias = st.selectbox('Selecione o período', ['7 dias','15 dias', '21 dias', '30 dias'])

    num_dias = int(qte_dias.replace(' dias', ''))

    dados = carregar_dados()

    dados = dados[-num_dias:]

    st.area_chart(dados, x='Data', y='Contratos')