from inicio import animacion_inicio
from musica import start_music, stop_music
import uasyncio as asyncio
from machine import Pin, I2C
from sh1106 import SH1106_I2C
import time
import random

start_music()
# Configuración I2C y pantalla
i2c = I2C(0, scl=Pin(4), sda=Pin(5))
oled = SH1106_I2C(128, 64, i2c, rotate=270)
oled.fill(0)
oled.show()

#botones pines
btn_rotar = Pin(17, Pin.IN, Pin.PULL_UP)
btn_bajar = Pin(16, Pin.IN, Pin.PULL_UP)
btn_derecha = Pin(18, Pin.IN, Pin.PULL_UP)
btn_izquierda = Pin(19, Pin.IN, Pin.PULL_UP)

# Variables globales
sig_pieza = False
game_over = False
velocidad = 5
puntuacion = 0
TAM_BLOQUE = 4

# Campo de juego: 16x26 bloques aprox (64x104)
ancho_bloques = 16
alto_bloques = 26
campo = [[0 for _ in range(ancho_bloques)] for _ in range(alto_bloques)]
# ---------- DEFINICIÓN DE PIEZAS (ahora en coordenadas de tablero) ----------
# Cada bloque se define como (x, y) en celdas, no en píxeles
pieza1 = [(0, 0), (1, 0), (2, 0), (3, 0)]  # Línea
pieza2 = [(0, 0), (1, 0), (0, 1), (1, 1)]  # Cuadrado
pieza3 = [(0, 0), (1, 0), (1, 1), (1, 2)]  # L
pieza4 = [(1, 0), (0, 1), (1, 1), (2, 1)]  # T
pieza5 = [(0, 0), (1, 0), (1, 1), (2, 1)]  # Z

piezas = [pieza1, pieza2, pieza3, pieza4, pieza5]

# ---------- CLASE PIEZA ----------
class Pieza:
    def __init__(self, forma):
        self.forma = forma  # lista de coordenadas de bloques (x, y)
        self.x = 6          # posición inicial horizontal en el campo
        self.y = 0          # posición inicial vertical en el campo

    def bajar(self, dy=2):
        self.y += dy

    def mover(self, dx):
        self.x += dx
        # Evitar salir del campo
        if self.colisiona():
            self.x -= dx

    def rotar(self):
        # Centro de rotación: (0,0) relativo a la pieza
        nueva_forma = [(-by, bx) for bx, by in self.forma]  # Rotación 90° CW
        vieja_forma = self.forma
        self.forma = nueva_forma
        if self.colisiona():  # Si colisiona, cancela rotación
            self.forma = vieja_forma

    def get_posiciones(self):
        return [(self.x + bx, self.y + by) for bx, by in self.forma]

    def colisiona(self):
        for x, y in self.get_posiciones():
            if y >= alto_bloques or x < 0 or x >= ancho_bloques:
                return True
            if y >= 0 and campo[y][x]:
                return True
        return False

    def fijar(self):
        for x, y in self.get_posiciones():
            if 0 <= y < alto_bloques and 0 <= x < ancho_bloques:
                campo[y][x] = 1

    def dibujar(self):
        for x, y in self.get_posiciones():
            oled.rect(x * TAM_BLOQUE, y * TAM_BLOQUE, TAM_BLOQUE, TAM_BLOQUE, 1)


# ---------- FUNCIONES VISUALES ----------
def siguiente_pieza(forma):
    oled.rect(0, 106, 24, 22, 1)
    for bx, by in forma:
        oled.rect(4 + bx * 4, 110 + by * 4, 4, 4, 1)

def visor_puntuacion():
    global puntuacion
    # Caja de puntuación (máximo 4 dígitos)
    oled.rect(25, 106, 38, 22, 1)
    p = str(puntuacion)
    if len(p) < 4:
        p = "0" * (4 - len(p)) + p
    elif len(p) > 4:
        p = "9999"
    oled.text(p, 28, 114, 1)

# ---------- FUNCIONES DE JUEGO ----------
def limpiar_filas():
    global campo, puntuacion
    nuevas = []
    lineas = 0
    for fila in campo:
        if all(fila):
            lineas += 1
        else:
            nuevas.append(fila)
    while len(nuevas) < alto_bloques:
        nuevas.insert(0, [0] * ancho_bloques)
    campo = nuevas
    puntuacion += lineas * 100

def leer_boton(btn):
    # Lee el valor y espera a que se estabilice
    if btn.value() == 0:
        time.sleep_ms(80)  # filtro de rebote
        if btn.value() == 0:
            return True
    return False


async def game():
    global puntuacion, velocidad, game_over, sig_pieza

    actual = Pieza(random.choice(piezas))
    siguiente = random.choice(piezas)
    sig_pieza = True
    actual.y = 1
    
    animacion_inicio(oled)

    while not game_over:
        oled.fill(0)
        oled.rect(0, 0, 63, 104, 1)  # Marco del campo

        # Actualizar velocidad por puntuación
        if puntuacion >= 500:
            velocidad = 40
        elif puntuacion >= 400:
            velocidad = 30
        elif puntuacion >= 300:
            velocidad = 20
        elif puntuacion >= 200:
            velocidad = 15
        elif puntuacion >= 100:
            velocidad = 10
        else:
            velocidad = 5

        # Mostrar siguiente pieza y puntuación
        siguiente_pieza(siguiente)
        visor_puntuacion()

        # Dibujar campo
        for y in range(alto_bloques):
            for x in range(ancho_bloques):
                if campo[y][x]:
                    oled.rect(x * TAM_BLOQUE, y * TAM_BLOQUE, 4, 4, 1)

        # Movimiento automático
        actual.bajar()

        if actual.colisiona():
            actual.y -= 1  # Retroceder una fila
            actual.fijar()
            limpiar_filas()
            puntuacion += 4

            # Nueva pieza
            actual = Pieza(siguiente)
            siguiente = random.choice(piezas)

            if actual.colisiona():
                game_over = True
                break
            
        if leer_boton(btn_derecha):
            actual.mover(1)
        elif leer_boton(btn_izquierda):
            actual.mover(-1)
        elif leer_boton(btn_bajar):
            actual.bajar(2)
        elif leer_boton(btn_rotar):
            actual.rotar()


        # Dibujar la pieza actual
        actual.dibujar()
        oled.show()
        await asyncio.sleep(1 / velocidad)

    # Pantalla final
    oled.fill(0)
    oled.text("GAME", 12, 50, 1)
    oled.text("OVER", 22, 64, 1)
    oled.text(str(puntuacion),24, 30, 1)
    oled.show()


# ---------- MAIN ----------
async def main():
    await game()

asyncio.run(main())
