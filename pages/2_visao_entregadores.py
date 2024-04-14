from haversine import haversine 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import streamlit as st
from datetime import datetime
from PIL import Image 
import folium
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Visão Entregadores",
    page_icon='',
    layout='wide'
)

#------------------------------------------
     #funções
#------------------------------------------
def top_deliverys(df1, top_asc):
    df2=(df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']].groupby(['City','Delivery_person_ID'])
                                                                   .mean()
                                                                   .sort_values(['City','Time_taken(min)'], ascending=top_asc)
                                                                   .reset_index())
    df_aux1=df2.loc[df2['City']=='Metropolitian',:].head(10)
    df_aux2=df2.loc[df2['City']=='Urban',:].head(10)
    df_aux3=df2.loc[df2['City']=='Semi_Urban',:].head(10)
    df3=pd.concat([df_aux1,df_aux2,df_aux3]).reset_index(drop=True)
    return df3



def clean_code(df1):
    """ Esta função tem responsabilidade de limpeza do dataframe
    
        Tipos de limpeza:
        
        1:Limpeza da coluna de tempo
        2:limpando NaN
        3:Mudança de tipo de colunas de dados
        4:Remoção dos espaços da variaveis de texto
        5:formatação da coluna Datas

        Input:Dataframe
        Output:Dataframe
    """   
    df1.dropna(inplace=True)
    #Removendo NaN
    linha=df1['multiple_deliveries']!='NaN '
    df1=df1.loc[linha,:].copy()
    linha=df1['Road_traffic_density']!='NaN '
    df1=df1.loc[linha,:].copy()
    linha=df1['City']!='NaN'
    df1=df1.loc[linha,:].copy()
    linha=df1 ['Delivery_person_Age']!='NaN '
    df1=df1.loc[linha,:].copy()
    #1 convertendo a coluna age para int
    df1['Delivery_person_Age'] =df1['Delivery_person_Age'].astype(int)
    #2 convertendo a coluna ratings para numero decimal(float)
    df1['Delivery_person_Ratings']=df1['Delivery_person_Ratings'].astype(float)
    #3 convertendo orde dat para data
    df1['Order_Date']=pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')
    #4 convertendo multiple_deliveries  para int
    df1['multiple_deliveries']=df1['multiple_deliveries'].astype(int)
    #5 removendo espaço dentro de strings texto\object
    df1.loc[:,'ID']=df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Type_of_order']=df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Delivery_person_ID']=df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density']=df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_vehicle']=df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City']=df1.loc[:,'City'].str.strip()
    df1.loc[:,'Time_taken(min)']=df1.loc[:,'Time_taken(min)'].str.strip()

    #limpando o min
    df1['Time_taken(min)']=df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)']=df1['Time_taken(min)'].astype(int)

    return df1

df=pd.read_csv("train.csv")
df1=clean_code(df)



#---------------------
#Barra lateral
#---------------------
st.header('Marketplace - Visão Entregadores')

image=Image.open('logo.png')
st.sidebar.image(image,width=120)
st.sidebar.markdown('# Curry Cumpany')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider=st.sidebar.slider(
    "Até qual valor?",
    value=datetime(2022,4,13),
    min_value=datetime(2022,2,11),
    max_value=datetime(2022,4,6),
    format="MM.DD.YYYY")
st.sidebar.markdown("""---""")

trafic_option=st.sidebar.multiselect(
    'Quais as condições de transito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Comunidade DS')

#filtro de data
linhas_selecionadas=df1['Order_Date'] < date_slider
df1=df1.loc[linhas_selecionadas,:]

#filtro de transito
linhas_selecionadas=df1['Road_traffic_density'].isin(trafic_option)
df1=df1.loc[linhas_selecionadas,:]

#==========================
#layout do Streamlit
#==========================

tab1,tab2,tab3=st.tabs(['Visão gerencial','',''])

with tab1:
    with st.container():
        st.markdown('# Overval Metrics')
        
        col1,col2,col3,col4=st.columns(4, gap='large')
        
        with col1:
       
            maior_idade=df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade',maior_idade)


            

        with col2:
            
            menor_idade=df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade',menor_idade)


        with col3:
           
            melhor_condicao=df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição de veiculo',melhor_condicao)



        with col4:
           
            pior_condicao=df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição de veiculo',pior_condicao)



        with st.container():
            
            st.markdown('''---''')
            st.title('Avaliações')
            


            col1,col2=st.columns(2)

            with col1:
                st.markdown('##### Avaliação media por Entregador')
                df_avaliacao_media=(df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                       .groupby('Delivery_person_ID')
                                       .mean()
                                       .reset_index())
                st.dataframe(df_avaliacao_media)

            with col2:
                st.markdown('##### Avaliação media por transito ')
                df_avaliacao_media_transito=(df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                                .groupby('Road_traffic_density')
                                                .agg({'Delivery_person_Ratings':['mean','std']}))
                
                df_avaliacao_media_transito.columns=['delivery_mean','delivery_std']
                df_avaliacao_media_transito.reset_index()
                st.dataframe(df_avaliacao_media_transito)
                

                
                st.markdown('##### Avaliação media por clima ')
                df_avaliacao_media_clima=(df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                             .groupby('Weatherconditions')
                                             .agg({'Delivery_person_Ratings':['mean','std']}))

                df_avaliacao_media_clima.columns=['delivery_mean','delivery_std']
                df_avaliacao_media_clima=df_avaliacao_media_clima.reset_index()
                st.dataframe(df_avaliacao_media_clima)
                
            st.markdown('''---''')

        with st.container():
            
            st.markdown('# Velocidade de entrega')
            col1,col2=st.columns(2)

            with col1:
                st.markdown('##### Top entregadores mais rapidos')
                df3=top_deliverys(df1,top_asc=True)
                st.dataframe(df3)


            with col2:
                st.markdown('##### Top entregadores mais lentos')
                df3=top_deliverys(df1,top_asc=False)
                st.dataframe(df3)
                
       
      







   









