
# https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY?hl=pt-br

import streamlit as st
import geemap.foliumap as geemap  # Importação correta para Streamlit
import ee
import datetime
from datetime import timedelta

# Inicializar o Google Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# Configuração do aplicativo
st.set_page_config(layout="wide")
st.title("Visualizador de Precipitação Diária - CHIRPS (Brasil)")

# Função para obter geometria do Brasil
def obter_geometria_brasil():
    brasil = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017") \
              .filter(ee.Filter.eq("country_na", "Brazil"))
    return brasil.geometry()

# Função principal para obter imagem CHIRPS
def obter_imagem_chirps_para_o_brasil(data_selecionada):
    data_inicial = data_selecionada.strftime("%Y-%m-%d")
    data_final = (data_selecionada + timedelta(days=1)).strftime("%Y-%m-%d")

    colecao_chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                        .filterDate(data_inicial, data_final)

    if colecao_chirps.size().getInfo() == 0:
        st.warning(f"Não há dados para {data_inicial}. Buscando dados mais recentes...")

        for dias_volta in range(1, 31):
            nova_data = data_selecionada - timedelta(days=dias_volta)
            nova_inicial = nova_data.strftime("%Y-%m-%d")
            nova_final = (nova_data + timedelta(days=1)).strftime("%Y-%m-%d")

            nova_colecao = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                              .filterDate(nova_inicial, nova_final)

            if nova_colecao.size().getInfo() > 0:
                st.info(f"Mostrando dados de {nova_inicial}")
                colecao_chirps = nova_colecao
                break
        else:
            st.error("Sem dados de precipitação recentes.")
            return None

    imagem = colecao_chirps.first()
    return imagem.clip(obter_geometria_brasil())

# Interface do usuário
col1, col2 = st.columns([1, 3])

with col1:
    st.header("Configurações")

    hoje = datetime.date.today()
    data_disponivel = hoje - timedelta(days=60)

    data_selecionada = st.date_input(
        "Selecione uma data",
        value=data_disponivel,
        min_value=datetime.date(1981, 1, 1),
        max_value=data_disponivel
    )

    st.subheader("Visualização do Mapa")
    valor_minimo = st.slider("Valor mínimo (mm)", 0.1, 50.0, 0.1)
    valor_maximo = st.slider("Valor máximo (mm)", 0.1, 300.0, 50.0)
    opacidade = st.slider("Opacidade", 0.0, 1.0, 0.8)
    paleta_cores = st.text_input(
        "Paleta de cores (separada por vírgulas)",
        "white,blue,darkblue,lime,yellow,red"
    )

with col2:
    st.header(f"Precipitação no Brasil - {data_selecionada.strftime('%Y-%m-%d')}")
    imagem_chirps = obter_imagem_chirps_para_o_brasil(data_selecionada)

    mapa = geemap.Map(center=[-15, -55], zoom=4)

    if imagem_chirps:
        precipitacao = imagem_chirps.select("precipitation")
        parametros = {
            'min': valor_minimo,
            'max': valor_maximo,
            'palette': [c.strip() for c in paleta_cores.split(',')],
            'opacity': opacidade
        }

        mapa.addLayer(precipitacao, parametros, "Precipitação (mm)")

        contorno = ee.Image().byte().paint(
            featureCollection=obter_geometria_brasil(),
            color=1,
            width=2
        )
        mapa.addLayer(contorno, {'palette': 'red'}, "Limite do Brasil")

        mapa.addLayerControl()

        try:
            media = precipitacao.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=obter_geometria_brasil(),
                scale=5500,
                maxPixels=1e10
            ).getInfo().get('precipitation', None)

            maximo = precipitacao.reduceRegion(
                reducer=ee.Reducer.max(),
                geometry=obter_geometria_brasil(),
                scale=5500,
                maxPixels=1e10
            ).getInfo().get('precipitation', None)

            if media is not None:
                st.write(f"Precipitação média: {media:.1f} mm")
            if maximo is not None:
                st.write(f"Precipitação máxima: {maximo:.1f} mm")

        except Exception as e:
            st.warning(f"Erro ao calcular estatísticas: {e}")
    else:
        st.error("Nenhum dado disponível.")

    mapa.to_streamlit(height=600)

# Rodapé
st.markdown("---")
st.markdown("""
**Fonte de dados:**  
- [CHIRPS Daily](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY)  
- [LSIB Simplified (Limites de países)](https://developers.google.com/earth-engine/datasets/catalog/USDOS_LSIB_SIMPLE_2017)
""")
