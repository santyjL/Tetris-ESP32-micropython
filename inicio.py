from time import sleep

def animacion_inicio(oled):
    oled.fill(0)
    y_linea = 0
    x_linea = 0
    
    # --- Mostrar “TETRIS” ---
    oled.fill(0)
    oled.text("TETRIS", 12, 50, 1)
    oled.show()
    sleep(2)

    # --- cambio de pantallla---
    oled.fill(0)
    for i in range(64):  # caen piezas rápidas
        oled.fill_rect(0, y_linea, 64 ,2, 1)
        y_linea += 2
        oled.show()
        sleep(0.01)
        
    y_linea = 127
    for i in range(64):  # caen piezas rápidas
        oled.fill_rect(0, y_linea, 64 ,2, 1)
        y_linea -= 2
        oled.show()
        sleep(0.01)
        
    # --- Mostrar “START” ---
    sleep(1.2)
    oled.fill(0)
    oled.text("START", 12, 50, 1)
    oled.show()
    sleep(2)

    sleep(1)
    oled.fill(0)
    oled.show()

