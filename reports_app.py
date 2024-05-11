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



#######################
#Functions

#Plot
def make_radar(names, percentiles, slice_colors, text_colors, size):
   
    baker = PyPizza(
            params=names,                  # list of parameters
            straight_line_color="#000000",  # color for straight lines
            straight_line_lw=1,             # linewidth for straight lines
            last_circle_lw=1,               # linewidth of last circle
            other_circle_lw=1,              # linewidth for other circles
            other_circle_ls="-."            # linestyle for other circles
        )
    
    radar, ax = baker.make_pizza(
        percentiles,              # list of values
        figsize=(size, size),      # adjust figsize according to your need
        param_location=110,
        slice_colors=slice_colors,
        value_colors = text_colors,
        value_bck_colors=slice_colors,
        # where the parameters will be added
        kwargs_slices=dict(
            facecolor="cornflowerblue", edgecolor="#000000",
            zorder=2, linewidth=1
        ),                   # values to be used when plotting slices
        kwargs_params=dict(
            color="#000000", fontsize=5,
            # fontproperties=font_normal.prop, va="center"
        ),                   # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000", fontsize=5,
            # fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
         )                    # values to be used when adding parameter-values
        ) 

    return radar

#######################
# Page configuration
st.set_page_config(
    page_title="Scouting SL",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
#Clear Cache
def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)
        

# Load data
df = pd.read_excel("data/source_informes.xlsx")

#Init Cloudinary
config = cloudinary.config(secure=True)

# #Init filters
# if 'filters' not in st.session_state:
#     st.session_state['filters'] = ()


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


#Init Transfermarket

if "Filtro_Transfermarket" not in st.session_state:
    st.session_state["Filtro_Transfermarket"] = (0,100)


with st.sidebar:

    _min = float(df["Transfermarket"].min())
    _max = float(df["Transfermarket"].max())
    step = (_max - _min) / 100
    Filtro_Transfermarket = st.slider( "Valor de Mercado", _min, _max,step=step, key="Filtro_Transfermarket")




df = df[df["Transfermarket"].between(*st.session_state.Filtro_Transfermarket)].reset_index()
#Filters
dynamic_filters = DynamicFilters(df, filters=["Posicion", "Pierna Habil", "Division", "Categoria", "Vencimiento_Contrato", "Nombre_Jugador"])

dynamic_filters.display_filters(location='sidebar')

df = dynamic_filters.filter_df().reset_index()

with st.sidebar:
    st.button('Reset All Filters', on_click=clear_cache)


#Variables

if len(df) > 1:
    st.write(df[["Nombre_Jugador", "Posicion", "Pierna Habil", "Transfermarket"]])


