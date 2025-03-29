import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import spacy

nlp = spacy.load("en_core_web_sm")

data = pd.read_excel("fake_name_generator_db.xlsx", sheet_name="Worksheet")

app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Roboto:wght@400;700&display=swap"  
    ]
)

app.layout = dbc.Container([
    html.H1("Concessionária - Dashboard", className="text-center mb-4 text-light", style={"font-family": "Poppins, sans-serif"}),

    dbc.Row([
        dbc.Col(dcc.Input(
            id='input-filtro',
            type='text',
            placeholder='Pesquise por cidade ou estado...',
            debounce=True,
            className='form-control mb-3',
            style={"font-family": "Poppins, sans-serif"}
        ), width=6),
        dbc.Col(dcc.Dropdown(
            id='filtro-genero',
            options=[{'label': genero, 'value': genero} for genero in data['Gender'].unique()],
            placeholder='Selecione o gênero',
            className='mb-3'
        ), width=3),
        dbc.Col(dcc.RangeSlider(
            id='filtro-idade',
            min=data['Age'].min(),
            max=data['Age'].max(),
            step=1,
            marks={i: str(i) for i in range(data['Age'].min(), data['Age'].max()+1, 10)},
            tooltip={"placement": "bottom", "always_visible": True}
        ), width=3)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='carros-mais-vendidos', config={'displayModeBar': False}), width=6),
        dbc.Col(dcc.Graph(id='clientes-por-localizacao', config={'displayModeBar': False}), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='vendas-por-estado', config={'displayModeBar': False}), width=6),
        dbc.Col(dcc.Graph(id='marcas-populares', config={'displayModeBar': False}), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='diversidade-veiculos', config={'displayModeBar': False}), width=6)
    ])
], 
    fluid=True, 
    className="bg-dark p-4",
    style={
        "background": "linear-gradient(to bottom, #000B18, #00172D, #00264D, #02386E, #00498D, #0052A2)",
        "minHeight": "100vh", 
        "padding": "20px"
    }
)

@app.callback(
    [
        Output('carros-mais-vendidos', 'figure'),
        Output('clientes-por-localizacao', 'figure'),
        Output('vendas-por-estado', 'figure'),
        Output('marcas-populares', 'figure'),
        Output('diversidade-veiculos', 'figure')
    ],
    [
        Input('input-filtro', 'value'),
        Input('filtro-genero', 'value'),
        Input('filtro-idade', 'value')
    ]
)
def update_graphs(filtro, genero, idade_range):
    data_filtrada = data

    if filtro:
        filtro_lower = filtro.lower()
        data_filtrada = data_filtrada[data_filtrada['City'].str.lower().str.contains(filtro_lower) |
                                      data_filtrada['State'].str.lower().str.contains(filtro_lower)]
    
    if genero:
        data_filtrada = data_filtrada[data_filtrada['Gender'] == genero]

    if idade_range:
        data_filtrada = data_filtrada[(data_filtrada['Age'] >= idade_range[0]) & (data_filtrada['Age'] <= idade_range[1])]

    top_carros = data_filtrada['Vehicle'].value_counts().nlargest(10)
    fig_carros = px.bar(
        x=top_carros.values, 
        y=top_carros.index,
        labels={'x': 'Quantidade Vendida', 'y': 'Modelo'},
        title='Top 10: Carros Mais Vendidos',
        template='plotly_dark',
        text_auto=True,
        orientation='h'
    )
    fig_carros.update_traces(marker_color='cyan', marker_line_width=1.5)
    fig_carros.update_layout(title_font_family="Roboto")

    clientes_localizacao = data_filtrada['City'].value_counts().nlargest(10)
    fig_clientes = px.bar(
        x=clientes_localizacao.values,
        y=clientes_localizacao.index,
        labels={'x': 'Número de Clientes', 'y': 'Cidade'},
        title='Clientes por Localização',
        template='plotly_dark',
        text_auto=True,
        orientation='h'
    )
    fig_clientes.update_layout(title_font_family="Roboto")

    vendas_estados = data_filtrada['State'].value_counts()
    fig_estado = px.bar(
        x=vendas_estados.values,
        y=vendas_estados.index,
        labels={'x': 'Carros Vendidos', 'y': 'Estados'},
        title='Estados Mais Frequentes',
        template='plotly_dark',
        text_auto=True,
        orientation='h'
    )
    fig_estado.update_layout(title_font_family="Roboto")

    marcas = data_filtrada['Vehicle'].apply(lambda x: x.split()[0] if len(x.split()) > 0 else x).value_counts().sort_values()
    fig_marcas = px.bar(
        x=marcas.values,
        y=marcas.index,
        labels={'x': 'Quantidade Vendida', 'y': 'Marca'},
        title='Marcas Populares (Ordem Crescente)',
        template='plotly_dark',
        text_auto=True,
        orientation='h'
    )
    fig_marcas.update_layout(title_font_family="Roboto")

    diversidade_veiculos = data_filtrada['Vehicle'].nunique()
    fig_diversidade = px.pie(
        names=['Variados', 'Repetidos'],
        values=[diversidade_veiculos, len(data_filtrada) - diversidade_veiculos],
        title='Diversidade de Veículos',
        template='plotly_dark'
    )
    fig_diversidade.update_layout(title_font_family="Roboto")

    return fig_carros, fig_clientes, fig_estado, fig_marcas, fig_diversidade

if __name__ == '__main__':
    app.run(debug=True)
