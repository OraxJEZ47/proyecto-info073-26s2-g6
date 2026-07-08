# Importamos módulos requeridos
import math
import os
import random

import pygame

# Estados del juego
ESTADO_INICIO = "inicio"
ESTADO_INSTRUCCIONES = "instrucciones"
ESTADO_JUGANDO = "jugando"
ESTADO_JEFE = "jefe"
ESTADO_JEFE_EXPLOTANDO = "jefe_explotando"
ESTADO_DERROTA = "derrota"
ESTADO_VICTORIA = "victoria"

# Rutas a la carpeta de imágenes de pantallas
DIR_PANTALLAS = os.path.join(os.path.dirname(__file__), "data", "pantallas")

# Se específica el nombre del archivo para cada imagen de pantalla.
# El formato de imagen utilizado puede ser PNG, JPG/JPEG, BMP, o GIF.
PANTALLA_INICIO = "pantalla_inicio.bmp"
PANTALLA_INSTRUCCIONES = "pantalla_instrucciones.bmp"
PANTALLA_VICTORIA = "pantalla_victoria.bmp"
PANTALLA_DERROTA = "pantalla_derrota.bmp"

DIR_TEXTURAS = os.path.join(os.path.dirname(__file__), "data", "texturas")

TEXTURA_JUGADOR = "terian.png"
TEXTURA_VEHICULO = "vehiculo.png"
TEXTURA_BICICLETA = "bicicleta.png"
TEXTURA_MANZANA = "comida.png"
TEXTURA_JEFE = "gordo.png"
TEXTURA_PROYECTIL = "proyectil.png"
TEXTURA_FONDO = "fondo.png"

# Para evitar que el jugador se mueva demasiado rápido
RETRASO = 350

# Códigos de cada elemento del tablero
VACIO = 0
VEHICULO = 1
JUGADOR = 2
MANZANA = 3
BICICLETA = 4
JEFE = 5
PROYECTIL = 6

# Tamaño del tablero
# Si se cambian estas constantes, se debe modificar la definición
# del tablero que se encuentra en función reiniciar().
FILAS = 15
COLUMNAS = 15

MANZANAS_PARA_GANAR = 5
ALTURA_BARRA = 50

VELOCIDAD_VEHICULO_MIN = 900
VELOCIDAD_VEHICULO_MAX = 900

VELOCIDAD_BICICLETA_MIN = 1200
VELOCIDAD_BICICLETA_MAX = 1200

TIPOS_POR_FILA = {
    0: BICICLETA,
    1: BICICLETA,
    2: VEHICULO,
    3: VEHICULO,
    4: VEHICULO,
    5: VEHICULO,
    6: BICICLETA,
    7: BICICLETA,
    8: BICICLETA,
    9: VEHICULO,
    10: VEHICULO,
    11: VEHICULO,
    12: BICICLETA,
    13: BICICLETA,
    14: BICICLETA,
}

TIEMPO_SOBREVIVIR_JEFE = 30000

VELOCIDAD_JEFE = 1500

DURACION_SHAKE = 400

DURACION_SHAKE_JEFE = 5000
DURACION_FRAGMENTOS_JEFE = 500

VELOCIDAD_PROYECTIL_INICIAL = 1000
VELOCIDAD_PROYECTIL_FINAL = 100

DURACION_FASE_INICIAL_PROYECTIL = 1000


def aparecer_aleatorio(tablero, id_elem):
    """
    Coloca un elemento en una casilla vacía aleatoria del tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - id_elem: El número identificador del elemento que queremos colocar.

    Retorna:
        - (columna, fila): Tupla que indica posición en la que se colocó el elemento.
    """

    # Debemos detectar los espacios vacíos, para ello recorremos
    # el tablero y almacenamos tuplas de (columna, fila) las posiciones
    # en las que un elemento "VACIO" (el número 0 en este caso) se encuentre.
    vacios = []

    # Forma vista en clases de recorrer el arreglo multidimensional.
    # Tanto fila como columna son números.
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            # Obtenemos el elemento que se encuentra en esa fila y columna.
            elem_pos = tablero[fila][columna]

            if elem_pos == VACIO:
                # Al utilizar los paréntesis () dentro de la función, lo estaremos
                # añadiendo como una tupla con la estructura (columna, fila).
                vacios.append((columna, fila))

    # Si no hay casillas vacías, retornamos un valor especial.
    if len(vacios) == 0:
        return -1, -1

    # Usando la función random.choice(lista) podremos obtener una tupla
    # aleatoria desde el arreglo "vacios" que definimos anteriormente.
    columna, fila = random.choice(vacios)

    # Finalmente, colocamos el elemento al poner su número en la casilla
    # del tablero correspondiente.
    tablero[fila][columna] = id_elem

    return columna, fila

