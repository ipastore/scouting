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

posicion_opciones = ['','Arquero', 'Defensor Central', 'Lateral Derecho', 'Lateral Izquierdo', 'Contención', 'Mixto', 'Ofensivo', 'Centro Delantero']

division_opciones = ['','Primera', 'Reserva', 'Juveniles']

seleccion_opciones = ['','Mayor', 'Sub20', 'Sub17', 'Sub15', 'No']

pierna_habil_opciones = ['','Diestro', 'Zurdo', 'Ambidiestro']

# Set the minimum and maximum values for the date input
min_date_nacimiento = datetime.date(1900, 1, 1)
max_date_nacimiento = datetime.date.today()
min_date_vencimiento_contrato = datetime.date.today()
max_date_vencimiento_contrato = datetime.date(2100, 1, 1)




# Cargar datos de tablas relacionadas

# Convert UUID columns to strings in the DataFrame
def convert_uuid_to_str(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
    return df

## Funciones de GETS
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

def get_all_club_jugador():
    query = select(club_jugador.c.jugador_uid, club_jugador.c.club_uid)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)

def get_all_club_entrenador():
    query = select(club_entrenador.c.entrenador_uid, club_entrenador.c.club_uid)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)

def get_all_tiene_video():
    query = select(tiene_video.c.jugador_uid, tiene_video.c.video_uid, tiene_video.c.entrenador_uid)
    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return convert_uuid_to_str(df)


## Funciones CHECKS de existencia
def jugador_representante_exists(nombre, representante_uid):
    query = select(jugador).where(func.lower(jugador.c.nombre) == func.lower(nombre), jugador.c.representante_uid == representante_uid)
    result = session.execute(query).fetchone()
    return result is not None

def jugador_exists(nombre):
    query = select(jugador).where(func.lower(jugador.c.nombre) == func.lower(nombre))
    result = session.execute(query).fetchone()
    return result is not None

def club_exists(nombre):
    query = select(club).where(func.lower(club.c.nombre) == func.lower(nombre))
    result = session.execute(query).fetchone()
    return result is not None

def entrenador_exists(nombre):
    query = select(entrenador).where(func.lower(entrenador.c.nombre) == func.lower(nombre))
    result = session.execute(query).fetchone()
    return result is not None

def representante_exists(nombre):
    query = select(representante).where(func.lower(representante.c.nombre) == func.lower(nombre))
    result = session.execute(query).fetchone()
    return result is not None

def video_exists(url):
    query = select(videos).where(videos.c.url == url)
    result = session.execute(query).fetchone()
    return result is not None

## Tener en cuenta que es una tabla de entrenadores con clubes asignados. Si 
## no se asigna club, un entrenador tiene NULL.
## Se asume que no puede existir un club si no tiene entrenador.
def club_entrenador_exists(club_uid):
    query = select(club_entrenador).where(club_entrenador.c.club_uid == club_uid)
    result = session.execute(query).fetchone()
    return result is not None

## Tener en cuenta que es una tabla de jugadores con clubes asignados. Si
## no se asigna club, un jugador tiene NULL.
## Se asune qye no puede existir un club si no tiene jugador.
## Esta tabla sirve para saber a qué club pertenece un jugador en un momento dado.
## Este check no se utiliza porque es redundante con jugador_exists
def club_jugador_exists(club_uid, jugador_uid):
    query = select(club_jugador).where(club_jugador.c.club_uid == club_uid, club_jugador.c.jugador_uid == jugador_uid)
    result = session.execute(query).fetchone()
    return result is not None

def tiene_video_exists(jugador_uid, video_uid):
    query = select(tiene_video).where(tiene_video.c.jugador_uid == jugador_uid, tiene_video.c.video_uid == video_uid)
    result = session.execute(query).fetchone()
    return result is not None

###### Funciones de ADDS ###########
def add_jugador(data):
    insert_stmt = jugador.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Jugador agregado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar jugador: {e}')

def add_club(data):
    insert_stmt = club.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Club agregado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar club: {e}')

