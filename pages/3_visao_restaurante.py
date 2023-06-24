# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from datetime import datetime 

from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Restaurantes", layout =  "wide")


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

def avg_distance (df1):
    cols = ["Restaurant_latitude","Restaurant_longitude",	"Delivery_location_latitude","Delivery_location_longitude"]
    avg_distance = df1.loc[:,cols].apply(lambda x : haversine((x["Restaurant_latitude"],x["Restaurant_longitude"]),(x["Delivery_location_latitude"],x["Delivery_location_longitude"])), axis = 1).mean()
    avg_distance = np.round(avg_distance,2)
    return avg_distance

def festival(df1, col, festival):          
    df_aux = (df1.loc[:,["Time_taken(min)", "Festival"]]
                 .groupby("Festival")
                 .agg({"Time_taken(min)":["mean", "std"]}))
    
    df_aux.columns = ["avg_time","std_time"]
    df_aux = df_aux.reset_index()
    
    linhas = df_aux["Festival"] == festival
    df_aux = np.round(df_aux.loc[linhas,col],2)
    return df_aux

def delivers_city(df1):            
    cols = ["City", "Time_taken(min)"]
    df_aux = (df1.loc[:,cols]
                 .groupby("City")
                 .agg({"Time_taken(min)":["mean","std"]})
                 .reset_index())
    df_aux.columns = ["City","avg_time","std_time"]
    
    
    fig = (go.Figure(data = [go.Bar(name = "Control", 
                                    x = df_aux["City"], 
                                    y = df_aux["avg_time"], 
                                    error_y = dict(type = "data", 
                                                   array = df_aux["std_time"]))]))
    return fig 


def distance_city(df1):
    cols = ["City", "Time_taken(min)","Type_of_order"]
    df_aux = (df1.loc[:,cols]
                 .groupby(["City","Type_of_order"])
                 .agg({"Time_taken(min)":["mean","std"]})
                 .reset_index())
    df_aux.columns = ["City","Tipo","mean","std"]
    return df_aux    

def avg_distance_city(df1):
    cols = ["Restaurant_latitude","Restaurant_longitude",	"Delivery_location_latitude","Delivery_location_longitude"]

    df1["distance"] = (df1.loc[:,cols]
                          .apply(lambda x:
                                haversine((x["Restaurant_latitude"],x["Restaurant_longitude"]),
                                          (x["Delivery_location_latitude"],x["Delivery_location_longitude"])), axis = 1))
    avg_distance = df1.loc[:,["City","distance"]].groupby("City").mean().reset_index()

    
    fig = go.Figure( data = [ go.Pie( labels = avg_distance["City"], 
                                      values = avg_distance["distance"], 
                                      pull = [0,0.1,0])])
    return fig 

def time_delivery(df1):
    cols = ["City", "Time_taken(min)","Road_traffic_density"]

    df_aux = (df1.loc[:,cols]
                 .groupby(["City","Road_traffic_density"])
                 .agg({"Time_taken(min)":["mean","std"]})
                 .reset_index())
    df_aux.columns = ["City","Traffic","avg_time","std_time"]
    
    fig = px.sunburst (df_aux, 
                       path = ["City","Traffic"],
                       values = "avg_time", 
                       color = "std_time", 
                       color_continuous_scale ="RdBu", 
                       color_continuous_midpoint = np.average (df_aux["std_time"]))
    return fig     
#----------------------------------------------------------------------------------------------------------------------------------------------
    
# Import dataset
df = pd.read_csv( 'train.crdownload' )

df1 = clean_code(df)



# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Restaurante' )

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
        col1, col2, col3, col4, col5, col6  = st.columns( 6 )
        
        with col1:
            delivery_unique = len(df["Delivery_person_ID"].unique())
            col1.metric("Entregadores ", delivery_unique)
            
        with col2:
            avg_distance = avg_distance(df1)
            col2.metric("Distancia", avg_distance)
            
        with col3:
            df_festival = festival(df1, col = "avg_time", festival = "Yes")
            col3.metric("Tempo médio c/Festival",df_festival)
            
        with col4:
            df_festival = festival(df1, col = "std_time", festival = "Yes")
            col4.metric("STD c/Festival",df_festival)
            
        with col5:
            df_festival = festival(df1, col = "avg_time", festival = "No")
            col5.metric("Tempo médio s/Festival",df_festival)

        with col6:
            df_festival = festival(df1, col = "std_time", festival = "No")
            col6.metric("STD s/Festival",df_festival)

    
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Tempo Médio de Entrega por cidade")
            fig = delivers_city(df1)
            st.plotly_chart(fig,use_container_width = True)
            
        with col2:
            st.markdown("#### Distribuição da Distancia")
            df_city = distance_city(df1)
            st.dataframe(df_city)

        
    with st.container():
        st.markdown("""---""")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Distancia média dos restaurantes")
            fig = avg_distance_city(df1)            
            st.plotly_chart(fig,use_container_width = True)
            
        with col2:
            st.markdown ("Tempo Médio da entrega")
            fig = time_delivery(df1)                
            st.plotly_chart(fig,use_container_width = True)


    
            
    
            