def aparecer_jefe(tablero):
    return aparecer_aleatorio(tablero, JEFE)


def encontrar_elemento(tablero, id_elem):
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            if tablero[fila][columna] == id_elem:
                return columna, fila

    return -1, -1


def colocar_manzanas_iniciales(tablero):
    manzanas = []

    cantidad = random.randint(2, 5)

    for i in range(cantidad):
        columna, fila = aparecer_aleatorio(tablero, MANZANA)
        if columna != -1:
            manzanas.append((columna, fila))

    return manzanas


def crear_vehiculos():
    vehiculos = []

    for fila in range(0, FILAS):
        tipo = TIPOS_POR_FILA.get(fila)

        if tipo is None:
            continue

        if tipo == VEHICULO:
            velocidad = random.randint(VELOCIDAD_VEHICULO_MIN, VELOCIDAD_VEHICULO_MAX)
        else:
            velocidad = random.randint(VELOCIDAD_BICICLETA_MIN, VELOCIDAD_BICICLETA_MAX)

        vehiculo = {
            "fila": fila,
            "col": random.randint(0, COLUMNAS - 1),
            "velocidad": velocidad,
            "ultimo_mov": 0,
            "tipo": tipo
        }
        vehiculos.append(vehiculo)

    return vehiculos


def mover_vehiculos(tablero, vehiculos, manzanas, tiempo_actual):
    for v in vehiculos:
        if tablero[v["fila"]][v["col"]] == VEHICULO or tablero[v["fila"]][v["col"]] == BICICLETA:
            tablero[v["fila"]][v["col"]] = VACIO

    for i in range(len(manzanas)):
        columna_manzana = manzanas[i][0]
        fila_manzana = manzanas[i][1]
        if tablero[fila_manzana][columna_manzana] == VACIO:
            tablero[fila_manzana][columna_manzana] = MANZANA

    for v in vehiculos:
        if not v.get("destruyendo", False) and tiempo_actual - v["ultimo_mov"] >= v["velocidad"]:
            tablero[v["fila"]][v["col"]] = VACIO

            if v["col"] + 1 >= COLUMNAS:
                v["col"] = 0
            else:
                v["col"] = v["col"] + 1

            v["ultimo_mov"] = tiempo_actual

        tablero[v["fila"]][v["col"]] = v["tipo"]


def verificar_colision_vehiculos(pos_jugador, vehiculos):
    col_jugador, fila_jugador = pos_jugador

    for v in vehiculos:
        if v["fila"] == fila_jugador and v["col"] == col_jugador:
            return True

    return False


def mover_jefe(jefe, pos_jugador, tiempo_actual):
    if tiempo_actual - jefe["ultimo_mov"] >= VELOCIDAD_JEFE:
        col_jugador, fila_jugador = pos_jugador

        if jefe["col"] < col_jugador:
            jefe["col"] += 1
        elif jefe["col"] > col_jugador:
            jefe["col"] -= 1

        if jefe["fila"] < fila_jugador:
            jefe["fila"] += 1
        elif jefe["fila"] > fila_jugador:
            jefe["fila"] -= 1

        jefe["ultimo_mov"] = tiempo_actual


def verificar_colision_jefe(pos_jugador, jefe):
    col_jugador, fila_jugador = pos_jugador
    return jefe["fila"] == fila_jugador and jefe["col"] == col_jugador


