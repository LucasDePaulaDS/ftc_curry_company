import streamlit as st

st.set_page_config(page_title="Home")


st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write("# Curry Company Growth Dashboard")

st.markdown (
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    -  Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento semanal dos indicadores dos entregadores.
    - Visão Restaurante: 
        - Acompanhamento semanal dos indicadores dos restaurantes.
    ### Ask for Help
    - Lucas de Paula
""")
    