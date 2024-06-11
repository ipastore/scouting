#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
from mplsoccer import PyPizza
from streamlit_dynamic_filters import DynamicFilters
from dotenv import load_dotenv
load_dotenv()
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
import helpers


#######################
# Page configuration
st.set_page_config(
    page_title="Entrenadores",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded")
alt.themes.enable("dark")

df_entrenadores = pd.read_excel("data/source_informes.xlsx", sheet_name="Entrenadores")

# with st.sidebar:
#     col = st.columns((1,5,1), gap='medium')

#     with col[1]:

#Filters
filters_entrenadores = {
    "Nombre Entrenador": None,
    "Club": None,
}
filters_entrenadores_name= ["Nombre Entrenador","Club"]

dynamic_filters_entrenadores = DynamicFilters(df_entrenadores, filters_entrenadores, filters_entrenadores_name)
dynamic_filters_entrenadores.display_filters(location='sidebar')

df_entrenadores = dynamic_filters_entrenadores.filter_df().reset_index()


with st.sidebar:
    st.button('Reset All Filters', on_click=helpers.clear_cache)

if len(df_entrenadores) > 1:
    st.write(df_entrenadores[["Nombre Entrenador", "Nacionalidad", "Club"]])


if len(df_entrenadores) == 1:

    Nombre_Entrenador = df_entrenadores["Nombre Entrenador"][0]
    Nacionalidad = df_entrenadores["Nacionalidad"][0]
    Club = df_entrenadores["Club"][0]
    Fecha_Nacimiento = df_entrenadores["Fecha de Nacimiento"][0]
    Edad =  df_entrenadores["Edad"][0]
    Esquemas = df_entrenadores["Esquemas Predilectos"][0]
    Nombre_Foto_Entrenador = df_entrenadores["Nombre Foto Entrenador"][0]
    Nombre_Foto_Escudo = df_entrenadores["Nombre Foto Escudo"][0]
    Nombre_Foto_Plantel_Club = df_entrenadores["Nombre Foto Plantel Club"][0]
    Nombre_Foto_Carrera_Entrenador = df_entrenadores["Nombre Foto Carrera Entrenador"][0]
    Fase_Ofensiva = df_entrenadores["Fase Ofensiva"][0]
    Nombre_Video_Fase_Ofensiva = df_entrenadores["Nombre Video Fase Ofensiva"][0]
    Fase_Defensiva = df_entrenadores["Fase Defensiva"][0]
    Nombre_Video_Fase_Defensiva = df_entrenadores["Nombre Video Fase Defensiva"][0]
    Transiciones = df_entrenadores["Transiciones"][0]
    Nombre_Video_Transiciones = df_entrenadores["Nombre Video Transiciones"][0]
    Otras_Observaciones = df_entrenadores["Otras Observaciones"][0]
    Nombre_Video_Otras_Observaciones = df_entrenadores["Nombre Video Otras Observaciones"][0]
    Ultimos_Partidos = df_entrenadores["Ultimos Partidos"][0]
    Nombre_Foto_Ultimos_Partidos1 = df_entrenadores["Nombre Foto Ultimos Partidos 1"][0]
    Nombre_Foto_Ultimos_Partidos2 = df_entrenadores["Nombre Foto Ultimos Partidos 2"][0]

    cols = st.columns((10,10,15), gap="small")
    
    with cols[0]:
        # Foto Entrenador
        path_Foto = f"data/fotos/entrenadores/{Nombre_Foto_Entrenador}"
        st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    aspect_ratio = "1.0",
                    width = 150,
                    gravity="faces",
                    crop="fill",
                    radius="max"))
        concat_Nombre_Entrenador = "<h3>" + Nombre_Entrenador +"</h3>"
        st.caption(concat_Nombre_Entrenador, unsafe_allow_html=True)

    with cols[1]:
        # Foto Escudo    
        path_Foto = f"data/fotos/escudos/{Nombre_Foto_Escudo}"
        concat_Club = "<h3>" + Club +"</h3>"
        st.image(CloudinaryImage(public_id = path_Foto).build_url(
            aspect_ratio = "1.0",
            width = 150,
            gravity="faces",
            crop="fill",
            radius="max"))
        st.caption(concat_Club, unsafe_allow_html=True)
    
    with cols[2]:
        # Descripciones
        n_cols = 2
        n_rows = 3
        rows = [st.container() for _ in range(n_rows)]
        cols_per_row = [r.columns(n_cols) for r in rows]
        cols_grid = [column for row in cols_per_row for column in row]

        ## Nacionalidad
        with cols_grid[0]:
            st.markdown("<p><b>Nacionalidad</b></p>", unsafe_allow_html=True)
        with cols_grid[1]:
            st.markdown(Nacionalidad)
        
        ## Fecha de Nacimiento
        with cols_grid[2]:
            st.markdown("<p><b>Fecha de Nacimiento</b></p>", unsafe_allow_html=True)
        with cols_grid[3]:
            concat_Fecha_Nacimiento_Edad = str(Fecha_Nacimiento) + " (" + str(Edad) + " años)"
            st.markdown(concat_Fecha_Nacimiento_Edad)
        
        ## Esquemas Predilectos
        with cols_grid[4]:
            st.markdown("<p><b>Esquemas predilectos</b></p>", unsafe_allow_html=True)
        with cols_grid[5]:
            st.markdown(Esquemas)

    # Plantel Club
    if not pd.isna(Nombre_Foto_Plantel_Club):
        st.markdown("#### Plantel")
        
        cols = st.columns((5,10,5), gap="small")

        with cols[1]:

            path_Foto = f"data/fotos/plantel_club/{Nombre_Foto_Plantel_Club}"
            st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    width = 1000))


    # Carrera Entrenador
    if not pd.isna(Nombre_Foto_Carrera_Entrenador):
        st.markdown("#### Carrera Entrenador")
        path_Foto = f"data/fotos/carrera_entrenadores/{Nombre_Foto_Carrera_Entrenador}"
        st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    width = 1000))
        
    # Fase Ofensiva
    if not pd.isna(Fase_Ofensiva): 
        st.markdown("#### Fase Ofensiva")
        st.markdown(Fase_Ofensiva)
    if not pd.isna(Nombre_Video_Fase_Ofensiva): 
        st.video(Nombre_Video_Fase_Ofensiva)

    ## Fase Defensiva
    if not pd.isna(Fase_Defensiva): 
        st.markdown("#### Fase Defensiva")
        st.markdown(Fase_Defensiva) 
    if not pd.isna(Nombre_Video_Fase_Defensiva):
        st.video(Nombre_Video_Fase_Defensiva)
    
    ## Transiciones
    if not pd.isna(Transiciones):
        st.markdown("#### Transiciones")
        st.markdown(Transiciones)
    if not pd.isna(Nombre_Video_Transiciones):    
        st.video(Nombre_Video_Transiciones)	


    ## Observaciones   
    if not pd.isna(Otras_Observaciones): 
        st.markdown("#### Otras Observaciones")
        st.markdown(Otras_Observaciones)  
    if not pd.isna(Nombre_Video_Otras_Observaciones):
        st.video(Nombre_Video_Otras_Observaciones)	

    ## Ultimos partidos
    if not pd.isna(Nombre_Foto_Ultimos_Partidos1) or not pd.isna(Nombre_Foto_Ultimos_Partidos2) or not pd.isna(Ultimos_Partidos):
        st.markdown("#### Últimos Partidos")
        
        # Descripcion Ultimos Partidos
        if not pd.isna(Ultimos_Partidos):
            st.markdown(Ultimos_Partidos)
        

        cols = st.columns((5,10,5), gap="small")

        with cols[1]:
        
            # Foto Ultimos Partidos1
            path_Foto = f"data/fotos/alineaciones/{Nombre_Foto_Ultimos_Partidos1}"
            st.image(CloudinaryImage(public_id = path_Foto).build_url(
                        width = 1000))

            # Foto Ultimos Partidos2
            path_Foto = f"data/fotos/alineaciones/{Nombre_Foto_Ultimos_Partidos2}"
            st.image(CloudinaryImage(public_id = path_Foto).build_url(
                        width = 1000))

