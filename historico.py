import streamlit as st
import pandas as pd
import altair as alt

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    layout='wide',
    initial_sidebar_state='expanded',
)

# Função para carregar os dados do Excel
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name='uorg')
        df['Percentual'] = df['Percentual'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
        df['Percentual'] = df['Percentual'] * 100
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# Carregar os dados
file_path = 'historico.xlsx'
df = load_data(file_path)

# Verificar se o dataframe não está vazio
if not df.empty:
    # Título da aplicação
    st.title('Dados do Inventário Realizado em 2023')

    # Barra lateral para seleção da unidade organizacional
    uorgs = df['Uorg'].unique()
    selected_uorg = st.sidebar.selectbox('Unidade', uorgs)

    # Filtrar os dados pela unidade selecionada
    filtered_data = df[df['Uorg'] == selected_uorg]

    # Filtrar os dados para o exercício de 2023
    data_2023 = filtered_data[filtered_data['Exercicio'] == 2023]

    # Obter o valor da "Carga de Classificação" para o exercício de 2023
    carga_classificacao_2023 = data_2023['Carga Classificação'].values[0] if not data_2023.empty else None
    bens_inventariados_2023 = data_2023['Bens Inventariados'].values[0] if not data_2023.empty else None
    percentual_2023 = data_2023['Percentual'].values[0] if not data_2023.empty else None

    # Exibir os valores em colunas no topo da página
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Carga de Classificação", value=carga_classificacao_2023)
    with col2:
        st.metric(label="Bens Inventariados", value=bens_inventariados_2023)
    with col3:
        st.metric(label="Percentual 2023", value=f"{percentual_2023:.2f}%")

    # Configuração do tema e estilo do gráfico
    alt.themes.enable('fivethirtyeight')  # Aplicar um tema mais moderno (opcional)

    # Gráfico de colunas com percentuais de classificação usando Altair
    bar = alt.Chart(filtered_data).mark_bar(
        color='black',  # Cor das barras
        size=100  # Tamanho das barras
    ).encode(
        x=alt.X('Exercicio:O', 
                title='Exercício', 
                axis=alt.Axis(labelAngle=0, 
                              labelColor='black', 
                              titleColor='black',
                              labelFontSize=15,  # Tamanho das letras dos rótulos do eixo x
                              titleFontSize=17)),  # Tamanho do título do eixo x
        y=alt.Y('Percentual:Q', 
                title='Percentual (%)', 
                scale=alt.Scale(domain=[0, 100]), 
                axis=alt.Axis(labelColor='black', 
                              titleColor='black',
                              labelFontSize=15,  # Tamanho das letras dos rótulos do eixo y
                              titleFontSize=17)),  # Tamanho do título do eixo y
        tooltip=['Exercicio', alt.Tooltip('Percentual', format='.2f')]
    ).properties(
        title=f'SISAP - Evolução Historica do Inventário ({selected_uorg})',
        width=600,  # Largura do gráfico
        height=400  # Altura do gráfico
    )

    # Criar a sombra das barras
    shadow = alt.Chart(filtered_data).mark_bar(
        color='gray',  # Cor da sombra
        size=100,  # Tamanho das barras (igual ao tamanho das barras principais)
        opacity=0.4  # Opacidade para criar um efeito de sombra
    ).encode(
        x=alt.X('Exercicio:O'),
        y=alt.Y('Percentual:Q', title='Percentual (%)', scale=alt.Scale(domain=[0, 100]))
    ).properties(
        width=600,
        height=400
    ).transform_filter(
        alt.datum.Percentual > 0  # Apenas adicionar sombra para valores positivos
    )

    # Adicionar rótulos no topo das colunas
    text = bar.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,  # Ajuste a posição vertical do texto
        color='black',  # Cor do texto
        fontSize=15  # Tamanho da fonte do texto
    ).encode(
        text=alt.Text('Percentual:Q', format='.2f')
    )

    # Combinar o gráfico de barras e os rótulos de texto
    chart = (bar + text).configure_view(
        strokeOpacity=0  # Remover a linha de borda do gráfico
    )

    # Mostrar o gráfico
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para exibição.")
