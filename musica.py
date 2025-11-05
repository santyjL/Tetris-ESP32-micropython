from machine import Pin, PWM
from time import sleep_ms
import _thread

# --- Frecuencias de las notas ---
NOTES = {
    "B0": 31, "C1": 33, "CS1": 35, "D1": 37, "DS1": 39, "E1": 41, "F1": 44, "FS1": 46,
    "G1": 49, "GS1": 52, "A1": 55, "AS1": 58, "B1": 62, "C2": 65, "CS2": 69, "D2": 73,
    "DS2": 78, "E2": 82, "F2": 87, "FS2": 93, "G2": 98, "GS2": 104, "A2": 110, "AS2": 117,
    "B2": 123, "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175, "FS3": 185,
    "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 247, "C4": 262, "CS4": 277, "D4": 294,
    "DS4": 311, "E4": 330, "F4": 349, "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466,
    "B4": 494, "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698, "FS5": 740,
    "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988, "C6": 1047, "CS6": 1109, "D6": 1175,
    "DS6": 1245, "E6": 1319, "F6": 1397, "FS6": 1480, "G6": 1568, "GS6": 1661, "A6": 1760,
    "AS6": 1865, "B6": 1976, "C7": 2093, "CS7": 2217, "D7": 2349, "DS7": 2489, "E7": 2637,
    "F7": 2794, "FS7": 2960, "G7": 3136, "GS7": 3322, "A7": 3520, "AS7": 3729, "B7": 3951,
    "C8": 4186, "CS8": 4435, "D8": 4699, "DS8": 4978, "REST": 0
}

# --- Configuración ---
TEMPO = 144
BUZZER_PIN = 14  # cambia según tu conexión
pwm = PWM(Pin(BUZZER_PIN))
pwm.duty(128)

# --- Melodía del tema del Tetris ---
melody = [
    ("E5", 4), ("B4", 8), ("C5", 8), ("D5", 4), ("C5", 8), ("B4", 8),
    ("A4", 4), ("A4", 8), ("C5", 8), ("E5", 4), ("D5", 8), ("C5", 8),
    ("B4", -4), ("C5", 8), ("D5", 4), ("E5", 4),
    ("C5", 4), ("A4", 4), ("A4", 4), ("REST", 4),

    ("REST", 8), ("D5", 4), ("F5", 8), ("A5", 4), ("G5", 8), ("F5", 8),
    ("E5", -4), ("C5", 8), ("E5", 4), ("D5", 8), ("C5", 8),
    ("B4", 4), ("B4", 8), ("C5", 8), ("D5", 4), ("E5", 4),
    ("C5", 4), ("A4", 4), ("A4", 4), ("REST", 4),

    ("E5", 2), ("C5", 2),
    ("D5", 2), ("B4", 2),
    ("C5", 2), ("A4", 2),
    ("B4", 1),

    ("E5", 2), ("C5", 2),
    ("D5", 2), ("B4", 2),
    ("C5", 4), ("E5", 4), ("A5", 2),
    ("GS5", 1)
]

# --- Cálculo de la duración de una nota entera ---
wholenote = int((60000 * 4) / TEMPO)

# --- Control global del hilo ---
_music_running = True

def play_note(note, duration):
    """Reproduce una sola nota"""
    freq = NOTES[note]
    if freq == 0:
        pwm.duty(0)
        sleep_ms(duration)
    else:
        pwm.freq(freq)
        pwm.duty(420)
        sleep_ms(int(duration * 0.9))
        pwm.duty(0)
        sleep_ms(int(duration * 0.1))

def play_tetris_theme_loop():
    """Reproduce el tema del Tetris en bucle infinito"""
    global _music_running
    while _music_running:
        for n, divider in melody:
            if not _music_running:
                break
            if divider > 0:
                note_duration = wholenote // divider
            else:
                note_duration = int((wholenote // abs(divider)) * 1.5)
            play_note(n, note_duration)
    pwm.deinit()

def start_music():
    """Inicia la música del Tetris en un hilo"""
    global _music_running
    _music_running = True
    _thread.start_new_thread(play_tetris_theme_loop, ())

def stop_music():
    """Detiene la música"""
    global _music_running
    _music_running = False
    pwm.duty(0)
    pwm.deinit()
