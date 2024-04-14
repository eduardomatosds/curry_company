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
    page_title="Visão Empresa",
    page_icon='',
    layout='wide'
)
#------------------------------------------
     #funções
#------------------------------------------
def country_maps (df1):
    
    cols=['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux=(df1.loc[:,cols]
                    .groupby(['City','Road_traffic_density'])
                    .median()
                    .reset_index())
    df_aux=df_aux.loc[df_aux["City"]!='NaN', :]
    df_aux=df_aux.loc[df_aux['Road_traffic_density']!= 'NaN', :] 

    map=folium.Map()
    for index,location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City','Road_traffic_density']] ).add_to(map)
        

    folium_static( map , width=1024 ,height=600)


def order_share_by_week (df1):
    
         
    df_aux=df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2=(df1.loc[:,['Delivery_person_ID','week_of_year']]
                .groupby('week_of_year')
                .nunique()
                .reset_index())
    df_aux=pd.merge(df_aux,df_aux2,how='inner', on='week_of_year')
    df_aux['order_by_delivery']=df_aux['ID']/df_aux['Delivery_person_ID']
    fig=px.line(df_aux,x='week_of_year',y='order_by_delivery')
        
    return fig

def order_by_week (df1):
    
    df1['week_of_year']=df1['Order_Date'].dt.strftime('%U')
    df_aux=df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig=px.line(df_aux,x='week_of_year',y='ID')
    
    return fig

def order_by_days(df1):
    
    df_aux=(df1.loc[:,['ID','Order_Date']]
               .groupby('Order_Date')
               .count()
               .reset_index())
    fig=px.bar(df_aux,x='Order_Date',y='ID')

    return fig

def traffic_order_share(df1):
    df_aux=(df1.loc[:,['ID','Road_traffic_density']]
               .groupby('Road_traffic_density')
               .count()
               .reset_index())
    df_aux['perc_ID']=df_aux['ID']/df_aux['ID'].sum()
    fig=px.pie(df_aux, values='perc_ID',names='Road_traffic_density')
    
    return fig

def traffic_order_city(df1):
    df_aux=(df1.loc[:,['ID','City','Road_traffic_density']]
               .groupby(['City','Road_traffic_density'])
               .count()
               .reset_index())
    fig=px.scatter(df_aux,x='City',y='Road_traffic_density',size='ID',color='City')

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

#Barra lateral
st.header('Marketplace - Visão Cliente')

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
#Filtro de data

linhas_selecionadas=df1['Order_Date'] < date_slider
df1=df1.loc[linhas_selecionadas,:]
#filtro de transito
linhas_selecionadas=df1['Road_traffic_density'].isin(trafic_option)
df1=df1.loc[linhas_selecionadas,:]

#st.dataframe(df1)
#=====================================
#layout streamlit
#======================================
tab1,tab2,tab3=st.tabs(['visão gerencial','visão tática','visão geográfica'])

with tab1:
    with st.container():
        fig=order_by_days(df1)
        st.markdown('# Order by Days')
        st.plotly_chart(fig,use_container_width=True)
                
    with st.container():
        col1,col2=st.columns(2)
        with col1:
            fig=traffic_order_share(df1)
            st.markdown('# Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig=traffic_order_city(df1)
            st.markdown('# Traffic Order City')
            st.plotly_chart(fig,use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig=order_by_week (df1)
        st.plotly_chart(fig,use_container_width=True )


    with st.container():
        st.markdown('# Order Share by Week')
        fig=order_share_by_week(df1)
        st.plotly_chart(fig,use_container_width=True) 
        
            

with tab3:
     st.markdown('#  Country Maps')
     country_maps(df1)
     
    




