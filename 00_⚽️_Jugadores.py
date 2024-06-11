#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
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
    page_title="Scouting SL",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")
#######################

# Load data
df = pd.read_excel("data/source_informes.xlsx", sheet_name="Jugadores")


##Init Cloudinary
# # LOCAL
# config = cloudinary.config(secure=True)

# STREAMLIT
config = cloudinary.config(cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
                            api_key=st.secrets["CLOUDINARY_API_KEY"],
                            api_secret=st.secrets["CLOUDINARY_SECRET_KEY"],
                            secure=True)

#Sidebar
with st.sidebar:
    col = st.columns((1,5,1), gap='medium')

    with col[1]:
        Nombre_Escudo = "San_Lorenzo"
        path_Escudo = f"data/fotos/escudos/{Nombre_Escudo}"
        result_photo = cloudinary.Search()  .expression(f"resource_type:image AND public_id={path_Escudo}").execute()
        st.image(result_photo["resources"][0]["url"], width=100)

    
    col = st.columns((5,50,5), gap='medium')

    with col[1]:
       st.markdown("# San Lorenzo")
    
    st.markdown("### Scouting")


###Init Transfermarket
if "Filtro_Transfermarket" not in st.session_state:
    st.session_state["Filtro_Transfermarket"] = (0,100)


with st.sidebar:
    _min = float(df["Transfermarket"].min())
    _max = float(df["Transfermarket"].max())
    step = (_max - _min) / 100
    Filtro_Transfermarket = st.slider( "Valor de Mercado", _min, _max,step=step, key="Filtro_Transfermarket")


df = df[df["Transfermarket"].between(*st.session_state.Filtro_Transfermarket)].reset_index()
#Filters
filter_jugadores =  {
    "Posicion": None,
    "Pierna Habil": None,
    "Division": None,
    "Categoria": None,
    "Vencimiento Contrato": None,
    "Nombre Jugador": None,
}

#Dynamic Filters
filter_jugadores_name = ["Posicion", "Pierna Habil", 
                         "Division", "Categoria", "Vencimiento Contrato", 
                         "Nombre Jugador"]

dynamic_filters_jugadores = DynamicFilters(df, filter_jugadores)
dynamic_filters_jugadores.display_filters(location='sidebar')

df = dynamic_filters_jugadores.filter_df().reset_index()

with st.sidebar:
    st.button('Reset All Filters', on_click=helpers.clear_cache)


#Rendering without filter
if len(df) > 1:
    st.write(df[["Nombre Jugador", "Posicion", "Pierna Habil", "Transfermarket"]])


