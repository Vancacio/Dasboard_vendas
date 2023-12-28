import	streamlit as st 
import requests 
import pandas as pd 
import plotly.express as px 

st.set_page_config(layout= 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.3f} {unidade}' 
        valor/= 1000        
    return f'{prefixo} {valor:.3f} Milhões'      
        
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'

regioes = ['Brasil','Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''
    
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('ano', 2020, 2023)
    
query_string = {'regiao': regiao.lower(), 'ano':ano}

response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas Receitas

receita_estados = dados.groupby('Local da compra')[['Preço']].sum()

receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()

receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year 

receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values(by = 'Preço', ascending=False) 

## Tabelas de Vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Tabelas Quantidades

# Criando o DataFrame com a contagem de ocorrências
quantidade_estados = dados.groupby('Local da compra').size().reset_index(name='Quantidade')

# Mesclando os DataFrames e ordenando por quantidade em ordem decrescente
quantidade_estados = pd.merge(
    dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']],
    quantidade_estados,
    on='Local da compra'
).sort_values(by='Quantidade', ascending=False)


quantidade_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M')).size().reset_index(name='Quantidade')

quantidade_mensal['Ano'] = quantidade_mensal['Data da Compra'].dt.year 

quantidade_mensal['Mes'] = quantidade_mensal['Data da Compra'].dt.month_name()

quantidade_categorias = dados.groupby('Categoria do Produto').size().reset_index(name='Quantidade').sort_values(by='Quantidade', ascending=False) 

## Gráficos Receitas

fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y =(0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                                            x = 'Local da compra',
                                            y = 'Preço',
                                            text_auto = True,
                                            title = 'Top estados'
                                            )

fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto= True,
                                title= "Receita por Categoria"
                               )

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Gráficos Quantidades

fig_mapa_quantidade = px.scatter_geo(quantidade_estados, 
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Quantidade',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'quantidade por Estado')

fig_quantidade_mensal = px.line(quantidade_mensal,
                             x = 'Mes',
                             y = 'Quantidade',
                             markers = True,
                             range_y =(0,quantidade_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'quantidade mensal')

fig_quantidade_mensal.update_layout(yaxis_title = 'Quantidade')

fig_quantidade_estados = px.bar(quantidade_estados.head(),
                                            x = 'Local da compra',
                                            y = 'Quantidade',
                                            text_auto = True,
                                            title = 'Top estados'
                                            )

fig_quantidade_estados.update_layout(yaxis_title = 'Quantidade')

fig_quantidade_categorias = px.bar(quantidade_categorias,
                                    x='Categoria do Produto',
                                    y='Quantidade',
                                    text_auto= True,
                                    title= "Quantidade por Categoria"
                                 )

fig_quantidade_categorias.update_layout(yaxis_title = 'Quantidade')

## Visualização no streamlit

aba1, aba2, aba3 = st.tabs(['Receita','Quantidade de vendas','Vendedores'])

with aba1:

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width= True)
        st.plotly_chart(fig_receita_categorias, use_container_width= True)
    
with aba2:

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_quantidade, use_container_width=True)
        st.plotly_chart(fig_quantidade_estados, use_container_width= True)
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_quantidade_mensal, use_container_width= True)
        st.plotly_chart(fig_quantidade_categorias, use_container_width= True)
        
with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        
        st.plotly_chart(fig_receita_vendedores, use_container_width= True)
        
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        
        st.plotly_chart(fig_vendas_vendedores, use_container_width= True)
        
st.dataframe(dados)
    