if len(df) == 1:

    Nombre_Jugador = df["Nombre_Jugador"][0]
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
    Vencimiento_Contrato = df["Vencimiento_Contrato"][0]
    Sueldo = df["Sueldo"][0]
    Representante = df["Representante"][0]
    Club = df["Club"][0]
    Transfermarket = df["Transfermarket"][0]
    Nombre_Foto_Carrera_Club = df["Nombre_Foto_Carrera_Club"][0]
    Nombre_Foto_Carrera_Seleccion = df["Nombre_Foto_Carrera_Seleccion"][0]

    cols = st.columns((10,10,10), gap="small")
    
    with cols[0]:
        path_Foto_Jugador = f"data/fotos/jugadores/{Nombre_Foto_Jugador}"
        result_photo = cloudinary.Search().expression(f"resource_type:image AND public_id={path_Foto_Jugador}").execute()
        st.image(result_photo["resources"][0]["url"])
        concat_Nombre_Jugador = "<h2>" + Nombre_Jugador +"</h2>"
        st.caption(concat_Nombre_Jugador, unsafe_allow_html=True)
    
    with cols[1]:
        path_Foto_Escudo = f"data/fotos/escudos/{Nombre_Foto_Escudo}"
        concat_Club = "<h2>" + Club +"</h2>"
        result_photo = cloudinary.Search().expression(f"resource_type:image AND public_id={path_Foto_Escudo}").execute()
        st.image(result_photo["resources"][0]["url"])
        st.caption(concat_Club, unsafe_allow_html=True)
    
    with cols[2]:
        n_cols = 2
        n_rows = 9
        rows = [st.container() for _ in range(n_rows)]
        cols_per_row = [r.columns(n_cols) for r in rows]
        cols_grid = [column for row in cols_per_row for column in row]

        with cols_grid[0]:
            st.write("Nacionalidad")
        with cols_grid[1]:
            st.markdown(Nacionalidad)
        with cols_grid[2]:
            st.markdown("Selección Nacional")
        with cols_grid[3]:
            st.markdown(Seleccion)  
        with cols_grid[4]:
            st.markdown("Altura")
        with cols_grid[5]:
            concat_Altura = str(Altura) + " m"
            st.markdown(concat_Altura)
        with cols_grid[6]:
            st.markdown("Peso")
        with cols_grid[7]:
            concat_Peso = str(Peso) + " kg"
            st.markdown(concat_Peso)
        with cols_grid[8]:
            st.markdown("Pierna Hábil")
        with cols_grid[9]:
            st.markdown(Pierna)
        with cols_grid[10]:
            st.markdown("Fin de Contrato")
        with cols_grid[11]:
            st.markdown(Vencimiento_Contrato)  
        with cols_grid[12]:
            st.markdown("Valor de Mercado")
        with cols_grid[13]:
            concat_Transfermarket = str(Transfermarket) + " MM"
            st.markdown(concat_Transfermarket)
        with cols_grid[14]:
            st.markdown("Sueldo")
        with cols_grid[15]:
            concat_Sueldo = str(Sueldo) + " USD"
            st.markdown(concat_Sueldo)
        with cols_grid[16]:
            st.markdown("Representante")
        with cols_grid[17]:
            st.markdown(Representante)

    cols = st.columns((10,10), gap="small")

    with cols[0]:
        path_Foto_Carrera_Club = f"data/fotos/carrera_club/{Nombre_Foto_Carrera_Club}"
        st.markdown("#### Carrera en Clubes")
        result_photo = cloudinary.Search().expression(f"resource_type:image AND public_id={path_Foto_Carrera_Club}").execute()
        st.image(result_photo["resources"][0]["url"])
   
    with cols[1]:
        path_Foto_Carrera_Seleccion = f"data/fotos/carrera_seleccion/{Nombre_Foto_Carrera_Seleccion}"
        st.markdown("#### Carrera en Seleccion")
        result_photo = cloudinary.Search().expression(f"resource_type:image AND public_id={path_Foto_Carrera_Seleccion}").execute()
        st.image(result_photo["resources"][0]["url"])


    cols = st.columns((5,10,5), gap="small")
    
    if Posicion == "Volante Contencion":
        
        with cols[1]:
        #Plot
            slice_colors = ["blue"] + ["green"]  + ["red"] *2
            text_colors = ["white"]*4
            names =  ["Control", "Tensión de pase", "Pase de primera", "Anticipo"]
            percentiles = [Control,Tension_Pase,Pase_Primera, Anticipo]
            size_radar = 3

            radar = make_radar(names, percentiles, slice_colors, text_colors, size_radar)

            st.pyplot(radar, use_container_width=False) 
        
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
    
            radar = make_radar(names, percentiles, slice_colors, text_colors,size_radar)
    
    
            st.pyplot(radar, use_container_width=False) 

    
    st.markdown("#### Aspectos Técnicos")
    Aspectos_Tecnicos = df["Aspectos_Tecnicos"][0]
    st.markdown(Aspectos_Tecnicos)

    st.markdown("#### Aspectos Tácticos")
    Aspectos_Tacticos = df["Aspectos_Tacticos"][0]
    st.markdown(Aspectos_Tacticos)
    
    st.markdown("#### Aspectos Físicos")
    Aspectos_Fisicos = df["Aspectos_Fisicos"][0]
    st.markdown(Aspectos_Fisicos)	
    
    st.markdown("#### Personalidad y Perfil Psicológico")
    Personalidad = df["Personalidad"][0]
    st.markdown(Personalidad)	

    st.markdown("#### Otras Observaciones")
    Otras_Observaciones = df["Otras_Observaciones"][0]
    st.markdown(Otras_Observaciones)	


    st.markdown("#### Video Compacto")
    Nombre_Video_Compacto = df["Nombre_Video_Compacto"][0]
    st.video(Nombre_Video_Compacto)
  

    # #Video
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