def add_entrenador(data):
    insert_stmt = entrenador.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Entrenador agregado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar entrenador: {e}')

def add_representante(data):
    insert_stmt = representante.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Representante agregado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar representante: {e}')

def add_video(data):
    insert_stmt = videos.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Video agregado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar video: {e}')

def add_tiene_video(data):
    insert_stmt = tiene_video.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Relación entre jugador y video agregada exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar relación entre jugador y video: {e}')

def add_club_entrenador(data):
    insert_stmt = club_entrenador.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Relación entre club y entrenador agregada exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar relación entre club y entrenador: {e}')

def add_club_jugador(data):
    insert_stmt = club_jugador.insert().values(data)
    try:
        session.execute(insert_stmt)
        session.commit()
        st.success('Relación entre club y jugador agregada exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al agregar relación entre club y jugador: {e}')


### Funciones de DELETE
def delete_representante(representante_uid):
    delete_stmt = representante.delete().where(representante.c.representante_uid == representante_uid)
    try:
        session.execute(delete_stmt)
        session.commit()
        st.success('Representante eliminado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al eliminar representante: {e}')

def delete_club(club_uid):
    delete_stmt = club.delete().where(club.c.club_uid == club_uid)
    try:
        session.execute(delete_stmt)
        session.commit()
        st.success('Club eliminado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al eliminar club: {e}')

def delete_entrenador(entrenador_uid):
    delete_stmt = entrenador.delete().where(entrenador.c.entrenador_uid == entrenador_uid)
    try:
        session.execute(delete_stmt)
        session.commit()
        st.success('Entrenador eliminado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al eliminar entrenador: {e}')

def delete_jugador(jugador_uid):
    delete_stmt = jugador.delete().where(jugador.c.jugador_uid == jugador_uid)
    try:
        session.execute(delete_stmt)
        session.commit()
        st.success('Jugador eliminado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al eliminar jugador: {e}')

def delete_video(video_uid):
    delete_stmt = videos.delete().where(videos.c.video_uid == video_uid)
    try:
        session.execute(delete_stmt)
        session.commit()
        st.success('Video eliminado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al eliminar video: {e}')


#### Funciones de UPDATE
def update_representante(representante_uid, data):
    update_stmt = representante.update().where(representante.c.representante_uid == representante_uid).values(data)
    try:
        session.execute(update_stmt)
        session.commit()
        st.success('Representante actualizado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al actualizar representante: {e}')

def update_club(club_uid, data):
    update_stmt = club.update().where(club.c.club_uid == club_uid).values(data)
    try:
        session.execute(update_stmt)
        session.commit()
        st.success('Club actualizado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al actualizar club: {e}')

def update_entrenador(entrenador_uid, data):
    update_stmt = entrenador.update().where(entrenador.c.entrenador_uid == entrenador_uid).values(data)
    try:
        session.execute(update_stmt)
        session.commit()
        st.success('Entrenador actualizado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al actualizar entrenador: {e}')

def update_jugador(jugador_uid, data):
    update_stmt = jugador.update().where(jugador.c.jugador_uid == jugador_uid).values(data)
    try:
        session.execute(update_stmt)
        session.commit()
        st.success('Jugador actualizado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al actualizar jugador: {e}')

def update_video(video_uid, data):
    update_stmt = videos.update().where(videos.c.video_uid == video_uid).values(data)
    try:
        session.execute(update_stmt)
        session.commit()
        st.success('Video actualizado exitosamente')
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f'Error al actualizar video: {e}')




# Obtener datos para listas desplegables
df_representantes = get_all_representantes()
df_clubs = get_all_clubs()
df_videos = get_all_videos()
df_entrenadores = get_all_entrenadores()
df_jugadores = get_all_jugadores()
df_tiene_video = get_all_tiene_video()
df_club_jugador = get_all_club_jugador()
df_club_entrenador = get_all_club_entrenador()


