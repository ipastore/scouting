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
import matplotlib.pyplot as plt
import seaborn as sns


#######################
# Page configuration
st.set_page_config(
    page_title="Scouting SL",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")
#######################


# #Init Cloudinary
# # LOCAL
# config = cloudinary.config(secure=True)

# # Load data LOCAL para Branches
# df_Arquero = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Arquero")
# df_Central = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Central")
# df_LatDer = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Lat Der")
# df_LatIzq = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Lat Izq")
# df_Contencion = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Contencion")
# df_Mixto = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Mixto")
# df_Ofensivo = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Ofensivo")
# df_Extremo = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Extremo")
# df_Centrodelantero = pd.read_excel("data/source_informes_LOCAL.xlsx", sheet_name="Centrodelantero")


# STREAMLIT
config = cloudinary.config(cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
                            api_key=st.secrets["CLOUDINARY_API_KEY"],
                            api_secret=st.secrets["CLOUDINARY_SECRET_KEY"],
                            secure=True)

df_Arquero = pd.read_excel("data/source_informes.xlsx", sheet_name="Arquero")
df_Central = pd.read_excel("data/source_informes.xlsx", sheet_name="Central")
df_LatDer = pd.read_excel("data/source_informes.xlsx", sheet_name="Lat Der")
df_LatIzq = pd.read_excel("data/source_informes.xlsx", sheet_name="Lat Izq")
df_Contencion = pd.read_excel("data/source_informes.xlsx", sheet_name="Contencion")
df_Mixto = pd.read_excel("data/source_informes.xlsx", sheet_name="Mixto")
df_Ofensivo = pd.read_excel("data/source_informes.xlsx", sheet_name="Ofensivo")
df_Extremo = pd.read_excel("data/source_informes.xlsx", sheet_name="Extremo")
df_Centrodelantero = pd.read_excel("data/source_informes.xlsx", sheet_name="Centrodelantero")



# Concatenate DataFrames
df = pd.concat([df_Central, df_Arquero,df_LatDer, df_LatIzq, df_Contencion,
                          df_Mixto, df_Ofensivo, df_Extremo, df_Centrodelantero], ignore_index=True)


# Optionally, replace NaN with None (pandas automatically uses NaN for missing values)
df = df.where(pd.notnull(df), None)



#Sidebar
with st.sidebar:
    col = st.columns((1,5,1), gap='medium')
    with col[1]:
        st.markdown("### Headers Scouting")


###Init Transfermarket
if "Filtro_Transfermarket" not in st.session_state:
    st.session_state["Filtro_Transfermarket"] = (0,100)

# Ensure the 'Transfermarket' column is numeric
df['Transfermarket'] = pd.to_numeric(df['Transfermarket'], errors='coerce')

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
    Club = df["Club"][0]
    Nacionalidad = df["Nacionalidad"][0]
    Fecha_Nacimiento = df["Fecha de Nacimiento"][0]
    Edad =  df["Edad"][0]
    Posicion = df["Posicion"][0]
    Posicion_Alternativa = df["Posicion Alternativa"][0]
    Categoria = df["Categoria"][0]
    Division = df["Division"][0]
    Seleccion = df["Seleccion"][0]
    Altura = df["Altura"][0]
    Peso = df["Peso"][0]
    Pierna = df["Pierna Habil"][0]
    Vencimiento_Contrato = df["Vencimiento Contrato"][0]
    Sueldo = df["Sueldo"][0]
    Transfermarket = df["Transfermarket"][0]
    Representante = df["Representante"][0]
    Nombre_Foto_Escudo = df["Nombre Foto Escudo"][0]
    Nombre_Foto_Jugador = df["Nombre Foto Jugador"][0]
    Nombre_Foto_Carrera_Club = df["Nombre Foto Carrera Club"][0]
    Nombre_Foto_Carrera_Seleccion = df["Nombre Foto Carrera Seleccion"][0]
    Nombre_Video_Compacto = df["Nombre Video Compacto"][0]
    Aspectos_Tecnicos_Tacticos = df["Aspectos Tecnicos Tacticos"][0]
    Aspectos_Fisicos = df["Aspectos Fisicos"][0]
    Personalidad = df["Personalidad"][0]
    Otras_Observaciones = df["Otras Observaciones"][0]
    Cantidad_Videos = df["Cantidad Videos"][0]


    cols = st.columns((15,8,15), gap="small")
    
    # Foto Juagdor
    with cols[0]:
        path_Foto = f"data/fotos/jugadores/{Nombre_Foto_Jugador}"
        st.image(CloudinaryImage(public_id = path_Foto).build_url(
                    aspect_ratio = "1.0",
                    width = 300,
                    gravity="faces",
                    crop="fill",
                    # radius="max",
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
        n_rows = 10
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
        
        # Categoria
        with cols_grid[18]:
            st.markdown("<p><b>Categoría</b></p>", unsafe_allow_html=True)
        with cols_grid[19]:
            if not pd.isna(Categoria):
                st.markdown(Categoria)
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

    # ###################### Plot ######################

    
    #  Arquero
    if Posicion == "Arquero":
            data = {
            'Attribute': ["Tecnica Individual", "Atajadas", "Pelotas Aereas", "De Libero",
               "Penales", "Circulacion", "Pase largo", "1 vs 1", "Posicionamiento Movilidad"],
             'Value': [df["Tecnica Individual"][0], df["Atajadas"][0], 
                   df["Pelotas Aereas"][0],
                    df["De Libero"][0], df["Penales"][0], 
                    df["Circulacion"][0], df["Pase largo"][0],
                     df["1 vs 1"][0], df["Posicionamiento Movilidad"][0]]
            }

    # Central
    elif Posicion == "Central":
        with cols[1]:
            data = {
            'Attribute': ["Tecnica Individual", "Anticipacion", "Duelos por abajo", "Duelos Aereos",
               "Salida", "Cierres-Coberturas", "Pase Paralelo", "1 vs 1", "Velocidad",
                 "Resistencia", "Pelota Detenida"],
             'Value': [df["Tecnica Individual"][0], df["Anticipacion"][0], 
                   df["Duelos por abajo"][0],
                    df["Duelos Aereos"][0], df["Salida"][0], 
                    df["Cierres-Coberturas"][0], df["Pase Paralelo"][0],
                     df["1 vs 1"][0], df["Velocidad"][0],
                     df["Resistencia"][0], df["Pelota Detenida"][0]]
                }
    
    elif Posicion == "Lateral Derecho":
        with cols[1]:
            data = {"Attribute": ["Tecnica Individual", "Anticipacion", "Duelos por abajo", 
                                  "Duelos aereos", "Salida", "Cierres/coberturas", "Pasa Paralelo",
                                  "1 vs 1 defensivo", "Velocidad", "Resistencia", "Centros",
                                  "1 vs 1 ofensivo", "Remates", "Juego Ofensivo"],
                    "Value": [df["Tecnica Individual"][0], df["Anticipacion"][0], df["Duelos por abajo"][0],
                              df["Duelos aereos"][0], df["Salida"][0], df["Cierres/coberturas"][0],
                              df["Pasa Paralelo"][0], df["1 vs 1 defensivo"][0], df["Velocidad"][0],
                              df["Resistencia"][0], df["Centros"][0], df["1 vs 1 ofensivo"][0],
                              df["Remates"][0], df["Juego Ofensivo"][0]]
                    }


    elif Posicion == "Lateral Izquierdo":
        with cols[1]:
            data = {"Attribute": ["Tecnica Individual", "Anticipacion", "Duelos por abajo",
                                    "Duelos aereos", "Salida", "Cierres/coberturas", "Pasa Paralelo",
                                    "1 vs 1 defensivo", "Velocidad", "Resistencia", "Centros",
                                    "1 vs 1 ofensivo", "Remates", "Juego Ofensivo"],
                        "Value": [df["Tecnica Individual"][0], df["Anticipacion"][0], df["Duelos por abajo"][0],
                                df["Duelos aereos"][0], df["Salida"][0], df["Cierres/coberturas"][0],
                                df["Pasa Paralelo"][0], df["1 vs 1 defensivo"][0], df["Velocidad"][0],
                                df["Resistencia"][0], df["Centros"][0], df["1 vs 1 ofensivo"][0],
                                df["Remates"][0], df["Juego Ofensivo"][0]]
                        }
    
    elif Posicion == "Contencion":
        with cols [1]:
            data = {"Attribute": ["Tecnica Individual", "Cambio de frente", "Pase espacio - filtrado",
                                    "Duelos aereos", "Salida - Circulacion", "Relevos/Vigilancias",
                                    "Recuperaciones", "Duelos por abajo", "Velocidad", "Resistencia",
                                    "Despliegue", "Coberturas/Cierres", "Remate"],
                        "Value": [df["Tecnica Individual"][0], df["Cambio de frente"][0], df["Pase espacio - filtrado"][0],
                                  df["Duelos aereos"][0], df["Salida - Circulacion"][0], df["Relevos/Vigilancias"][0],
                                  df["Recuperaciones"][0], df["Duelos por abajo"][0], df["Velocidad"][0],
                                  df["Resistencia"][0], df["Despliegue"][0], df["Coberturas/Cierres"][0],
                                  df["Remate"][0]]}

    
    elif Posicion == "Mixto":
        data = {"Attribute": ["Tecnica Individual", "Cambio de frente", "Pase espacio - filtrado",
                              "Duelos aereos", "Salida - Circulacion", "Duelos defensivos",
                              "Recuperaciones", "Duelos Ofensivos", "Velocidad", "Resistencia",
                              "Despliegue", "Remate", "Regate", "Centros"],
                "Value": [df["Tecnica Individual"][0], df["Cambio de frente"][0], df["Pase espacio - filtrado"][0],
                          df["Duelos aereos"][0], df["Salida - Circulacion"][0], df["Duelos defensivos"][0],
                          df["Recuperaciones"][0], df["Duelos Ofensivos"][0], df["Velocidad"][0],
                          df["Resistencia"][0], df["Despliegue"][0], df["Remate"][0], df["Regate"][0],
                          df["Centros"][0]]}

   
    elif Posicion == "Ofensivo":
        data = {"Attribute": ["Tecnica Individual", "Cambio de frente", "Pase espacio - filtrado",
                                "Asociaciones", "Regates", "Remates", "Retroceso Defensivo",
                                "Explosividad", "Velocidad", "Resistencia", "Determinacion"],
                "Value": [df["Tecnica Individual"][0], df["Cambio de frente"][0], df["Pase espacio - filtrado"][0],
                            df["Asociaciones"][0], df["Regates"][0], df["Remates"][0], df["Retroceso Defensivo"][0],
                            df["Explosividad"][0], df["Velocidad"][0], df["Resistencia"][0], df["Determinacion"][0]]}
        
    elif Posicion == "Extremo":
        data = {"Attribute": ["Tecnica Individual", "Asociaciones", "Centros", "Duelos aereos",
                              "Regates", "Remates", "Retroceso Defensivo", "Explosividad",
                              "Velocidad", "Resistencia", "Definicion/Peligrosidad"],
                "Value": [df["Tecnica Individual"][0], df["Asociaciones"][0], df["Centros"][0],
                          df["Duelos aereos"][0], df["Regates"][0], df["Remates"][0],
                          df["Retroceso Defensivo"][0], df["Explosividad"][0], df["Velocidad"][0],
                          df["Resistencia"][0], df["Definicion/Peligrosidad"][0]]}
    
    elif Posicion == "Centrodelantero":
        data = {"Attribute": ["Tecnica Individual", "Juego de espaldas", "Duelos aereos", "Regates",
                                "Remates", "Presion", "Movilidad/Desmarques", "Velocidad", "Resistencia",
                                "Definicion/Peligrosidad", "Explosividad", "Remate cabeza"],
                    "Value": [df["Tecnica Individual"][0], df["Juego de espaldas"][0], df["Duelos aereos"][0],
                            df["Regates"][0], df["Remates"][0], df["Presion"][0], df["Movilidad/Desmarques"][0],
                            df["Velocidad"][0], df["Resistencia"][0], df["Definicion/Peligrosidad"][0],
                            df["Explosividad"][0], df["Remate cabeza"][0]]}
            
    st.markdown("#### Evaluación Técnica")    
    cols = st.columns((5,20,5), gap="small")
    with cols[1]:
                fig = helpers.make_bar_plot(data)
                st.pyplot(fig)
                
    # ###################### Plot ######################
    
    
    # Aspectos Tecnicos
    if not pd.isna(Aspectos_Tecnicos_Tacticos):
        st.markdown("#### Aspectos Técnicos")
        st.markdown(Aspectos_Tecnicos_Tacticos)

    
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
    if not pd.isna(Nombre_Video_Compacto):
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