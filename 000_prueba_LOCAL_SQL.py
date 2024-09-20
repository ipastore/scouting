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
import psycopg2
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.exc import SQLAlchemyError
import datetime
import uuid
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import math



#######################
# Page configuration
st.set_page_config(
    page_title="Headers DataBase",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")
#######################

# #Init Cloudinary
# # LOCAL
config = cloudinary.config(secure=True)


#Sidebar
with st.sidebar:
    col = st.columns((1,5,1), gap='medium')
    with col[1]:
       st.markdown("### Headers DataBase")


# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()

# Definir tablas
jugador = Table('jugador', metadata, autoload_with=engine)
extremo = Table('extremo', metadata, autoload_with=engine)
arquero = Table('arquero', metadata, autoload_with=engine)
centro_delantero = Table('centro_delantero', metadata, autoload_with=engine)
contencion = Table('contencion', metadata, autoload_with=engine)
defensor_central = Table('defensor_central', metadata, autoload_with=engine)
lateral_derecho = Table('lateral_derecho', metadata, autoload_with=engine)
lateral_izquierdo = Table('lateral_izquierdo', metadata, autoload_with=engine)
mixto = Table('mixto', metadata, autoload_with=engine)
ofensivo = Table('ofensivo', metadata, autoload_with=engine)
club = Table('club', metadata, autoload_with=engine)
videos = Table('videos', metadata, autoload_with=engine)
entrenador = Table('entrenador', metadata, autoload_with=engine)
tiene_video = Table('tiene_video', metadata, autoload_with=engine)
club_jugador = Table('club_jugador', metadata, autoload_with=engine)
club_entrenador = Table('club_entrenador', metadata, autoload_with=engine)
representante = Table('representante', metadata, autoload_with=engine)

# Lista de datos posibles para poder llenar

esquema_predilecto_opciones = ['','no tiene','4-4-2', '4-3-3', '4-2-3-1', '3-5-2', '3-4-3', '5-3-2', 
                                                  '4-3-1-2', '4-2-4', '4-2-1-3 MD', '4-2-1-3 MI', 
                                                  '4-3-3 MD', '4-3-3 MI', '3-3-2-2', '3-4-1-2', '3-3-1-3', 
                                                  '4-2-2-2', '5-4-1']
nacionalidad_opciones =  ['','Argentina', 'Brasil', 'Uruguay', 'Chile', 'Paraguay',
                           'Bolivia', 'Perú', 'Colombia', 'Venezuela', 'Ecuador']

posicion_opciones = ['','Arquero', 'Defensor Central', 'Lateral Derecho', 'Lateral Izquierdo', 'Contención', 'Mixto', 'Ofensivo', 'Centro Delantero', 'Extremo']

division_opciones = ['','Primera', 'Reserva', 'Juveniles']

seleccion_opciones = ['','Mayor', 'Sub20', 'Sub17', 'Sub15', 'No']

pierna_habil_opciones = ['','Diestro', 'Zurdo', 'Ambidiestro']

# Set the minimum and maximum values for the date input
min_date_nacimiento = datetime.date(1900, 1, 1)
max_date_nacimiento = datetime.date.today()
min_date_vencimiento_contrato = datetime.date.today()
max_date_vencimiento_contrato = datetime.date(2100, 1, 1)

# Dictionary to map entity names to table objects
ENTITIES = {
    'jugador': jugador,
    'representante': representante,
    'club': club,
    'entrenador': entrenador,
    'videos': videos,
    'club_jugador': club_jugador,
    'club_entrenador': club_entrenador,
    'tiene_video': tiene_video,
    'arquero': arquero,
    'centro_delantero': centro_delantero,
    'contencion': contencion,
    'defensor_central': defensor_central,
    'extremo': extremo,
    'lateral_derecho': lateral_derecho,
    'lateral_izquierdo': lateral_izquierdo,
    'mixto': mixto,
    'ofensivo': ofensivo
}

# Create a mapping from position to entity key
position_to_entity_key = {
    'Arquero': 'arquero',
    'Defensor Central': 'defensor_central',
    'Lateral Derecho': 'lateral_derecho',
    'Lateral Izquierdo': 'lateral_izquierdo',
    'Contención': 'contencion',
    'Mixto': 'mixto',
    'Ofensivo': 'ofensivo',
    'Centro Delantero': 'centro_delantero',
    'Extremo': 'extremo'
}


# Cargar datos de tablas relacionadas

# Convert UUID columns to strings in the DataFrame
def convert_uuid_to_str(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
    return df

# ## Funciones de GETS
def get_all(entidad_name):
    if entidad_name not in ENTITIES:
        raise ValueError(f"Entidad '{entidad_name}' no es válida. Las entidades válidas son: {list(ENTITIES.keys())}")
    
    entidad = ENTITIES[entidad_name]
    query = select(entidad)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)


## Funciones CHECKS de existencia
def entidad_ncolumna_nvalor_exists(entidad_name, columnas_valores):
    if entidad_name not in ENTITIES:
        raise ValueError(f"Entidad '{entidad_name}' no es válida. Las entidades válidas son: {list(ENTITIES.keys())}")
    
    entidad = ENTITIES[entidad_name]
    conditions = []
    
    for columna, valor in columnas_valores.items():
        column_obj = getattr(entidad.c, columna)  # Get the column object from the table
        if isinstance(column_obj.type, UUID):
            conditions.append(column_obj == valor)
        else:
            conditions.append(func.lower(column_obj) == func.lower(valor))
    
    query = select(entidad).where(*conditions)
    
    result = session.execute(query).fetchone()
    return result is not None


###### Funciones de ADDS ###########

def add_entidad(entidad_name, data):
    if entidad_name not in ENTITIES:
        raise ValueError(f"Entidad '{entidad_name}' no es válida. Las entidades válidas son: {list(ENTITIES.keys())}")
    
    entidad = ENTITIES[entidad_name]
    insert_stmt = entidad.insert().values(data)
    
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success(f"{entidad_name.capitalize()} agregado exitosamente")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Error al agregar {entidad_name}: {e}")



### Funciones de DELETE

def delete_entidad(entidad_name, uid):
    if entidad_name not in ENTITIES:
        raise ValueError(f"Entidad '{entidad_name}' no es válida. Las entidades válidas son: {list(ENTITIES.keys())}")
    
    entidad = ENTITIES[entidad_name]
    delete_stmt = entidad.delete().where(entidad.c[f"{entidad_name}_uid"] == uid)
    
    try:
        session.execute(delete_stmt)
        session.commit()
        st.success(f"{entidad_name.capitalize()} eliminado exitosamente")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Error al eliminar {entidad_name}: {e}")



#### Funciones de UPDATE

def update_entidad(entidad_name, uid, data):
    if entidad_name not in ENTITIES:
        raise ValueError(f"Entidad '{entidad_name}' no es válida. Las entidades válidas son: {list(ENTITIES.keys())}")
    
    entidad = ENTITIES[entidad_name]
    update_stmt = entidad.update().where(entidad.c[f"{entidad_name}_uid"] == uid).values(data)
    
    try:
        session.execute(update_stmt)
        session.commit()
        st.success(f"{entidad_name.capitalize()} actualizado exitosamente")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Error al actualizar {entidad_name}: {e}")




# Obtener datos para listas desplegables
df_representantes = get_all('representante')
df_clubs = get_all('club')
df_videos = get_all('videos')
df_entrenadores = get_all('entrenador')
df_jugadores = get_all('jugador')
df_tiene_video = get_all('tiene_video')
df_club_jugador = get_all('club_jugador')
df_club_entrenador = get_all('club_entrenador')
df_extremos= get_all('extremo')
df_arqueros = get_all('arquero')
df_centro_delanteros = get_all('centro_delantero')
df_contenciones = get_all('contencion')
df_defensores_centrales = get_all('defensor_central')
df_laterales_derechos = get_all('lateral_derecho')
df_laterales_izquierdos = get_all('lateral_izquierdo')
df_mixtos = get_all('mixto')
df_ofensivos = get_all('ofensivo')



# ####### FORMS de AGREGAR ##############
st.subheader('Agregar Jugador')
posicion = st.selectbox('Posición', posicion_opciones, key='agregar_posicion_a_jugador')


# Form agregar jugador
with st.form('Agregar Jugador'):

    #NOT NULL
    nombre_jugador = st.text_input('Nombre')
    club_nombre = st.selectbox('Club',[''] + df_clubs['nombre'].tolist(), key='agregar_club_a_jugador')
    if club_nombre == '':
        club_uid = None
    else:
        club_uid = df_clubs[df_clubs['nombre'] == club_nombre]['club_uid'].values[0] 
    nacionalidad = st.selectbox('Nacionalidad', nacionalidad_opciones, key='agregar_nacionalidad_a_jugador')
    fecha_nacimiento = st.date_input('Fecha de Nacimiento', min_value=min_date_nacimiento, max_value=max_date_nacimiento, value=None)
    posicion_alternativa = st.selectbox('Posición Alternativa', posicion_opciones, key='agregar_posicion_alternativa_a_jugador')
    categoria = st.number_input('Categoría', min_value=1900, max_value=2100, step=1, value=None)
    division = st.selectbox('División', division_opciones, key='agregar_division_a_jugador')
    seleccion = st.selectbox('Selección', seleccion_opciones, key='agregar_seleccion_a_jugador')
    altura = st.number_input('Altura (m)', min_value=0.0, step=0.01, value=None)
    peso = st.number_input('Peso (kg)', min_value=0, step=1, value=None)
    pierna_habil = st.selectbox('Pierna Hábil',pierna_habil_opciones, key='agregar_pierna_habil_a_jugador')
    vencimiento_contrato = st.date_input('Vencimiento de Contrato', min_value=min_date_vencimiento_contrato, max_value=max_date_vencimiento_contrato, value=None)
    sueldo = st.number_input('Sueldo (USD)',min_value=0, step=1, value = None)
    valor_transfermarket = st.number_input('Valor Transfermarket (MM USD)',min_value=0.0, step=0.1, value = None)
    foto_jugador = st.text_input('Foto Jugador', value = None)
    foto_carrera_club = st.text_input('Foto Carrera Club', value = None)
    foto_carrera_seleccion = st.text_input('Foto Carrera Selección', value = None)
    aspectos_tecnicos_tacticos = st.text_area('Aspectos Técnicos/Tácticos', value = None)
    aspectos_fisicos = st.text_area('Aspectos Físicos', value = None)
    personalidad = st.text_area('Personalidad', value = None)
    otras_observaciones = st.text_area('Otras Observaciones', value = None)
    # Select representante from dropdown and add NULL option
    representante_nombre = st.selectbox('Representante', [''] + df_representantes['nombre'].tolist(), key='agregar_representante_a_jugador')
    if representante_nombre == '':
        representante_uid = None
    else:
        representante_uid = df_representantes[df_representantes['nombre'] == representante_nombre]['representante_uid'].values[0]

    if posicion == 'Extremo':
        st.subheader('Aspectos Técnicos del Extremo')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        asociaciones = st.number_input('Asociaciones', min_value=0, max_value=100, step=1, value=None)
        centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
        duelos_areos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
        regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
        remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
        retroceso_defensivo = st.number_input('Retroceso Defensivo', min_value=0, max_value=100, step=1, value=None)
        explosividad = st.number_input('Explosividad', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        definicion_peligrosidad = st.number_input('Definición / Peligrosidad', min_value=0, max_value=100, step=1, value=None)
    
    elif posicion == 'Arquero':
        st.subheader('Aspectos Técnicos del Arquero')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        atajadas = st.number_input('Atajadas', min_value=0, max_value=100, step=1, value=None)
        pelotas_aereas = st.number_input('Pelotas Aéreas', min_value=0, max_value=100, step=1, value=None)
        de_libero = st.number_input('De Libre', min_value=0, max_value=100, step=1, value=None)
        penales = st.number_input('Penales', min_value=0, max_value=100, step=1, value=None)
        circulacion = st.number_input('Circulación', min_value=0, max_value=100, step=1, value=None)
        pase_largo = st.number_input('Pase Largo', min_value=0, max_value=100, step=1, value=None)
        uno_vs_uno = st.number_input('Uno vs Uno', min_value=0, max_value=100, step=1, value=None)
        posicionamiento_movilidad = st.number_input('Posicionamiento / Movilidad', min_value=0, max_value=100, step=1, value=None)
    
    elif posicion == 'Centro Delantero':
        st.subheader('Aspectos Técnicos del Centro Delantero')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        juego_espaldas = st.number_input('Juego de Espaldas', min_value=0, max_value=100, step=1, value=None)
        duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
        regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
        remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
        presion = st.number_input('Presión', min_value=0, max_value=100, step=1, value=None)
        movilidad_desmarques = st.number_input('Movilidad / Desmarques', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        definicion_peligrosidad = st.number_input('Definición / Peligrosidad', min_value=0, max_value=100, step=1, value=None)
        explosividad = st.number_input('Explosividad', min_value=0, max_value=100, step=1, value=None)
        remate_cabeza = st.number_input('Remate de Cabeza', min_value=0, max_value=100, step=1, value=None)
    
    elif posicion == 'Contención':
        st.subheader('Aspectos Técnicos del Contención')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        cambio_frente = st.number_input('Cambio de Frente', min_value=0, max_value=100, step=1, value=None)
        pase_espacio_filtrado = st.number_input('Pase a Espacio Filtrado', min_value=0, max_value=100, step=1, value=None)
        duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
        salida_circulacion = st.number_input('Salida Circulación', min_value=0, max_value=100, step=1, value=None)
        relevos_vigilancias = st.number_input('Relevos / Vigilancias', min_value=0, max_value=100, step=1, value=None)
        recuperaciones = st.number_input('Recuperaciones', min_value=0, max_value=100, step=1, value=None)
        duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        despliegue = st.number_input('Despliegue', min_value=0, max_value=100, step=1, value=None)
        coberturas_cierres = st.number_input('Coberturas / Cierres', min_value=0, max_value=100, step=1, value=None)
        remate = st.number_input('Remate', min_value=0, max_value=100, step=1, value=None)
    
    elif posicion == 'Defensor Central':
        st.subheader('Aspectos Técnicos del Defensor Central')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        anticipacion = st.number_input('Anticipación', min_value=0, max_value=100, step=1, value=None)
        duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
        duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
        salida = st.number_input('Salida', min_value=0, max_value=100, step=1, value=None)
        cierres_coberturas = st.number_input('Cierres / Coberturas', min_value=0, max_value=100, step=1, value=None)
        pase_paralelo = st.number_input('Pase Paralelo', min_value=0, max_value=100, step=1, value=None)
        uno_vs_uno = st.number_input('Uno vs Uno', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        pelota_detenida = st.number_input('Pelota Detenida', min_value=0, max_value=100, step=1, value=None)

    elif posicion == 'Lateral Derecho':
        st.subheader('Aspectos Técnicos del Lateral Derecho')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        anticipacion = st.number_input('Anticipación', min_value=0, max_value=100, step=1, value=None)
        duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
        duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
        salida = st.number_input('Salida', min_value=0, max_value=100, step=1, value=None)
        cierres_coberturas = st.number_input('Cierres / Coberturas', min_value=0, max_value=100, step=1, value=None)
        pase_paralelo = st.number_input('Pase Paralelo', min_value=0, max_value=100, step=1, value=None)
        uno_vs_uno_defensivo = st.number_input('Uno vs Uno Defensivo', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
        uno_vs_uno_ofensivo = st.number_input('Uno vs Uno Ofensivo', min_value=0, max_value=100, step=1, value=None)
        remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
        juego_ofensivo = st.number_input('Juego Ofensivo', min_value=0, max_value=100, step=1, value=None)

    elif posicion == 'Lateral Izquierdo':
        st.subheader('Aspectos Técnicos del Lateral Izquierdo')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        anticipacion = st.number_input('Anticipación', min_value=0, max_value=100, step=1, value=None)
        duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
        duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
        salida = st.number_input('Salida', min_value=0, max_value=100, step=1, value=None)
        cierres_coberturas = st.number_input('Cierres / Coberturas', min_value=0, max_value=100, step=1, value=None)
        pase_paralelo = st.number_input('Pase Paralelo', min_value=0, max_value=100, step=1, value=None)
        uno_vs_uno_defensivo = st.number_input('Uno vs Uno Defensivo', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
        uno_vs_uno_ofensivo = st.number_input('Uno vs Uno Ofensivo', min_value=0, max_value=100, step=1, value=None)
        remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
        juego_ofensivo = st.number_input('Juego Ofensivo', min_value=0, max_value=100, step=1, value=None)
    
    elif posicion == 'Mixto':
        st.subheader('Aspectos Técnicos del Mixto')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        cambio_frente = st.number_input('Cambio de Frente', min_value=0, max_value=100, step=1, value=None)
        pase_espacio_filtrado = st.number_input('Pase a Espacio Filtrado', min_value=0, max_value=100, step=1, value=None)
        duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
        salida_circulacion = st.number_input('Salida Circulación', min_value=0, max_value=100, step=1, value=None)
        duelos_defensivos = st.number_input('Duelos Defensivos', min_value=0, max_value=100, step=1, value=None)
        recuperaciones = st.number_input('Recuperaciones', min_value=0, max_value=100, step=1, value=None)
        duelos_ofensivos = st.number_input('Duelos Ofensivos', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        despliegue = st.number_input('Despliegue', min_value=0, max_value=100, step=1, value=None)
        remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
        regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
        centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
    
    elif posicion == 'Ofensivo':
        st.subheader('Aspectos Técnicos del Ofensivo')

        tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
        cambio_frente = st.number_input('Cambio de Frente', min_value=0, max_value=100, step=1, value=None)
        pase_espacio_filtrado = st.number_input('Pase a Espacio Filtrado', min_value=0, max_value=100, step=1, value=None)
        asociaciones = st.number_input('Asociaciones', min_value=0, max_value=100, step=1, value=None)
        regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
        remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
        retroceso_defensivo = st.number_input('Retroceso Defensivo', min_value=0, max_value=100, step=1, value=None)
        explosividad = st.number_input('Explosividad', min_value=0, max_value=100, step=1, value=None)
        velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
        resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
        determinacion = st.number_input('Determinación', min_value=0, max_value=100, step=1, value=None)


    submit_jugador_button = st.form_submit_button('Agregar Jugador')

    if submit_jugador_button:
        warning = False
        if nombre_jugador == '' or posicion == '':
            st.warning('Nombre y Posición son campos obligatorios')
            st.stop()
        
        if entidad_ncolumna_nvalor_exists('jugador', {'nombre':nombre_jugador,
                                                    'representante_uid':representante_uid}):
            st.error('''El jugador con el mismo nombre y representante ya existe. 
                    Esto es altamente improbable, si quiere agregar un jugador con el
                      mismo nombre de jugador y representante, ponganse en contacto con el 
                     equipo de Headers'''
                     )
        elif entidad_ncolumna_nvalor_exists('jugador',{'nombre':nombre_jugador}):
            st.warning('El jugador con el mismo nombre ya existe')
            warning = True
            if warning and st.checkbox('Confirmar adición del jugador a pesar de la advertencia'):
                jugador_data = {
                    'nombre': nombre_jugador.title(),
                    'nacionalidad': nacionalidad if nacionalidad != '' else None,
                    'fecha_nacimiento': fecha_nacimiento,
                    'posicion': posicion,
                    'posicion_alternativa': posicion_alternativa if posicion_alternativa != '' else None,
                    'categoria': categoria,
                    'division': division if division != '' else None,
                    'seleccion': seleccion if seleccion != '' else None,
                    'altura': altura,
                    'peso': peso,
                    'pierna_habil': pierna_habil if pierna_habil != '' else None,
                    'vencimiento_contrato': vencimiento_contrato,
                    'sueldo': sueldo,
                    'valor_transfermarket': valor_transfermarket,
                    'foto_jugador': foto_jugador,
                    'foto_carrera_club': foto_carrera_club,
                    'foto_carrera_seleccion': foto_carrera_seleccion,
                    'aspectos_tecnicos_tacticos': aspectos_tecnicos_tacticos,
                    'aspectos_fisicos': aspectos_fisicos,
                    'personalidad': personalidad,
                    'otras_observaciones': otras_observaciones,
                    'representante_uid': representante_uid
                    }
                add_entidad('jugador',jugador_data)
                df_jugadores = get_all('jugador')
                jugador_uid = df_jugadores[df_jugadores['nombre'].str.lower() == nombre_jugador.lower()]['jugador_uid'].values[0]
                club_jugador_data = {
                    'jugador_uid': jugador_uid,
                    'club_uid': club_uid        
                    }
                add_entidad('club_jugador',club_jugador_data)

                if posicion == 'Extremo':
                    extremo_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'asociaciones': asociaciones,
                    'centros': centros,
                    'duelos_areos': duelos_areos,
                    'regates': regates,
                    'remates': remates,
                    'retroceso_defensivo': retroceso_defensivo,
                    'explosividad': explosividad,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'definicion_peligrosidad': definicion_peligrosidad
                }
                    add_entidad('extremo',extremo_data)
                    df_extremos = get_all('extremo')
                elif posicion == 'Arquero':
                    arquero_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'atajadas': atajadas,
                    'pelotas_aereas': pelotas_aereas,
                    'de_libero': de_libero,
                    'penales': penales,
                    'circulacion': circulacion,
                    'pase_largo': pase_largo,
                    'uno_vs_uno': uno_vs_uno,
                    'posicionamiento_movilidad': posicionamiento_movilidad
                }
                    add_entidad('arquero',arquero_data)
                    df_arqueros = get_all('arquero')
                
                elif posicion == 'Centro Delantero':
                    centro_delantero_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'juego_espaldas': juego_espaldas,
                    'duelos_aereos': duelos_aereos,
                    'regates': regates,
                    'remates': remates,
                    'presion': presion,
                    'movilidad_desmarques': movilidad_desmarques,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'definicion_peligrosidad': definicion_peligrosidad,
                    'explosividad': explosividad,
                    'remate_cabeza': remate_cabeza
                }
                    add_entidad('centro_delantero',centro_delantero_data)
                    df_centro_delanteros = get_all('centro_delantero')
                
                elif posicion == 'Contención':
                    contencion_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'cambio_frente': cambio_frente,
                    'pase_espacio_filtrado': pase_espacio_filtrado,
                    'duelos_aereos': duelos_aereos,
                    'salida_circulacion': salida_circulacion,
                    'relevos_vigilancias': relevos_vigilancias,
                    'recuperaciones': recuperaciones,
                    'duelos_por_abajo': duelos_por_abajo,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'despliegue': despliegue,
                    'coberturas_cierres': coberturas_cierres,
                    'remate': remate
                }
                    add_entidad('contencion',contencion_data)
                    df_contenciones = get_all('contencion')
                
                elif posicion == 'Defensor Central':
                    defensor_central_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'anticipacion': anticipacion,
                    'duelos_por_abajo': duelos_por_abajo,
                    'duelos_aereos': duelos_aereos,
                    'salida': salida,
                    'cierres_coberturas': cierres_coberturas,
                    'pase_paralelo': pase_paralelo,
                    'uno_vs_uno': uno_vs_uno,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'pelota_detenida': pelota_detenida
                }
                    add_entidad('defensor_central',defensor_central_data)
                    df_defensores_centrales = get_all('defensor_central')
                
                elif posicion == 'Lateral Derecho':
                    lateral_derecho_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'anticipacion': anticipacion,
                    'duelos_por_abajo': duelos_por_abajo,
                    'duelos_aereos': duelos_aereos,
                    'salida': salida,
                    'cierres_coberturas': cierres_coberturas,
                    'pase_paralelo': pase_paralelo,
                    'uno_vs_uno_defensivo': uno_vs_uno_defensivo,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'centros': centros,
                    'uno_vs_uno_ofensivo': uno_vs_uno_ofensivo,
                    'remates': remates,
                    'juego_ofensivo': juego_ofensivo
                }
                    add_entidad('lateral_derecho',lateral_derecho_data)
                    df_laterales_derechos = get_all('lateral_derecho')
                
                elif posicion == 'Lateral Izquierdo':
                    lateral_izquierdo_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'anticipacion': anticipacion,
                    'duelos_por_abajo': duelos_por_abajo,
                    'duelos_aereos': duelos_aereos,
                    'salida': salida,
                    'cierres_coberturas': cierres_coberturas,
                    'pase_paralelo': pase_paralelo,
                    'uno_vs_uno_defensivo': uno_vs_uno_defensivo,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'centros': centros,
                    'uno_vs_uno_ofensivo': uno_vs_uno_ofensivo,
                    'remates': remates,
                    'juego_ofensivo': juego_ofensivo
                }
                    add_entidad('lateral_izquierdo',lateral_izquierdo_data)
                    df_laterales_izquierdos = get_all('lateral_izquierdo')
                
                elif posicion == 'Mixto':
                    mixto_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'cambio_frente': cambio_frente,
                    'pase_espacio_filtrado': pase_espacio_filtrado,
                    'duelos_aereos': duelos_aereos,
                    'salida_circulacion': salida_circulacion,
                    'duelos_defensivos': duelos_defensivos,
                    'recuperaciones': recuperaciones,
                    'duelos_ofensivos': duelos_ofensivos,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'despliegue': despliegue,
                    'remates': remates,
                    'regates': regates,
                    'centros': centros
                }
                    add_entidad('mixto',mixto_data)
                    df_mixtos = get_all('mixto')
                
                elif posicion == 'Ofensivo':
                    ofensivo_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'cambio_frente': cambio_frente,
                    'pase_espacio_filtrado': pase_espacio_filtrado,
                    'asociaciones': asociaciones,
                    'regates': regates,
                    'remates': remates,
                    'retroceso_defensivo': retroceso_defensivo,
                    'explosividad': explosividad,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'determinacion': determinacion
                }
                    add_entidad('ofensivo',ofensivo_data)
                    df_ofensivos = get_all('ofensivo')
                


        elif not warning: 
            jugador_data = {
            'nombre': nombre_jugador.title(),
            'nacionalidad': nacionalidad if nacionalidad != '' else None,
            'fecha_nacimiento': fecha_nacimiento,
            'posicion': posicion,
            'posicion_alternativa': posicion_alternativa if posicion_alternativa != '' else None,
            'categoria': categoria,
            'division': division if division != '' else None,
            'seleccion': seleccion if seleccion != '' else None,
            'altura': altura,
            'peso': peso,
            'pierna_habil': pierna_habil if pierna_habil != '' else None,
            'vencimiento_contrato': vencimiento_contrato,
            'sueldo': sueldo,
            'valor_transfermarket': valor_transfermarket,
            'foto_jugador': foto_jugador,
            'foto_carrera_club': foto_carrera_club,
            'foto_carrera_seleccion': foto_carrera_seleccion,
            'aspectos_tecnicos_tacticos': aspectos_tecnicos_tacticos,
            'aspectos_fisicos': aspectos_fisicos,
            'personalidad': personalidad,
            'otras_observaciones': otras_observaciones,
            'representante_uid': representante_uid
            }                       
            add_entidad('jugador',jugador_data)
            df_jugadores = get_all('jugador')
            jugador_uid = df_jugadores[df_jugadores['nombre'].str.lower() == nombre_jugador.lower()]['jugador_uid'].values[0]
            club_jugador_data = {
                    'jugador_uid': jugador_uid,
                    'club_uid': club_uid,    
                    }
            add_entidad('club_jugador',club_jugador_data)

            if posicion == 'Extremo':
                    extremo_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'asociaciones': asociaciones,
                    'centros': centros,
                    'duelos_areos': duelos_areos,
                    'regates': regates,
                    'remates': remates,
                    'retroceso_defensivo': retroceso_defensivo,
                    'explosividad': explosividad,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'definicion_peligrosidad': definicion_peligrosidad
                }
                    add_entidad('extremo',extremo_data)
                    df_extremos = get_all('extremo')
            elif posicion == 'Arquero':
                    arquero_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'atajadas': atajadas,
                    'pelotas_aereas': pelotas_aereas,
                    'de_libero': de_libero,
                    'penales': penales,
                    'circulacion': circulacion,
                    'pase_largo': pase_largo,
                    'uno_vs_uno': uno_vs_uno,
                    'posicionamiento_movilidad': posicionamiento_movilidad
                }
                    add_entidad('arquero',arquero_data)
                    df_arqueros = get_all('arquero')
                
            elif posicion == 'Centro Delantero':
                    centro_delantero_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'juego_espaldas': juego_espaldas,
                    'duelos_aereos': duelos_aereos,
                    'regates': regates,
                    'remates': remates,
                    'presion': presion,
                    'movilidad_desmarques': movilidad_desmarques,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'definicion_peligrosidad': definicion_peligrosidad,
                    'explosividad': explosividad,
                    'remate_cabeza': remate_cabeza
                }
                    add_entidad('centro_delantero',centro_delantero_data)
                    df_centro_delanteros = get_all('centro_delantero')
                
            elif posicion == 'Contención':
                    contencion_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'cambio_frente': cambio_frente,
                    'pase_espacio_filtrado': pase_espacio_filtrado,
                    'duelos_aereos': duelos_aereos,
                    'salida_circulacion': salida_circulacion,
                    'relevos_vigilancias': relevos_vigilancias,
                    'recuperaciones': recuperaciones,
                    'duelos_por_abajo': duelos_por_abajo,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'despliegue': despliegue,
                    'coberturas_cierres': coberturas_cierres,
                    'remates': remates
                }
                    add_entidad('contencion',contencion_data)
                    df_contenciones = get_all('contencion')
                
            elif posicion == 'Defensor Central':
                    defensor_central_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'anticipacion': anticipacion,
                    'duelos_por_abajo': duelos_por_abajo,
                    'duelos_aereos': duelos_aereos,
                    'salida': salida,
                    'cierres_coberturas': cierres_coberturas,
                    'pase_paralelo': pase_paralelo,
                    'uno_vs_uno': uno_vs_uno,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'pelota_detenida': pelota_detenida
                }
                    add_entidad('defensor_central',defensor_central_data)
                    df_defensores_centrales = get_all('defensor_central')
                
            elif posicion == 'Lateral Derecho':
                    lateral_derecho_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'anticipacion': anticipacion,
                    'duelos_por_abajo': duelos_por_abajo,
                    'duelos_aereos': duelos_aereos,
                    'salida': salida,
                    'cierres_coberturas': cierres_coberturas,
                    'pase_paralelo': pase_paralelo,
                    'uno_vs_uno_defensivo': uno_vs_uno_defensivo,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'centros': centros,
                    'uno_vs_uno_ofensivo': uno_vs_uno_ofensivo,
                    'remates': remates,
                    'juego_ofensivo': juego_ofensivo
                }
                    add_entidad('lateral_derecho',lateral_derecho_data)
                    df_laterales_derechos = get_all('lateral_derecho')
                
            elif posicion == 'Lateral Izquierdo':
                    lateral_izquierdo_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'anticipacion': anticipacion,
                    'duelos_por_abajo': duelos_por_abajo,
                    'duelos_aereos': duelos_aereos,
                    'salida': salida,
                    'cierres_coberturas': cierres_coberturas,
                    'pase_paralelo': pase_paralelo,
                    'uno_vs_uno_defensivo': uno_vs_uno_defensivo,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'centros': centros,
                    'uno_vs_uno_ofensivo': uno_vs_uno_ofensivo,
                    'remates': remates,
                    'juego_ofensivo': juego_ofensivo
                }
                    add_entidad('lateral_izquierdo',lateral_izquierdo_data)
                    df_laterales_izquierdos = get_all('lateral_izquierdo')
                
            elif posicion == 'Mixto':
                    mixto_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'cambio_frente': cambio_frente,
                    'pase_espacio_filtrado': pase_espacio_filtrado,
                    'duelos_aereos': duelos_aereos,
                    'salida_circulacion': salida_circulacion,
                    'duelos_defensivos': duelos_defensivos,
                    'recuperaciones': recuperaciones,
                    'duelos_ofensivos': duelos_ofensivos,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'despliegue': despliegue,
                    'remate': remate,
                    'regates': regates,
                    'centros': centros
                }
                    add_entidad('mixto',mixto_data)
                    df_mixtos = get_all('mixto')
                
            elif posicion == 'Ofensivo':
                    ofensivo_data = {
                     'jugador_uid': jugador_uid,
                    'tecnica_individual': tecnica_individual,
                    'cambio_frente': cambio_frente,
                    'pase_espacio_filtrado': pase_espacio_filtrado,
                    'asociaciones': asociaciones,
                    'regates': regates,
                    'remates': remates,
                    'retroceso_defensivo': retroceso_defensivo,
                    'explosividad': explosividad,
                    'velocidad': velocidad,
                    'resistencia': resistencia,
                    'determinacion': determinacion
                }
                    add_entidad('ofensivo',ofensivo_data)
                    df_ofensivos = get_all('ofensivo')
 
                

