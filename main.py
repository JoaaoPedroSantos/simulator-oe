import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Função para realizar a simulação
def realizar_simulacao(dia, mes, ano, demanda_usuario, quantidade_demanda):
    dados = {
        "quantidade_demanda": quantidade_demanda,
        "quantidade_entrada": [1600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "status_documento": ["PO"] + ["STK"] * 20,
        "data": pd.date_range(start="2024-12-09", periods=21, freq="W-MON")
    }

    df_original = pd.DataFrame(dados)

    df = df_original.copy()

    # Realizando a projeção
    ne = 10000
    nivel = []
    passo = []
    for i in range(len(df)):
        ne = ne + df['quantidade_entrada'][i] - df['quantidade_demanda'][i]
        nivel.append(ne)
        passo.append(i + 1)
    df['projecao'] = nivel
    df['passo'] = passo

    # Criando a data fornecida pelo usuário
    raw_data = f"{ano}-{mes}-{dia}"
    data_n = pd.Timestamp(raw_data) - pd.Timedelta(days=pd.Timestamp(raw_data).weekday())

    # Adicionando o dado fornecido pelo usuário
    df_simu = pd.concat([df_original, pd.DataFrame([{
        "quantidade_demanda": demanda_usuario,
        "quantidade_entrada": 0,
        "status_documento": np.nan,
        "data": data_n
    }])], ignore_index=True)

    # Agrupando por data e somando as quantidades
    df_grouped = df_simu.groupby("data", as_index=False).sum()

    # Ordenando pelo menor para o maior
    df_grouped = df_grouped.sort_values(by="data")

    ne = 10000
    nivel = []
    passo = []
    for i in range(len(df_grouped)):
        ne = ne + df_grouped['quantidade_entrada'][i] - df_grouped['quantidade_demanda'][i]
        nivel.append(ne)
        passo.append(i + 1)
    df_grouped['projecao'] = nivel
    df_grouped['passo'] = passo

    # Criando o gráfico
    fig = go.Figure()

    # Adicionando a projeção fato (df)
    fig.add_trace(go.Scatter(
        x=df['data'],
        y=df['projecao'],
        mode='lines+markers',
        name='Projeção Fato',
        marker=dict(color='blue')
    ))

    # Adicionando a projeção simulação (df_grouped)
    fig.add_trace(go.Scatter(
        x=df_grouped['data'],
        y=df_grouped['projecao'],
        mode='lines+markers',
        name='Projeção Simulação',
        marker=dict(color='lightgreen')
    ))

    # Destacando o novo dado adicionado ao df_simu
    novo_ponto = df_grouped[df_grouped['data'] == data_n]
    if not novo_ponto.empty:
        fig.add_trace(go.Scatter(
            x=novo_ponto['data'],
            y=novo_ponto['projecao'],
            mode='markers',
            name='Data Necessidade',
            marker=dict(color='darkturquoise', size=10, symbol='circle')
        ))

    # Adicionando a linha vertical de lead time
    fig.add_shape(
        type="line",
        x0="2025-02-17",  # Data de fevereiro de 2025
        x1="2025-02-17",  # Mesma coordenada para a linha vertical
        y0=df['projecao'].min(),
        y1=df['projecao'].max(),
        line=dict(color="red", width=2, dash="dash"),
    )

    # Adicionando a descrição da linha vertical como "Lead Time"
    fig.add_annotation(
        x="2025-02-17",
        y=df['projecao'].max() * 0.9,
        text="LeadTime",
        showarrow=True,
        arrowhead=2,
        ax=20,
        ay=-40,
        font=dict(size=12, color="red"),
        arrowcolor="red"
    )

    # Configurando o layout do gráfico
    fig.update_layout(
        title='Projeção Fato vs Simulação',
        xaxis_title='Data',
        yaxis_title='Nível de Estoque',
        template='plotly_white'
    )

    return fig


# Cabeçalho
st.title("📈 Simulação de Efetividade")
st.markdown("""
Bem-vindo à ferramenta de simulação de efetividade. Aqui, você pode ajustar os parâmetros e visualizar a projeção do nível de estoque em relação à demanda e entradas. 
Escolha os parâmetros abaixo para realizar uma nova simulação.
""")

# Layout com colunas para os inputs
col1, col2, col3, col4 = st.columns(4)

with col1:
    ano_input = st.selectbox("🔢 Selecione o ano", [2024, 2025], index=1)
with col2:
    mes_input = st.selectbox("📅 Selecione o mês", [f"{i:02d}" for i in range(1, 13)], index=1)
with col3:
    dia_input = st.selectbox("📆 Selecione o dia", [f"{i:02d}" for i in range(1, 32)], index=10)
with col4:
    demanda_input = st.number_input("💡 Quantidade demanda", min_value=0, max_value=10000, value=1000)

# Botão para iniciar a simulação
if st.button('🚀 Iniciar Simulação'):
    fig = realizar_simulacao(dia_input, mes_input, ano_input, demanda_input, [0, 638, 1276, 1276, 1276, 1276, 1276, 1276, 638, 1276, 638, 1276, 1276, 1276, 638, 638, 638, 1276, 1276, 1276, 638])
    st.plotly_chart(fig, use_container_width=True, key="simulacao_inicial")

# Área de edição de dados para quantidade_demanda
st.subheader("✍️ Editar Quantidade de Demanda")

quantidade_demanda_input = st.text_area(
    "Alterar os valores de 'quantidade_demanda' abaixo (separados por vírgula). Exemplo: 638, 1276, 1000...",
    value="0, 638, 1276, 1276, 1276, 1276, 1276, 1276, 638, 1276, 638, 1276, 1276, 1276, 638, 638, 638, 1276, 1276, 1276, 638"
)

quantidade_demanda_lista = [int(i.strip()) for i in quantidade_demanda_input.split(",")]

# Botão para reiniciar a simulação com novos dados
if st.button('🔄 Reiniciar Simulação'):
    fig = realizar_simulacao(dia_input, mes_input, ano_input, demanda_input, quantidade_demanda_lista)
    st.plotly_chart(fig, use_container_width=True, key="simulacao_reiniciada")

# Seção de informações adicionais
st.markdown("""
### 🔍 Detalhes sobre o Gráfico
O gráfico acima mostra a projeção do nível de estoque (em azul e verde) e um ponto de referência com a "Data Necessidade" para uma demanda específica. O "Lead Time" é mostrado como uma linha vermelha, representando o tempo necessário para a reposição do estoque.

Fique à vontade para alterar os parâmetros e observar como isso afeta a projeção do estoque.
""")
