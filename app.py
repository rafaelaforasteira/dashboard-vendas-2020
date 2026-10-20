
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

ROOT = os.path.dirname(os.path.abspath(__file__))
dados = pd.read_excel(os.path.join(ROOT, "base_vendas.xlsx"))
dados = dados.drop(columns=["Unnamed: 0"], errors="ignore")
dados["Data_Pedido"] = pd.to_datetime(dados["Data_Pedido"], errors="coerce")
dados["Estado_Cliente"] = dados["Estado_Cliente"].replace({"MINAS": "MG"})
dados["Valor_Total_Venda"] = pd.to_numeric(dados["Valor_Total_Venda"], errors="coerce")
dados = dados.loc[(dados["Data_Pedido"].dt.year == 2020) & dados["Valor_Total_Venda"].notna()].copy()
dados["Mes_Num"] = dados["Data_Pedido"].dt.month
MESES = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
dados["Mes"] = dados["Mes_Num"].map(MESES)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Dashboard de Vendas | 2020")
server = app.server
BLUE = "#7C94FF"
PALETTE = ["#7C94FF","#B293FF","#42C9C0","#F5B76D","#F07A94","#7ED49E"]
def opts(col):
    return [{"label":str(v), "value":str(v)} for v in sorted(dados[col].dropna().astype(str).unique())]
def filter_data(meses, reps, regionais, produtos, clientes, estados=None, cidades=None):
    d=dados
    for col, vals in [("Mes_Num",meses),("Nome_Representante",reps),("Regional",regionais),("Nome_Produto",produtos),("Nome_Cliente",clientes),("Estado_Cliente",estados),("Cidade_Cliente",cidades)]:
        if vals:
            d=d[d[col].isin(vals)]
    return d