####### FORMS de AGREGAR ##############
st.subheader('Agregar Jugador')


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
    #NOT NULL
    posicion = st.selectbox('Posición', posicion_opciones, key='agregar_posicion_a_jugador')
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

    

    submit_jugador_button = st.form_submit_button('Agregar Jugador')

    if submit_jugador_button:
        warning = False
        if jugador_representante_exists(nombre_jugador, representante_uid):
            st.error('''El jugador con el mismo nombre y representante ya existe. 
                    Esto es altamente improbable, si quiere agregar un jugador con el
                      mismo nombre de jugador y representante, ponganse en contacto con el 
                     equipo de Headers'''
                     )
        elif jugador_exists(nombre_jugador):
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
                add_jugador(jugador_data)
                df_jugadores = get_all_jugadores()
                jugador_uid = df_jugadores[df_jugadores['nombre'].str.lower() == nombre_jugador.lower()]['jugador_uid'].values[0]
                club_jugador_data = {
                    'jugador_uid': jugador_uid,
                    'club_uid': club_uid        
                    }
                add_club_jugador(club_jugador_data)                
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
            add_jugador(jugador_data)
            df_jugadores = get_all_jugadores()
            jugador_uid = df_jugadores[df_jugadores['nombre'].str.lower() == nombre_jugador.lower()]['jugador_uid'].values[0]
            club_jugador_data = {
                    'jugador_uid': jugador_uid,
                    'club_uid': club_uid,    
                    }
            add_club_jugador(club_jugador_data)     

################### Form agregar Club ####################
st.subheader('Agregar Club')

with st.form('Agregar Club'):
    nombre_club = st.text_input('Nombre')
    foto_escudo = st.text_input('Foto Escudo')
    foto_plantel = st.text_input('Foto Plantel')
    submit_club_button = st.form_submit_button('Agregar Club')

    if submit_club_button:
        if club_exists(nombre_club):
            st.error('El club con el mismo nombre ya existe')
        else:
            club_data = {
                'nombre': nombre_club.title(),
                'foto_escudo': foto_escudo,
                'foto_plantel': foto_plantel
            }
            add_club(club_data)

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
        if entrenador_exists(nombre_entrenador):
            st.error('El entrenador con el mismo nombre ya existe')
        ## if club_ui already exists in the table club_entrenador
        elif club_entrenador_exists(club_uid):
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
            add_entrenador(entrenador_data)
            df_entrenadores = get_all_entrenadores()
            entrenador_uid = df_entrenadores[df_entrenadores['nombre'].str.lower() == nombre_entrenador.lower()]['entrenador_uid'].values[0]
            club_entrenador_data = {
                'entrenador_uid': entrenador_uid,
                'club_uid': club_uid,
            }
            add_club_entrenador(club_entrenador_data)
    
################### Form agregar Representante ####################
st.subheader('Agregar Representante')

with st.form('Agregar Representante'):
    nombre_representante = st.text_input('Nombre')
    submit_representante_button = st.form_submit_button('Agregar Representante')

    if submit_representante_button:
        if representante_exists(nombre_representante):
            st.error('El representante con el mismo nombre ya existe')
        else:
            representante_data = {
                'nombre': nombre_representante.title()
            }
            add_representante(representante_data)

################### Form agregar Video ####################
st.subheader('Agregar Video')

# Step 1: Choose whether to associate the video with a player or coach
st.write("Asociar Video a:")
asociar_opcion_agregar_video = st.radio("Seleccionar:", ['Entrenador', 'Jugador'])

# Initialize the jugador_uid and entrenador_uid to None
jugador_uid = None
entrenador_uid = None

