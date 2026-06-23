import tkinter as tk
from tkinter import messagebox
import socket
import threading
import time
import random

#====================Conexion Wifi=====================
IP_PICO = "10.53.179.250" 
PUERTO = 65432
#======================================================

#====================Colores para la interfaz==========
COLOR_BG = "#100601"
COLOR_CARD = "#1e193c"
COLOR_ACCENT = "#3a5fe5"
COLOR_PLAYER_A = "#ff1515"
COLOR_PLAYER_B = "#00b54c"
#======================================================

#====================== Diccionarios de los caracters ===========================
MORSE = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
         'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
         'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
         'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
         'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
         '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
         '9': '----.', '0': '-----','+': '.-.-.','-':'-....-'}
MORSE_INV = {v: k for k, v in MORSE.items()}
#================================================================================

class JuegoMorseFinal:
    #Contsructor
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("STRANGERTEC")
        self.ventana.geometry("600x800")
        self.ventana.configure(bg=COLOR_BG)
        #Variables inicializadas
        self.nombre_a = tk.StringVar(value="Jugador A")
        self.nombre_b = tk.StringVar(value="Jugador B")
        self.unidad = tk.DoubleVar(value=0.2)
        self.modo_juego = tk.StringVar(value="Escucha")
        self.salida = tk.StringVar(value="FACIL") 
        self.juega_en_maqueta = "B" 
        self.juega_en_pc = "A"
        self.indice_actual = 0
        self.correctas_actuales = 0
        self.puntos_a = 0
        self.puntos_b = 0
        self.frases_ingresadas = tk.StringVar(value="SOS, SI, NO, LUZ, MAR, HOLA, NOTA, SIETE, MAS+, 12")
        self.lista_frases_juego = [] 
        self.labels_letras = []
        
        self.turno_actual = "A"
        self.contador_frases = 0
        self.timer_letra = None
        self.lbl_instruccion = None
        
        self.intentos_morse_actual = ""
        self.frase_actual = ""
        self.t_inicio = None
    
        self.t_ultima_soltada = None  
        self.lista_precisiones = []   
        self.switch_activo = False 

        self.pantalla_configuracion()

    def limpiar_ventana(self):
        for w in self.ventana.winfo_children(): w.destroy()
    #Ventana Inicio/Configuracion
    def pantalla_configuracion(self):
        self.limpiar_ventana()
        tk.Label(self.ventana, text="StrangerTec", font=("Impact", 35), bg=COLOR_BG, fg=COLOR_ACCENT).pack(pady=20)
        
        card = tk.Frame(self.ventana, bg=COLOR_CARD, padx=20, pady=20)
        card.pack(padx=30, fill="x")

        tk.Label(card, text="Jugadores", bg=COLOR_CARD, fg="gray", font=("Arial", 13, "bold")).pack(anchor="w")
        tk.Entry(card, textvariable=self.nombre_a, fg=COLOR_PLAYER_A, bg=COLOR_BG, bd=0, font=("Arial", 12)).pack(fill="x", pady=5)
        tk.Entry(card, textvariable=self.nombre_b, fg=COLOR_PLAYER_B, bg=COLOR_BG, bd=0, font=("Arial", 12)).pack(fill="x", pady=5)

        tk.Label(card, text="Duracion de la unidad", bg=COLOR_CARD, fg="gray", font=("Arial", 13, "bold")).pack(anchor="w", pady=(15, 0))
        f_unid = tk.Frame(card, bg=COLOR_CARD); f_unid.pack(fill="x", pady=5)
        tk.Radiobutton(f_unid, text="Opción A (0.2s)", variable=self.unidad, value=0.2, bg=COLOR_CARD,font=("Arial", 13, "bold"), fg="white", selectcolor=COLOR_BG).pack(side="left", padx=10)
        tk.Radiobutton(f_unid, text="Opción B (0.3s)", variable=self.unidad, value=0.3, bg=COLOR_CARD,font=("Arial", 13, "bold"), fg="white", selectcolor=COLOR_BG).pack(side="left", padx=10)

        tk.Label(card, text="Modos de juego", bg=COLOR_CARD, fg="gray", font=("Arial", 13, "bold")).pack(anchor="w", pady=(15, 0))
        tk.Radiobutton(card, text="Escucha y Transmisión", variable=self.modo_juego, value="Escucha", bg=COLOR_CARD,font=("Arial", 13, "bold"), fg="white", selectcolor=COLOR_BG).pack(anchor="w")
        tk.Radiobutton(card, text="Transmisión Sencilla", variable=self.modo_juego, value="Simple", bg=COLOR_CARD,font=("Arial", 13, "bold"), fg="white", selectcolor=COLOR_BG).pack(anchor="w")
        

        tk.Label(card, text="Salida de la frase", bg=COLOR_CARD, fg="gray", font=("Arial", 13, "bold")).pack(anchor="w", pady=(15, 0))
        tk.Radiobutton(card, text="LEDS", variable=self.salida, value="FACIL", bg=COLOR_CARD,font=("Arial", 13, "bold"), fg="white", selectcolor=COLOR_BG).pack(anchor="w")
        tk.Radiobutton(card, text="SONIDO", variable=self.salida, value="DIFICIL", bg=COLOR_CARD,font=("Arial", 13, "bold"), fg="white", selectcolor=COLOR_BG).pack(anchor="w")

        tk.Label(card, text="Tus frases (Separadas por comas, min 10)", bg=COLOR_CARD, fg="gray", font=("Arial", 13, "bold")).pack(anchor="w", pady=(15, 0))
        tk.Entry(card, textvariable=self.frases_ingresadas, font=("Arial", 12), bg=COLOR_BG, fg=COLOR_ACCENT, insertbackground="white", bd=0).pack(fill="x", pady=5)

        tk.Button(self.ventana, text="Jugar", bg=COLOR_ACCENT, font=("Arial", 12, "bold"), command=self.conectar).pack(pady=30)

    def conectar(self):
        try:
            #Convierte el Entry en mayusculas
            texto_crudo = self.frases_ingresadas.get().upper()
            #Divide por ,
            self.lista_frases_juego = [p.strip() for p in texto_crudo.split(",") if p.strip()]
            #Lista minima si el entry llega vacio
            if not self.lista_frases_juego:
                self.lista_frases_juego = ["SOS","SI","NO","DOS3","MAS+"]

            #Conexion a la pico
            self.socket_pico = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_pico.connect((IP_PICO, PUERTO))

            self.pantalla_juego()    
            threading.Thread(target=self.hilo_escucha_pico, daemon=True).start()        
            self.ventana.after(500, self.iniciar_nueva_frase)
            
        except Exception as e:
            messagebox.showerror("Error", f"Pico no encontrada: {e}")

    #Ventana de juego como tal
    def pantalla_juego(self):
        self.limpiar_ventana()
        #Labels de los jugadores 
        header = tk.Frame(self.ventana, bg=COLOR_CARD, pady=10); header.pack(fill="x")
        self.lbl_pa = tk.Label(header, text="0", font=("Impact", 30), fg=COLOR_PLAYER_A, bg=COLOR_CARD); self.lbl_pa.pack(side="left", padx=30)
        self.lbl_pb = tk.Label(header, text="0", font=("Impact", 30), fg=COLOR_PLAYER_B, bg=COLOR_CARD); self.lbl_pb.pack(side="right", padx=30)

        self.lbl_turno = tk.Label(self.ventana, text="", font=("Arial", 14, "bold"), bg=COLOR_BG); self.lbl_turno.pack(pady=10)

        display = tk.Frame(self.ventana, bg=COLOR_CARD, pady=40); display.pack(padx=30, fill="x")

        self.lbl_instruccion = tk.Label(self.ventana, text="", font=("Courier", 14, "bold"), bg=COLOR_BG, fg=COLOR_ACCENT,pady=10
        )
        self.lbl_instruccion.pack()

        #Palabra actual
        self.frame_secreto = tk.Frame(display, bg=COLOR_CARD)
        self.frame_secreto.pack(pady=10)
        self.lbl_feedback = tk.Label(self.ventana, text="", font=("Courier", 20), bg=COLOR_BG, fg="white"); self.lbl_feedback.pack(pady=20)

        #Comparacion en pantalla
        self.lbl_ascii_comp = tk.Label(self.ventana, text="Esperando letra en código Morse...", font=("Arial", 11, "bold"), bg=COLOR_CARD, 
        fg="#95a5a6", bd=2, relief="groove", padx=15, pady=15)
        self.lbl_ascii_comp.pack(pady=10, fill="x", padx=30)

        #Teclado para Jugador A
        self.ventana.bind("<KeyPress-space>", self.on_press_teclado)
        self.ventana.bind("<KeyRelease-space>", self.on_release_teclado)

    #Binds del teclado a quien este en la pc
    def on_press_teclado(self, event):
        if self.modo_juego.get() != "Simple" and self.turno_actual == self.juega_en_pc:
            if self.t_inicio is None:
                self.iniciar_presion()

    def on_release_teclado(self, event):
        if self.modo_juego.get() != "Simple" and self.turno_actual == self.juega_en_pc:
            self.finalizar_presion(self.turno_actual)

    def iniciar_presion(self):
        #Revisa si la pausa es entre estimulos o letras
        if hasattr(self, 'timer_letra') and self.timer_letra:
            self.ventana.after_cancel(self.timer_letra)
            self.timer_letra = None
        #Ver si ya estaba presionado
        if self.t_inicio is None:
            #Guarda la hora
            ahora = time.time()
            #Revisa si ya se pulso antes
            if self.t_ultima_soltada is not None:
                #Calcula cuanto duro la pausa
                pausa = ahora - self.t_ultima_soltada
                #U es la unidad seleccionada en config
                u = self.unidad.get()
                
                if self.intentos_morse_actual != "":
                    #Si la pausa es entre estimulos
                    ideal = u 
                else:
                    if self.indice_actual > 0 and self.frase_actual[self.indice_actual-1] == " ":
                        #Si la pausa es entre palabras
                        ideal = u * 7
                    else:
                        #Si la pausa es entre caracteres
                        ideal = u * 3 
                
                #Calcula si esta mal el caracter
                error = abs(pausa - ideal) / ideal
                precision = max(0, 1 - error)
                self.lista_precisiones.append(precision)

            self.t_inicio = ahora


    def finalizar_presion(self, origen):
        #Cuando termina el estimulo, los convierte en . o -
        if self.t_inicio is not None:
            duracion = time.time() - self.t_inicio
            self.t_inicio = None
            self.t_ultima_soltada = time.time()
            
            u = self.unidad.get()
            simbolo = "." if duracion < u * 2 else "-"
            self.intentos_morse_actual += simbolo
            self.lbl_feedback.config(text=self.intentos_morse_actual)

            if hasattr(self, 'timer_letra') and self.timer_letra:
                self.ventana.after_cancel(self.timer_letra)
            
            #IMPORTANTEEEE
            #Aqui no segui las indicaciones, lo cambie por 5 porque la pausa entre 3 no le daba tiempo al boton fisico a responder
            self.timer_letra = self.ventana.after(int(u * 5 * 1000), self.validar_letra, origen, duracion, simbolo)
    
    def validar_letra(self, origen, duracion, simbolo):
        #Convierte los estimulos en letras, verifica si esta bien y añade puntos
        letra = MORSE_INV.get(self.intentos_morse_actual, "?")

        #Extraccion de codigo ASCII
        if self.switch_activo and letra != "?" and letra != " ":
            try:
                cod_ascii = ord(letra)
                bits_4 = cod_ascii & 0x0F
                resultado_soft = (bits_4 + 5) & 0x0F

                binario_entrada = f"{bits_4:04b}"
                binario_resultado = f"{resultado_soft:04b}"

                info_pantalla = (
                    f"Binario enviado: {binario_entrada}\n"
                    f"Resultado Esperado: {binario_resultado}"
                )
                self.lbl_ascii_comp.config(text=info_pantalla, fg="#3a5fe5")

                if hasattr(self, 'socket_pico') and self.socket_pico:
                    self.socket_pico.sendall(f"ASCII:{bits_4}\n".encode())
            except Exception as e:
                print("Error procesando código binario:", e)

        #Si no existe devuelve ?
        self.intentos_morse_actual = ""
        self.lbl_feedback.config(text="")
        
        #Comparacion de letras y su indice
        if self.indice_actual < len(self.frase_actual):
            letra_esperada = self.frase_actual[self.indice_actual]
            es_correcta = (letra == letra_esperada)
            lbl_actual = self.labels_letras[self.indice_actual]
            
            if es_correcta: #Añade 20pts
                lbl_actual.config(text=letra_esperada, fg="#00b800")
                pts_letra = 20
                self.correctas_actuales += 1
            else: #Si no, solo añade 5
                lbl_actual.config(text=letra_esperada, fg="#d50000")
                pts_letra = 5 
            #Revisa que jugador es y le suma sus puntos
            if origen == "A": self.puntos_a += pts_letra
            else: self.puntos_b += pts_letra
            #Actualiza el label
            self.lbl_pa.config(text=str(self.puntos_a))
            self.lbl_pb.config(text=str(self.puntos_b))
            
            self.indice_actual += 1

            if self.indice_actual < len(self.frase_actual): #Revisa si es un espacio 
                if self.frase_actual[self.indice_actual] == " ":
                    self.indice_actual += 1

            if self.indice_actual == len(self.frase_actual):
                self.contador_frases += 1

                #IMPORTANTEEE
                #Aqui hay un fallo de codigo, ya que ambos modos terminan cuando se completaron 4 turnos,
                #y en el segundo modo deberia terminar con 2
                if self.contador_frases >= 4:
                    self.ventana.after(1000, self.pantalla_final)
                else:
                    self.turno_actual = "B" if self.turno_actual == "A" else "A"
                    self.ventana.after(1000, self.iniciar_nueva_frase)
    


    def iniciar_nueva_frase(self):
        #Cambian de pc a maqueta y viceversa
        if self.modo_juego.get() != "Simple" and self.contador_frases > 0 and self.contador_frases % 2 == 0:
            self.juega_en_maqueta, self.juega_en_pc = self.juega_en_pc, self.juega_en_maqueta
            messagebox.showinfo("Primera ronda lista", f"Cambio de lugares\n"f"{self.nombre_a.get() if self.juega_en_pc == 'A' else self.nombre_b.get()} pasa a la PC.\n"f"{self.nombre_a.get() if self.juega_en_maqueta == 'A' else self.nombre_b.get()} pasa al BOTÓN.")

        #Limpia todo de la partida anterior
        self.indice_actual = 0
        self.correctas_actuales = 0
        self.t_ultima_soltada = None
        self.lista_precisiones = []
        self.intentos_morse_actual = ""

        
        lista_de_frases = self.frases_ingresadas.get().split(",")
        self.frase_actual = random.choice(lista_de_frases).strip().upper()

        if hasattr(self, 'socket_pico') and self.socket_pico:
            try:
                #Se envian configuraciones de la partida
                config_msg = f"CONFIG:{self.unidad.get()}:{self.salida.get()}\n"
                self.socket_pico.sendall(config_msg.encode())
                
                #Tiempo para que no se caiga
                time.sleep(0.1) 
                
                #Se envia la palabra/frase random a la raspy
                play_msg = f"PLAY:{self.frase_actual}\n"
                self.socket_pico.sendall(play_msg.encode())
                
                print(f"Enviado a Pico: {play_msg.strip()}") #Print para ver que palabra escogio
            except Exception as e:
                print(f"Error de red: {e}") #Print por si se cayo

        #Quien y donde juega
        quien_juega = self.nombre_a.get() if self.turno_actual == "A" else self.nombre_b.get()
        if self.modo_juego.get() == "Simple":
            donde_juega = "BOTÓN FÍSICO"
        else:
            donde_juega = "PC" if self.turno_actual == self.juega_en_pc else "BOTÓN FÍSICO"
        self.lbl_instruccion.config(text=f"Turno de: {quien_juega}\nJugando en: {donde_juega}")

        for widget in self.frame_secreto.winfo_children(): 
            widget.destroy()
            
        self.labels_letras = []
        for carac in self.frase_actual:
            # Si es un espacio, lo mostramos vacío; si es letra, un asterisco
            texto_inicial = "*" if carac != " " else " "
            lbl = tk.Label(self.frame_secreto, text=texto_inicial, font=("Courier", 40, "bold"), 
                           bg=COLOR_CARD, fg="gray")
            lbl.pack(side="left", padx=2)
            self.labels_letras.append(lbl)
            
        if self.frase_actual.startswith(" "):
            self.indice_actual += 1

    def actualizar_switch(self, activado):
        self.switch_activo = activado
        if activado:
            # Vuelve a mostrarse si estaba oculto
            if not self.lbl_ascii_comp.winfo_ismapped():
                self.lbl_ascii_comp.pack(pady=10, fill="x", padx=30)
            self.lbl_ascii_comp.config(
                text="Esperando letra en código Morse...",
                fg="#95a5a6"
            )
        else:
            # Oculta completamente la interfaz de comparacion
            self.lbl_ascii_comp.pack_forget()

    def actualizar_ui(self):
        nombre = self.nombre_a.get() if self.turno_actual == "A" else self.nombre_b.get()
        color = COLOR_PLAYER_A if self.turno_actual == "A" else COLOR_PLAYER_B
        self.lbl_turno.config(text=f"Turno de: {nombre}", fg=color)

    def hilo_escucha_pico(self):
        #Este es el puente entre la raspy y el server
        while True:
            try:
                raw_data = self.socket_pico.recv(1024)
                if not raw_data: #Si no recibe datos, se cayo
                    break
                data = raw_data.decode().strip()#Convierte de bytes a str y le quita espacios

                if "SWITCH_ON" in data:
                    self.ventana.after(0, self.actualizar_switch, True)
                elif "SWITCH_OFF" in data:
                    self.ventana.after(0, self.actualizar_switch, False)

                if self.modo_juego.get() == "Simple" or self.turno_actual == self.juega_en_maqueta:
                    if "BOTON_DOWN" in data:
                        #Detecta si hay un boton presionado
                        if hasattr(self, 'timer_letra') and self.timer_letra:
                            print("Siiiiii")
                            self.ventana.after_cancel(self.timer_letra)
                            self.timer_letra = None
                        self.ventana.after(0, self.iniciar_presion)
                        
                    elif "BOTON_UP" in data:
                        self.ventana.after(0, self.finalizar_presion, self.turno_actual)
            except Exception as e:
                print(f"Error en hilo de escucha: {e}")
                break
    
    def pantalla_final(self):
        self.limpiar_ventana()
        
        #Anuncia ganador
        if self.puntos_a > self.puntos_b:
            ganador = f"El ganador es {self.nombre_a.get()}!"
            color_ganador = COLOR_PLAYER_A
        elif self.puntos_b > self.puntos_a:
            ganador = f"El ganador es {self.nombre_b.get()}!"
            color_ganador = COLOR_PLAYER_B
        else:
            ganador = "Hubo un empate!"
            color_ganador = "white"

        tk.Label(self.ventana, text="Resultados!", font=("Impact", 40), bg=COLOR_BG, fg=COLOR_ACCENT).pack(pady=30)
        
        res_frame = tk.Frame(self.ventana, bg=COLOR_CARD, padx=40, pady=20)
        res_frame.pack(pady=10)

        tk.Label(res_frame, text=f"{self.nombre_a.get()}: {self.puntos_a} pts", font=("Arial", 20), bg=COLOR_CARD, fg=COLOR_PLAYER_A).pack()
        tk.Label(res_frame, text=f"{self.nombre_b.get()}: {self.puntos_b} pts", font=("Arial", 20), bg=COLOR_CARD, fg=COLOR_PLAYER_B).pack(pady=10)
        
        tk.Label(self.ventana, text=ganador, font=("Arial", 25, "bold"), bg=COLOR_BG, fg=color_ganador).pack(pady=40)

        # Botones de salida
        btn_frame = tk.Frame(self.ventana, bg=COLOR_BG)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Jugar otra vez", font=("Arial", 14, "bold"), bg=COLOR_ACCENT, 
                  command=self.reiniciar_todo, width=15).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Salir", font=("Arial", 14, "bold"), bg="#444", fg="white", 
                  command=self.ventana.destroy, width=15).pack(side="left", padx=10)
    #Ventana del comprobador de codigos del juego
    

    def reiniciar_todo(self):

        #Limpia variables
        self.puntos_a = 0
        self.puntos_b = 0
        self.contador_frases = 0
        self.turno_actual = "A"
        self.juega_en_maqueta = "B"
        self.juega_en_pc = "A"
        #Vuelve a inicio
        self.pantalla_configuracion()

    def finalizar(self):
        messagebox.showinfo("Final", f"{self.nombre_a.get()}: {self.puntos_a}\n{self.nombre_b.get()}: {self.puntos_b}")
        self.ventana.destroy()

if __name__ == "__main__":
    ventana = tk.Tk()
    app = JuegoMorseFinal(ventana)
    ventana.mainloop()