def graph(fig, height=330):
    fig.update_layout(template="plotly_dark",paper_bgcolor="#171F31",plot_bgcolor="#171F31",
        font=dict(family="Arial",color="#CED6E7",size=12),height=height,
        margin=dict(l=22,r=16,t=34,b=34),
        colorway=PALETTE, legend=dict(orientation="h",y=-0.28),
        hoverlabel=dict(bgcolor="#263451"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#303C51",zeroline=False)
    return fig
def empty_fig(title):
    f=go.Figure()
    f.add_annotation(text="Sem dados para os filtros selecionados",showarrow=False,font=dict(size=15,color="#B9C6DC"))
    f.update_layout(title=title)
    return graph(f)
def chart(title, elem):
    return html.Div([html.H3(title,className="chart-title"),elem],className="panel")
def dropdown(label, did, options):
    return html.Div([html.Label(label,className="filter-label"),
       dcc.Dropdown(id=did, options=options, multi=True, placeholder="Todos",className="filter-dropdown")],className="filter-item")
app.layout=html.Div(className="app-shell",children=[
    html.Header([html.Div([html.Div("SALES INTELLIGENCE  /  2020",className="eyebrow"),
                          html.H1("Visão Geral de Vendas"),
                          html.P("Análise interativa do desempenho comercial em 2020",className="subtitle")]),
                html.Div("ANO-BASE · 2020",className="year-pill")],className="header"),
    html.Div([
        dropdown("Mês","mes", [{"label":MESES[i],"value":i} for i in range(1,13)]),
        dropdown("Representante","rep",opts("Nome_Representante")),
        dropdown("Regional","reg",opts("Regional")),
        dropdown("Produto","prod",opts("Nome_Produto")),
        dropdown("Cliente","cli",opts("Nome_Cliente")),
        html.Button("Limpar filtros",id="clear",n_clicks=0,className="clear-btn")
    ],className="filter-panel"),
    html.Div([
        html.Div([html.Div("FATURAMENTO",className="kpi-label"),html.Div(id="kpi-total",className="kpi-value")],className="kpi"),
        html.Div([html.Div("PEDIDOS",className="kpi-label"),html.Div(id="kpi-pedidos",className="kpi-value")],className="kpi"),
        html.Div([html.Div("TICKET MÉDIO",className="kpi-label"),html.Div(id="kpi-ticket",className="kpi-value")],className="kpi"),
        html.Div([html.Div("UNIDADES VENDIDAS",className="kpi-label"),html.Div(id="kpi-unidades",className="kpi-value")],className="kpi"),
    ],className="kpi-grid"),
    html.Div([
        chart("Evolução mensal do faturamento",dcc.Graph(id="monthly",config={"displayModeBar":False})),
        chart("Vendas por representante",dcc.Graph(id="representatives",config={"displayModeBar":False}))
    ],className="chart-grid"),
    html.Div([
        chart("Participação por regional",dcc.Graph(id="regional",config={"displayModeBar":False})),
        chart("Faturamento por estado",dcc.Graph(id="states",config={"displayModeBar":False}))
    ],className="chart-grid"),
    chart("Vendas por produto",html.Div(id="product-table",className="table-scroll")),
    html.Div([
        html.Div([html.Div("ANÁLISE GEOGRÁFICA",className="eyebrow"),html.H2("Estado e cidade",className="section-title"),
                  html.P("Selecione um estado para disponibilizar apenas as cidades correspondentes.",className="subtitle"),
                  html.Div([dropdown("Estado","estado",opts("Estado_Cliente")),
                            dropdown("Cidade","cidade",[])],className="geo-filters")]),
        dcc.Graph(id="city-chart",config={"displayModeBar":False})
    ],className="panel geo-panel"),
    html.Footer("Visualização de Dados • Base de vendas 2020 • Python + Dash + Plotly Express")
])
@app.callback(
    Output("mes","value"),Output("rep","value"),Output("reg","value"),Output("prod","value"),Output("cli","value"),
    Input("clear","n_clicks"),prevent_initial_call=True
)
def clear_all(_):
    return [],[],[],[],[]
@app.callback(Output("cidade","options"),Output("cidade","value"),
    Input("estado","value"),Input("cidade","value"))
def sync_cidades(estados,cidades):
    if not estados:
        return [],[]
    permitted=sorted(dados.loc[dados["Estado_Cliente"].isin(estados),"Cidade_Cliente"].dropna().unique())
    valid=[c for c in (cidades or []) if c in permitted]
    return [{"label":c,"value":c} for c in permitted],valid
@app.callback(
    Output("kpi-total","children"),Output("kpi-pedidos","children"),
    Output("kpi-ticket","children"),Output("kpi-unidades","children"),
    Output("monthly","figure"),Output("representatives","figure"),
    Output("regional","figure"),Output("states","figure"),Output("product-table","children"),
    Input("mes","value"),Input("rep","value"),Input("reg","value"),Input("prod","value"),Input("cli","value")
)
def general(meses,reps,regs,prods,clientes):
    d=filter_data(meses,reps,regs,prods,clientes)
    total=d.Valor_Total_Venda.sum()
    n=d.ID_Pedido.nunique()
    def brl(x):return "R$ "+f"{x:,.2f}".replace(",","X").replace(".",",").replace("X",".")
    if d.empty:
        f=empty_fig("Sem dados")
        return brl(0),"0",brl(0),"0",f,f,f,f,html.P("Nenhum produto encontrado.")
    monthly=d.groupby("Mes_Num",as_index=False).Valor_Total_Venda.sum()
    monthly=monthly.set_index("Mes_Num").reindex(range(1,13),fill_value=0).reset_index()
    monthly["Mês"]=monthly.Mes_Num.map(MESES)
    f1=px.area(monthly,x="Mês",y="Valor_Total_Venda",markers=True,
               labels={"Valor_Total_Venda":"Faturamento (R$)","Mês":"Mês"},
               category_orders={"Mês":list(MESES.values())})
    f1.update_traces(line_color=BLUE,fillcolor="rgba(124,148,255,.19)",
                     hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>")
    reps_data=d.groupby("Nome_Representante",as_index=False).Valor_Total_Venda.sum().sort_values("Valor_Total_Venda")
    f2=px.bar(reps_data,x="Valor_Total_Venda",y="Nome_Representante",orientation="h",
              labels={"Valor_Total_Venda":"Faturamento (R$)","Nome_Representante":""})
    f2.update_traces(marker_color=BLUE,hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>")
    regional_data=d.groupby("Regional",as_index=False).Valor_Total_Venda.sum()
    f3=px.pie(regional_data,names="Regional",values="Valor_Total_Venda",hole=0.42,color_discrete_sequence=PALETTE)
    f3.update_traces(textinfo="percent+label",hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>")
    state_data=d.groupby("Estado_Cliente",as_index=False).Valor_Total_Venda.sum().sort_values("Valor_Total_Venda")
    f4=px.bar(state_data,x="Valor_Total_Venda",y="Estado_Cliente",orientation="h",
              labels={"Valor_Total_Venda":"Faturamento (R$)","Estado_Cliente":""})
    f4.update_traces(marker_color="#42C9C0",hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>")
    products=d.groupby("Nome_Produto",as_index=False).agg(
        Vendas=("Valor_Total_Venda","sum"),Unidades=("Quantidade_Vendida","sum"),Pedidos=("ID_Pedido","nunique")
    ).sort_values("Vendas",ascending=False)
    rows=[html.Tr([html.Td(row.Nome_Produto),html.Td(brl(row.Vendas)),html.Td(f"{row.Unidades:,}".replace(",",".")),
                   html.Td(row.Pedidos)]) for row in products.itertuples()]
    table=html.Table([html.Thead(html.Tr([html.Th("Produto"),html.Th("Faturamento"),html.Th("Unidades"),html.Th("Pedidos")])),
                      html.Tbody(rows)],className="sales-table")
    return brl(total),f"{n:,}".replace(",","."),brl(total/n if n else 0),f"{d.Quantidade_Vendida.sum():,}".replace(",","."),graph(f1),graph(f2),graph(f3),graph(f4),table
@app.callback(Output("city-chart","figure"),
    Input("estado","value"),Input("cidade","value"),
    Input("mes","value"),Input("rep","value"),Input("reg","value"),Input("prod","value"),Input("cli","value"))
def geo(estados,cidades,meses,reps,regs,prods,clientes):
    if not estados:
        return empty_fig("Selecione um estado")
    d=filter_data(meses,reps,regs,prods,clientes,estados,cidades)
    if d.empty:
        return empty_fig("Nenhuma venda encontrada")
    bycity=d.groupby(["Estado_Cliente","Cidade_Cliente"],as_index=False).Valor_Total_Venda.sum()
    bycity["Local"]=bycity.Cidade_Cliente+" / "+bycity.Estado_Cliente
    bycity=bycity.sort_values("Valor_Total_Venda")
    fig=px.bar(bycity,x="Valor_Total_Venda",y="Local",orientation="h",
               labels={"Valor_Total_Venda":"Faturamento (R$)","Local":""})
    fig.update_traces(marker_color="#B293FF",hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>")
    return graph(fig,max(330,45*len(bycity)+100))
if __name__=="__main__":
    app.run(debug=os.environ.get("DASH_DEBUG")=="1",host="0.0.0.0",port=int(os.environ.get("PORT",8050)))
