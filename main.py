# Importamos módulos requeridos
import os
import random

import pygame

# Estados del juego
ESTADO_INICIO = "inicio"
ESTADO_INSTRUCCIONES = "instrucciones"
ESTADO_JUGANDO = "jugando"
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

# Para evitar que el jugador se mueva demasiado rápido
RETRASO = 200

# Códigos de cada elemento del tablero
VACIO = 0
VEHICULO = 1
JUGADOR = 2
MANZANA = 3
BICICLETA = 4

# Tamaño del tablero
# Si se cambian estas constantes, se debe modificar la definición
# del tablero que se encuentra en función reiniciar().
FILAS = 15
COLUMNAS = 15

# Manzanas necesarias para ganar y altura de la barra de progreso
MANZANAS_PARA_GANAR = 5
ALTURA_BARRA = 50


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


def colocar_manzanas_iniciales(tablero):
    """
    Coloca entre 2 y 5 manzanas en posiciones aleatorias del tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.

    Retorna:
        - manzanas: Lista de tuplas (columna, fila) con la posición de cada manzana.
    """
    manzanas = []

    cantidad = random.randint(2, 5)

    for i in range(cantidad):
        columna, fila = aparecer_aleatorio(tablero, MANZANA)
        if columna != -1:
            manzanas.append((columna, fila))

    return manzanas


def crear_vehiculos():
    vehiculos = []

    for fila in range(1, FILAS - 1):
        # 60% vehículos, 40% bicicletas
        numero = random.randint(1, 10)
        if numero <= 6:
            tipo = VEHICULO
        else:
            tipo = BICICLETA

        vehiculo = {
            "fila": fila,
            "col": random.randint(0, COLUMNAS - 1),
            "velocidad": random.randint(300, 900),
            "ultimo_mov": 0,
            "tipo": tipo
        }
        vehiculos.append(vehiculo)

    return vehiculos


def mover_vehiculos(tablero, vehiculos, manzanas, tiempo_actual):
    # Primero borramos todos los obstáculos del tablero
    for v in vehiculos:
        if tablero[v["fila"]][v["col"]] == VEHICULO or tablero[v["fila"]][v["col"]] == BICICLETA:
            tablero[v["fila"]][v["col"]] = VACIO

    # Restauramos las manzanas que pudieron haber sido borradas(por colisionar con un obstaculo)
    for i in range(len(manzanas)):
        columna_manzana = manzanas[i][0]
        fila_manzana = manzanas[i][1]
        if tablero[fila_manzana][columna_manzana] == VACIO:
            tablero[fila_manzana][columna_manzana] = MANZANA

    # Movemos cada obstáculo y lo colocamos en su nueva posición
    for v in vehiculos:
        if tiempo_actual - v["ultimo_mov"] >= v["velocidad"]:
            # Borramos la posición anterior
            tablero[v["fila"]][v["col"]] = VACIO

            # Avanzamos una columna, si llega al borde vuelve al inicio
            if v["col"] + 1 >= COLUMNAS:
                v["col"] = 0
            else:
                v["col"] = v["col"] + 1

            v["ultimo_mov"] = tiempo_actual

        # Siempre marcamos la posición actual del obstáculo en el tablero
        tablero[v["fila"]][v["col"]] = v["tipo"]


def verificar_colision_vehiculos(pos_jugador, vehiculos):
    col_jugador, fila_jugador = pos_jugador

    for v in vehiculos:
        if v["fila"] == fila_jugador and v["col"] == col_jugador:
            return True

    return False