################### Form agregar Club ####################
st.subheader('Agregar Club')

with st.form('Agregar Club'):
    nombre_club = st.text_input('Nombre')
    foto_escudo = st.text_input('Foto Escudo')
    foto_plantel = st.text_input('Foto Plantel')
    submit_club_button = st.form_submit_button('Agregar Club')

    if submit_club_button:
        if nombre_club == '':
            st.warning('Nombre es un campo obligatorio')

        elif entidad_ncolumna_nvalor_exists('club',{'nombre':nombre_club}):
            st.error('El club con el mismo nombre ya existe')
        else:
            club_data = {
                'nombre': nombre_club.title(),
                'foto_escudo': foto_escudo,
                'foto_plantel': foto_plantel
            }
            add_entidad('club',club_data)

################### Form agregar Entreador ####################
st.subheader('Agregar Entrenador')

with st.form('Agregar Entrenador'):
    nombre_entrenador = st.text_input('Nombre')
    club_nombre = st.selectbox('Club',[''] + df_clubs['nombre'].tolist(), key='agregar_club_a_entrenador')
    if club_nombre == '':
        club_uid = None
    else: #Modificar aca algo de nombre lower?
        club_uid = df_clubs[df_clubs['nombre'] == club_nombre]['club_uid'].values[0]
    nacionalidad_entrenador = st.selectbox('Nacionalidad', nacionalidad_opciones, key='agregar_nacionalidad_a_entrenador')
    fecha_nacimiento_entrenador = st.date_input('Fecha de Nacimiento', min_value=min_date_nacimiento, max_value=max_date_nacimiento, value=None)
    esquema_predilecto = st.selectbox('Esquema Predilecto',esquema_predilecto_opciones, key='agregar_esquema_predilecto_a_entrenador')
    foto_entrenador = st.text_input('Foto Entrenador')
    foto_carrera_entrenador = st.text_input('Foto Carrera Entrenador')
    foto_carrera_como_jugador = st.text_input('Foto Carrera Como Jugador')
    fase_ofensiva = st.text_area('Fase Ofensiva')
    fase_defensiva = st.text_area('Fase Defensiva')
    transiciones = st.text_area('Transiciones')
    otras_observaciones_entrenador = st.text_area('Otras Observaciones')
    ultimos_partidos = st.text_area('Últimos Partidos')
    foto_ultimos_partidos1 = st.text_input('Foto Últimos Partidos 1')
    foto_ultimos_partidos2 = st.text_input('Foto Últimos Partidos 2')
    submit_entrenador_button = st.form_submit_button('Agregar Entrenador')

    if submit_entrenador_button:
        if nombre_entrenador == '':
            st.warning('Nombre es un campo obligatorio')
        elif entidad_ncolumna_nvalor_exists('entrenador', {'nombre':nombre_entrenador}):
            st.error('El entrenador con el mismo nombre ya existe')
        ## if club_ui already exists in the table club_entrenador
        elif entidad_ncolumna_nvalor_exists('club_entrenador',{'club_uid':club_uid}):
            ## Tener en cuenta que es una tabla de entrenadores con clubes asignados. Si  
            ## no se asigna club, un entrenador tiene NULL.
            ## Se asume que no puede existir un club si no tiene entrenador.
            st.error('El club ya tiene un entrenador asignado')
        else:
            entrenador_data = {
                'nombre': nombre_entrenador.title(),
                'nacionalidad': nacionalidad_entrenador if nacionalidad_entrenador != '' else None,
                'fecha_nacimiento': fecha_nacimiento_entrenador,
                'esquema_predilecto': esquema_predilecto if esquema_predilecto != '' else None, 
                'foto_entrenador': foto_entrenador,
                'foto_carrera_entrenador': foto_carrera_entrenador,
                'foto_carrera_como_jugador': foto_carrera_como_jugador,
                'fase_ofensiva': fase_ofensiva,
                'fase_defensiva': fase_defensiva,
                'transiciones': transiciones,
                'otras_observaciones': otras_observaciones_entrenador,
                'ultimos_partidos': ultimos_partidos,
                'foto_ultimos_partidos1': foto_ultimos_partidos1,
                'foto_ultimos_partidos2': foto_ultimos_partidos2
            }
            add_entidad('entrenador',entrenador_data)
            df_entrenadores = get_all('entrenador')
            entrenador_uid = df_entrenadores[df_entrenadores['nombre'].str.lower() == nombre_entrenador.lower()]['entrenador_uid'].values[0]
            club_entrenador_data = {
                'entrenador_uid': entrenador_uid,
                'club_uid': club_uid,
            }
            add_entidad('club_entrenador',club_entrenador_data)
    