# Step 2: Display the form based on the selection
with st.form('Agregar Video'):
    video_url = st.text_input('URL del Video')
    video_titulo = st.text_input('Título del Video')
    video_descripcion = st.text_area('Descripción del Video', value=None)

    if asociar_opcion_agregar_video == 'Jugador':
        if df_jugadores.empty:
            st.warning("No hay jugadores disponibles para asociar con el video.")
        else: 
            jugador_nombre = st.selectbox('Jugador', df_jugadores['nombre'].tolist(), key='elegir_jugador_para_video')
            jugador_uid = df_jugadores[df_jugadores['nombre'] == jugador_nombre]['jugador_uid'].values[0]
    elif asociar_opcion_agregar_video == 'Entrenador':
        if df_entrenadores.empty:
            st.warning("No hay entrenadores disponibles para asociar con el video.")
        else:
            entrenador_nombre = st.selectbox('Entrenador', df_entrenadores['nombre'].tolist(), key='elegir_entrenador_para_video')
            entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == entrenador_nombre]['entrenador_uid'].values[0]

    submit_video_button = st.form_submit_button('Agregar Video')

    if submit_video_button:
        if video_exists(video_url):
            st.error('El video con la misma URL ya existe')
        else:
            video_data = {
                'url': video_url,
                'titulo': video_titulo.title(),
                'descripcion': video_descripcion
            }
            add_video(video_data)
            df_videos = get_all_videos()
            video_uid = df_videos[df_videos['url'] == video_url]['video_uid'].values[0]
            tiene_video_data = {
                'jugador_uid': jugador_uid,
                'entrenador_uid': entrenador_uid,
                'video_uid': video_uid
            }
            add_tiene_video(tiene_video_data)

####### FORMS de DELETE ##############
#### Representante
st.subheader('Borrar Representante')
with st.form('Borrar Representante'):
    representante_nombre = st.selectbox('Representante', [''] + df_representantes['nombre'].tolist(),key='borrar_representante')
    if representante_nombre == '':
        representante_uid = None
    else:
        representante_uid = df_representantes[df_representantes['nombre'] == representante_nombre]['representante_uid'].values[0]
    submit_delete_representante_button = st.form_submit_button('Borrar Representante')

    if submit_delete_representante_button:
        if representante_uid is None:
            st.warning('No se seleccionó ningún representante')
        else:
            delete_representante(representante_uid)
            df_representantes = get_all_representantes()

#### Club
st.subheader('Borrar Club')
with st.form('Borrar Club'):
    club_nombre = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='borrar_club')
    if club_nombre == '':
        club_uid = None
    else:
        club_uid = df_clubs[df_clubs['nombre'] == club_nombre]['club_uid'].values[0]
    submit_delete_club_button = st.form_submit_button('Borrar Club')

    if submit_delete_club_button:
        if club_uid is None:
            st.warning('No se seleccionó ningún club')
        else:
            delete_club(club_uid)
            df_clubs = get_all_clubs()

### Entrenador
st.subheader('Borrar Entrenador')
with st.form('Borrar Entrenador'):
    entrenador_nombre = st.selectbox('Entrenador', [''] + df_entrenadores['nombre'].tolist(),key='borrar_entrenador')
    if entrenador_nombre == '':
        entrenador_uid = None
    else:
        entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == entrenador_nombre]['entrenador_uid'].values[0]
    submit_delete_entrenador_button = st.form_submit_button('Borrar Entrenador')

    if submit_delete_entrenador_button:
        if entrenador_uid is None:
            st.warning('No se seleccionó ningún entrenador')
        else:
            delete_entrenador(entrenador_uid)
            df_entrenadores = get_all_entrenadores()

### Jugador
st.subheader('Borrar Jugador')

# Step 1: Select Club
club_nombre = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='elegir_club_para_borrar_jugador')

# If no club is selected, display all players
if club_nombre == '':
    jugadores_filtrados = df_jugadores
else:
    # Obtener el club_uid del club seleccionado
    club_uid = df_clubs[df_clubs['nombre'] == club_nombre]['club_uid'].values[0]
    
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
            delete_jugador(jugador_uid)
            df_jugadores = get_all_jugadores()  # Refresh the jugadores list

### Video
st.subheader('Borrar Video')
# Step 1: Choose whether to delete a video associated with a Jugador or an Entrenador
asociar_opcion_borrar_video = st.radio("Seleccionar tipo:", ['Jugador', 'Entrenador'])

