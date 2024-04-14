from haversine import haversine 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import streamlit as st
from datetime import datetime
from PIL import Image 
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(
    page_title="Visão Restaurantes",
    page_icon='',
    layout='wide'
)

#-----------------------
#    Funcões
#-----------------------
def avg_std_time_on_traffic(df1):

    cols=['City','Time_taken(min)','Road_traffic_density']        
    df_aux=(df1.loc[:,['City','Time_taken(min)','Road_traffic_density']]
               .groupby(['City','Road_traffic_density'])
               .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns=['avg_time','std_time']
    df_aux=df_aux.reset_index()
    fig=px.sunburst(df_aux,path=['City','Road_traffic_density'],values='avg_time',
                          color='std_time',color_continuous_scale='RdBu',
                          color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig
def avg_std_time_graph(df1):
    
    
    df_aux=df1.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})

    df_aux.columns=['avg_time','std_time']       
    df_aux=df_aux.reset_index()
    fig=go.Figure()
    fig.add_trace (go.Bar(name='Control',x=df_aux['City'],y=df_aux['avg_time'],error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
                
    return fig
def avg_std_time_delivery(df1, Festival, op):
    """
        Esta função calcula o tempo medio eo desvio padrão das entregas
        Parametros:
           input:
             -df: dataframe com os dados necessarios para o calculo
             -op: Tipo de operação que precisa ser calculado
                 'avg_time':calcula o tempo medio 
                 'std_time': calcula o desvio padrão

           output:
             - df: dataframe com 2 colunas e 1 linha
    
    """
          
    df_aux=(df1.loc[:,['Time_taken(min)','Festival']]
               .groupby('Festival')
               .agg({'Time_taken(min)':['mean','std']}) )

    df_aux.columns=['avg_time','std_time']
    df_aux=df_aux.reset_index()
    df_aux=np.round (df_aux.loc[df_aux['Festival']==Festival,op],2)

                
    return df_aux
    
def distance(df1,fig):
    if fig==False:
        coluns=['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude'] 
        df1['distance']=df1.loc[:,coluns].apply(lambda x:
                            haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                      (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
        avg_distance=np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        coluns=['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df1['distance']=df1.loc[:,coluns].apply(lambda x:
                                        haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                  (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
        avg_distance=np.round(df1['distance'].mean(), 2)
        avg_distance=df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
        fig=go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['distance'],pull=[0,0.1,0])])
        
        return fig

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
    linha=df1['City']!='NaN '
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
    df1.loc[:,'Festival']=df1.loc[:,'Festival'].str.strip()
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
#------------------------
  #Barra lateral
#-------------------------
st.header('Marketplace - Visão Restaurantes')

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

#layout do Streamlit
tab1,tab2,tab3=st.tabs(['Visão gerencial','',''])

with tab1:
    with st.container():
        st.markdown('### visao restaurante')

        col1,col2,col3,col4,col5,col6=st.columns(6)

        with col1:
            e_unicos= len (df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('entregadores_unicos',e_unicos)

        with col2:
            avg_distance=distance(df1,fig=False)
            col2.metric('Distancia_media',avg_distance)
            
        with col3:

            df_aux=avg_std_time_delivery(df1,'Yes','avg_time')
            col3.metric('Tempo medio de entrega', df_aux)
            
        with col4:
            df_aux=avg_std_time_delivery(df1,'Yes','std_time')
            col4.metric('Desvio padrão das entregas ', df_aux)


        with col5:  
            df_aux=avg_std_time_delivery(df1,'No','avg_time')
            col5.metric('tempo medio ce entrega C/ Festival ', df_aux)



        with col6:
            
            df_aux=avg_std_time_delivery(df1,'No','std_time')
            col6.metric('Desvio padrão das entregas ', df_aux)

           

    with st.container():
        st.markdown('''---''')
        col1,col2=st.columns(2)
        with col1:
            fig=avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)
        

            
        with col2:
            df_aux=df1.loc[:,['City','Time_taken(min)','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})

            df_aux.columns=['avg_time','std_time']
            df_aux=df_aux.reset_index()

            st.dataframe(df_aux)
            
    with st.container():
        
        st.markdown('''---''')

        st.title('Distribuição do tempo')

        col1,col2=st.columns(2)
        with col1:
            fig=distance(df1,fig=True)
            st.plotly_chart(fig, use_container_width=True) 

        with col2:
            fig=avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
            

            


        