def verificar_colisiones_vehiculos_jefe(vehiculos, jefe, tiempo_actual):
    for v in vehiculos:
        if not v.get("destruyendo", False):
            if v["fila"] == jefe["fila"] and v["col"] == jefe["col"]:
                v["destruyendo"] = True
                v["tiempo_inicio_destruccion"] = tiempo_actual


def procesar_destruccion_vehiculos(tablero, vehiculos, proyectiles, tiempo_actual, pos_jugador):

    vehiculos_restantes = []

    for v in vehiculos:
        if v.get("destruyendo", False) and tiempo_actual - v["tiempo_inicio_destruccion"] >= DURACION_SHAKE:
            tablero[v["fila"]][v["col"]] = VACIO

            col_jugador, fila_jugador = pos_jugador
            delta_col = col_jugador - v["col"]
            delta_fila = fila_jugador - v["fila"]

            if abs(delta_col) >= abs(delta_fila):
                dir_col = 1 if delta_col >= 0 else -1
                dir_fila = 0
            else:
                dir_col = 0
                dir_fila = 1 if delta_fila >= 0 else -1

            proyectiles.append({
                "fila": v["fila"],
                "col": v["col"],
                "dir_col": dir_col,
                "dir_fila": dir_fila,
                "tiempo_creacion": tiempo_actual,
                "ultimo_mov": tiempo_actual,
            })

            continue

        vehiculos_restantes.append(v)

    return vehiculos_restantes


def mover_proyectiles(proyectiles, tiempo_actual):

    proyectiles_restantes = []

    for p in proyectiles:
        tiempo_transcurrido = tiempo_actual - p["tiempo_creacion"]

        if tiempo_transcurrido < DURACION_FASE_INICIAL_PROYECTIL:
            velocidad = VELOCIDAD_PROYECTIL_INICIAL
        else:
            velocidad = VELOCIDAD_PROYECTIL_FINAL

        if tiempo_actual - p["ultimo_mov"] >= velocidad:
            p["col"] = p["col"] + p["dir_col"]
            p["fila"] = p["fila"] + p["dir_fila"]
            p["ultimo_mov"] = tiempo_actual

        if 0 <= p["col"] < COLUMNAS and 0 <= p["fila"] < FILAS:
            proyectiles_restantes.append(p)

    return proyectiles_restantes


def verificar_colision_proyectiles(pos_jugador, proyectiles):
    col_jugador, fila_jugador = pos_jugador

    for p in proyectiles:
        if p["fila"] == fila_jugador and p["col"] == col_jugador:
            return True

    return False