# Step 2: Select the specific Jugador or Entrenador
if asociar_opcion_borrar_video == 'Jugador':
    if df_jugadores.empty:
        st.warning("No hay jugadores disponibles.")
        jugador_uid = None
    else:
        jugador_nombre = st.selectbox('Jugador', df_jugadores['nombre'].tolist(), key='elegir_jugador_para_borrar_video')
        jugador_uid = df_jugadores[df_jugadores['nombre'] == jugador_nombre]['jugador_uid'].values[0]
        entrenador_uid = None
elif asociar_opcion_borrar_video == 'Entrenador':
    if df_entrenadores.empty:
        st.warning("No hay entrenadores disponibles.")
        entrenador_uid = None
    else:
        entrenador_nombre = st.selectbox('Entrenador', df_entrenadores['nombre'].tolist(), key='elegir_entrenador_para_borrar_video')
        entrenador_uid = df_entrenadores[df_entrenadores['nombre'] == entrenador_nombre]['entrenador_uid'].values[0]
        jugador_uid = None

# Step 3: Filter and select the video associated with the selected Jugador or Entrenador
if jugador_uid:
    tiene_video_filtrado = df_tiene_video[df_tiene_video['jugador_uid'] == jugador_uid]
elif entrenador_uid:
    tiene_video_filtrado = df_tiene_video[df_tiene_video['entrenador_uid'] == entrenador_uid]
else:
    tiene_video_filtrado = None

if tiene_video_filtrado is not None and not tiene_video_filtrado.empty:
    video_uids = tiene_video_filtrado['video_uid'].tolist()
    videos_filtrados = df_videos[df_videos['video_uid'].isin(video_uids)]
    video_titulo = st.selectbox('Video', videos_filtrados['titulo'].tolist(), key='borrar_video')
    video_uid = videos_filtrados[videos_filtrados['titulo'] == video_titulo]['video_uid'].values[0]
else:
    video_uid = None
    st.warning('No hay videos asociados disponibles para eliminar.')

# Form to delete the video
with st.form('Borrar Video'):
    submit_delete_video_button = st.form_submit_button('Borrar Video')

    if submit_delete_video_button:
        if video_uid is None:
            st.warning('No se seleccionó ningún video')
        else:
            delete_video(video_uid)
            df_videos = get_all_videos()  # Refresh the videos list


### FORM de Actualizar
# Actualizar Representante
st.subheader('Actualizar Representante')

with st.form('Actualizar Representante'):
    representante_nombre = st.selectbox('Representante', [''] + df_representantes['nombre'].tolist(), key='actualizar_representante')
    if representante_nombre == '':
        representante_uid = None
    else:
        representante_uid = df_representantes[df_representantes['nombre'] == representante_nombre]['representante_uid'].values[0]
    nuevo_nombre_representante = st.text_input('Nuevo Nombre')
    submit_update_representante_button = st.form_submit_button('Actualizar Representante')

    if submit_update_representante_button:
        if representante_uid is None:
            st.warning('No se seleccionó ningún representante')
        else:
            if representante_exists(nuevo_nombre_representante):
                st.error('El representante con el mismo nombre ya existe')
            else:
                representante_data = {
                    'nombre': nuevo_nombre_representante.title()
                }
                update_representante(representante_uid, representante_data)
                df_representantes = get_all_representantes()

# Actualizar Club
st.subheader('Actualizar Club')

# Step 1: Select Club (outside the form)
update_club_nombre_option = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='actualizar_club')

if update_club_nombre_option == '':
    club_uid = None

