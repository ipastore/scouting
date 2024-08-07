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
pertenece = Table('pertenece', metadata, autoload_with=engine)
representante = Table('representante', metadata, autoload_with=engine)


# Cargar datos de tablas relacionadas

# Convert UUID columns to strings in the DataFrame
def convert_uuid_to_str(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
    return df

## GETS
def get_all_jugadores():
    query = select(jugador.c.jugador_uid, jugador.c.nombre, jugador.c.nacionalidad, 
                   jugador.c.fecha_nacimiento, jugador.c.posicion, jugador.c.posicion_alternativa, 
                   jugador.c.categoria, jugador.c.division, jugador.c.seleccion, jugador.c.altura, 
                   jugador.c.peso, jugador.c.pierna_habil, jugador.c.vencimiento_contrato, jugador.c.sueldo, 
                   jugador.c.valor_transfermarket, jugador.c.foto_jugador, jugador.c.foto_carrera_club,
                     jugador.c.foto_carrera_seleccion, jugador.c.aspectos_tecnicos_tacticos, jugador.c.aspectos_fisicos,
                       jugador.c.personalidad, jugador.c.otras_observaciones, jugador.c.representante_uid)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)

def get_all_representantes():
    query = select(representante.c.representante_uid, representante.c.nombre)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)

def get_all_clubs():
    query = select(club.c.club_uid, club.c.nombre, club.c.foto_escudo, club.c.foto_plantel)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)

def get_all_entrenadores():
    query = select(entrenador.c.entrenador_uid, entrenador.c.nombre, entrenador.c.nacionalidad, entrenador.c.fecha_nacimiento, 
                   entrenador.c.esquema_predilecto, entrenador.c.foto_entrenador, entrenador.c.foto_carrera_entrenador, 
                   entrenador.c.foto_carrera_como_jugador, entrenador.c.fase_ofensiva, entrenador.c.fase_defensiva,
                    entrenador.c.transiciones, entrenador.c.otras_observaciones, entrenador.c.ultimos_partidos, 
                    entrenador.c.foto_ultimos_partidos1, entrenador.c.foto_ultimos_partidos2)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)

def get_all_videos():
    query = select(videos.c.video_uid, videos.c.url, videos.c.titulo, videos.c.descripcion)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)


## CHECKS de existencia
def jugador_exists_representante(nombre, representante_uid):
    query = select(jugador).where(jugador.c.nombre == nombre, jugador.c.representante_uid == representante_uid)
    result = session.execute(query).fetchone()
    return result is not None

def jugador_exists(nombre):
    query = select(jugador).where(jugador.c.nombre == nombre)
    result = session.execute(query).fetchone()
    return result is not None

def club_exists(nombre):
    query = select([club]).where(club.c.nombre == nombre)
    result = session.execute(query).fetchone()
    return result is not None

def entrenador_exists(nombre):
    query = select([entrenador]).where(entrenador.c.nombre == nombre)
    result = session.execute(query).fetchone()
    return result is not None

def representante_exists(nombre):
    query = select([representante]).where(representante.c.nombre == nombre)
    result = session.execute(query).fetchone()
    return result is not None

## ADDS
def add_jugador(data):
    insert_stmt = jugador.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Jugador agregado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar jugador: {e}')


## UPDATES
def update_jugador(player_id, data):
    update_stmt = jugador.update().where(jugador.c.jugador_uid == player_id).values(data)
    try:
        session.execute(update_stmt)
        session.commit()
        st.success('Jugador actualizado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al actualizar jugador: {e}')

# ## DELETES ACA ME QUEDE
# def delete_player(player_id):
#     delete_stmt = jugador.delete().where(jugador.c.jugador_uid == player_id)
#     try:
#         session.execute(delete_stmt)
#         session.commit()
#         st.success('Jugador eliminado exitosamente')
#     except SQLAlchemyError as e:
#         session.rollback()
#         st.error(f'Error al eliminar jugador: {e}')

# def delete_jugador(jugador_uid):
#     with engine.connect() as connection:
#         with connection.begin():
#             connection.execute(jugador.delete().where(jugador.c.jugador_uid == jugador_uid))
#         st.success('Jugador eliminado con éxito!')

# Obtener datos para listas desplegables
df_representantes = get_all_representantes()
df_clubs = get_all_clubs()
df_videos = get_all_videos()
df_entrenadores = get_all_entrenadores()
df_jugadores = get_all_jugadores()