def refrescar_tablero(screen, tablero, manzanas, manzanas_comidas,
                       jefe=None, proyectiles=None, vehiculos=None, tiempo_restante_jefe=None,
                       jefe_shake=False, jefe_explotando=False, texturas=None):
    # Rellena la pantalla con el color gris, básicamente pintando
    # por encima de lo que estaba anteriormente.
    screen.fill("gray30")

    if texturas is not None and texturas.get("fondo") is not None:
        screen.blit(texturas["fondo"], (0, ALTURA_BARRA))

    alto_elem = 800 / FILAS
    ancho_elem = screen.get_width() / COLUMNAS
    # Como el jugador es un círculo, se necesita el radio.
    radio = ancho_elem / 2

    celdas_shake = set()
    if vehiculos is not None:
        for v in vehiculos:
            if v.get("destruyendo", False):
                celdas_shake.add((v["fila"], v["col"]))

    pos_y = ALTURA_BARRA

    for i in range(FILAS):
        # Posición en eje "x" en unidad de píxeles.
        pos_x = 0
        for j in range(COLUMNAS):
            offset_x = 0
            offset_y = 0
            if (i, j) in celdas_shake:
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)

            textura_vehiculo = texturas.get("vehiculo") if texturas is not None else None
            textura_bicicleta = texturas.get("bicicleta") if texturas is not None else None
            textura_jugador = texturas.get("jugador") if texturas is not None else None
            textura_manzana = texturas.get("manzana") if texturas is not None else None

            if tablero[i][j] == VEHICULO:
                if textura_vehiculo is not None:
                    screen.blit(textura_vehiculo, (pos_x + offset_x, pos_y + offset_y))
                else:
                    pygame.draw.rect(
                        screen,
                        "black",
                        pygame.Rect((pos_x + offset_x, pos_y + offset_y), (ancho_elem, alto_elem)),
                    )
            elif tablero[i][j] == BICICLETA:
                if textura_bicicleta is not None:
                    screen.blit(textura_bicicleta, (pos_x + offset_x, pos_y + offset_y))
                else:
                    margen = 4
                    punta = (pos_x + ancho_elem / 2 + offset_x, pos_y + margen + offset_y)
                    esquina_izq = (pos_x + margen + offset_x, pos_y + alto_elem - margen + offset_y)
                    esquina_der = (pos_x + ancho_elem - margen + offset_x, pos_y + alto_elem - margen + offset_y)
                    pygame.draw.polygon(screen, (30, 120, 255), [punta, esquina_izq, esquina_der])
            elif tablero[i][j] == JUGADOR:
                if textura_jugador is not None:
                    screen.blit(textura_jugador, (pos_x, pos_y))
                else:
                    pygame.draw.circle(
                        screen,
                        "green",
                        (pos_x + radio, pos_y + radio),
                        radio,
                    )
            elif tablero[i][j] == MANZANA:
                if textura_manzana is not None:
                    screen.blit(textura_manzana, (pos_x, pos_y))
                else:
                    pygame.draw.rect(
                        screen,
                        "red",
                        # Acá reducimos el tamaño del rectángulo
                        # para identificarlo más fácilmente
                        pygame.Rect(
                            (pos_x + 10, pos_y + 10),
                            (ancho_elem - 20, alto_elem - 20),
                        ),
                    )

            # Estamos recorriendo los píxeles de la pantalla, por lo que
            # debemos sumar el ancho y altura en pixeles de cada elemento que
            # ya hayamos recorrido para avanzar al siguiente.
            pos_x += ancho_elem
        pos_y += alto_elem

    if jefe is not None:
        centro_x = jefe["col"] * ancho_elem + ancho_elem / 2
        centro_y = ALTURA_BARRA + jefe["fila"] * alto_elem + alto_elem / 2
        radio_jefe = min(ancho_elem, alto_elem) / 2

        if jefe_explotando:
            for _ in range(12):
                frag_x = centro_x + random.randint(-int(radio_jefe), int(radio_jefe))
                frag_y = centro_y + random.randint(-int(radio_jefe), int(radio_jefe))
                pygame.draw.rect(screen, "red", pygame.Rect(frag_x - 5, frag_y - 5, 10, 10))
        else:
            offset_x = 0
            offset_y = 0
            if jefe_shake:
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)

            textura_jefe = texturas.get("jefe") if texturas is not None else None

            if textura_jefe is not None:
                pos_img_x = centro_x - textura_jefe.get_width() / 2 + offset_x
                pos_img_y = centro_y - textura_jefe.get_height() / 2 + offset_y
                screen.blit(textura_jefe, (pos_img_x, pos_img_y))
            else:
                puntos_hexagono = []
                for k in range(6):
                    angulo = math.radians(60 * k - 90)
                    punto_x = centro_x + offset_x + radio_jefe * math.cos(angulo)
                    punto_y = centro_y + offset_y + radio_jefe * math.sin(angulo)
                    puntos_hexagono.append((punto_x, punto_y))

                pygame.draw.polygon(screen, "yellow", puntos_hexagono)

    textura_proyectil = texturas.get("proyectil") if texturas is not None else None
    rotaciones_proyectil = texturas.get("proyectil_rotaciones") if texturas is not None else None

    if proyectiles is not None:
        for p in proyectiles:
            pos_x_proyectil = p["col"] * ancho_elem
            pos_y_proyectil = ALTURA_BARRA + p["fila"] * alto_elem

            textura_actual = None
            if rotaciones_proyectil is not None:
                textura_actual = rotaciones_proyectil.get((p["dir_col"], p["dir_fila"]))

            if textura_actual is not None:
                screen.blit(textura_actual, (pos_x_proyectil, pos_y_proyectil))
            elif textura_proyectil is not None:
                screen.blit(textura_proyectil, (pos_x_proyectil, pos_y_proyectil))
            else:
                pygame.draw.rect(
                    screen,
                    (255, 140, 0),
                    pygame.Rect(
                        (pos_x_proyectil + 8, pos_y_proyectil + 8),
                        (ancho_elem - 16, alto_elem - 16),
                    ),
                )

    pygame.draw.rect(screen, "black", pygame.Rect(0, 0, 800, ALTURA_BARRA))

    pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(20, 14, 760, 22))

    fuente = pygame.font.SysFont("monospace", 15, bold=True)

    if tiempo_restante_jefe is not None:
        fraccion_restante = tiempo_restante_jefe / TIEMPO_SOBREVIVIR_JEFE
        ancho_relleno = int(760 * fraccion_restante)
        if ancho_relleno > 0:
            pygame.draw.rect(screen, "yellow", pygame.Rect(20, 14, ancho_relleno, 22))

        segundos_restantes = math.ceil(tiempo_restante_jefe / 1000)
        texto = fuente.render("Sobrevive: " + str(segundos_restantes) + "s", True, "white")
        screen.blit(texto, (400 - texto.get_width() // 2, 17))
    else:
        ancho_relleno = int(760 * manzanas_comidas / MANZANAS_PARA_GANAR)
        if ancho_relleno > 0:
            pygame.draw.rect(screen, "red", pygame.Rect(20, 14, ancho_relleno, 22))

        texto = fuente.render("Manzanas: " + str(manzanas_comidas) + " / " + str(MANZANAS_PARA_GANAR), True, "white")
        screen.blit(texto, (400 - texto.get_width() // 2, 17))

    # Refresca el contenido que se ve en pantalla.
    pygame.display.flip()


def cambiar_direccion(keys, direccion_actual):
    """
    Cambia la dirección del jugador.

    Parámetros:
        - keys: Arreglo de teclas presionadas.
        - direccion_actual: La dirección en la que estaba avanzando justo antes de analizar
            si hubo un cambio de dirección.

    Retorna:
        - direccion_actual: La nueva dirección del jugador.
    """

    # Tecla W
    if keys[pygame.K_w]:
        return (0, -1)

    # Tecla S
    if keys[pygame.K_s]:
        return (0, 1)

    # Tecla A
    if keys[pygame.K_a]:
        return (-1, 0)

    # Tecla D
    if keys[pygame.K_d]:
        return (1, 0)

    # Si no se presiona ninguna de las teclas anteriores, la dirección
    # será la misma que la anterior.
    return direccion_actual


def avanzar(tablero, pos_jugador, direccion, manzanas, manzanas_comidas):
    dir_col, dir_fila = direccion
    ind_actual_col, ind_actual_fila = pos_jugador

    # Aplicamos la dirección a la posición del jugador.
    ind_nueva_col = ind_actual_col + dir_col
    ind_nueva_fila = ind_actual_fila + dir_fila

    # Verificamos que no haya choque con el borde del tablero.
    if not (0 <= ind_nueva_col < COLUMNAS and 0 <= ind_nueva_fila < FILAS):
        return "derrota", pos_jugador, manzanas, manzanas_comidas

    # Obtenemos el elemento que se encuentre en el tablero en la nueva posición del jugador.
    pos_elem = tablero[ind_nueva_fila][ind_nueva_col]

    if pos_elem == VEHICULO or pos_elem == BICICLETA:
        return "derrota", pos_jugador, manzanas, manzanas_comidas

    if pos_elem == MANZANA:
        manzanas_nuevas = []
        for i in range(len(manzanas)):
            columna_m = manzanas[i][0]
            fila_m = manzanas[i][1]
            if not (columna_m == ind_nueva_col and fila_m == ind_nueva_fila):
                manzanas_nuevas.append(manzanas[i])
        manzanas = manzanas_nuevas
        manzanas_comidas = manzanas_comidas + 1

        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        if manzanas_comidas < MANZANAS_PARA_GANAR:
            nueva_col, nueva_fila = aparecer_aleatorio(tablero, MANZANA)
            if nueva_col != -1:
                manzanas.append((nueva_col, nueva_fila))

        if manzanas_comidas >= MANZANAS_PARA_GANAR:
            columna, fila = aparecer_jefe(tablero)
            return "jefe", (ind_nueva_col, ind_nueva_fila), manzanas, manzanas_comidas

        return "ok", (ind_nueva_col, ind_nueva_fila), manzanas, manzanas_comidas

    # Movimiento normal, si es que no encontramos manzana ni obstáculo.
    tablero[ind_actual_fila][ind_actual_col] = VACIO
    tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

    return "ok", (ind_nueva_col, ind_nueva_fila), manzanas, manzanas_comidas


def mover_jugador_jefe(tablero, pos_jugador, direccion):
    dir_col, dir_fila = direccion
    ind_actual_col, ind_actual_fila = pos_jugador

    ind_nueva_col = ind_actual_col + dir_col
    ind_nueva_fila = ind_actual_fila + dir_fila

    if not (0 <= ind_nueva_col < COLUMNAS and 0 <= ind_nueva_fila < FILAS):
        return "derrota", pos_jugador

    tablero[ind_actual_fila][ind_actual_col] = VACIO
    tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

    return "ok", (ind_nueva_col, ind_nueva_fila)


def reiniciar():
    # Si se modifica constante FILAS o COLUMNAS al inicio, también
    # se debe modificar este arreglo de tablero con los valores correspondientes.
    tablero = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    vehiculos = crear_vehiculos()
    for v in vehiculos:
        tablero[v["fila"]][v["col"]] = v["tipo"]

    manzanas = colocar_manzanas_iniciales(tablero)

    # Colocamos al jugador en una posición aleatoria.
    pos_jugador = aparecer_aleatorio(tablero, JUGADOR)

    return tablero, pos_jugador, vehiculos, manzanas


def cargar_textura(nombre_archivo, tamano):
    ruta = os.path.join(DIR_TEXTURAS, nombre_archivo)

    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        imagen = pygame.transform.scale(imagen, tamano)
        return imagen
    except (FileNotFoundError, pygame.error) as error:
        print(f"Advertencia: No se pudo cargar la textura {ruta} ({error})")
        return None


def cargar_texturas():
    ancho_elem = 800 / COLUMNAS
    alto_elem = 800 / FILAS
    tamano_celda = (int(ancho_elem), int(alto_elem))

    textura_proyectil = cargar_textura(TEXTURA_PROYECTIL, tamano_celda)

    texturas = {
        "jugador": cargar_textura(TEXTURA_JUGADOR, tamano_celda),
        "vehiculo": cargar_textura(TEXTURA_VEHICULO, tamano_celda),
        "bicicleta": cargar_textura(TEXTURA_BICICLETA, tamano_celda),
        "manzana": cargar_textura(TEXTURA_MANZANA, tamano_celda),
        "jefe": cargar_textura(TEXTURA_JEFE, tamano_celda),
        "proyectil": textura_proyectil,
        "fondo": cargar_textura(TEXTURA_FONDO, (800, 800)),
    }

    if textura_proyectil is not None:
        texturas["proyectil_rotaciones"] = {
            (1, 0): textura_proyectil,
            (-1, 0): pygame.transform.rotate(textura_proyectil, 180),
            (0, -1): pygame.transform.rotate(textura_proyectil, 90),
            (0, 1): pygame.transform.rotate(textura_proyectil, 270),
        }
    else:
        texturas["proyectil_rotaciones"] = None

    return texturas


def mostrar_pantalla(screen, nombre_archivo):
    """
    Carga una imagen y la muestra escalada a la ventana.

    Parámetros:
        - screen: La pantalla donde colocaremos la imagen.
        - nombre_archivo: El nombre del archivo de la imagen.
    """

    ruta = os.path.join(DIR_PANTALLAS, nombre_archivo)

    try:
        imagen = pygame.image.load(ruta)
        imagen = pygame.transform.scale(imagen, screen.get_size())

        # Dibujamos la imagen en la pantalla en la coordenada (0, 0).
        screen.blit(imagen, (0, 0))

        # Refrescamos pantalla.
        pygame.display.flip()
    except FileNotFoundError:
        # Fallback de seguridad en caso de que las imágenes no existan aún
        screen.fill("black")
        pygame.display.flip()
        print(f"Advertencia: No se encontró la imagen {ruta}")


def main():
    pygame.init()

    # Establecemos la resolución de la pantalla
    screen = pygame.display.set_mode((800, 850))

    # Establecemos el título de la ventana.
    pygame.display.set_caption("Juego Básico")

    running = True

    clock = pygame.time.Clock()

    estado = ESTADO_INICIO
    tablero = []
    vehiculos = []
    manzanas = []
    manzanas_comidas = 0
    pos_jugador = (0, 0)
    direccion = (0, 0)
    tiempo_ultimo_mov = 0

    jefe = None
    proyectiles = []
    tiempo_inicio_jefe = 0
    tiempo_inicio_explosion_jefe = 0

    texturas = cargar_texturas()
    print("Texturas cargadas:", {nombre: (imagen is not None) for nombre, imagen in texturas.items() if nombre != "proyectil_rotaciones"})

    mostrar_pantalla(screen, PANTALLA_INICIO)

    # Este es el bucle principal del juego, todo lo que sucede en el juego
    # está aquí.
    while running:
        clock.tick(60)

        # Se analizan los eventos del bucle actual.
        for evento in pygame.event.get():
            # Si es que se quiere cerrar la ventana.
            if evento.type == pygame.QUIT:
                running = False

            # Si es que se presiona alguna tecla.
            if evento.type == pygame.KEYDOWN:
                if estado == ESTADO_INICIO:
                    if evento.key == pygame.K_i:
                        estado = ESTADO_INSTRUCCIONES
                        mostrar_pantalla(screen, PANTALLA_INSTRUCCIONES)
                    else:
                        tablero, pos_jugador, vehiculos, manzanas = reiniciar()
                        manzanas_comidas = 0
                        direccion = (0, 0)
                        # Obtiene tiempo en milisegundos
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        jefe = None
                        proyectiles = []
                        tiempo_inicio_explosion_jefe = 0
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, manzanas, manzanas_comidas, texturas=texturas)

                elif estado == ESTADO_INSTRUCCIONES:
                    estado = ESTADO_INICIO
                    mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado in (ESTADO_DERROTA, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        tablero, pos_jugador, vehiculos, manzanas = reiniciar()
                        manzanas_comidas = 0
                        direccion = (0, 0)
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        jefe = None
                        proyectiles = []
                        tiempo_inicio_explosion_jefe = 0
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, manzanas, manzanas_comidas, texturas=texturas)

                    if evento.key == pygame.K_ESCAPE:
                        estado = ESTADO_INICIO
                        mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado == ESTADO_JUGANDO or estado == ESTADO_JEFE:
                    direccion = cambiar_direccion(pygame.key.get_pressed(), direccion)

        if estado == ESTADO_JUGANDO:
            tiempo_actual = pygame.time.get_ticks()  # En milisegundos

            mover_vehiculos(tablero, vehiculos, manzanas, tiempo_actual)

            if verificar_colision_vehiculos(pos_jugador, vehiculos):
                estado = ESTADO_DERROTA
                mostrar_pantalla(screen, PANTALLA_DERROTA)
            else:
                # La variable RETRASO hace que si no han pasado esa cantidad de ticks,
                # entonces no se avanzará en el tablero.
                if direccion != (0, 0) and tiempo_actual - tiempo_ultimo_mov >= RETRASO:
                    resultado, pos_jugador, manzanas, manzanas_comidas = avanzar(
                        tablero, pos_jugador, direccion, manzanas, manzanas_comidas
                    )

                    if resultado == "derrota":
                        estado = ESTADO_DERROTA
                        mostrar_pantalla(screen, PANTALLA_DERROTA)
                    elif resultado == "victoria":
                        estado = ESTADO_VICTORIA
                        mostrar_pantalla(screen, PANTALLA_VICTORIA)
                    elif resultado == "jefe":
                        for columna_m, fila_m in manzanas:
                            tablero[fila_m][columna_m] = VACIO
                        manzanas = []

                        col_jefe, fila_jefe = encontrar_elemento(tablero, JEFE)
                        if col_jefe != -1:
                            tablero[fila_jefe][col_jefe] = VACIO

                        jefe = {
                            "fila": fila_jefe,
                            "col": col_jefe,
                            "ultimo_mov": tiempo_actual,
                        }
                        proyectiles = []
                        tiempo_inicio_jefe = tiempo_actual
                        tiempo_ultimo_mov = tiempo_actual
                        estado = ESTADO_JEFE
                    else:
                        tiempo_ultimo_mov = tiempo_actual

                if estado == ESTADO_JUGANDO:
                    refrescar_tablero(screen, tablero, manzanas, manzanas_comidas, texturas=texturas)

        elif estado == ESTADO_JEFE:
            tiempo_actual = pygame.time.get_ticks()  # En milisegundos

            mover_vehiculos(tablero, vehiculos, manzanas, tiempo_actual)

            verificar_colisiones_vehiculos_jefe(vehiculos, jefe, tiempo_actual)

            vehiculos = procesar_destruccion_vehiculos(tablero, vehiculos, proyectiles, tiempo_actual, pos_jugador)

            mover_jefe(jefe, pos_jugador, tiempo_actual)

            proyectiles = mover_proyectiles(proyectiles, tiempo_actual)

            if (verificar_colision_vehiculos(pos_jugador, vehiculos)
                    or verificar_colision_jefe(pos_jugador, jefe)
                    or verificar_colision_proyectiles(pos_jugador, proyectiles)):
                estado = ESTADO_DERROTA
                mostrar_pantalla(screen, PANTALLA_DERROTA)
            else:
                if direccion != (0, 0) and tiempo_actual - tiempo_ultimo_mov >= RETRASO:
                    resultado, pos_jugador = mover_jugador_jefe(tablero, pos_jugador, direccion)

                    if resultado == "derrota":
                        estado = ESTADO_DERROTA
                        mostrar_pantalla(screen, PANTALLA_DERROTA)
                    else:
                        tiempo_ultimo_mov = tiempo_actual

                        if (verificar_colision_vehiculos(pos_jugador, vehiculos)
                                or verificar_colision_jefe(pos_jugador, jefe)
                                or verificar_colision_proyectiles(pos_jugador, proyectiles)):
                            estado = ESTADO_DERROTA
                            mostrar_pantalla(screen, PANTALLA_DERROTA)

                if estado == ESTADO_JEFE:
                    tiempo_transcurrido_jefe = tiempo_actual - tiempo_inicio_jefe

                    if tiempo_transcurrido_jefe >= TIEMPO_SOBREVIVIR_JEFE:
                        estado = ESTADO_JEFE_EXPLOTANDO
                        tiempo_inicio_explosion_jefe = tiempo_actual
                    else:
                        tiempo_restante_jefe = TIEMPO_SOBREVIVIR_JEFE - tiempo_transcurrido_jefe
                        refrescar_tablero(
                            screen, tablero, manzanas, manzanas_comidas,
                            jefe=jefe, proyectiles=proyectiles, vehiculos=vehiculos,
                            tiempo_restante_jefe=tiempo_restante_jefe, texturas=texturas,
                        )

        elif estado == ESTADO_JEFE_EXPLOTANDO:
            tiempo_actual = pygame.time.get_ticks()  # En milisegundos
            tiempo_transcurrido_explosion = tiempo_actual - tiempo_inicio_explosion_jefe

            if tiempo_transcurrido_explosion < DURACION_SHAKE_JEFE:
                refrescar_tablero(
                    screen, tablero, manzanas, manzanas_comidas,
                    jefe=jefe, vehiculos=vehiculos, tiempo_restante_jefe=0,
                    jefe_shake=True, texturas=texturas,
                )
            elif tiempo_transcurrido_explosion < DURACION_SHAKE_JEFE + DURACION_FRAGMENTOS_JEFE:
                refrescar_tablero(
                    screen, tablero, manzanas, manzanas_comidas,
                    jefe=jefe, vehiculos=vehiculos, tiempo_restante_jefe=0,
                    jefe_explotando=True, texturas=texturas,
                )
            else:
                estado = ESTADO_VICTORIA
                mostrar_pantalla(screen, PANTALLA_VICTORIA)

    pygame.quit()


if __name__ == "__main__":
    main()