else:
    # Get club_uid and current values from the selected club
    club_uid = df_clubs[df_clubs['nombre'] == update_club_nombre_option]['club_uid'].values[0]
    current_club = df_clubs[df_clubs['club_uid'] == club_uid]
    current_nombre = current_club['nombre'].values[0]
    current_foto_escudo = current_club['foto_escudo'].values[0]
    current_foto_plantel = current_club['foto_plantel'].values[0]
    
    # Step 2: Prepopulate the form fields with current values (inside the form)
    with st.form('Actualizar Club'):
        nuevo_nombre_club = st.text_input('Nuevo Nombre', value=current_nombre)
        nuevo_foto_escudo = st.text_input('Nueva Foto Escudo', value=current_foto_escudo)
        nuevo_foto_plantel = st.text_input('Nueva Foto Plantel', value=current_foto_plantel)

        submit_update_club_button = st.form_submit_button('Actualizar Club')

        if submit_update_club_button:
            if club_exists(nuevo_nombre_club) and nuevo_nombre_club.lower() != current_nombre.lower():
                st.error('El club con el mismo nombre ya existe')
            else:
                club_data = {
                    'nombre': nuevo_nombre_club.title(),
                    'foto_escudo': nuevo_foto_escudo,
                    'foto_plantel': nuevo_foto_plantel,
                }
                update_club(club_uid, club_data)
                df_clubs = get_all_clubs()  # Refresh the list of clubs

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
            if entrenador_exists(nuevo_nombre_entrenador) and nuevo_nombre_entrenador.lower() != current_nombre_entrenador.lower():
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
                update_entrenador(entrenador_uid, entrenador_data)
                df_entrenadores = get_all_entrenadores()

# Actualizar Jugador
st.subheader('Actualizar Jugador')

# Step 1: Select Club
club_nombre = st.selectbox('Club', [''] + df_clubs['nombre'].tolist(), key='elegir_club_para_actualizar_jugador')

# If no club is selected, display all players
if club_nombre == '':
    jugadores_filtrados = df_jugadores
else:
    # Obtener el club_uid del club seleccionado
    club_uid = df_clubs[df_clubs['nombre'] == club_nombre]['club_uid'].values[0]
    
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
    



####ACA ME QUEDE 09/08/24
    with st.form('Actualizar Jugador'):
            
            # Form fields to update the player
            nuevo_nombre_jugador = st.text_input('Nuevo Nombre', value=current_nombre_jugador)
            nuevo_nacionalidad = st.selectbox('Nueva Nacionalidad', nacionalidad_opciones, key='actualizar_nacionalidad_jugador',
                                        index=nacionalidad_opciones.index(current_nacionalidad) if current_nacionalidad else 0)
            nuevo_fecha_nacimiento = st.date_input('Nueva Fecha de Nacimiento', min_value=min_date_nacimiento, max_value=max_date_nacimiento, value=current_fecha_nacimiento)
            nuevo_posicion = st.selectbox('Nueva Posición', posicion_opciones, key='actualizar_posicion_jugador',
                                    index=posicion_opciones.index(current_posicion) if current_posicion else 0)
            nuevo_posicion_alternativa = st.selectbox('Nueva Posición Alternativa', posicion_opciones, key='actualizar_posicion_alternativa_jugador',
                                                index=posicion_opciones.index(current_posicion_alternativa) if current_posicion_alternativa else 0)
            nuevo_categoria = st.number_input('Nueva Categoría', min_value=1900, max_value=2100, step=1, value=current_categoria)
            nuevo_division = st.selectbox('Nueva División', division_opciones, key='actualizar_division_jugador',
                                    index=division_opciones.index(current_division) if current_division else 0)
            nuevo_seleccion = st.selectbox('Nueva Selección', seleccion_opciones, key='actualizar_seleccion_jugador',
                                    index=seleccion_opciones.index(current_seleccion) if current_seleccion else 0)
            nueva_altura = st.number_input('Nueva Altura (m)', min_value=0.00, step=0.01, value=float(current_altura))
            nuevo_peso = st.number_input('Nuevo Peso (kg)', min_value=0, step=1, value=current_peso)
            nueva_pierna_habil = st.selectbox('Nueva Pierna Hábil', pierna_habil_opciones, key='actualizar_pierna_habil_jugador',
                                    index=pierna_habil_opciones.index(current_pierna_habil) if current_pierna_habil else 0)
            nuevo_vencimiento_contrato = st.date_input('Nuevo Vencimiento de Contrato', min_value=min_date_vencimiento_contrato, max_value=max_date_vencimiento_contrato, value=current_vencimiento_contrato)
            nuevo_sueldo = st.number_input('Nuevo Sueldo (USD)', min_value=0, step=1, value=current_sueldo)
            nuevo_valor_transfermarket = st.number_input('Nuevo Valor Transfermarket (MM USD)', min_value=0.0, step=0.1, value=current_valor_transfermarket)
            nueva_foto_jugador = st.text_input('Nueva Foto Jugador', value=current_foto_jugador)
            nueva_foto_carrera_club = st.text_input('Nueva Foto Carrera Club', value=current_foto_carrera_club)
            nueva_foto_carrera_seleccion = st.text_input('Nueva Foto Carrera Selección', value=current_foto_carrera_seleccion)
            nuevos_aspectos_tecnicos_tacticos = st.text_area('Nuevos Aspectos Técnicos/Tácticos', value=current_aspectos_tecnicos_tacticos)
            nuevos_aspectos_fisicos = st.text_area('Nuevos Aspectos Físicos', value=current_aspectos_fisicos)
            nueva_personalidad = st.text_area('Nueva Personalidad', value=current_personalidad)
            nuevas_otras_observaciones = st.text_area('Nuevas Otras Observaciones', value=current_otras_observaciones)
            nuevo_representante = st.selectbox('Nuevo Representante', [''] + df_representantes['nombre'].tolist(), key='actualizar_representante_jugador',
                                    index=df_representantes[df_representantes['representante_uid'] == current_representante_uid].index[0] if current_representante_uid else 0)
        
            submit_update_jugador_button = st.form_submit_button('Actualizar Jugador')
            
            if submit_update_jugador_button:
                if jugador_exists(nuevo_nombre_jugador) and nuevo_nombre_jugador.lower() != current_nombre_jugador.lower():
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
                        'altura': float(nueva_altura),
                        'peso': int(nuevo_peso),
                        'pierna_habil': nueva_pierna_habil if nueva_pierna_habil != '' else None,
                        'vencimiento_contrato': nuevo_vencimiento_contrato,
                        'sueldo': int(nuevo_sueldo),
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
                    update_jugador(jugador_uid, jugador_data)
                    df_jugadores = get_all_jugadores()

