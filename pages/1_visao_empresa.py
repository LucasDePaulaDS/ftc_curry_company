# Libraries 
import pandas as pd 
import numpy as np
import plotly.express as px
import folium
import streamlit as st
from haversine import haversine
from datetime import datetime 
from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Empresa", layout =  "wide")


#----------------------
# Funções
#----------------------

def clean_code(df):
    """ Limpeza do Dataframe
        Tipos de Limpeza:
        1. Remoção dos NaN
        2. Mudança do tipo de coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo
    """
    #Limpeza de dados 
    df1 = df.copy()
    
    ## Remover valores Nulos
    df1 = df1.dropna()
    for i in range(19):
      linhas_vazias = df1.iloc[:,i] != 'NaN '
      df1 = df1.loc[linhas_vazias, :]
    df1 = df1.reset_index(drop = True)
    
    ## Remover Espaços 
    df1["ID"]= df1["ID"].str.strip()
    df1["Delivery_person_ID"]= df1["Delivery_person_ID"].str.strip()
    df1["Road_traffic_density"]= df1["Road_traffic_density"].str.strip()
    df1["Type_of_order"]= df1["Type_of_order"].str.strip()
    df1["Type_of_vehicle"]= df1["Type_of_vehicle"].str.strip()
    df1["Festival"]= df1["Festival"].str.strip()
    df1["City"]= df1["City"].str.strip()
    
    ## Convertendo em Inteiros 
    df1["Delivery_person_Age"]= df1["Delivery_person_Age"].astype(int)
    df1["multiple_deliveries"]= df1["multiple_deliveries"].astype(int)
    df1["Delivery_person_Ratings"]= df1["Delivery_person_Ratings"].astype(float)
    df1["Vehicle_condition"]= df1["Vehicle_condition"].astype(float)
    
    ##  Convertendo em Datetime
    df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format = "%d-%m-%Y")
    
    ## Convertendo Time_Taken
    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply(lambda x: x.split("(min)")[1])
    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)
    
    ## Criando Coluna Week_Year
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )

    return df1

def orders_by_day(df1):
    #Quantidade de pedidos por dia.
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    # gráfico
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    return fig 
    
def order_share(df1):
    # 3. Distribuição dos pedidos por tipo de tráfego.
    columns = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    return fig 

def traffic_city(df1):
    # 4. Comparação do volume de pedidos por cidade e tipo de tráfego.
    columns = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    #px.bar( df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group')
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density',size='ID', color='City')
    return fig 

def order_share_week (df1): 
    # Quantidade de pedidos por entregador por Semana
    # Quantas entregas na semana / Quantos entregadores únicos por semana
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig 
    
def order_week (df1):
    # 2. Quantidade de pedidos por semana.
    cols = ['ID', 'week_of_year']
    df_aux = df1.loc[:,cols ].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig 
    
def country_maps(df1):
        
    # 6. A localização central de cada cidade por tipo de tráfego.
    columns = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    columns_groupby = ['City', 'Road_traffic_density']
    
    data_plot = df1.loc[:, columns].groupby( columns_groupby ).median().reset_index()
    
    # Desenhar o mapa
    map = folium.Map( zoom_start=100 )
    for index, location_info in data_plot.iterrows():
       folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']], 
                      popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static(map, width =800, height = 600  )

    

#--------------------------------------------------------------------------------------------------------------------------------

    
# Import Dataset
df = pd.read_csv("train.crdownload")

# limpeza de Dados 
df1 = clean_code(df)
    

# =======================================
# Barra Lateral
# =======================================
st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value= datetime( 2022, 4,13 ),
    min_value= datetime(2022, 2, 11 ),
    max_value= datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """---""" )


traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low','High','Medium','Jam'],
    default = ['Low','High','Medium','Jam'])

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] <  date_slider 
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# =======================================
# Layout Streamlit 
# =======================================
st.header( 'Marketplace - Visão Empresa' )

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown ("# Orders by day")
        fig = orders_by_day( df1)
        st.plotly_chart( fig, use_container_width= True)

    with st.container():
        col1,col2 = st.columns (2)
        with col1:
            st.header ("Traffic Order Share")
            fig = order_share(df1)    
            st.plotly_chart (fig, use_container_width = True)
    
            
        with col2:
            st.header("Traffic Order City")
            fig = traffic_city(df1)
            st.plotly_chart (fig, use_container_width = True)
   
with tab2:
    with st.container():
        st.markdown ("Order Share by Week ")
        fig = order_share_week(df1)
        st.plotly_chart (fig, use_container_width = True)

        
    with st.container():
        st.markdown ("Order by Week ")
        fig = order_week(df1)
        st.plotly_chart (fig, use_container_width = True)

with tab3:
    st.markdown ("Country Maps")
    country_maps(df1)
    



