# ################### Form agregar Representante ####################
# st.subheader('Agregar Representante')

# with st.form('Agregar Representante'):
#     nombre_representante = st.text_input('Nombre')
#     submit_representante_button = st.form_submit_button('Agregar Representante')

#     if submit_representante_button:
#         if nombre_representante == '':
#             st.warning('Nombre es un campo obligatorio')
#         if entidad_ncolumna_nvalor_exists('representante',{'nombre': nombre_representante}):
#             st.error('El representante con el mismo nombre ya existe')
#         else:
#             representante_data = {
#                 'nombre': nombre_representante.title()
#             }
#             add_entidad('representante',representante_data)

# ################### Form agregar Video ####################
# st.subheader('Agregar Video')

# # Step 1: Choose whether to associate the video with a player or coach
# st.write("Asociar Video a:")
# asociar_opcion_agregar_video = st.radio("Seleccionar:", ['Entrenador', 'Jugador'],key='asociar_opcion_agregar_video')

# # Initialize the jugador_uid and entrenador_uid to None
# jugador_uid = None
# entrenador_uid = None

# # Step 2: Display the form based on the selection
# with st.form('Agregar Video'):
#     video_url = st.text_input('URL del Video')
#     video_titulo = st.text_input('Título del Video')
#     video_descripcion = st.text_area('Descripción del Video', value=None)

