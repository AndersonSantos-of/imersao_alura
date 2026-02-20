import pandas as pd
import plotly.express as px
import streamlit as st

#configurando o título da página e a orientação
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
df= pd.read_csv('https://raw.githubusercontent.com/AndersonSantos-of/imersao_alura/refs/heads/main/df_limpo.csv')

# --- cria a Barra Lateral e define o título
st.sidebar.header("🔎 Filtros")

#criando os filtros para a barra lateral.
#sorted e unique pega os valores únicos e organiza, ele ficam guardado na variável.
#st.sidebar.multiselect cria um filtro com múltipla seleção.
#st.sidebar.multiselect('titulo do filtro', variavel para filtrar, default=valor padrão)

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
experiencia_disponiveis = sorted(df['experiencia'].unique())
experiencia_selecionadas = st.sidebar.multiselect("Experiência", experiencia_disponiveis, default=experiencia_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# criando um dataframe para filtrar os dados com base na seleção dos filtros
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
# .isin(lista) Verifica quais valores estão na lista de cada filtro
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['experiencia'].isin(experiencia_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🗃️ Dashboard de Análise de Salários na Área de Dados") #título principal da página
st.markdown("Explore os dados salariais na área de dados nos últimos anos. "
"**Utilize os filtros à esquerda para refinar sua análise.**") #texto abaixo do título

# --- criando uma linha para as Métricas Principais
st.subheader("Métricas gerais (Salário anual em USD)") #subtítulo

#Evita erro quando não há dados após o filtro.
if not df_filtrado.empty:
    salario_medio = df_filtrado['salario_em_usd'].mean()
    salario_maximo = df_filtrado['salario_em_usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

#define quantas colunas vai ter em uma linha
col1, col2, col3, col4 = st.columns(4)
#.metric('título', valor) diz o que vai ficar dentro de cada coluna criada e seu título
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")#subtítulo

#cada st.columns() cria uma nova linha
#cria duas colunas em uma linha
col_graf1, col_graf2 = st.columns(2)

#with é outra forma de dizer o que vai fica dentro de uma coluna
#dentro de cada coluna vai um gráfico que eu crio com o plotly
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['salario_em_usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='salario_em_usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'salario_em_usd': 'Média salarial anual (USD)', 'cargo': ''},
            color_discrete_sequence=["#17d527"] #definindo a cor das barras
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)# para carregar o gráfico dentro da coluna
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='salario_em_usd',
            nbins=50,
            title="Distribuição de salários anuais",
            labels={'salario_em_usd': 'Faixa salarial (USD)', 'count': ''},
            color_discrete_sequence=["#17d527"]
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

#crindo uma nova linha com mais colunas
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['tipo_trabalho'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho2', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho2',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            color_discrete_sequence=["#006aff", "#FF9D00", "#15f463"] #selecionando as cores do gráfico
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        # Lista os cargos disponíveis após aplicar os filtros da sidebar.
        cargos_disponiveis = sorted(df_filtrado['cargo'].unique())
        # Define "Data Scientist" como padrão quando existir; caso contrário usa o primeiro cargo.
        cargo_padrao = cargos_disponiveis.index('Data Scientist') if 'Data Scientist' in cargos_disponiveis else 0
        # Cria o seletor para o usuário escolher qual cargo visualizar no mapa.
        cargo_selecionado = st.selectbox(
            "Selecione o cargo para visualizar no mapa:",
            cargos_disponiveis,
            index=cargo_padrao
        )

        # Filtra somente os registros do cargo selecionado.
        df_cargo = df_filtrado[df_filtrado['cargo'] == cargo_selecionado]
        # Calcula o salário médio por país para o cargo escolhido.
        media_cargo_pais = df_cargo.groupby('residencia_iso3')['salario_em_usd'].mean().reset_index()

        # Só desenha o mapa se houver dados agregados por país.
        if not media_cargo_pais.empty:
            # Monta o mapa coroplético com escala de cor baseada no salário médio.
            grafico_paises = px.choropleth(
                media_cargo_pais,
                locations='residencia_iso3',
                color='salario_em_usd',
                color_continuous_scale='rdylgn',
                title=f'Salário médio de {cargo_selecionado} por país',
                labels={'salario_em_usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
            )
            # Ajusta o alinhamento do título e renderiza o gráfico na coluna.
            grafico_paises.update_layout(title_x=0.1)
            st.plotly_chart(grafico_paises, use_container_width=True)
        else:
            # Exibe aviso quando o cargo escolhido não possui dados no mapa.
            st.warning("Nenhum dado para exibir no mapa para o cargo selecionado.")
    else:
        # Exibe aviso quando os filtros removem todos os registros do dataset.
        st.warning("Nenhum dado para exibir no gráfico de países.")