# Mostrar datos de ejemplo
st.write('Representantes:', df_representantes)
st.write('Clubs:', df_clubs)
st.write('Videos:', df_videos)
st.write('Entrenadores:', df_entrenadores)
st.write('Jugadores:', df_jugadores)

st.subheader('Agregar Jugador')

# Set the minimum and maximum values for the date input
min_date_nacimiento = datetime.date(1900, 1, 1)
max_date_nacimiento = datetime.date.today()
min_date_vencimiento_contrato = datetime.date.today()
max_date_vencimiento_contrato = datetime.date(2100, 1, 1)

with st.form('Agregar Jugador'):

    #NOT NULL
    nombre = st.text_input('Nombre') 
    nacionalidad = st.selectbox('Nacionalidad', ['','Argentina', 'Brasil', 'Uruguay', 'Chile', 'Paraguay', 'Bolivia', 'Perú', 'Colombia', 'Venezuela', 'Ecuador'])
    fecha_nacimiento = st.date_input('Fecha de Nacimiento', min_value=min_date_nacimiento, max_value=max_date_nacimiento, value=None)
    #NOT NULL
    posicion = st.selectbox('Posición', ['Arquero', 'Defensor Central', 'Lateral Derecho', 'Lateral Izquierdo', 'Contención', 'Mixto', 'Ofensivo', 'Centro Delantero'])
    posicion_alternativa = st.selectbox('Posición Alternativa', ['','Arquero', 'Defensor Central', 'Lateral Derecho', 'Lateral Izquierdo', 'Contención', 'Mixto', 'Ofensivo', 'Centro Delantero'])
    categoria = st.number_input('Categoría', min_value=1900, max_value=2100, step=1, value=None)
    division = st.selectbox('División', ['','Primera', 'Reserva', 'Juveniles'])
    seleccion = st.selectbox('Selección', ['','Mayor', 'Sub20', 'Sub17', 'Sub15', 'No'])
    altura = st.number_input('Altura (m)', min_value=0.0, step=0.01, value=None)
    peso = st.number_input('Peso (kg)', min_value=0, step=1, value=None)
    pierna_habil = st.selectbox('Pierna Hábil', ['','Diestro', 'Zurdo', 'Ambidiestro'])
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
    representante_nombre = st.selectbox('Representante', [''] + df_representantes['nombre'].tolist())
    if representante_nombre == '':
        representante_uid = None
    else:
        representante_uid = df_representantes[df_representantes['nombre'] == representante_nombre]['representante_uid'].values[0]

    submit_button = st.form_submit_button('Agregar')

    # if submit_button:
    #     add_jugador_data = {
    #         'nombre': nombre,
    #         'nacionalidad': nacionalidad if nacionalidad != '' else None,
    #         'fecha_nacimiento': fecha_nacimiento,
    #         'posicion': posicion,
    #         'posicion_alternativa': posicion_alternativa if posicion_alternativa != '' else None,
    #         'categoria': categoria,
    #         'division': division if division != '' else None,
    #         'seleccion': seleccion if seleccion != '' else None,
    #         'altura': altura,
    #         'peso': peso,
    #         'pierna_habil': pierna_habil if pierna_habil != '' else None,
    #         'vencimiento_contrato': vencimiento_contrato,
    #         'sueldo': sueldo,
    #         'valor_transfermarket': valor_transfermarket,
    #         'foto_jugador': foto_jugador,
    #         'foto_carrera_club': foto_carrera_club,
    #         'foto_carrera_seleccion': foto_carrera_seleccion,
    #         'aspectos_tecnicos_tacticos': aspectos_tecnicos_tacticos,
    #         'aspectos_fisicos': aspectos_fisicos,
    #         'personalidad': personalidad,
    #         'otras_observaciones': otras_observaciones,
    #         'representante_uid': representante_uid
    #     }
    #     add_jugador(add_jugador_data)

    if submit_button:
        warning = False
        if jugador_exists_representante(nombre, representante_uid):
            st.error('''El jugador con el mismo nombre y representante ya existe. 
                    Esto es altamente improbable, si quiere agregar un jugador con el
                      mismo nombre de jugador y representante, ponganse en contacto con el 
                     equipo de Headers'''
                     )
        elif jugador_exists(nombre):
            st.warning('El jugador con el mismo nombre ya existe')
            warning = True
            if warning and st.checkbox('Confirmar adición del jugador a pesar de la advertencia'):
                add_jugador_data = {
                    'nombre': nombre,
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
                add_jugador(add_jugador_data)                
        elif not warning: 
            add_jugador_data = {
            'nombre': nombre,
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
            add_jugador(add_jugador_data)