def refrescar_tablero(screen, tablero, manzanas, manzanas_comidas):
    """
    Dibuja el estado actual del tablero en la pantalla.

    Parámetros:
        - screen: La pantalla sobre la cual estamos dibujando.
        - tablero: El tablero con sus posiciones actuales.
        - manzanas: Lista de posiciones de las manzanas (para la barra).
        - manzanas_comidas: Cantidad de manzanas comidas (para la barra).
    """

    # Rellena la pantalla con el color gris, básicamente pintando
    # por encima de lo que estaba anteriormente.
    screen.fill("gray30")

    # El tablero ocupa 800x800, empezando en y=50 (debajo de la barra).
    alto_elem = 800 / FILAS
    ancho_elem = screen.get_width() / COLUMNAS
    # Como el jugador es un círculo, se necesita el radio.
    radio = ancho_elem / 2

    # Posición en eje "y" en unidad de píxeles. Empieza debajo de la barra.
    pos_y = ALTURA_BARRA

    for i in range(FILAS):
        # Posición en eje "x" en unidad de píxeles.
        pos_x = 0
        for j in range(COLUMNAS):
            if tablero[i][j] == VEHICULO:
                # Dibuja un rectángulo negro para el vehículo.
                pygame.draw.rect(
                    screen,
                    "black",
                    pygame.Rect((pos_x, pos_y), (ancho_elem, alto_elem)),
                )
            elif tablero[i][j] == BICICLETA:
                # Dibuja un triángulo azul para la bicicleta.
                margen = 4
                punta = (pos_x + ancho_elem / 2, pos_y + margen)
                esquina_izq = (pos_x + margen, pos_y + alto_elem - margen)
                esquina_der = (pos_x + ancho_elem - margen, pos_y + alto_elem - margen)
                pygame.draw.polygon(screen, (30, 120, 255), [punta, esquina_izq, esquina_der])
            elif tablero[i][j] == JUGADOR:
                # Dibujamos un círculo verde para el jugador.
                pygame.draw.circle(
                    screen,
                    "green",
                    (pos_x + radio, pos_y + radio),
                    radio,
                )
            elif tablero[i][j] == MANZANA:
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

    # Dibujamos la barra de progreso en la franja superior
    pygame.draw.rect(screen, "black", pygame.Rect(0, 0, 800, ALTURA_BARRA))

    # Fondo gris de la barra (vacía)
    pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(20, 14, 760, 22))

    # Relleno de la barra
    ancho_relleno = int(760 * manzanas_comidas / MANZANAS_PARA_GANAR)
    if ancho_relleno > 0:
        pygame.draw.rect(screen, "red", pygame.Rect(20, 14, ancho_relleno, 22))

    # Texto del contador
    fuente = pygame.font.SysFont("monospace", 15, bold=True)
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
    """
    Avanza el jugador un paso en la dirección dada.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - pos_jugador: Tupla con la posición actual (columna, fila) del jugador.
        - direccion: Tupla con la dirección en la que está avanzando actualmente el jugador.
        - manzanas: Lista de posiciones (columna, fila) de las manzanas.
        - manzanas_comidas: Cantidad de manzanas comidas hasta ahora.

    Retorna:
        - (resultado, nueva_pos_jugador, manzanas, manzanas_comidas)
    """

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
        # Sacamos la manzana comida de la lista
        manzanas_nuevas = []
        for i in range(len(manzanas)):
            columna_m = manzanas[i][0]
            fila_m = manzanas[i][1]
            if not (columna_m == ind_nueva_col and fila_m == ind_nueva_fila):
                manzanas_nuevas.append(manzanas[i])
        manzanas = manzanas_nuevas
        manzanas_comidas = manzanas_comidas + 1

        # Movemos al jugador
        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        # Spawnear una nueva manzana aleatoria
        nueva_col, nueva_fila = aparecer_aleatorio(tablero, MANZANA)
        if nueva_col != -1:
            manzanas.append((nueva_col, nueva_fila))

        if manzanas_comidas >= MANZANAS_PARA_GANAR:
            return "victoria", (ind_nueva_col, ind_nueva_fila), manzanas, manzanas_comidas

        return "ok", (ind_nueva_col, ind_nueva_fila), manzanas, manzanas_comidas

    # Movimiento normal, si es que no encontramos manzana ni obstáculo.
    tablero[ind_actual_fila][ind_actual_col] = VACIO
    tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

    return "ok", (ind_nueva_col, ind_nueva_fila), manzanas, manzanas_comidas


def reiniciar():
    """
    Crea un nuevo tablero y estado para una nueva partida.

    Retorna:
        - (tablero, pos_jugador, vehiculos, manzanas): Tablero nuevo, posición del jugador,
          lista de obstáculos y lista de manzanas.
    """

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

    # Crear vehículos/bicicletas y colocarlos en el tablero
    vehiculos = crear_vehiculos()
    for v in vehiculos:
        tablero[v["fila"]][v["col"]] = v["tipo"]

    # Colocar las manzanas iniciales
    manzanas = colocar_manzanas_iniciales(tablero)

    # Colocamos al jugador en una posición aleatoria.
    pos_jugador = aparecer_aleatorio(tablero, JUGADOR)

    return tablero, pos_jugador, vehiculos, manzanas


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

    # Clock para controlar que el bucle corra máximo 60 veces por segundo.
    clock = pygame.time.Clock()

    estado = ESTADO_INICIO
    tablero = []
    vehiculos = []
    manzanas = []
    manzanas_comidas = 0
    pos_jugador = (0, 0)
    direccion = (0, 0)
    tiempo_ultimo_mov = 0

    mostrar_pantalla(screen, PANTALLA_INICIO)

    # Este es el bucle principal del juego, todo lo que sucede en el juego
    # está aquí.
    while running:
        # Limita el bucle a 60 ciclos por segundo.
        clock.tick(60)

        # Se analizan los eventos del bucle actual.
        for evento in pygame.event.get():
            # Si es que se quiere cerrar la ventana.
            if evento.type == pygame.QUIT:
                running = False

            # Si es que se presiona alguna tecla.
            if evento.type == pygame.KEYDOWN:
                if estado == ESTADO_INICIO:
                    if evento.key == pygame.K_SPACE:
                        tablero, pos_jugador, vehiculos, manzanas = reiniciar()
                        manzanas_comidas = 0
                        direccion = (0, 0)
                        # Obtiene tiempo en milisegundos
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, manzanas, manzanas_comidas)
                    elif evento.key == pygame.K_i:
                        estado = ESTADO_INSTRUCCIONES
                        mostrar_pantalla(screen, PANTALLA_INSTRUCCIONES)

                elif estado == ESTADO_INSTRUCCIONES:
                    estado = ESTADO_INICIO
                    mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado in (ESTADO_DERROTA, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        tablero, pos_jugador, vehiculos, manzanas = reiniciar()
                        manzanas_comidas = 0
                        direccion = (0, 0)
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, manzanas, manzanas_comidas)

                    if evento.key == pygame.K_ESCAPE:
                        estado = ESTADO_INICIO
                        mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado == ESTADO_JUGANDO:
                    direccion = cambiar_direccion(pygame.key.get_pressed(), direccion)

        if estado == ESTADO_JUGANDO:
            tiempo_actual = pygame.time.get_ticks()  # En milisegundos

            mover_vehiculos(tablero, vehiculos, manzanas, tiempo_actual)

            # Verificamos si un vehículo atropelló al jugador mientras estaba quieto
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
                    else:
                        tiempo_ultimo_mov = tiempo_actual

                # Solo refrescamos el tablero si seguimos jugando
                if estado == ESTADO_JUGANDO:
                    refrescar_tablero(screen, tablero, manzanas, manzanas_comidas)

    pygame.quit()


if __name__ == "__main__":
    main()
