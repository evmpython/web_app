# https://github.com/LeviLucena/vendas/blob/main/app.py
# ==============================================================================================================#
#                                           IMPORTA BIBLIOTECAS
# ==============================================================================================================#
import streamlit as st
import streamlit_extras
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import numpy as np
from streamlit_folium import st_folium
import folium
import time

# ==============================================================================================================#
#                                     DEFINE FUNÇÕES
# ==============================================================================================================#
# Cache the conversion to prevent computation on every rerun
# Função que carrega os dados de focos tabulares


@st.cache_data
def load_data():

    # leitura do dataframe
    # df = pd.read_csv(
    #    'C:/Users/enriq/Downloads/PROCESSAMENTO_PYTHON/dashboards/01_queimadas/focos_br_AQUA_2003_2024.csv', compression='zip')

    # lendo todos dataframes
    df_lat = pd.read_csv(
        'lat.csv', compression='zip')
    df_lon = pd.read_csv(
        'lon.csv', compression='zip')
    df_municipios = pd.read_csv(
        'municipios.csv', compression='zip')
    df_estados = pd.read_csv(
        'estados.csv', compression='zip')
    df_biomas = pd.read_csv(
        'biomas.csv', compression='zip')

    # junta
    df = pd.concat([df_lat, df_lon, df_municipios,
                   df_estados, df_biomas], axis=1)

    # insere a coluna data como DateTime no DataFrame
    df['data'] = pd.to_datetime(df['data'])

    # seta a coluna data com o index do dataframe
    df.set_index('data', inplace=True)

    # coloca em ordem crescente de data
    df = df.sort_values('data')

    return df

# Função que tranforma dataframe para CSV


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


# ==============================================================================================================#
#                                         CONFIGURAÇÃO DA PÁGINA
# ==============================================================================================================#
# exemplos de ícones: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.set_page_config(page_title="DASHBOARD DE QUEIMADAS",
                   page_icon=":fire:",
                   layout='wide',
                   initial_sidebar_state='expanded')

# all graphs we use custom css not streamlit
theme_plotly = None

# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# st.image("logo_queimadas.png", use_column_width=True)
# st.title('Série Temporal de Focos de Calor')

# ==============================================================================================================#
#                                                    SIDEBAR
# ==============================================================================================================#
with st.sidebar:

    # st.image("logo_filtros.jpg", use_column_width=True)
    st.title(':gray-background[FILTROS] :sunglasses:')

    # st.divider()

    st.write("-------------------")

    tipo_analise = st.radio(":orange[**Escolha o Tipo de Análise**]",
                            ["**Série Temporal**", "**Distribuição Espacial**"],
                            captions=["Gráficos temporais", "Mapas"])

