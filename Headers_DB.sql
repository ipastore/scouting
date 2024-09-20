-- Crear tipos de datos personalizados si no existen
-- posicion
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'posicion_t') THEN
        CREATE TYPE posicion_t AS ENUM ('Arquero','Defensor Central','Lateral Derecho', 'Lateral Izquierdo',
                                        'Contención', 'Mixto', 'Ofensivo', 'Centro Delantero', 'Extremo');
    END IF;
END $$;


-- division
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'division_t') THEN
        CREATE TYPE division_t AS ENUM ('Primera','Juveniles','Reserva');
    END IF;
END $$;


-- seleccion
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'seleccion_t') THEN
        CREATE TYPE seleccion_t AS ENUM ('Mayor', 'Sub20', 'Sub17', 'Sub15', 'No');
    END IF;
END $$;


-- pierna_habil
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pierna_habil_t') THEN
        CREATE TYPE pierna_habil_t AS ENUM ('Diestro', 'Zurdo', 'Ambidiestro');
    END IF;
END $$;

-- nacionalidad
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'nacionalidad_t') THEN
        CREATE TYPE nacionalidad_t AS ENUM ('Argentina', 'Brasil', 'Uruguay', 'Chile', 'Paraguay', 'Bolivia',
                                            'Perú', 'Colombia', 'Venezuela', 'Ecuador');
    END IF;
END $$;

-- esquema_predilecto
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'esquema_predilecto_t') THEN
        CREATE TYPE esquema_predilecto_t AS ENUM ('4-4-2', '4-3-3', '4-2-3-1', '3-5-2', '3-4-3', '5-3-2', 
                                                  '4-3-1-2', '4-2-4', '4-2-1-3 MD', '4-2-1-3 MI', 'no tiene',
                                                  '4-3-3 MD', '4-3-3 MI', '3-3-2-2', '3-4-1-2', '3-3-1-3', 
                                                  '4-2-2-2', '5-4-1');
    END IF;
END $$;


-- Representante
CREATE TABLE IF NOT EXISTS representante (
representante_uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
nombre VARCHAR(50) NOT NULL
);


-- Club
CREATE TABLE IF NOT EXISTS club (
club_uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
nombre VARCHAR(50) NOT NULL,
foto_escudo VARCHAR(100) NOT NULL,
foto_plantel VARCHAR(100)
);


-- Entrenador (edad se calcula del lado del cliente)
CREATE TABLE IF NOT EXISTS entrenador (
entrenador_uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
nombre VARCHAR(50) NOT NULL,
nacionalidad nacionalidad_t,
fecha_nacimiento DATE,
esquema_predilecto esquema_predilecto_t,
foto_entrenador VARCHAR(100),
foto_carrera_entrenador VARCHAR(100),
foto_carrera_como_jugador VARCHAR(100),
fase_ofensiva TEXT,
fase_defensiva TEXT,
transiciones TEXT,
otras_observaciones TEXT,
ultimos_partidos TEXT,
foto_ultimos_partidos1 VARCHAR(100),
foto_ultimos_partidos2 VARCHAR(100)
);


-- Tabla de jugadores (edad se calcula del lado del cliente)
CREATE TABLE IF NOT EXISTS jugador (
jugador_uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
nombre VARCHAR(50) NOT NULL,
nacionalidad nacionalidad_t,
fecha_nacimiento DATE,
posicion posicion_t NOT NULL,
posicion_alternativa posicion_t,
categoria INT,
division division_t,
seleccion seleccion_t,
altura DECIMAL(3,2),
peso INT,
pierna_habil pierna_habil_t,
vencimiento_contrato DATE,
sueldo INT,
valor_transfermarket DECIMAL(5,2),
foto_jugador VARCHAR(100),
foto_carrera_club VARCHAR(100),
foto_carrera_seleccion VARCHAR(100),
aspectos_tecnicos_tacticos TEXT,
aspectos_fisicos TEXT,
personalidad TEXT,
otras_observaciones TEXT,
representante_uid UUID,
FOREIGN KEY (representante_uid) REFERENCES representante(representante_uid) ON DELETE SET NULL,
CHECK (categoria BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE))
);


-- Arquero
CREATE TABLE IF NOT EXISTS arquero (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
atajadas INT,
pelotas_aereas INT,
de_libero INT,
penales INT,
circulacion INT,
pase_largo INT,
uno_vs_uno INT,
posicionamiento_movilidad INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    atajadas BETWEEN 0 AND 100 AND
    pelotas_aereas BETWEEN 0 AND 100 AND
    de_libero BETWEEN 0 AND 100 AND
    penales BETWEEN 0 AND 100 AND
    circulacion BETWEEN 0 AND 100 AND
    pase_largo BETWEEN 0 AND 100 AND
    uno_vs_uno BETWEEN 0 AND 100 AND
    posicionamiento_movilidad BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);