#Rendering with filter
if len(df) == 1:

    #Data
    Nombre_Jugador = df["Nombre Jugador"][0]
    Edad =  df["Edad"][0]
    Posicion = df["Posicion"][0]
    Control =  df["Control"][0]
    Tension_Pase =  df["Tension_Pase"][0]
    Pase_Primera = df["Pase_Primera"][0]
    Pase_Diagonal_Circulacion = df["Pase_Diagonal_Circulacion"][0]
    Pase_Interior_Circulacion = df["Pase_Interior_Circulacion"][0]
    Anticipo = df["Anticipo"][0]
    Cobertura_Relevo = df["Cobertura_Relevo"][0]
    Pierna = df["Pierna Habil"][0]
    Cantidad_Videos = df["Cantidad_Videos"][0]
    Nombre_Foto_Jugador = df["Nombre_Foto_Jugador"][0]
    Nombre_Foto_Escudo = df["Nombre_Foto_Escudo"][0]
    Nacionalidad = df["Nacionalidad"][0]
    Seleccion = df["Seleccion"][0]
    Altura = df["Altura"][0]
    Peso = df["Peso"][0]
    Vencimiento_Contrato = df["Vencimiento Contrato"][0]
    Sueldo = df["Sueldo"][0]
    Representante = df["Representante"][0]
    Club = df["Club"][0]
    Transfermarket = df["Transfermarket"][0]
    Nombre_Foto_Carrera_Club = df["Nombre_Foto_Carrera_Club"][0]
    Nombre_Foto_Carrera_Seleccion = df["Nombre_Foto_Carrera_Seleccion"][0]
    Aspectos_Tecnicos = df["Aspectos_Tecnicos"][0]
    Aspectos_Tacticos = df["Aspectos_Tacticos"][0]
    Aspectos_Fisicos = df["Aspectos_Fisicos"][0]
    Personalidad = df["Personalidad"][0]
    Otras_Observaciones = df["Otras_Observaciones"][0]
    Nombre_Video_Compacto = df["Nombre_Video_Compacto"][0]


    cols = st.columns((15,8,15), gap="small")
    
    # Foto Juagdor
    with cols[0]:
        path_Foto = f"data/fotos/jugadores/{Nombre_Foto_Jugador}"
        st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    aspect_ratio = "1.0",
                    width = 300,
                    gravity="faces",
                    crop="fill",
                    radius="max",
                    ))
        concat_Nombre_Jugador = "<h2>" + Nombre_Jugador +"</h2>"
        st.caption(concat_Nombre_Jugador, unsafe_allow_html=True)
    
    # Foto Escudo
    with cols[1]:
        path_Foto = f"data/fotos/escudos/{Nombre_Foto_Escudo}"
        st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    aspect_ratio = "1.0",
                    width = 150,
                    gravity="faces",
                    crop="fill",
                    # radius="max",
                    ))
        concat_Club = "<h2>" + Club +"</h2>"
        st.caption(concat_Club, unsafe_allow_html=True)
    
    # Grid de Informacion
    with cols[2]:
        n_cols = 2
        n_rows = 9
        rows = [st.container() for _ in range(n_rows)]
        cols_per_row = [r.columns(n_cols) for r in rows]
        cols_grid = [column for row in cols_per_row for column in row]

        # Nacionalidad
        with cols_grid[0]:
            st.markdown("<p><b>Nacionalidad</b></p>", unsafe_allow_html=True)
        with cols_grid[1]:
            if not pd.isna(Nacionalidad):
                st.markdown(Nacionalidad)
            else:
                st.markdown("-")
        
        # Seleccion Nacional
        with cols_grid[2]:
            st.markdown("<p><b>Selección Nacional</b></p>", unsafe_allow_html=True)
        with cols_grid[3]:
            if not pd.isna(Seleccion):
                st.markdown(Seleccion)
            else:
                st.markdown("-")        
        
        # Altura
        with cols_grid[4]:
            st.markdown("<p><b>Altura</b></p>", unsafe_allow_html=True)
        with cols_grid[5]:
            if not pd.isna(Altura):
                concat_Altura = str(Altura) + " m"
                st.markdown(concat_Altura)
            else:
                st.markdown("-")
       
        # Peso
        with cols_grid[6]:
            st.markdown("<p><b>Peso</b></p>", unsafe_allow_html=True)
        with cols_grid[7]:
            if not pd.isna(Peso):
                concat_Peso = str(Peso) + " kg"
                st.markdown(concat_Peso)
            else:
                st.markdown("-")
        
        # Pierna Habil
        with cols_grid[8]:
            st.markdown("<p><b>Pierna Hábil</b></p>", unsafe_allow_html=True)
        with cols_grid[9]:
            if not pd.isna(Pierna):
                st.markdown(Pierna)
            else:
                st.markdown("-")
        
        # Vencimiento Contrato
        with cols_grid[10]:
            st.markdown("<p><b>Fin de Contrato</b></p>", unsafe_allow_html=True)
        with cols_grid[11]:
            if not pd.isna(Vencimiento_Contrato):
                st.markdown(Vencimiento_Contrato) 
            else:
                st.markdown("-") 
        
        # Valor de Mercado
        with cols_grid[12]:
            st.markdown("<p><b>Valor de Mercado</b></p>", unsafe_allow_html=True)
        with cols_grid[13]:
            if not pd.isna(Transfermarket):
                concat_Transfermarket = str(Transfermarket) + " MM"
                st.markdown(concat_Transfermarket)
            else:
                st.markdown("-")
        
        # Sueldo
        with cols_grid[14]:
            st.markdown("<p><b>Sueldo</b></p>", unsafe_allow_html=True)
        with cols_grid[15]:
            if not pd.isna(Sueldo):
                concat_Sueldo = str(Sueldo) + " USD"
                st.markdown(concat_Sueldo)
            else:
                st.markdown("-")

        # Representante
        with cols_grid[16]:
            st.markdown("<p><b>Representante</b></p>", unsafe_allow_html=True)
        with cols_grid[17]:
            if not pd.isna(Representante):
                st.markdown(Representante)
            else:
                st.markdown("-")

    
    # Carreras
    cols = st.columns((10,10), gap="small")

    # Carrera Club
    with cols[0]:
        if not pd.isna(Nombre_Foto_Carrera_Club): 
                st.markdown("#### Carrera en Clubes")
                path_Foto= f"data/fotos/carrera_club/{Nombre_Foto_Carrera_Club}"
                st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    # aspect_ratio = "1.0",
                    # width = 150,
                    # gravity="faces",
                    # crop="fill",
                    # radius="max",
                    ))

   
    # Carrera Seleccion
    with cols[1]:
        if not pd.isna(Nombre_Foto_Carrera_Seleccion):
                st.markdown("#### Carrera en Seleccion")
                path_Foto = f"data/fotos/carrera_seleccion/{Nombre_Foto_Carrera_Seleccion}"
                st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    # aspect_ratio = "1.0",
                    # width = 150,
                    # gravity="faces",
                    # crop="fill",
                    # radius="max",
                    ))

    # Radar
    cols = st.columns((5,10,5), gap="small")
    
    # Radar Volante Contencion
    if Posicion == "Volante Contencion":
        
        with cols[1]:
        #Plot
            slice_colors = ["blue"] + ["green"]  + ["red"] *2
            text_colors = ["white"]*4
            names =  ["Control", "Tensión de pase", "Pase de primera", "Anticipo"]
            percentiles = [Control,Tension_Pase,Pase_Primera, Anticipo]
            size_radar = 3

            radar = helpers.make_radar(names, percentiles, slice_colors, text_colors, size_radar)

            st.pyplot(radar, use_container_width=False)

    # Radar Volante Ofensivo
    elif Posicion == "Volante Ofensivo":

        with cols[1]:
                
             #Plot
            slice_colors = ["blue"]*5 + ["green"]*5 + ["red"]*5
            text_colors = ["white"]*15
            names =  ["Control", "Tensión de pase", "Pase Interior en Circulación", "Pase Diagonal en Circulación", "Cobertura de Relevo",
                      "Control", "Tensión de pase", "Pase Interior en Circulación", "Pase Diagonal en Circulación", "Cobertura de Relevo",
                      "Control", "Tensión de pase", "Pase Interior en Circulación", "Pase Diagonal en Circulación", "Cobertura de Relevo"]
            percentiles = [Control,Tension_Pase, Pase_Interior_Circulacion, Pase_Diagonal_Circulacion, Cobertura_Relevo,
                           Control,Tension_Pase, Pase_Interior_Circulacion, Pase_Diagonal_Circulacion, Cobertura_Relevo,
                           Control,Tension_Pase, Pase_Interior_Circulacion, Pase_Diagonal_Circulacion, Cobertura_Relevo]
            size_radar = 3
    
            radar = helpers.make_radar(names, percentiles, slice_colors, text_colors,size_radar)
    
    
            st.pyplot(radar, use_container_width=False) 

    
    # Aspectos Tecnicos
    if not pd.isna(Aspectos_Tecnicos):
        st.markdown("#### Aspectos Técnicos")
        st.markdown(Aspectos_Tecnicos)

    # Aspectos Tacticos
    if not pd.isna(Aspectos_Tacticos):
        st.markdown("#### Aspectos Tácticos")
        st.markdown(Aspectos_Tacticos)
    
    # Aspectos Fisicos
    if not pd.isna(Aspectos_Fisicos):
        st.markdown("#### Aspectos Físicos")
        st.markdown(Aspectos_Fisicos)	
    
    # Personalidad
    if not pd.isna(Personalidad):
        st.markdown("#### Personalidad y Perfil Psicológico")
        st.markdown(Personalidad)	

    # Otras Observaciones
    if not pd.isna(Otras_Observaciones):
        st.markdown("#### Otras Observaciones")
        st.markdown(Otras_Observaciones)	

    # Video Compacto
    if not pd.isna(Otras_Observaciones):
        st.markdown("#### Video Compacto")
        st.video(Nombre_Video_Compacto)
  

    #Videos partidos
    if not pd.isna(Cantidad_Videos):
        for x in range(Cantidad_Videos):
            concat_Nombre_Video = "Nombre_Video_" + str(x+1)
            concat_Descripcion_Video = "Descripcion_Video_" + str(x+1)
            concat_Titulo_video = "Titulo_Video_" + str(x+1)
            Titulo_Video = df[concat_Titulo_video][0]
            Nombre_Video = df[concat_Nombre_Video][0]
            Descripcion_Video = df[concat_Descripcion_Video][0]
            string_Titulo_Video = "#### " + Titulo_Video
            st.markdown(string_Titulo_Video)
            st.video(Nombre_Video)
            st.markdown(Descripcion_Video)