#     if asociar_opcion_agregar_video == 'Jugador':
#         if df_jugadores.empty:
#             st.warning("No hay jugadores disponibles para asociar con el video.")
#         else: 
#             jugador_nombre = st.selectbox('Jugador', df_jugadores['nombre'].tolist(), key='elegir_jugador_para_video')
#             jugador_uid = df_jugadores[df_jugadores['nombre'] == jugador_nombre]['jugador_uid'].values[0]
#     elif asociar_opcion_agregar_video == 'Entrenador':
#         if df_entrenadores.empty:
#             st.warning("No hay entrenadores disponibles para asociar con el video.")
#         else:
#             entrenador_nombre = st.selectbox('Entrenador', df_entrenadores['nombre'].tolist(), key='elegir_entrenador_para_video')
#             entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == entrenador_nombre]['entrenador_uid'].values[0]

#     submit_video_button = st.form_submit_button('Agregar Video')

#     if submit_video_button:
#         if video_url == '':
#             st.warning('URL del video es un campo obligatorio')

#         elif entidad_ncolumna_nvalor_exists('videos',{ 'url': video_url}):
#             st.error('El video con la misma URL ya existe')
#         else:
#             video_data = {
#                 'url': video_url,
#                 'titulo': video_titulo.title(),
#                 'descripcion': video_descripcion
#             }
#             add_entidad('video',video_data)
#             df_videos = get_all('videos')
#             video_uid = df_videos[df_videos['url'] == video_url]['video_uid'].values[0]
#             tiene_video_data = {
#                 'jugador_uid': jugador_uid,
#                 'entrenador_uid': entrenador_uid,
#                 'video_uid': video_uid
#             }
#             add_entidad('tiene_video',tiene_video_data)

# ####### FORMS de DELETE ##############
# #### Representante
# st.subheader('Borrar Representante')
# with st.form('Borrar Representante'):
#     representante_nombre = st.selectbox('Representante', [''] + df_representantes['nombre'].tolist(),key='borrar_representante')
#     if representante_nombre == '':
#         representante_uid = None
#     else:
#         representante_uid = df_representantes[df_representantes['nombre'] == representante_nombre]['representante_uid'].values[0]
#     submit_delete_representante_button = st.form_submit_button('Borrar Representante')

#     if submit_delete_representante_button:
#         if representante_uid is None:
#             st.warning('No se seleccionó ningún representante')
#         else:
#             delete_entidad('representante',representante_uid)
#             df_representantes = get_all('representante')

# #### Club
# st.subheader('Borrar Club')
# with st.form('Borrar Club'):
#     club_nombre = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='borrar_club')
#     if club_nombre == '':
#         club_uid = None
#     else:
#         club_uid = df_clubs[df_clubs['nombre'] == club_nombre]['club_uid'].values[0]
#     submit_delete_club_button = st.form_submit_button('Borrar Club')

#     if submit_delete_club_button:
#         if club_uid is None:
#             st.warning('No se seleccionó ningún club')
#         else:
#             delete_entidad('club',club_uid)
#             df_clubs = get_all('club')

# ### Entrenador
# st.subheader('Borrar Entrenador')
# with st.form('Borrar Entrenador'):
#     entrenador_nombre = st.selectbox('Entrenador', [''] + df_entrenadores['nombre'].tolist(),key='borrar_entrenador')
#     if entrenador_nombre == '':
#         entrenador_uid = None
#     else:
#         entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == entrenador_nombre]['entrenador_uid'].values[0]
#     submit_delete_entrenador_button = st.form_submit_button('Borrar Entrenador')

#     if submit_delete_entrenador_button:
#         if entrenador_uid is None:
#             st.warning('No se seleccionó ningún entrenador')
#         else:
#             delete_entidad('entrenador',entrenador_uid)
#             df_entrenadores = get_all('entrenador')

### Jugador
st.subheader('Borrar Jugador')

# Step 1: Select Club
club_nombre_borrar_jugador = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='elegir_club_para_borrar_jugador')

# If no club is selected, display all players
if club_nombre_borrar_jugador == '':
    jugadores_filtrados = df_jugadores
else:
    # Obtener el club_uid del club seleccionado
    club_uid = df_clubs[df_clubs['nombre'] == club_nombre_borrar_jugador]['club_uid'].values[0]
    
    # Filtrar la relación club_jugador por club_uid y obtener los jugador_uid
    jugadores_en_club = df_club_jugador[df_club_jugador['club_uid'] == club_uid]['jugador_uid'].tolist()
    
    # Filtrar df_jugadores para obtener solo los jugadores de ese club
    jugadores_filtrados = df_jugadores[df_jugadores['jugador_uid'].isin(jugadores_en_club)]

