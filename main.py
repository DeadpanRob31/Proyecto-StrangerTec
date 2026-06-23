import machine
import time
import network
import usocket as socket
import utime
import gc
import machine
import _thread

# Liberar memoria acumulada
gc.collect()

# Registro1
AB1=machine.Pin(18,machine.Pin.OUT)
CLK1=machine.Pin(19,machine.Pin.OUT)
# Registro 2
AB2=machine.Pin(16,machine.Pin.OUT)
CLK2=machine.Pin(17,machine.Pin.OUT)
# Leds solas
FilaLeds1=machine.Pin(13,machine.Pin.OUT)
FilaLeds2=machine.Pin(14,machine.Pin.OUT)
FilaLeds3=machine.Pin(15,machine.Pin.OUT)
buzzer = machine.PWM(machine.Pin(6))

#ADICION DE LA SEGUNDA PARTE
#Interruptor ACII
pin_switch = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)

#Pines de salida
pin_A = machine.Pin(2, machine.Pin.OUT)
pin_B = machine.Pin(3, machine.Pin.OUT)
pin_C = machine.Pin(4, machine.Pin.OUT)
pin_D = machine.Pin(5, machine.Pin.OUT)

# Boton
boton = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP) 
estado_anterior = boton.value()

def limpiar_registros():
    for _ in range(8):
        AB1(0); CLK1(1); CLK1(0)
        AB2(0); CLK2(1); CLK2(0)

limpiar_registros()

S0 = [0,0,0,0,0,0,0,0]
unidad_tiempo = 0.2 
dificultad = "FACIL" 

#Wifi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm = 0xa11140)
    wlan.connect('Abi', 'gatossss')

    print("Conectando a Wi-Fi...")
    timeout = 15
    while timeout > 0 and not wlan.isconnected():
        timeout -= 1
        utime.sleep(1)
        print(".")

    if wlan.isconnected():
        print("Conexion exitosa a la IP:", wlan.ifconfig()[0])
        return True
    return False

S_AB0=[1,0,0,0,0,0,0,0]
S_CD1=[0,1,0,0,0,0,0,0]
S_EF2=[0,0,1,0,0,0,0,0]
S_GH3=[0,0,0,1,0,0,0,0]
S_IJ4=[0,0,0,0,1,0,0,0]
S_KL5=[0,0,0,0,0,1,0,0]
S_MN6=[0,0,0,0,0,0,1,0]
S_OP7=[0,0,0,0,0,0,0,1]
S_QR8=[1,0,0,0,0,0,0,0]
S_ST9=[0,1,0,0,0,0,0,0]
S_UVMenos=[0,0,1,0,0,0,0,0]
S_WXMas=[0,0,0,1,0,0,0,0]
S_YZ=[0,0,0,0,1,0,0,0]

MAPA_LETRAS = {
    'A': (S_AB0,S0,FilaLeds1),
    'B': (S_AB0,S0,FilaLeds2),
    '0': (S_AB0,S0,FilaLeds3),
    'C': (S_CD1,S0,FilaLeds1),
    'D': (S_CD1,S0,FilaLeds2),
    '1': (S_CD1,S0,FilaLeds3),
    'E': (S_EF2,S0,FilaLeds1),
    'F': (S_EF2,S0,FilaLeds2),
    '2': (S_EF2,S0,FilaLeds3),
    'G': (S_GH3,S0,FilaLeds1),
    'H': (S_GH3,S0,FilaLeds2),
    '3': (S_GH3,S0,FilaLeds3),
    'I': (S_IJ4,S0,FilaLeds1),
    'J': (S_IJ4,S0,FilaLeds2),
    '4': (S_IJ4,S0,FilaLeds3),
    'K': (S_KL5,S0,FilaLeds1),
    'L': (S_KL5,S0,FilaLeds2),
    '5': (S_KL5,S0,FilaLeds3),
    'M': (S_MN6,S0,FilaLeds1),
    'N': (S_MN6,S0,FilaLeds2),
    '6': (S_MN6,S0,FilaLeds3),
    'O': (S_OP7,S0,FilaLeds1),
    'P': (S_OP7,S0,FilaLeds2),
    '7': (S_OP7,S0,FilaLeds3),
    'Q': (S0,S_QR8,FilaLeds1),
    'R': (S0,S_QR8,FilaLeds2),
    '8': (S0,S_QR8,FilaLeds3),
    'S': (S0,S_ST9,FilaLeds1),
    'T': (S0,S_ST9,FilaLeds2),
    '9': (S0,S_ST9,FilaLeds3),
    'U': (S0,S_UVMenos,FilaLeds1),
    'V': (S0,S_UVMenos,FilaLeds2),
    '-': (S0,S_UVMenos,FilaLeds3),
    'W': (S0,S_WXMas,FilaLeds1),
    'X': (S0,S_WXMas,FilaLeds2),
    '+': (S0,S_WXMas,FilaLeds3),
    'Y': (S0,S_YZ,FilaLeds1),
    'Z': (S0,S_YZ,FilaLeds2),
}