-- Defensor Central
CREATE TABLE IF NOT EXISTS defensor_central (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
anticipacion INT,
duelos_por_abajo INT,
duelos_aereos INT,
salida INT,
cierres_coberturas INT,
pase_paralelo INT,
uno_vs_uno INT,
velocidad INT,
resistencia INT,
pelota_detenida INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    anticipacion BETWEEN 0 AND 100 AND
    duelos_por_abajo BETWEEN 0 AND 100 AND
    duelos_aereos BETWEEN 0 AND 100 AND
    salida BETWEEN 0 AND 100 AND
    cierres_coberturas BETWEEN 0 AND 100 AND
    pase_paralelo BETWEEN 0 AND 100 AND
    uno_vs_uno BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    pelota_detenida BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

-- Lateral Derecho
CREATE TABLE IF NOT EXISTS lateral_derecho (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
anticipacion INT,
duelos_por_abajo INT,
duelos_aereos INT,
salida INT,
cierres_coberturas INT,
pase_paralelo INT,
uno_vs_uno_defensivo INT,
velocidad INT,
resistencia INT,
centros INT,
uno_vs_uno_ofensivo INT,
remates INT,
juego_ofensivo INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    anticipacion BETWEEN 0 AND 100 AND
    duelos_por_abajo BETWEEN 0 AND 100 AND
    duelos_aereos BETWEEN 0 AND 100 AND
    salida BETWEEN 0 AND 100 AND
    cierres_coberturas BETWEEN 0 AND 100 AND
    pase_paralelo BETWEEN 0 AND 100 AND
    uno_vs_uno_defensivo BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    centros BETWEEN 0 AND 100 AND
    uno_vs_uno_ofensivo BETWEEN 0 AND 100 AND
    remates BETWEEN 0 AND 100 AND
    juego_ofensivo BETWEEN 0 AND 100
), 
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

-- Lateral Izquierdo
CREATE TABLE IF NOT EXISTS lateral_izquierdo (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
anticipacion INT,
duelos_por_abajo INT,
duelos_aereos INT,
salida INT,
cierres_coberturas INT,
pase_paralelo INT,
uno_vs_uno_defensivo INT,
velocidad INT,
resistencia INT,
centros INT,
uno_vs_uno_ofensivo INT,
remates INT,
juego_ofensivo INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    anticipacion BETWEEN 0 AND 100 AND
    duelos_por_abajo BETWEEN 0 AND 100 AND
    duelos_aereos BETWEEN 0 AND 100 AND
    salida BETWEEN 0 AND 100 AND
    cierres_coberturas BETWEEN 0 AND 100 AND
    pase_paralelo BETWEEN 0 AND 100 AND
    uno_vs_uno_defensivo BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    centros BETWEEN 0 AND 100 AND
    uno_vs_uno_ofensivo BETWEEN 0 AND 100 AND
    remates BETWEEN 0 AND 100 AND
    juego_ofensivo BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

-- Contención:
CREATE TABLE IF NOT EXISTS contencion (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
cambio_frente INT,
pase_espacio_filtrado INT,
duelos_aereos INT,
salida_circulacion INT,
relevos_vigilancias INT,
recuperaciones INT,
duelos_por_abajo INT,
velocidad INT,
resistencia INT,
despliegue INT,
coberturas_cierres INT,
remate INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    cambio_frente BETWEEN 0 AND 100 AND
    pase_espacio_filtrado BETWEEN 0 AND 100 AND
    duelos_aereos BETWEEN 0 AND 100 AND
    salida_circulacion BETWEEN 0 AND 100 AND
    relevos_vigilancias BETWEEN 0 AND 100 AND
    recuperaciones BETWEEN 0 AND 100 AND
    duelos_por_abajo BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    despliegue BETWEEN 0 AND 100 AND
    coberturas_cierres BETWEEN 0 AND 100 AND
    remate BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

-- Mixto
CREATE TABLE IF NOT EXISTS mixto (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
cambio_frente INT,
pase_espacio_filtrado INT,
duelos_aereos INT,
salida_circulacion INT,
duelos_defensivos INT,
recuperaciones INT,
duelos_ofensivos INT,
velocidad INT,
resistencia INT,
despliegue INT,
remate INT,
regate INT,
centros INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    cambio_frente BETWEEN 0 AND 100 AND
    pase_espacio_filtrado BETWEEN 0 AND 100 AND
    duelos_aereos BETWEEN 0 AND 100 AND
    salida_circulacion BETWEEN 0 AND 100 AND
    duelos_defensivos BETWEEN 0 AND 100 AND
    recuperaciones BETWEEN 0 AND 100 AND
    duelos_ofensivos BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    despliegue BETWEEN 0 AND 100 AND
    remate BETWEEN 0 AND 100 AND
    regate BETWEEN 0 AND 100 AND
    centros BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

-- Ofensivo
CREATE TABLE IF NOT EXISTS ofensivo (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
cambio_frente INT,
pase_espacio_filtrado INT,
asociaciones INT,
regates INT,
remates INT,
retroceso_defensivo INT,
explosividad INT,
velocidad INT,
resistencia INT,
determinacion INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    cambio_frente BETWEEN 0 AND 100 AND
    pase_espacio_filtrado BETWEEN 0 AND 100 AND
    asociaciones BETWEEN 0 AND 100 AND
    regates BETWEEN 0 AND 100 AND
    remates BETWEEN 0 AND 100 AND
    retroceso_defensivo BETWEEN 0 AND 100 AND
    explosividad BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    determinacion BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

-- Extremo
CREATE TABLE IF NOT EXISTS extremo (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
asociaciones INT,
centros INT,
duelos_aereos INT,
regates INT,
remates INT,
retroceso_defensivo INT,
explosividad INT,
velocidad INT,
resistencia INT,
definicion_peligrosidad INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    asociaciones BETWEEN 0 AND 100 AND
    centros BETWEEN 0 AND 100 AND
    duelos_aereos BETWEEN 0 AND 100 AND
    regates BETWEEN 0 AND 100 AND
    remates BETWEEN 0 AND 100 AND
    retroceso_defensivo BETWEEN 0 AND 100 AND
    explosividad BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    definicion_peligrosidad BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

--Centro Delantero:
CREATE TABLE IF NOT EXISTS centro_delantero (
jugador_uid UUID NOT NULL PRIMARY KEY,
tecnica_individual INT,
juego_espaldas INT,
duelos_aereos INT,
regates INT,
remates INT,
presion INT,
movilidad_desmarques INT,
velocidad INT,
resistencia INT,
definicion_peligrosidad INT,
explosividad INT,
remate_cabeza INT,
CHECK (
    tecnica_individual BETWEEN 0 AND 100 AND
    juego_espaldas BETWEEN 0 AND 100 AND
    duelos_aereos BETWEEN 0 AND 100 AND
    regates BETWEEN 0 AND 100 AND
    remates BETWEEN 0 AND 100 AND
    presion BETWEEN 0 AND 100 AND
    movilidad_desmarques BETWEEN 0 AND 100 AND
    velocidad BETWEEN 0 AND 100 AND
    resistencia BETWEEN 0 AND 100 AND
    definicion_peligrosidad BETWEEN 0 AND 100 AND
    explosividad BETWEEN 0 AND 100 AND
    remate_cabeza BETWEEN 0 AND 100
),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE
);

-- Videos
CREATE TABLE IF NOT EXISTS videos (
video_uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
url VARCHAR(255),
titulo VARCHAR(50),
descripcion TEXT,
CHECK (url ~ '^(https?://)?([a-z0-9-]+\.)+[a-z]{2,6}(/.*)?$'),
UNIQUE (url)
);

-- tiene_video
CREATE TABLE IF NOT EXISTS tiene_video (
jugador_uid UUID,
video_uid UUID NOT NULL,
entrenador_uid UUID,
PRIMARY KEY (video_uid),
FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE,
FOREIGN KEY (video_uid) REFERENCES videos(video_uid) ON DELETE CASCADE,
FOREIGN KEY (entrenador_uid) REFERENCES entrenador(entrenador_uid) ON DELETE CASCADE,
UNIQUE (video_uid, jugador_uid),
UNIQUE (video_uid, entrenador_uid),
    CHECK (
        (jugador_uid IS NOT NULL AND entrenador_uid IS NULL) OR
        (jugador_uid IS NULL AND entrenador_uid IS NOT NULL)
    )
);

-- Table for the relationship between jugador and club
CREATE TABLE IF NOT EXISTS club_jugador (
    jugador_uid UUID NOT NULL,
    club_uid UUID,
    PRIMARY KEY (jugador_uid),
    FOREIGN KEY (jugador_uid) REFERENCES jugador(jugador_uid) ON DELETE CASCADE,
    FOREIGN KEY (club_uid) REFERENCES club(club_uid) ON DELETE SET NULL,
    UNIQUE (jugador_uid, club_uid)
);

-- Table for the relationship between entrenador and club
CREATE TABLE IF NOT EXISTS club_entrenador (
    entrenador_uid UUID NOT NULL,
    club_uid UUID,
    PRIMARY KEY (entrenador_uid),
    FOREIGN KEY (entrenador_uid) REFERENCES entrenador(entrenador_uid) ON DELETE CASCADE,
    FOREIGN KEY (club_uid) REFERENCES club(club_uid) ON DELETE SET NULL, 
    UNIQUE (club_uid)
);


-- Agregp Index con Constraints de UNIQUE con Lower
--club
CREATE UNIQUE INDEX unique_club_nombre ON club (LOWER(nombre));

--entrenador
CREATE UNIQUE INDEX unique_entrenador_nombre ON entrenador (LOWER(nombre));

--representante
CREATE UNIQUE INDEX unique_representante_nombre ON representante (LOWER(nombre));

--jugador
CREATE UNIQUE INDEX unique_jugador_nombre_representante ON jugador (LOWER(nombre),representante_uid);


-- Seteo formato de fecha en DD-MM-YYYY
SET datestyle TO iso, dmy;