# Step 2: Select Player from the list (filtered or not)
with st.form('Borrar Jugador'):
    jugador_nombre = st.selectbox('Jugador', [''] + jugadores_filtrados['nombre'].tolist(), key='borrar_jugador')
    
    if jugador_nombre == '':
        jugador_uid = None
    else:
        jugador_uid = jugadores_filtrados[jugadores_filtrados['nombre'] == jugador_nombre]['jugador_uid'].values[0]
    
    submit_delete_jugador_button = st.form_submit_button('Borrar Jugador')

    if submit_delete_jugador_button:
        if jugador_uid is None:
            st.warning('No se seleccionó ningún jugador')
        else:
            delete_entidad('jugador',jugador_uid)
            df_jugadores = get_all('jugador')  # Refresh the jugadores list

# ### Video
# st.subheader('Borrar Video')
# # Step 1: Choose whether to delete a video associated with a Jugador or an Entrenador
# asociar_opcion_borrar_video = st.radio("Seleccionar tipo:", ['Jugador', 'Entrenador'], key='asociar_opcion_borrar_video')   

# # Step 2: Select the specific Jugador or Entrenador
# if asociar_opcion_borrar_video == 'Jugador':
#     entrenador_uid = None
#     if df_jugadores.empty:
#         st.warning("No hay jugadores disponibles.")
#         jugador_uid = None
#     else:
#         jugador_nombre = st.selectbox('Jugador', [''] + df_jugadores['nombre'].tolist(), key='elegir_jugador_para_borrar_video')
#         if jugador_nombre == '':
#             jugador_uid = None
#         else:
#             jugador_uid = df_jugadores[df_jugadores['nombre'] == jugador_nombre]['jugador_uid'].values[0]
# elif asociar_opcion_borrar_video == 'Entrenador':
#     jugador_uid = None
#     if df_entrenadores.empty:
#         st.warning("No hay entrenadores disponibles.")
#         entrenador_uid = None
#     else:
#         entrenador_nombre = st.selectbox('Entrenador', [''] + df_entrenadores['nombre'].tolist(), key='elegir_entrenador_para_borrar_video')
#         if entrenador_nombre == '':
#             entrenador_uid = None
#         else: 
#             entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == entrenador_nombre]['entrenador_uid'].values[0]

# # Step 3: Filter and select the video associated with the selected Jugador or Entrenador
# tiene_video_filtrado = None
# if jugador_uid:
#     tiene_video_filtrado = df_tiene_video[df_tiene_video['jugador_uid'] == jugador_uid]
#     if tiene_video_filtrado.empty:
#         st.warning('No hay videos asociados al jugador')
# elif entrenador_uid:
#     tiene_video_filtrado = df_tiene_video[df_tiene_video['entrenador_uid'] == entrenador_uid]
#     if tiene_video_filtrado.empty:
#         st.warning('No hay videos asociados al entrenador')


# if tiene_video_filtrado is not None and not tiene_video_filtrado.empty:
#     video_uids = tiene_video_filtrado['video_uid'].tolist()
#     videos_filtrados = df_videos[df_videos['video_uid'].isin(video_uids)]
#     video_titulo = st.selectbox('Videos', videos_filtrados['titulo'].tolist(), key='borrar_video')
#     video_uid = videos_filtrados[videos_filtrados['titulo'] == video_titulo]['video_uid'].values[0]
# else:
#     video_uid = None

# # Form to delete the video
# with st.form('Borrar Video'):
#     submit_delete_video_button = st.form_submit_button('Borrar Video')

#     if submit_delete_video_button:
#         if video_uid is None:
#             st.warning('No se seleccionó ningún video')
#         else:
#             delete_entidad('video',video_uid)
#             df_videos = get_all('videos') # Refresh the videos list


### FORM de Actualizar
# Actualizar Representante
st.subheader('Actualizar Representante')

representante_nombre_a_actualizar = st.selectbox('Representante', [''] + df_representantes['nombre'].tolist(), key='actualizar_representante')

if representante_nombre_a_actualizar == '':
        representante_uid = None

else:
    representante_uid = df_representantes[df_representantes['nombre'] == representante_nombre_a_actualizar]['representante_uid'].values[0]
    current_nombre_representante = df_representantes[df_representantes['representante_uid'] == representante_uid]['nombre'].values[0]

    with st.form('Actualizar Representante'):
        nuevo_nombre_representante = st.text_input('Nuevo Nombre', value =current_nombre_representante)
        
        submit_update_representante_button = st.form_submit_button('Actualizar Representante')

    if submit_update_representante_button:

        if representante_uid is None:
            st.warning('No se seleccionó ningún representante')

        elif nuevo_nombre_representante == '':
            st.warning('Nombre es un campo obligatorio')

        elif entidad_ncolumna_nvalor_exists('representante',{ 'nombre': nuevo_nombre_representante}):
            st.error('El representante con el mismo nombre ya existe')
       
        else:
            representante_data = {
                    'nombre': nuevo_nombre_representante.title()
            }
            update_entidad('representante',representante_uid, representante_data)
            df_representantes = get_all('representante')  # Refresh the list of representantes

# Actualizar Club
st.subheader('Actualizar Club')

# Step 1: Select Club (outside the form)
club_nombre_actualizar = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='actualizar_club')

if club_nombre_actualizar == '':
    club_uid = None

else:
    # Get club_uid and current values from the selected club
    club_uid = df_clubs[df_clubs['nombre'] == club_nombre_actualizar]['club_uid'].values[0]
    current_club = df_clubs[df_clubs['club_uid'] == club_uid]
    current_nombre_club = current_club['nombre'].values[0]
    current_foto_escudo = current_club['foto_escudo'].values[0]
    current_foto_plantel = current_club['foto_plantel'].values[0]
    
    # Step 2: Prepopulate the form fields with current values (inside the form)
    with st.form('Actualizar Club'):
        nuevo_nombre_club = st.text_input('Nuevo Nombre', value=current_nombre_club)
        nuevo_foto_escudo = st.text_input('Nueva Foto Escudo', value=current_foto_escudo)
        nuevo_foto_plantel = st.text_input('Nueva Foto Plantel', value=current_foto_plantel)

        submit_update_club_button = st.form_submit_button('Actualizar Club')

        if submit_update_club_button:
            if nuevo_nombre_club == '':
                st.warning('Nombre es un campo obligatorio, no puede dejarse vacío')
            elif club_uid is None:
                st.warning('No se seleccionó ningún club')
            elif entidad_ncolumna_nvalor_exists('club',{'nombre':nuevo_nombre_club}) and nuevo_nombre_club.lower() != current_nombre_club.lower():
                st.error('El club con el mismo nombre ya existe')
            else:
                club_data = {
                    'nombre': nuevo_nombre_club.title(),
                    'foto_escudo': nuevo_foto_escudo,
                    'foto_plantel': nuevo_foto_plantel,
                }
                update_entidad('club',club_uid, club_data)
                df_clubs = get_all('club')  # Refresh the list of clubs

# ## Actualizar Entrenador
st.subheader('Actualizar Entrenador')

# Step 1: Select Entrenador (outside the form)
update_entrenador_nombre_option = st.selectbox('Entrenador', [''] + df_entrenadores['nombre'].tolist(), key='actualizar_entrenador')

if update_entrenador_nombre_option == '':
    entrenador_uid = None

else:
    # Get entrenador_uid and current values from the selected entrenador
    entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == update_entrenador_nombre_option]['entrenador_uid'].values[0]
    current_entrenador = df_entrenadores[df_entrenadores['entrenador_uid'] == entrenador_uid]
    current_nombre_entrenador = current_entrenador['nombre'].values[0]
    current_nacionalidad_entrenador = current_entrenador['nacionalidad'].values[0]
    current_fecha_nacimiento_entrenador = current_entrenador['fecha_nacimiento'].values[0]
    current_esquema_predilecto = current_entrenador['esquema_predilecto'].values[0]
    current_foto_entrenador = current_entrenador['foto_entrenador'].values[0]
    current_foto_carrera_entrenador = current_entrenador['foto_carrera_entrenador'].values[0]
    current_foto_carrera_como_jugador = current_entrenador['foto_carrera_como_jugador'].values[0]
    current_fase_ofensiva = current_entrenador['fase_ofensiva'].values[0]
    current_fase_defensiva = current_entrenador['fase_defensiva'].values[0]
    current_transiciones = current_entrenador['transiciones'].values[0]
    current_otras_observaciones_entrenador = current_entrenador['otras_observaciones'].values[0]
    current_ultimos_partidos = current_entrenador['ultimos_partidos'].values[0]
    current_foto_ultimos_partidos1 = current_entrenador['foto_ultimos_partidos1'].values[0]
    current_foto_ultimos_partidos2 = current_entrenador['foto_ultimos_partidos2'].values[0]

    # Step 2: Prepopulate the form fields with current values (inside the form)
    with st.form('Actualizar Entrenador'):
        nuevo_nombre_entrenador = st.text_input('Nuevo Nombre', value=current_nombre_entrenador)
        nuevo_nacionalidad_entrenador = st.selectbox('Nueva Nacionalidad', nacionalidad_opciones, key='actualizar_nacionalidad_entrenador', 
                                                     index=nacionalidad_opciones.index(current_nacionalidad_entrenador) if current_nacionalidad_entrenador else 0)
        nuevo_fecha_nacimiento_entrenador = st.date_input('Nueva Fecha de Nacimiento', min_value=min_date_nacimiento, max_value=max_date_nacimiento, value=current_fecha_nacimiento_entrenador)
        nuevo_esquema_predilecto = st.selectbox('Nuevo Esquema Predilecto', esquema_predilecto_opciones, key='actualizar_esquema_predilecto_a_entrenador',
                                                  index=esquema_predilecto_opciones.index(current_esquema_predilecto) if current_esquema_predilecto else 0)
        nuevo_foto_entrenador = st.text_input('Nueva Foto Entrenador', value=current_foto_entrenador)
        nuevo_foto_carrera_entrenador = st.text_input('Nueva Foto Carrera Entrenador', value=current_foto_carrera_entrenador)
        nuevo_foto_carrera_como_jugador = st.text_input('Nueva Foto Carrera Como Jugador', value=current_foto_carrera_como_jugador)
        nueva_fase_ofensiva = st.text_area('Nueva Fase Ofensiva', value=current_fase_ofensiva)
        nueva_fase_defensiva = st.text_area('Nueva Fase Defensiva', value=current_fase_defensiva)
        nuevas_transiciones = st.text_area('Nuevas Transiciones', value=current_transiciones)
        nuevas_otras_observaciones_entrenador = st.text_area('Nuevas Otras Observaciones', value=current_otras_observaciones_entrenador)
        nuevos_ultimos_partidos = st.text_area('Nuevos Últimos Partidos', value=current_ultimos_partidos)
        nueva_foto_ultimos_partidos1 = st.text_input('Nueva Foto Últimos Partidos 1', value=current_foto_ultimos_partidos1)
        nueva_foto_ultimos_partidos2 = st.text_input('Nueva Foto Últimos Partidos 2', value=current_foto_ultimos_partidos2)

        submit_update_entrenador_button = st.form_submit_button('Actualizar Entrenador')

        if submit_update_entrenador_button:
            if nuevo_nombre_entrenador == '':
                st.warning('Nombre es un campo obligatorio, no puede dejarse vacío')
            elif entrenador_uid is None:
                st.warning('No se seleccionó ningún entrenador para actualizar')

            elif entidad_ncolumna_nvalor_exists('entrenador',{'nombre':nuevo_nombre_entrenador}) and nuevo_nombre_entrenador.lower() != current_nombre_entrenador.lower():
                st.error('El entrenador con el mismo nombre ya existe')
            else:
                entrenador_data = {
                    'nombre': nuevo_nombre_entrenador.title(),
                    'nacionalidad': nuevo_nacionalidad_entrenador if nuevo_nacionalidad_entrenador != '' else None,
                    'fecha_nacimiento': nuevo_fecha_nacimiento_entrenador,
                    'esquema_predilecto': nuevo_esquema_predilecto if nuevo_esquema_predilecto != '' else None,
                    'foto_entrenador': nuevo_foto_entrenador,
                    'foto_carrera_entrenador': nuevo_foto_carrera_entrenador,
                    'foto_carrera_como_jugador': nuevo_foto_carrera_como_jugador,
                    'fase_ofensiva': nueva_fase_ofensiva,
                    'fase_defensiva': nueva_fase_defensiva,
                    'transiciones': nuevas_transiciones,
                    'otras_observaciones': nuevas_otras_observaciones_entrenador,
                    'ultimos_partidos': nuevos_ultimos_partidos,
                    'foto_ultimos_partidos1': nueva_foto_ultimos_partidos1,
                    'foto_ultimos_partidos2': nueva_foto_ultimos_partidos2
                }
                update_entidad('entrenador',entrenador_uid, entrenador_data)
                df_entrenadores = get_all('entrenador')  # Refresh the list of entrenadores