# ==============================================================================================================#
#                                           ANÁLISE TEMPORAL
# ==============================================================================================================#
if tipo_analise == '**Série Temporal**':

    # --------------------------------------------------------#
    #                      SIDEBAR
    # --------------------------------------------------------#
    with st.sidebar:

        st.divider()

        # with st.spinner('Carregando os dados. Favor aguardar...'):
        #    time.sleep(5)

        st.write('Carregando os dados. Favor aguardar...')

        # carrega os dados
        df = load_data()
        # st.success(':orange[Carregamento dos dados finalizado!]')

        # seleciona o "ESTADO"
        estados = sorted(df['estado'].unique().tolist())
        estado_selecionado = st.selectbox(
            ':orange[**Selecione o ESTADO**]:', estados)

        # seleciona a "DATA"
        data_inicial = st.date_input(
            ':orange[**Digite a data INICIAL**:]', datetime.date(2002, 3, 1))

        data_final = st.date_input(':orange[**Digite a data FINAL**]:', min_value=datetime.date(
            2002, 3, 1), max_value=datetime.date(2024, 5, 31))

        # filtra por Data
        df_filtrado = df.loc[str(data_inicial):str(data_final)]

        # filtra por Estado
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_selecionado]

    # https://plotly.com/python/figure-labels/
    st.markdown('# Série Temporal')
    st.markdown(f'### Estado selecionado = :red[{estado_selecionado.title()}]')

    # esta parte será usada para os gráficos
    col1, col2 = st.columns(2)  # 2 colunas
    col3, col4 = st.columns(2)  # 2 colunas
    col5, col6 = st.columns([2.0, 1.0], gap='medium')  # 2 colunas

    # --------------------------------------------------------#
    #               GRÁFICO: DIÁRIO TOTAL
    # --------------------------------------------------------#
    with col1:
        tab1, tab2 = st.tabs(['Gráfico', 'Dados'])
        with tab1:
            diaria = df_filtrado.groupby(pd.Grouper(freq='1D')).count()['lat']
            fig_diaria = px.line(diaria, width=300, height=300)
            fig_diaria.update_layout(showlegend=False, xaxis_title="Mês/Ano", yaxis_title="Focos de Calor",
                                     title={'text': 'Diária',
                                            'y': 0.93,
                                            'x': 0.5,
                                            'xanchor': 'center',
                                            'yanchor': 'top',
                                            'font_size': 20,
                                            'font_color': 'red'})
            col1.plotly_chart(fig_diaria, use_container_width=True)

        with tab2:
            st.dataframe(diaria)

        # botão de downaload dos dados
        dfx = pd.DataFrame({'data': diaria.index, 'focos': diaria.values})
        csv = convert_df(dfx)
        st.download_button(label="Download data",
                           data=csv,
                           file_name="focos_diario_total.csv")

        st.divider()

    # --------------------------------------------------------#
    #               GRÁFICO: ANUAL TOTAL
    # --------------------------------------------------------#
    with col2:
        tab1, tab2 = st.tabs(['Gráfico', 'Dados'])
        with tab1:
            anual = df_filtrado.groupby(pd.Grouper(freq='1Y')).count()['lat']
            fig_anual = px.bar(x=anual.index.year,
                               y=anual.values, width=300, height=300)
            fig_anual.update_layout(showlegend=False, xaxis_title="Ano", yaxis_title="Focos de Calor",
                                    title={'text': 'Anual',
                                           'y': 0.93,
                                           'x': 0.5,
                                           'xanchor': 'center',
                                           'yanchor': 'top',
                                           'font_size': 20,
                                           'font_color': 'red'})
            col2.plotly_chart(fig_anual, use_container_width=True)

        with tab2:
            st.dataframe(anual)

        # botão de downaload dos dados
        dfx = pd.DataFrame({'data': anual.index, 'focos': anual.values})
        csv = convert_df(dfx)
        st.download_button(label="Download data",
                           data=csv,
                           file_name="focos_anual_total.csv")
        st.divider()

    # --------------------------------------------------------#
    #               GRÁFICO: MENSAL TOTAL
    # --------------------------------------------------------#
    with col3:
        tab1, tab2 = st.tabs(['Gráfico', 'Dados'])
        with tab1:
            mensal = df_filtrado.groupby(pd.Grouper(freq='1M')).count()['lat']
            fig_mensal = px.line(mensal, width=300, height=300)
            fig_mensal.update_layout(showlegend=False, xaxis_title="Mês/Ano", yaxis_title="Focos de Calor",
                                     title={'text': 'Mensal',
                                            'y': 0.93,
                                            'x': 0.5,
                                            'xanchor': 'center',
                                            'yanchor': 'top',
                                            'font_size': 20,
                                            'font_color': 'red'})
            col3.plotly_chart(fig_mensal, use_container_width=True)

        with tab2:
            st.dataframe(mensal)

        # botão de downaload dos dados
        dfx = pd.DataFrame({'data': mensal.index, 'focos': mensal.values})
        csv = convert_df(dfx)
        st.download_button(label="Download data",
                           data=csv,
                           file_name="focos_mensal_total.csv")

    # --------------------------------------------------------#
    #               GRÁFICO: MENSAL MÉDIO
    # --------------------------------------------------------#
    with col4:
        tab1, tab2 = st.tabs(['Gráfico', 'Dados'])
        with tab1:
            mensal_climatologia = mensal.groupby(mensal.index.month).mean()
            meses = np.array(['Jan', 'Fev', 'Mar', 'Abr', 'Mai',
                             'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
            mensal_climatologia.index = meses
            fig_mensal_climatologia = px.bar(
                mensal_climatologia, width=300, height=300)
            fig_mensal_climatologia.update_layout(showlegend=False, xaxis_title="Mês", yaxis_title="Focos de Calor",
                                                  title={'text': 'Mensal Média',
                                                         'y': 0.93,
                                                         'x': 0.5,
                                                         'xanchor': 'center',
                                                         'yanchor': 'top',
                                                         'font_size': 20,
                                                         'font_color': 'red'})
            col4.plotly_chart(fig_mensal_climatologia,
                              use_container_width=True)

        with tab2:
            st.dataframe(mensal_climatologia)

        # botão de downaload dos dados
        dfx = pd.DataFrame({'mês': meses,
                            'focos': mensal_climatologia.values})
        csv = convert_df(dfx)
        st.download_button(label="Download data",
                           data=csv,
                           file_name="focos_mensal_climatologica.csv")

    # --------------------------------------------------------#
    #               GRÁFICO: TOP5 CIDADES
    # --------------------------------------------------------#
    with col5:

        tab1, tab2 = st.tabs(['Gráfico', 'Dados'])

        with tab1:
            top5 = df_filtrado['municipio'].value_counts(
                normalize=False, ascending=False)[0:2]

            fig_top5_cidades = px.bar(top5, width=300, height=600, orientation='h', color=[
                                      "goldenrod", "goldenrod"])

            fig_top5_cidades.update_layout(showlegend=False, xaxis_title="Cidades", yaxis_title="Focos de Calor",
                                           title={'text': 'Top5 cidades com maiores ocorrências',
                                                  'y': 0.93,
                                                  'x': 0.5,
                                                  'xanchor': 'center',
                                                  'yanchor': 'top',
                                                  'font_size': 20,
                                                  'font_color': 'white'},
                                           paper_bgcolor='#18C99F',
                                           plot_bgcolor='#18C99F',
                                           yaxis={'color': 'white'},
                                           font=dict(
                                               family='Arial', size=64, color='rgb(67, 67, 67)')
                                           )

            col5.plotly_chart(fig_top5_cidades, use_container_width=True)

        with tab2:
            st.dataframe(top5)

        expander = st.expander("See explanation")
        expander.write('''
                        The chart above shows some numbers I picked for you.
                        I rolled actual dice for these, so they're *guaranteed* to
                        be random.
                        ''')
        expander.image("https://static.streamlit.io/examples/dice.jpg")

        # botão de downaload dos dados
        dfx = pd.DataFrame({'cidades': top5.index, 'focos': top5.values})
        csv = convert_df(dfx)
        st.download_button(label="Download data", data=csv,
                           file_name="top5_cidades.csv")

    # --------------------------------------------------------#
    #                   GRÁFICO: BIOMA
    # --------------------------------------------------------#
    with col6:
        tab1, tab2 = st.tabs(['Gráfico', 'Dados'])
        with tab1:

            top5 = df_filtrado['bioma'].value_counts(
                normalize=False, ascending=False)[0:5]

            fig_top5_cidades = px.bar(top5, width=300, height=300)
            fig_top5_cidades.update_layout(showlegend=False, xaxis_title="Cidades", yaxis_title="Focos de Calor",
                                           title={'text': 'Top5 cidades com maiores ocorrências',
                                                  'y': 0.93,
                                                  'x': 0.5,
                                                  'xanchor': 'center',
                                                  'yanchor': 'top',
                                                  'font_size': 20,
                                                  'font_color': 'red'})
            col6.plotly_chart(fig_top5_cidades, use_container_width=True)

        with tab2:
            st.dataframe(top5)

        expander = st.expander("See explanation")
        expander.write('''
                        The chart above shows some numbers I picked for you.
                        I rolled actual dice for these, so they're *guaranteed* to
                        be random.
                        ''')
        expander.image("https://static.streamlit.io/examples/dice.jpg")

    # --------------------------------------------------------#
    #               GRÁFICO: MAPA FOLIUM
    # --------------------------------------------------------#

# ==============================================================================================================#
#                                           ANÁLISE ESPACIAL
# ==============================================================================================================#
elif tipo_analise == '**Distribuição Espacial**':

    # --------------------------------------------------------#
    #                      SIDEBAR
    # --------------------------------------------------------#
    with st.sidebar:

        st.divider()

        frequencia_analise = st.radio(":black[**Escolha o Tipo de Análise**]",
                                      ["**Climatologia**", "**Anomalia**"],
                                      captions=["Soma dos focos de calor", "Climatologia menos a média"])

        # meses = ['Jan', 'Fev', 'Mar', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        # anos = np.arange(2003, 2025, 1).tolist()
        # ano_selecionado = st.selectbox('Selecione o :red[**Ano**]:', anos)

    # --------------------------------------------------------#
    #                    GRÁFICOS
    # --------------------------------------------------------#
    if frequencia_analise == "**Climatologia**":
        st.markdown('# Distribuição Espacial')
        st.header(':black[Climatologia]')
        c1, c2 = st.columns(2)

        with c1:

            # seleciona o "ANO"
            anos = np.arange(2003, 2025, 1).tolist()
            ano_selecionado = st.selectbox('Selecione o :red[**Ano**]:', anos)
            st.image(f'Fig_0_acumulado_e_anomalia_focos_{
                     ano_selecionado}_BRASIL.png', use_column_width=True)

        with c2:

            # seleciona o "MÊS"
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            mes_selecionado = st.selectbox('Selecione o :red[**Mês**]:', meses)
            st.image(
                'Fig_0_acumulado_e_anomalia_focos_2023_BRASIL.png', use_column_width=True)

    # --------------------------------------------------------#
    #                    GRÁFICOS
    # --------------------------------------------------------#
    elif frequencia_analise == "**Anomalia**":
        st.markdown('# Distribuição Espacial')
        st.header(':black[Anomalia]')
        c1, c2 = st.columns(2)

        with c1:

            # seleciona o "ANO"
            anos = np.arange(2003, 2025, 1).tolist()
            ano_selecionado = st.selectbox('Selecione o :red[**Ano**]:', anos)
            st.image(f'Fig_0_acumulado_e_anomalia_focos_{
                     ano_selecionado}_BRASIL.png', use_column_width=True)

        with c2:

            # seleciona o "MÊS"
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            mes_selecionado = st.selectbox('Selecione o :red[**Mês**]:', meses)
            st.image(
                f'Fig_0_acumulado_e_anomalia_focos_2023_BRASIL.png', use_column_width=True)


# ==============================================================================================================#
#                                            FINALIZAÇÃO DO APP
# ==============================================================================================================#
with st.sidebar:
    st.sidebar.divider()
    st.sidebar.markdown('**Desenvolvido por**: Prof. Enrique V. Mattos')
    st.sidebar.markdown('**Universidade Federal de Itajubá (UNIFEI)**')
    st.sidebar.markdown('**Contato**: enrique@unifei.edu.br')


st.divider()
add_vertical_space(1)
st.markdown("#### Maiores Informações:")
links_row = row(3, vertical_align="center")
links_row.link_button("📖  Visite a documentação",
                      "https://terrabrasilis.dpi.inpe.br/queimadas/portal/",
                      use_container_width=True)

links_row.link_button("🐙  Acesso aos dados originais",
                      "https://terrabrasilis.dpi.inpe.br/queimadas/portal/dados-abertos/#da-focos",
                      use_container_width=True)

links_row.link_button("0️⃣  Visite nosso repositório",
                      "https://github.com/evmpython",
                      use_container_width=True)