#Jugador data para comparar
#             jugador_data = {
            # 'nombre': nombre_jugador.title(),
            # 'nacionalidad': nacionalidad if nacionalidad != '' else None,
            # 'fecha_nacimiento': fecha_nacimiento,
            # 'posicion': posicion,
            # 'posicion_alternativa': posicion_alternativa if posicion_alternativa != '' else None,
            # 'categoria': categoria,
            # 'division': division if division != '' else None,
            # 'seleccion': seleccion if seleccion != '' else None,
            # 'altura': altura,
            # 'peso': peso,
            # 'pierna_habil': pierna_habil if pierna_habil != '' else None,
            # 'vencimiento_contrato': vencimiento_contrato,
            # 'sueldo': sueldo,
            # 'valor_transfermarket': valor_transfermarket,
            # 'foto_jugador': foto_jugador,
            # 'foto_carrera_club': foto_carrera_club,
            # 'foto_carrera_seleccion': foto_carrera_seleccion,
            # 'aspectos_tecnicos_tacticos': aspectos_tecnicos_tacticos,
            # 'aspectos_fisicos': aspectos_fisicos,
            # 'personalidad': personalidad,
            # 'otras_observaciones': otras_observaciones,
            # 'representante_uid': representante_uid
            # } 
            
st.markdown('Actualizacion de datos')

# Obtener datos para listas desplegables
df_representantes = get_all_representantes()
df_clubs = get_all_clubs()
df_videos = get_all_videos()
df_entrenadores = get_all_entrenadores()
df_jugadores = get_all_jugadores()
df_tiene_video = get_all_tiene_video()
df_club_jugador = get_all_club_jugador()
df_club_entrenador = get_all_club_entrenador()


# Mostrar datos de ejemplo
st.write('Representantes:', df_representantes)
st.write('Clubs:', df_clubs)
st.write('Videos:', df_videos)
st.write('Entrenadores:', df_entrenadores)
st.write('Jugadores:', df_jugadores)
st.write('Tiene Video:', df_tiene_video)
st.write('Club_entrenador:', df_club_entrenador)
st.write('Club_jugador:', df_club_jugador)