# Actualizar Jugador
st.subheader('Actualizar Jugador')

# Step 1: Select Club
club_nombre_actualizar_jugador = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='elegir_club_para_actualizar_jugador')

# If no club is selected, display all players
if club_nombre_actualizar_jugador == '':
    jugadores_filtrados = df_jugadores
else:
    # Obtener el club_uid del club seleccionado
    club_uid = df_clubs[df_clubs['nombre'] == club_nombre_actualizar_jugador]['club_uid'].values[0]
    
    # Filtrar la relación club_jugador por club_uid y obtener los jugador_uid
    jugadores_en_club = df_club_jugador[df_club_jugador['club_uid'] == club_uid]['jugador_uid'].tolist()
    
    # Filtrar df_jugadores para obtener solo los jugadores de ese club
    jugadores_filtrados = df_jugadores[df_jugadores['jugador_uid'].isin(jugadores_en_club)]


jugador_nombre = st.selectbox('Jugador', [''] + jugadores_filtrados['nombre'].tolist(), key='actualizar_jugador')
    
if jugador_nombre == '':
    jugador_uid = None
else:
    jugador_uid = jugadores_filtrados[jugadores_filtrados['nombre'] == jugador_nombre]['jugador_uid'].values[0]
    current_jugador = df_jugadores[df_jugadores['jugador_uid'] == jugador_uid]
    current_nombre_jugador = current_jugador['nombre'].values[0]
    current_nacionalidad = current_jugador['nacionalidad'].values[0]
    current_fecha_nacimiento = current_jugador['fecha_nacimiento'].values[0]
    current_posicion = current_jugador['posicion'].values[0]
    current_posicion_alternativa = current_jugador['posicion_alternativa'].values[0]
    current_categoria = current_jugador['categoria'].values[0]
    current_division = current_jugador['division'].values[0]
    current_seleccion = current_jugador['seleccion'].values[0]
    current_altura = current_jugador['altura'].values[0]
    current_peso = current_jugador['peso'].values[0]
    current_pierna_habil = current_jugador['pierna_habil'].values[0]
    current_vencimiento_contrato = current_jugador['vencimiento_contrato'].values[0]
    current_sueldo = current_jugador['sueldo'].values[0]
    current_valor_transfermarket = current_jugador['valor_transfermarket'].values[0]
    current_foto_jugador = current_jugador['foto_jugador'].values[0]
    current_foto_carrera_club = current_jugador['foto_carrera_club'].values[0]
    current_foto_carrera_seleccion = current_jugador['foto_carrera_seleccion'].values[0]
    current_aspectos_tecnicos_tacticos = current_jugador['aspectos_tecnicos_tacticos'].values[0]
    current_aspectos_fisicos = current_jugador['aspectos_fisicos'].values[0]
    current_personalidad = current_jugador['personalidad'].values[0]
    current_otras_observaciones = current_jugador['otras_observaciones'].values[0]
    current_representante_uid = current_jugador['representante_uid'].values[0]
    nuevo_posicion = st.selectbox('Nueva Posición', posicion_opciones, key='actualizar_posicion_jugador',
                                    index=posicion_opciones.index(current_posicion) if current_posicion else 0)
    

## ACA FALTA PONER LOS CURRENT ASPECTOS TECNICOS CON LOS NUMEROS
    

