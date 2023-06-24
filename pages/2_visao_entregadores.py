# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime 

from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Entregadores", layout =  "wide")

#-------------------------------------------------
# Funções
#--------------------------------------------------
def clean_code(df):
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

def avg_deliver(df1):
    df_avg_ratings_per_deliver = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                      .groupby( 'Delivery_person_ID' )
                                      .mean()
                                      .reset_index() )
    return df_avg_ratings_per_deliver

def avg_traffic(df1):        
    df_avg_std_rating_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                        .groupby( 'Road_traffic_density')
                                        .agg( {'Delivery_person_Ratings': ['mean', 'std' ]} ) )

    # mudanca de nome das colunas
    df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

    # reset do index
    df_avg_traffic = df_avg_std_rating_by_traffic.reset_index()
    return df_avg_traffic

def avg_weather(df1):
    df_avg_std_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                        .groupby( 'Weatherconditions')
                                        .agg( {'Delivery_person_Ratings': ['mean', 'std']} ) )

    # mudanca de nome das colunas
    df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

    # reset do index
    df_weather = df_avg_std_rating_by_weather.reset_index()
    return df_weather

def top_delivers ( df1, top_asc):
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby( ['City', 'Delivery_person_ID'] )
               .mean()
               .sort_values( ['City', 'Time_taken(min)'], ascending = top_asc ).reset_index() )
    
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
    return df3 

#----------------------------------------------------------------------------------------------------------------------------------------------
# Import dataset
df = pd.read_csv( 'train.crdownload' )

df1 = clean_code(df)


# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Entregadores' )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime(2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect( 
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] <  date_slider 
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


# =======================================
# Layout no Streamlit
# =======================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior de idade', maior_idade )
            
        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )
            
        with col3:
            # A maior idade dos entregadores
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao', melhor_condicao )
            
        with col4:
            # A menor idade dos entregadores
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condicao', pior_condicao )
            
    with st.container():
        st.markdown( """---""" )
        st.title( 'Avaliacoes' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliacao medias por Entregador' )
            df_avg = avg_deliver(df1)
            st.dataframe( df_avg )
                
        with col2:
            st.markdown( '##### Avaliacao media por transito' )
            df_traffic = avg_traffic(df1)
            st.dataframe( df_traffic )
         
            st.markdown( '##### Avaliacao media por clima' )
            df_weather = avg_weather(df1)
            st.dataframe( df_weather )
            
    
    with st.container():
        st.markdown( """---""" )
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Top Entregadores mais rapidos' )
            df_top = top_delivers (df1, top_asc = True)
            st.dataframe( df_top )
            
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df_down = top_delivers (df1, top_asc = False)
            st.dataframe( df_down )
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
                         
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        