MORSE = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----', '+': '.-.-.','-':'-....-'}

def enviar_a_registros(sec1, sec2):
    for i in range(8):
        AB1(sec1[7-i]); CLK1(1); CLK1(0)
    for i in range(8):
        AB2(sec2[7-i]); CLK2(1); CLK2(0)

def sonar_y_prender(letra, duracion):
    datos = MAPA_LETRAS.get(letra)
    if datos:
        sec1, sec2, fila_pin = datos
        if dificultad == "FACIL":
            fila_pin.on()
            enviar_a_registros(sec1, sec2)
        if dificultad == "DIFICIL":
            buzzer.freq(1000); buzzer.duty_u16(30000)
        time.sleep(duracion)
        buzzer.duty_u16(0);
        enviar_a_registros(S0, S0);
        fila_pin.off()
    elif letra == ' ':
        time.sleep(duracion)

def procesar_morse(mensaje):
    for caracter in mensaje:
        if caracter == ' ':
            time.sleep(unidad_tiempo * 7); continue
        if caracter in MORSE:
            codigo = MORSE[caracter]
            for i, pulso in enumerate(codigo):
                dur = unidad_tiempo * (1 if pulso == '.' else 3)
                sonar_y_prender(caracter, dur)
                if i < len(codigo) - 1: time.sleep(unidad_tiempo * 1)
            time.sleep(unidad_tiempo * 3)
#Segunda parte
def decimal_binario(num):
    pin_A.value((num >> 3) & 1)
    pin_B.value((num >> 2) & 1)
    pin_C.value((num >> 1) & 1)
    pin_D.value(num & 1)
    
def iniciar_servidor():
    global unidad_tiempo, dificultad
    
    if not conectar_wifi():
        print("No se pudo conectar. Reiniciando..")
        time.sleep(2)
        machine.reset()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind(('0.0.0.0', 65432))
        s.listen(1)
        print("Esperando conexión en puerto 65432...")

        while True:
            conn, addr = s.accept()
            print("Conectado con:", addr)
            conn.settimeout(0.01)
            estado_anterior = boton.value()
            estado_switch_anterior = pin_switch.value()
            
            try:
                if estado_switch_anterior == 0:
                    conn.sendall(b"SWITCH_ON\n")
                else:
                    conn.sendall(b"SWITCH_OFF\n")
            except:
                pass
            
            ultimo_numero=0

            while True:
                #Recibe info
                try:
                    data = conn.recv(1024)
                    if not data: break
                    msg = data.decode().strip().split(":")
                    if msg[0] == "CONFIG":
                        unidad_tiempo = float(msg[1])
                        dificultad = msg[2]
                        print("Nueva Config:", dificultad)
                        
                    elif msg[0] == "PLAY":
                        _thread.start_new_thread(procesar_morse, (msg[1],))
                    #Activar modo incrementador
                        
                    elif msg[0]=="ASCII":
                        ultimo_numero=int(msg[1])
                except OSError:
                    pass
                if pin_switch.value() == 0:
                    decimal_binario(ultimo_numero)
                else:
                    decimal_binario(0)
                
                #Envia el estado del switch al PC si cambio   # <-- NUEVO
                estado_switch_actual = pin_switch.value()
                if estado_switch_actual != estado_switch_anterior:
                    try:
                        if estado_switch_actual == 0:
                            conn.sendall(b"SWITCH_ON\n")
                        else:
                            conn.sendall(b"SWITCH_OFF\n")
                        estado_switch_anterior = estado_switch_actual
                    except:
                        break

                #Envia info del Boton
                print("Switch:", pin_switch.value(), "Boton:", boton.value())
                time.sleep(0.5)
                estado_actual = boton.value()
                if estado_actual != estado_anterior:
                    try:
                        if estado_actual == 0:
                            conn.sendall(b"BOTON_DOWN\n")
                        else:
                            conn.sendall(b"BOTON_UP\n")
                        estado_anterior = estado_actual
                    except:
                        break
                time.sleep(0.01)
            
            conn.close()
            print("PC desconectada.")

    except Exception as e:
        print("Error en servidor:", e)
    finally:
        s.close()
        print("Socket cerrado. Reiniciando...")
        time.sleep(1)
        machine.reset()

iniciar_servidor()