## FALTA CACHEAR EL CAMBIO DE POSICION PORQUE HAY QUE BORRAR LA POSICION ANTERIOR
## HAY QUE MANEJAR LOS Nan, NONTE TYPE ETC. Pasa en peso, altura y me pasó en categoría también. No se por que en input no puedo dejar nada.
    with st.form('Actualizar Jugador'):
            
            # Form fields to update the player
            nuevo_nombre_jugador = st.text_input('Nuevo Nombre', value=current_nombre_jugador)
            nuevo_nacionalidad = st.selectbox('Nueva Nacionalidad', nacionalidad_opciones, key='actualizar_nacionalidad_jugador',
                                        index=nacionalidad_opciones.index(current_nacionalidad) if current_nacionalidad else 0)
            nuevo_fecha_nacimiento = st.date_input('Nueva Fecha de Nacimiento', min_value=min_date_nacimiento, max_value=max_date_nacimiento, value=current_fecha_nacimiento)
            nuevo_posicion_alternativa = st.selectbox('Nueva Posición Alternativa', posicion_opciones, key='actualizar_posicion_alternativa_jugador',
                                                index=posicion_opciones.index(current_posicion_alternativa) if current_posicion_alternativa else 0)
            nuevo_categoria = st.number_input('Nueva Categoría', min_value=1900, max_value=2100, step=1, value=int(current_categoria) if current_categoria is not None and  math.isnan(current_categoria) == False else None)
            nuevo_division = st.selectbox('Nueva División', division_opciones, key='actualizar_division_jugador',
                                    index=division_opciones.index(current_division) if current_division else 0)
            nuevo_seleccion = st.selectbox('Nueva Selección', seleccion_opciones, key='actualizar_seleccion_jugador',
                                    index=seleccion_opciones.index(current_seleccion) if current_seleccion else 0)
            nueva_altura = st.number_input('Nueva Altura (m)', min_value=0.00, step=0.01, value=float(current_altura) if current_altura is not None and math.isnan(current_altura) == False else None)
            nuevo_peso = st.number_input('Nuevo Peso (kg)', min_value=0, step=1, value=int(current_peso) if current_peso is not None and math.isnan(current_peso) == False else None)
            nueva_pierna_habil = st.selectbox('Nueva Pierna Hábil', pierna_habil_opciones, key='actualizar_pierna_habil_jugador',
                                    index=pierna_habil_opciones.index(current_pierna_habil) if current_pierna_habil else 0)
            nuevo_vencimiento_contrato = st.date_input('Nuevo Vencimiento de Contrato', min_value=min_date_vencimiento_contrato, max_value=max_date_vencimiento_contrato, value=current_vencimiento_contrato)
            nuevo_sueldo = st.number_input('Nuevo Sueldo (USD)', min_value=0, step=1, value=int(current_sueldo) if current_sueldo is not None and math.isnan(current_sueldo) == False else None)
            nuevo_valor_transfermarket = st.number_input('Nuevo Valor Transfermarket (MM USD)', min_value=0.00, step=0.01, value=float(current_valor_transfermarket) if current_valor_transfermarket is not None and math.isnan(current_valor_transfermarket) == False else None)
            nueva_foto_jugador = st.text_input('Nueva Foto Jugador', value=current_foto_jugador)
            nueva_foto_carrera_club = st.text_input('Nueva Foto Carrera Club', value=current_foto_carrera_club)
            nueva_foto_carrera_seleccion = st.text_input('Nueva Foto Carrera Selección', value=current_foto_carrera_seleccion)
            nuevos_aspectos_tecnicos_tacticos = st.text_area('Nuevos Aspectos Técnicos/Tácticos', value=current_aspectos_tecnicos_tacticos)
            nuevos_aspectos_fisicos = st.text_area('Nuevos Aspectos Físicos', value=current_aspectos_fisicos)
            nueva_personalidad = st.text_area('Nueva Personalidad', value=current_personalidad)
            nuevas_otras_observaciones = st.text_area('Nuevas Otras Observaciones', value=current_otras_observaciones)
            nuevo_representante = st.selectbox('Nuevo Representante', [''] + df_representantes['nombre'].tolist(), key='actualizar_representante_jugador',
                                    index=df_representantes[df_representantes['representante_uid'] == current_representante_uid].index[0] if current_representante_uid else 0)
            
            if nuevo_posicion != current_posicion:
                if nuevo_posicion == 'Extremo':
                    st.subheader('Aspectos Técnicos del Nuevo Extremo')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_asociaciones = st.number_input('Asociaciones', min_value=0, max_value=100, step=1, value=None)
                    nuevo_centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_areos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_retroceso_defensivo = st.number_input('Retroceso Defensivo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_explosividad = st.number_input('Explosividad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_definicion_peligrosidad = st.number_input('Definición / Peligrosidad', min_value=0, max_value=100, step=1, value=None)
                
                elif nuevo_posicion == 'Arquero':
                    st.subheader('Aspectos Técnicos del Nuevo Arquero')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_atajadas = st.number_input('Atajadas', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pelotas_aereas = st.number_input('Pelotas Aéreas', min_value=0, max_value=100, step=1, value=None)
                    nuevo_de_libero = st.number_input('De Libre', min_value=0, max_value=100, step=1, value=None)
                    nuevo_penales = st.number_input('Penales', min_value=0, max_value=100, step=1, value=None)
                    nuevo_circulacion = st.number_input('Circulación', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pase_largo = st.number_input('Pase Largo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_uno_vs_uno = st.number_input('Uno vs Uno', min_value=0, max_value=100, step=1, value=None)
                    nuevo_posicionamiento_movilidad = st.number_input('Posicionamiento / Movilidad', min_value=0, max_value=100, step=1, value=None)
                
                elif nuevo_posicion == 'Centro Delantero':
                    st.subheader('Aspectos Técnicos del Nuevo Centro Delantero')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_juego_espaldas = st.number_input('Juego de Espaldas', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_presion = st.number_input('Presión', min_value=0, max_value=100, step=1, value=None)
                    nuevo_movilidad_desmarques = st.number_input('Movilidad / Desmarques', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_definicion_peligrosidad = st.number_input('Definición / Peligrosidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_explosividad = st.number_input('Explosividad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remate_cabeza = st.number_input('Remate de Cabeza', min_value=0, max_value=100, step=1, value=None)
               
                elif nuevo_posicion == 'Contención':
                    st.subheader('Aspectos Técnicos del Nuevo Contención')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_cambio_frente = st.number_input('Cambio de Frente', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pase_espacio_filtrado = st.number_input('Pase a Espacio Filtrado', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_salida_circulacion = st.number_input('Salida / Circulación', min_value=0, max_value=100, step=1, value=None)
                    nuevo_relevos_vigilancias = st.number_input('Relevos / Vigilancias', min_value=0, max_value=100, step=1, value=None)
                    nuevo_recuperaciones = st.number_input('Recuperaciones', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_despliegue = st.number_input('Despliegue', min_value=0, max_value=100, step=1, value=None)
                    nuevo_coberturas_cierres = st.number_input('Coberturas / Cierres', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remate = st.number_input('Remate', min_value=0, max_value=100, step=1, value=None)
                
                elif nuevo_posicion == 'Defensor Central':

                    st.subheader('Aspectos Técnicos del Nuevo Defensor Central')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_anticipacion = st.number_input('Anticipación', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_salida = st.number_input('Salida', min_value=0, max_value=100, step=1, value=None)
                    nuevo_cierres_coberturas = st.number_input('Cierres / Coberturas', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pase_paralelo = st.number_input('Pase Paralelo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_uno_vs_uno = st.number_input('Uno vs Uno', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pelota_detenida = st.number_input('Pelota Detenida', min_value=0, max_value=100, step=1, value=None)
                
                elif posicion == 'Lateral Derecho':
                    st.subheader('Aspectos Técnicos del Nuevo Lateral Derecho')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_anticipacion = st.number_input('Anticipación', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_salida = st.number_input('Salida', min_value=0, max_value=100, step=1, value=None)
                    nuevo_cierres_coberturas = st.number_input('Cierres / Coberturas', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pase_paralelo = st.number_input('Pase Paralelo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_uno_vs_uno_defensivo = st.number_input('Uno vs Uno Defensivo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
                    nuevo_uno_vs_uno_ofensivo = st.number_input('Uno vs Uno Ofensivo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_juego_ofensivo = st.number_input('Juego Ofensivo', min_value=0, max_value=100, step=1, value=None)

                elif posicion == 'Lateral Izquierdo':
                    st.subheader('Aspectos Técnicos del Nuevo Lateral Izquierdo')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_anticipacion = st.number_input('Anticipación', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_por_abajo = st.number_input('Duelos por Abajo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_salida = st.number_input('Salida', min_value=0, max_value=100, step=1, value=None)
                    nuevo_cierres_coberturas = st.number_input('Cierres / Coberturas', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pase_paralelo = st.number_input('Pase Paralelo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_uno_vs_uno_defensivo = st.number_input('Uno vs Uno Defensivo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
                    nuevo_uno_vs_uno_ofensivo = st.number_input('Uno vs Uno Ofensivo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_juego_ofensivo = st.number_input('Juego Ofensivo', min_value=0, max_value=100, step=1, value=None)
                
                elif posicion == 'Mixto':
                    st.subheader('Aspectos Técnicos del Nuevo Mixto')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_cambio_frente = st.number_input('Cambio de Frente', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pase_espacio_filtrado = st.number_input('Pase a Espacio Filtrado', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_aereos = st.number_input('Duelos Aéreos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_salida_circulacion = st.number_input('Salida / Circulación', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_defensivos = st.number_input('Duelos Defensivos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_recuperaciones = st.number_input('Recuperaciones', min_value=0, max_value=100, step=1, value=None)
                    nuevo_duelos_ofensivos = st.number_input('Duelos Ofensivos', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_despliegue = st.number_input('Despliegue', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_centros = st.number_input('Centros', min_value=0, max_value=100, step=1, value=None)
                
                elif posicion == 'Ofensivo':
                    st.subheader('Aspectos Técnicos del Nuevo Ofensivo')

                    nuevo_tecnica_individual = st.number_input('Tecnica individual', min_value=0, max_value=100,step=1, value=None)
                    nuevo_cambio_frente = st.number_input('Cambio de Frente', min_value=0, max_value=100, step=1, value=None)
                    nuevo_pase_espacio_filtrado = st.number_input('Pase a Espacio Filtrado', min_value=0, max_value=100, step=1, value=None)
                    nuevo_asociaciones = st.number_input('Asociaciones', min_value=0, max_value=100, step=1, value=None)
                    nuevo_regates = st.number_input('Regates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_remates = st.number_input('Remates', min_value=0, max_value=100, step=1, value=None)
                    nuevo_retroceso_defensivo = st.number_input('Retroceso Defensivo', min_value=0, max_value=100, step=1, value=None)
                    nuevo_explosividad = st.number_input('Explosividad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_velocidad = st.number_input('Velocidad', min_value=0, max_value=100, step=1, value=None)
                    nuevo_resistencia = st.number_input('Resistencia', min_value=0, max_value=100, step=1, value=None)
                    nuevo_determinacion = st.number_input('Determinación', min_value=0, max_value=100, step=1, value=None)

        
            submit_update_jugador_button = st.form_submit_button('Actualizar Jugador')
            
            if submit_update_jugador_button:
                if nuevo_nombre_jugador == '':
                    st.warning('Nombre es un campo obligatorio, no puede dejarse vacío')
                elif jugador_uid is None:
                    st.warning('No se seleccionó ningún jugador para actualizar')

                elif entidad_ncolumna_nvalor_exists('jugador',{'nombre':nuevo_nombre_jugador}) and nuevo_nombre_jugador.lower() != current_nombre_jugador.lower():
                    st.error('El jugador con el mismo nombre ya existe')
                else:
                    representante_uid = df_representantes[df_representantes['nombre'] == nuevo_representante]['representante_uid'].values[0] if nuevo_representante else None
                    jugador_data = {
                        'nombre': nuevo_nombre_jugador.title(),
                        'nacionalidad': nuevo_nacionalidad if nuevo_nacionalidad != '' else None,
                        'fecha_nacimiento': nuevo_fecha_nacimiento,
                        'posicion': nuevo_posicion if nuevo_posicion != '' else None,
                        'posicion_alternativa': nuevo_posicion_alternativa if nuevo_posicion_alternativa != '' else None,
                        'categoria': nuevo_categoria,
                        'division': nuevo_division if nuevo_division != '' else None,
                        'seleccion': nuevo_seleccion if nuevo_seleccion != '' else None,
                        'altura': nueva_altura,
                        'peso': nuevo_peso,
                        'pierna_habil': nueva_pierna_habil if nueva_pierna_habil != '' else None,
                        'vencimiento_contrato': nuevo_vencimiento_contrato,
                        'sueldo': nuevo_sueldo,
                        'valor_transfermarket': nuevo_valor_transfermarket,
                        'foto_jugador': nueva_foto_jugador,
                        'foto_carrera_club': nueva_foto_carrera_club,
                        'foto_carrera_seleccion': nueva_foto_carrera_seleccion,
                        'aspectos_tecnicos_tacticos': nuevos_aspectos_tecnicos_tacticos,
                        'aspectos_fisicos': nuevos_aspectos_fisicos,
                        'personalidad': nueva_personalidad,
                        'otras_observaciones': nuevas_otras_observaciones,
                        'representante_uid': representante_uid
                    }
                    update_entidad('jugador',jugador_uid, jugador_data)
                    df_jugadores = get_all('jugador')
                    # Check if the position has changed
                    if nuevo_posicion != current_posicion:
                        # Get the entity key corresponding to the current position
                        entity_key = position_to_entity_key.get(current_posicion)
                        if entity_key:
                            # Get the entity from the ENTITIES dictionary
                            entity = ENTITIES.get(entity_key)
                            if entity:
                                delete_entidad(entity, jugador_uid)
                                exec(f"df_{entity_key} = get_all(entity)")
                        

                        if posicion == 'Extremo':
                            extremo_data = {
                             'jugador_uid': jugador_uid,
                            'tecnica_individual': nuevo_tecnica_individual,
                            'asociaciones': nuevo_asociaciones,
                            'centros': nuevo_centros,
                            'duelos_areos': nuevo_duelos_areos,
                            'regates': nuevo_regates,
                            'remates': nuevo_remates,
                            'retroceso_defensivo': nuevo_retroceso_defensivo,
                            'explosividad': nuevo_explosividad,
                            'velocidad': nuevo_velocidad,
                            'resistencia': nuevo_resistencia,
                            'definicion_peligrosidad': nuevo_definicion_peligrosidad
                            }
                            add_entidad('extremo',extremo_data)
                            df_extremos = get_all('extremo')
                        elif posicion == 'Arquero':
                                arquero_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': nuevo_tecnica_individual,
                                'atajadas': nuevo_atajadas,
                                'pelotas_aereas': nuevo_pelotas_aereas,
                                'de_libero': nuevo_de_libero,
                                'penales': nuevo_penales,
                                'circulacion': nuevo_circulacion,
                                'pase_largo': nuevo_pase_largo,
                                'uno_vs_uno': nuevo_uno_vs_uno,
                                'posicionamiento_movilidad': nuevo_posicionamiento_movilidad
                            }
                                add_entidad('arquero',arquero_data)
                                df_arqueros = get_all('arquero')
                
                        elif posicion == 'Centro Delantero':
                                centro_delantero_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': nuevo_tecnica_individual,
                                'juego_espaldas': nuevo_juego_espaldas,
                                'duelos_aereos': nuevo_duelos_aereos,
                                'regates': nuevo_regates,
                                'remates': nuevo_remates,
                                'presion': nuevo_presion,
                                'movilidad_desmarques': nuevo_movilidad_desmarques,
                                'velocidad': nuevo_velocidad,
                                'resistencia': nuevo_resistencia,
                                'definicion_peligrosidad': nuevo_definicion_peligrosidad,
                                'explosividad': nuevo_explosividad,
                                'remate_cabeza': nuevo_remate_cabeza
                            }
                                add_entidad('centro_delantero',centro_delantero_data)
                                df_centro_delanteros = get_all('centro_delantero')
                
                        elif posicion == 'Contención':
                                contencion_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': nuevo_tecnica_individual,
                                'cambio_frente': nuevo_cambio_frente,
                                'pase_espacio_filtrado': nuevo_pase_espacio_filtrado,
                                'duelos_aereos': nuevo_duelos_aereos,
                                'salida_circulacion': nuevo_salida_circulacion,
                                'relevos_vigilancias': nuevo_relevos_vigilancias,
                                'recuperaciones': nuevo_recuperaciones,
                                'duelos_por_abajo': nuevo_duelos_por_abajo,
                                'velocidad': nuevo_velocidad,
                                'resistencia': nuevo_resistencia,
                                'despliegue': nuevo_despliegue,
                                'coberturas_cierres': nuevo_coberturas_cierres,
                                'remate': nuevo_remate
                            }
                                add_entidad('contencion',contencion_data)
                                df_contenciones = get_all('contencion')

                        elif posicion == 'Defensor Central':
                                defensor_central_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': nuevo_tecnica_individual,
                                'anticipacion': nuevo_anticipacion,
                                'duelos_por_abajo': nuevo_duelos_por_abajo,
                                'duelos_aereos': nuevo_duelos_aereos,
                                'salida': nuevo_salida,
                                'cierres_coberturas': nuevo_cierres_coberturas,
                                'pase_paralelo': nuevo_pase_paralelo,
                                'uno_vs_uno': nuevo_uno_vs_uno,
                                'velocidad': nuevo_velocidad,
                                'resistencia': nuevo_resistencia,
                                'pelota_detenida': nuevo_pelota_detenida
                            }
                                add_entidad('defensor_central',defensor_central_data)
                                df_defensores_centrales = get_all('defensor_central')
                
                        elif posicion == 'Lateral Derecho':
                                lateral_derecho_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': tecnica_individual,
                                'anticipacion': nuevo_anticipacion,
                                'duelos_por_abajo': nuevo_duelos_por_abajo,
                                'duelos_aereos': nuevo_duelos_aereos,
                                'salida': nuevo_salida,
                                'cierres_coberturas': nuevo_cierres_coberturas,
                                'pase_paralelo': nuevo_pase_paralelo,
                                'uno_vs_uno_defensivo': nuevo_uno_vs_uno_defensivo,
                                'velocidad': nuevo_velocidad,
                                'resistencia': nuevo_resistencia,
                                'centros': nuevo_centros,
                                'uno_vs_uno_ofensivo': nuevo_uno_vs_uno_ofensivo,
                                'remates': nuevo_remates,
                                'juego_ofensivo': nuevo_juego_ofensivo
                            }
                                add_entidad('lateral_derecho',lateral_derecho_data)
                                df_laterales_derechos = get_all('lateral_derecho')
                
                        elif posicion == 'Lateral Izquierdo':
                                lateral_izquierdo_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': nuevo_tecnica_individual,
                                'anticipacion': nuevo_anticipacion,
                                'duelos_por_abajo': nuevo_duelos_por_abajo,
                                'duelos_aereos': nuevo_duelos_aereos,
                                'salida': nuevo_salida,
                                'cierres_coberturas': nuevo_cierres_coberturas,
                                'pase_paralelo': nuevo_pase_paralelo,
                                'uno_vs_uno_defensivo': nuevo_uno_vs_uno_defensivo,
                                'velocidad': nuevo_velocidad,
                                'resistencia': nuevo_resistencia,
                                'centros': nuevo_centros,
                                'uno_vs_uno_ofensivo': nuevo_uno_vs_uno_ofensivo,
                                'remates': nuevo_remates,
                                'juego_ofensivo': nuevo_juego_ofensivo
                            }
                                add_entidad('lateral_izquierdo',lateral_izquierdo_data)
                                df_laterales_izquierdos = get_all('lateral_izquierdo')

                        elif posicion == 'Mixto':
                                mixto_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': nuevo_tecnica_individual,
                                'cambio_frente': nuevo_cambio_frente,
                                'pase_espacio_filtrado': nuevo_pase_espacio_filtrado,
                                'duelos_aereos': nuevo_duelos_aereos,
                                'salida_circulacion': nuevo_salida_circulacion,
                                'duelos_defensivos': nuevo_duelos_defensivos,
                                'recuperaciones': nuevo_recuperaciones,
                                'duelos_ofensivos': nuevo_duelos_ofensivos,
                                'velocidad': nuevo_velocidad,
                                'resistencia': nuevo_resistencia,
                                'despliegue': nuevo_despliegue,
                                'remate': nuevo_remates,
                                'regate': nuevo_regates,
                                'centros': nuevo_centros
                            }
                                add_entidad('mixto',mixto_data)
                                df_mixtos = get_all('mixto')
                
                        elif posicion == 'Ofensivo':
                                ofensivo_data = {
                                 'jugador_uid': jugador_uid,
                                'tecnica_individual': nuevo_tecnica_individual,
                                'cambio_frente': nuevo_cambio_frente,
                                'pase_espacio_filtrado': nuevo_pase_espacio_filtrado,
                                'asociaciones': nuevo_asociaciones,
                                'regates': nuevo_regates,
                                'remates': nuevo_remates,
                                'retroceso_defensivo': nuevo_retroceso_defensivo,
                                'explosividad': nuevo_explosividad,
                                'velocidad': nuevo_velocidad,
                                'resistencia': nuevo_resistencia,
                                'determinacion': nuevo_determinacion
                            }
                                add_entidad('ofensivo',ofensivo_data)
                                df_ofensivos = get_all('ofensivo')
                        

# # Actualizar Video
# st.subheader('Actualizar Video')

# # Step 1: Choose whether to update a video associated with a Jugador or an Entrenador
# asociar_opcion_actualizar_video = st.radio("Seleccionar tipo:", ['Jugador', 'Entrenador'], key='asociar_opcion_actualizar_video')

# # Step 2: Select the specific Jugador or Entrenador
# if asociar_opcion_actualizar_video == 'Jugador':
#     entrenador_uid = None
#     if df_jugadores.empty:
#         st.warning("No hay jugadores disponibles.")
#         jugador_uid = None
#         entrenador_uid = None
#     else:
#         # Step 1: Select Club
#         club_nombre_actualizar_video = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='elegir_club_para_actualizar_video')

#         # If no club is selected, display all players
#         if club_nombre_actualizar_video == '':
#             jugadores_filtrados = df_jugadores
#         else:
#         # Obtener el club_uid del club seleccionado
#             club_uid = df_clubs[df_clubs['nombre'] == club_nombre_actualizar_video]['club_uid'].values[0]
    
#         # Filtrar la relación club_jugador por club_uid y obtener los jugador_uid
#             jugadores_en_club = df_club_jugador[df_club_jugador['club_uid'] == club_uid]['jugador_uid'].tolist()
    
#         # Filtrar df_jugadores para obtener solo los jugadores de ese club
#             jugadores_filtrados = df_jugadores[df_jugadores['jugador_uid'].isin(jugadores_en_club)]
#         jugador_nombre = st.selectbox('Jugador',[''] + jugadores_filtrados['nombre'].tolist(), key='actualizar_jugador_para_video')
#         if jugador_nombre == '':
#             jugador_uid = None
#         else:
#             jugador_uid = jugadores_filtrados[jugadores_filtrados['nombre'] == jugador_nombre]['jugador_uid'].values[0]
        
# elif asociar_opcion_actualizar_video == 'Entrenador':
#     jugador_uid = None
#     if df_entrenadores.empty:
#         st.warning("No hay entrenadores disponibles.")
#         entrenador_uid = None

#     else:
#         entrenador_nombre = st.selectbox('Entrenador', [''] + df_entrenadores['nombre'].tolist(), key='elegir_entrenador_para_actualizar_video')
#         if entrenador_nombre == '':
#             entrenador_uid = None
#         else:
#             entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == entrenador_nombre]['entrenador_uid'].values[0]

# # Step 3: Filter and select the video associated with the selected Jugador or Entrenador
# if jugador_uid:
#     tiene_video_filtrado = df_tiene_video[df_tiene_video['jugador_uid'] == jugador_uid]
#     if tiene_video_filtrado.empty:
#         st.warning('No hay video asociado al jugador.')
# elif entrenador_uid:
#     tiene_video_filtrado = df_tiene_video[df_tiene_video['entrenador_uid'] == entrenador_uid]
#     if tiene_video_filtrado.empty:
#         st.warning('No hay videos asociado a entrenador.')

# if tiene_video_filtrado is not None and not tiene_video_filtrado.empty:
#     video_uids = tiene_video_filtrado['video_uid'].tolist()
#     videos_filtrados = df_videos[df_videos['video_uid'].isin(video_uids)]
#     video_titulo = st.selectbox('Videos', [''] + videos_filtrados['titulo'].tolist(), key='actualizar_video')
#     if video_titulo == '':
#         video_uid = None
#     else:
#         video_uid = videos_filtrados[videos_filtrados['titulo'] == video_titulo]['video_uid'].values[0]
#         current_video = df_videos[df_videos['video_uid'] == video_uid]
#         current_url = current_video['url'].values[0]
#         current_titulo = current_video['titulo'].values[0]
#         current_descripcion = current_video['descripcion'].values[0]


#         # Form to update the video
#         with st.form('Actualizar Video'):
#             nuevo_url_video = st.text_input('Nueva URL del Video', value=current_url)
#             nuevo_titulo_video = st.text_input('Nuevo Título del Video', value=current_titulo)
#             nueva_descripcion_video = st.text_area('Nueva Descripción del Video', value=current_descripcion)

#             submit_update_video_button = st.form_submit_button('Actualizar Video')

#             if submit_update_video_button:
#                 if video_uid is None:
#                     st.warning('No se seleccionó ningún video para actualizar')
#                 if entidad_ncolumna_nvalor_exists('videos',{'url':nuevo_url_video}) and nuevo_url_video != current_url:
#                     st.error('El video con la misma URL ya existe')
#                 else:
#                     video_data = {
#                         'url': nuevo_url_video,
#                         'titulo': nuevo_titulo_video.title(),
#                         'descripcion': nueva_descripcion_video
#                     }
#                     update_entidad('video',video_uid, video_data)
#                     df_videos = get_all('videos')  


            
st.markdown('Actualizacion de datos')

# Obtener datos para listas desplegables
df_representantes = get_all('representante')
df_clubs = get_all('club')
df_videos = get_all('videos')
df_entrenadores = get_all('entrenador')
df_jugadores = get_all('jugador')
df_tiene_video = get_all('tiene_video')
df_club_jugador = get_all('club_jugador')
df_club_entrenador = get_all('club_entrenador')
df_extremos= get_all('extremo')
df_arqueros = get_all('arquero')
df_centro_delanteros = get_all('centro_delantero')
df_contenciones = get_all('contencion')
df_defensores_centrales = get_all('defensor_central')
df_laterales_derechos = get_all('lateral_derecho')
df_laterales_izquierdos = get_all('lateral_izquierdo')
df_mixtos = get_all('mixto')
df_ofensivos = get_all('ofensivo')





# Mostrar datos de ejemplo
st.write('Representantes:', df_representantes)
st.write('Clubs:', df_clubs)
st.write('Videos:', df_videos)
st.write('Entrenadores:', df_entrenadores)
st.write('Jugadores:', df_jugadores)
st.write('Tiene Video:', df_tiene_video)
st.write('Club_entrenador:', df_club_entrenador)
st.write('Club_jugador:', df_club_jugador)
st.write('Extremos:', df_extremos)
st.write('Arqueros:', df_arqueros)
st.write('Centro Delanteros:', df_centro_delanteros)
st.write('Contenciones:', df_contenciones)
st.write('Defensores Centrales:', df_defensores_centrales)
st.write('Laterales Derechos:', df_laterales_derechos)
st.write('Laterales Izquierdos:', df_laterales_izquierdos)
st.write('Mixtos:', df_mixtos)
st.write('Ofensivos:', df_ofensivos)
