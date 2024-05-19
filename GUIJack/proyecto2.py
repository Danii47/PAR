#PRÁCTICA REALIZADA POR: 
#                       SANDRA TORRALBA CABALLERO

import wx
import random

from externo import CartaBase, Mazo, Estrategia

class Carta(CartaBase):
    def __init__(self, indice):
        super().__init__(indice)
        self.indice = indice
        self.imagen = wx.Bitmap()
        self.imagen.LoadFile(f"./imgs/m{indice:02d}.png")

class Jugador: # Clase para representar a un jugador
    def __init__(self, manos = None, esCroupier = False):
        self.manos = [] if not manos else manos
        self.balance = 0
        self.esCroupier = esCroupier

    def agregarMano(self, mano): # Método para añadir una mano al jugador
        self.manos.append(mano) 
        
    def algunaManoActiva(self): # Método para comprobar si alguna mano del jugador está activa
        for mano in self.manos: 
            if mano.obtenerEstado() == "ACTIVA":
                return True  # Devuelve True si alguna mano está activa
        return False

class Mano: # Clase para representar una mano de cartas
    def __init__(self, sizer, panel, texto, apuesta = 0, cartas = None, estado = "ACTIVA"):
        self.apuesta = apuesta
        self.sizer = sizer
        self.panel = panel
        self.texto = texto
        self.cartas = [] if not cartas else cartas
        self.estado = estado
    
    def obtenerEstado(self): # Método para obtener el estado de la mano
        return self.estado
    
    def establecerEstado(self, estado): # Método para establecer el estado de la mano
        self.estado = estado
    
    def establecerApuesta(self, apuesta): # Método para establecer la apuesta de la mano
        self.apuesta = apuesta
        
    def obtenerApuesta(self): # Método para obtener la apuesta de la mano
        return self.apuesta
    
    def actualizarTexto(self, jugador): # Método para actualizar el texto de la mano
        
        if jugador.esCroupier: 
            self.texto.SetLabel(f"CROUPIER\n({self.obtenerValor()})\n{self.estado}")
        else:
            self.texto.SetLabel(f"({self.obtenerValor()})\n{self.apuesta}€\n{self.estado}")
        self.sizer.Layout() # Actualiza el texto de la mano

    def actualizarColor(self): # Método para actualizar el color de la mano
        if self.estado == "PASADA":
            self.panel.SetBackgroundColour(wx.Colour(209, 134, 32))
        elif self.estado == "CERRADA":
            self.panel.SetBackgroundColour(wx.Colour(107, 148, 174))
        self.panel.Refresh() # Actualiza el color de la mano

    def obtenerValor(self): # Método para calcular el valor de la mano, considerando el valor de los ases
        valor = 0
        numeroAses = 0
        for carta in self.cartas: 
            valor += carta.valor   # Suma el valor de cada carta a la mano
            if carta.valor == 1: 
                numeroAses += 1     
        if numeroAses > 0 and valor + 10 <= 21: 
            valor += 10
        return valor
    def recargarMano(self, jugador, seleccionarMano): # Método para recargar la mano
        self.panel.DestroyChildren() 
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL) 

        texto = "" 
        
        if jugador.esCroupier:
            texto = f"CROUPIER\n({self.obtenerValor()})\n{self.estado}"
        else:
            texto = f"({self.obtenerValor()})\n{self.apuesta}€\n{self.estado}"

        self.texto = wx.StaticText(self.panel, wx.ID_ANY, texto, style=wx.ALIGN_CENTER_HORIZONTAL)
        
        
        self.texto.SetForegroundColour(wx.Colour(255, 255, 255))
        self.texto.SetFont(wx.Font(20, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.texto.Bind(wx.EVT_LEFT_DOWN, lambda event: seleccionarMano(event, jugador, self)) # Asigna un evento al texto de la mano
        
        self.sizer.Add(self.texto, 0, wx.ALL, 10)

        for carta in self.cartas:
            bitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, carta.imagen)
            bitmap.Bind(wx.EVT_LEFT_DOWN, lambda event: seleccionarMano(event, jugador, self))
            self.sizer.Add(bitmap, 0, wx.ALL, 0)

        self.panel.SetSizer(self.sizer)
        
        
        self.actualizarTexto(jugador)
        
        self.sizer.Layout()

class MyFrame(wx.Frame): # Clase para representar la ventana principal
    def __init__(self, contenedor, id, titulo, croupier, jugador, mazo):
        
        self.mazo = mazo
        self.croupier = croupier
        self.jugador = jugador
        self.apuestaElegida = 2
        self.manoSeleccionada = None
        self.partida = 1
        self.balanceGlobal = 0
        self.balancePartida = 0
        self.cuentaAtras = 10
        self.modoJuego = "MANUAL"
        
        
        wx.Frame.__init__(self, contenedor, id, titulo) 
        self.SetSize((1456, 868))
        self.SetTitle("frame")
        
        self.contador = wx.Timer(self) # Temporizador para la cuenta atrás
        self.Bind(wx.EVT_TIMER, self.actualizarCuentaAtras, self.contador)
        
        self.contadorCroupier = wx.Timer(self) # Temporizador para el turno del croupier
        self.Bind(wx.EVT_TIMER, self.turnoCroupier, self.contadorCroupier)

        self.ventana_estado = self.CreateStatusBar(1) 
        self.ventana_estado.SetStatusWidths([-1]) 
        # statusbar fields
        ventana_estado_fields = ["Seleccione Jugada"] 
        for i in range(len(ventana_estado_fields)):
            self.ventana_estado.SetStatusText(ventana_estado_fields[i], i)

        self.zonatrabajo = wx.Panel(self, wx.ID_ANY)

        pantalla = wx.BoxSizer(wx.VERTICAL)

        divide_pantalla = wx.BoxSizer(wx.HORIZONTAL)
        pantalla.Add(divide_pantalla, 1, wx.ALL | wx.EXPAND, 3)

        comandos = wx.BoxSizer(wx.VERTICAL)
        divide_pantalla.Add(comandos, 0, wx.ALL, 0)

        sizer_M = wx.StaticBoxSizer(wx.StaticBox(self.zonatrabajo, wx.ID_ANY, "Modo de Juego"), wx.HORIZONTAL)
        comandos.Add(sizer_M, 0, wx.ALL | wx.EXPAND, 10)

        self.radio_boton_M = wx.RadioButton(self.zonatrabajo, wx.ID_ANY, "Manual")
        self.radio_boton_M.SetValue(1)
        sizer_M.Add(self.radio_boton_M, 0, wx.ALL | wx.EXPAND, 0)

        self.espacio_MJ = wx.Panel(self.zonatrabajo, wx.ID_ANY)
        self.espacio_MJ.SetMinSize((65, 30))
        sizer_M.Add(self.espacio_MJ, 1, wx.EXPAND, 0)

        self.radio_boton_A = wx.RadioButton(self.zonatrabajo, wx.ID_ANY, u"Automático")
        self.radio_boton_A.SetMinSize((100, 30))
        sizer_M.Add(self.radio_boton_A, 0, wx.ALL | wx.EXPAND, 0)

        sizer_R = wx.BoxSizer(wx.HORIZONTAL)
        comandos.Add(sizer_R, 0, wx.ALL | wx.EXPAND, 15)

        retardo = wx.StaticText(self.zonatrabajo, wx.ID_ANY, "Retardo:  ")
        retardo.SetFont(wx.Font(13, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_R.Add(retardo, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.introducir_retardo_num = wx.TextCtrl(self.zonatrabajo, wx.ID_ANY, "25", style=wx.TE_RIGHT)
        self.introducir_retardo_num.SetMinSize((60, 23))
        sizer_R.Add(self.introducir_retardo_num, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        unidades = wx.StaticText(self.zonatrabajo, wx.ID_ANY, "  ms.")
        unidades.SetFont(wx.Font(13, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_R.Add(unidades, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        sizer_A = wx.StaticBoxSizer(wx.StaticBox(self.zonatrabajo, wx.ID_ANY, u"Acción"), wx.VERTICAL)
        comandos.Add(sizer_A, 17, wx.ALL | wx.EXPAND, 10)

        self.boton_P = wx.Button(self.zonatrabajo, wx.ID_ANY, "PEDIR")
        self.boton_P.SetBackgroundColour(wx.Colour(193, 193, 190))
        self.boton_P.SetForegroundColour(wx.Colour(0, 0, 0))
        self.boton_P.SetFont(wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.boton_P.Disable()
        
        sizer_A.Add(self.boton_P, 25, wx.EXPAND, 0)

        self.boton_D = wx.Button(self.zonatrabajo, wx.ID_ANY, "DOBLAR")
        self.boton_D.SetBackgroundColour(wx.Colour(193, 193, 190))
        self.boton_D.SetForegroundColour(wx.Colour(0, 0, 0))
        self.boton_D.SetFont(wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.boton_D.Disable()
        
        sizer_A.Add(self.boton_D, 25, wx.ALL | wx.EXPAND, 2)

        self.boton_C = wx.Button(self.zonatrabajo, wx.ID_ANY, "CERRAR")
        self.boton_C.SetBackgroundColour(wx.Colour(193, 193, 190))
        self.boton_C.SetForegroundColour(wx.Colour(0, 0, 0))
        self.boton_C.SetFont(wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.boton_C.Disable()
        
        sizer_A.Add(self.boton_C, 25, wx.ALL | wx.EXPAND, 2)

        self.boton_S = wx.Button(self.zonatrabajo, wx.ID_ANY, "SEPARAR")
        self.boton_S.SetBackgroundColour(wx.Colour(193, 193, 190))
        self.boton_S.SetForegroundColour(wx.Colour(0, 0, 0))
        self.boton_S.SetFont(wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.boton_S.Disable()
        
        sizer_A.Add(self.boton_S, 25, wx.ALL | wx.EXPAND, 2)

        sizer_espacio_comandos = wx.BoxSizer(wx.HORIZONTAL)
        comandos.Add(sizer_espacio_comandos, 1, wx.ALL | wx.EXPAND, 10)

        self.espacio_comandos = wx.Panel(self.zonatrabajo, wx.ID_ANY)
        self.espacio_comandos.SetMinSize((200, 55))
        sizer_espacio_comandos.Add(self.espacio_comandos, 1, wx.EXPAND, 0)

        sizer_P = wx.StaticBoxSizer(wx.StaticBox(self.zonatrabajo, wx.ID_ANY, "Partida"), wx.VERTICAL)
        comandos.Add(sizer_P, 1, wx.ALL | wx.EXPAND, 10)

        self.num_partidas = wx.StaticText(self.zonatrabajo, wx.ID_ANY, f"{self.partida}", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.num_partidas.SetMinSize((200, 55))
        self.num_partidas.SetFont(wx.Font(30, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_P.Add(self.num_partidas, 0, wx.ALL | wx.EXPAND, 0)

        self.sizer_BG = wx.StaticBoxSizer(wx.StaticBox(self.zonatrabajo, wx.ID_ANY, "Balance Global"), wx.VERTICAL)
        comandos.Add(self.sizer_BG, 1, wx.ALL | wx.EXPAND, 10)

        self.sum_balance_global = wx.StaticText(self.zonatrabajo, wx.ID_ANY, f"+ {self.balanceGlobal} €", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.sum_balance_global.SetMinSize((200, 55))
        self.sum_balance_global.SetForegroundColour(wx.Colour(134, 179, 44))
        self.sum_balance_global.SetFont(wx.Font(30, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.sizer_BG.Add(self.sum_balance_global, 0, wx.ALL | wx.EXPAND, 0)

        self.sizer_BPA = wx.StaticBoxSizer(wx.StaticBox(self.zonatrabajo, wx.ID_ANY, "Balance Partida Actual"), wx.VERTICAL)
        comandos.Add(self.sizer_BPA, 1, wx.ALL | wx.EXPAND, 10)

        self.balance_actual = wx.StaticText(self.zonatrabajo, wx.ID_ANY, f"+ {self.balancePartida} €", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.balance_actual.SetMinSize((200, 55))
        self.balance_actual.SetForegroundColour(wx.Colour(134, 179, 44))
        self.balance_actual.SetFont(wx.Font(30, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.sizer_BPA.Add(self.balance_actual, 0, wx.ALL | wx.EXPAND, 0)

        self.sizer_CA = wx.StaticBoxSizer(wx.StaticBox(self.zonatrabajo, wx.ID_ANY, u"Cuenta Atrás"), wx.VERTICAL)
        comandos.Add(self.sizer_CA, 1, wx.ALL | wx.EXPAND, 10)

        self.num_cuenta_atras = wx.StaticText(self.zonatrabajo, wx.ID_ANY, "10", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.num_cuenta_atras.SetMinSize((200, 55))
        self.num_cuenta_atras.SetForegroundColour(wx.Colour(227, 0, 0))
        self.num_cuenta_atras.SetFont(wx.Font(35, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.sizer_CA.Add(self.num_cuenta_atras, 0, wx.ALL | wx.EXPAND, 0)

        self.tablero = wx.ScrolledWindow(self.zonatrabajo, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.tablero.SetBackgroundColour(wx.Colour(58, 78, 19))
        self.tablero.SetScrollRate(10, 10)
        divide_pantalla.Add(self.tablero, 1, wx.ALL | wx.EXPAND, 0)

        self.sizer_division_manos = wx.BoxSizer(wx.VERTICAL)


        self.tablero.SetSizer(self.sizer_division_manos)

        self.zonatrabajo.SetSizer(pantalla)

        self.Layout()
        self.Centre()

        self.Bind(wx.EVT_RADIOBUTTON, self.modo_manual, self.radio_boton_M)
        self.Bind(wx.EVT_RADIOBUTTON, self.modo_automatico, self.radio_boton_A)
        self.Bind(wx.EVT_BUTTON, self.boton_pedir, self.boton_P)
        self.Bind(wx.EVT_BUTTON, self.boton_doblar, self.boton_D)
        self.Bind(wx.EVT_BUTTON, self.boton_cerrar, self.boton_C)
        self.Bind(wx.EVT_BUTTON, self.boton_separar, self.boton_S)
        # end wxGlade

    def actualizarCuentaAtras(self, event): # Método para actualizar la cuenta atrás
        self.cuentaAtras -= 1 # Decrementa la cuenta atrás en 1
        self.num_cuenta_atras.SetLabel(str(self.cuentaAtras)) 
        
        if self.cuentaAtras == -1: # Si la cuenta atrás llega a -1
            self.jugadaAleatoria() # Realiza una jugada aleatoria

            if not self.jugador.algunaManoActiva(): # Si ninguna mano del jugador está activa
                self.contador.Stop() # Detiene el temporizador
                
        self.sizer_CA.Layout() 

    def jugadaAleatoria(self): # Método para realizar una jugada aleatoria
        opciones = ["PEDIR", "DOBLAR", "CERRAR"]
        
        manosPosibles = list(filter(lambda mano: mano.obtenerEstado() == "ACTIVA", self.jugador.manos))
        self.manoSeleccionada = manosPosibles[random.randint(0, len(manosPosibles) - 1)]

        if len(self.manoSeleccionada.cartas) == 2 and self.manoSeleccionada.cartas[0].valor == self.manoSeleccionada.cartas[1].valor: 
            opciones.append("SEPARAR")
            
        jugada = random.choice(opciones)
        
        if jugada == "PEDIR":
            self.boton_pedir(None)
        elif jugada == "DOBLAR":
            self.boton_doblar(None)
        elif jugada == "CERRAR":
            self.boton_cerrar(None)
        elif jugada == "SEPARAR":
            self.boton_separar(None)
            

    def modo_manual(self, event):  # wxGlade: MyFrame.<event_handler>
        self.modoJuego = "MANUAL"

    def modo_automatico(self, event):  # wxGlade: MyFrame.<event_handler>
        self.modoJuego = "AUTOMATICO"

    def reiniciarCA(self): # Método para reiniciar la cuenta atrás
        self.cuentaAtras = 10 
        self.num_cuenta_atras.SetLabel(str(self.cuentaAtras)) 
        self.sizer_CA.Layout()

    def boton_pedir(self, event):  # wxGlade: MyFrame.<event_handler>
        nuevaCarta = self.mazo.reparte() # Reparte una nueva carta
        
        self.manoSeleccionada.cartas.append(nuevaCarta) # Añade la carta a la mano seleccionada
        
        
        if self.manoSeleccionada.obtenerValor() > 21:
            self.manoSeleccionada.establecerEstado("PASADA") 
            self.boton_P.Disable() # Deshabilita el botón PEDIR
            self.boton_D.Disable()
            self.boton_C.Disable()
            self.boton_S.Disable()
        
        self.manoSeleccionada.sizer.Add(wx.StaticBitmap(self.manoSeleccionada.panel, wx.ID_ANY, nuevaCarta.imagen), 0, wx.ALL, 0)
        
        self.manoSeleccionada.actualizarTexto(self.jugador)
        self.manoSeleccionada.actualizarColor()
        
        if self.manoSeleccionada.obtenerValor() > 21:
            self.manoSeleccionada = None
        self.reiniciarCA()
        
        if not self.jugador.esCroupier and not self.jugador.algunaManoActiva():
            self.boton_P.Disable()
            self.boton_D.Disable()
            self.boton_C.Disable()
            self.boton_S.Disable()
            self.contador.Stop()
            self.num_cuenta_atras.SetLabel("-") # Muestra un guion en la cuenta atrás que se genera cuando no hay manos activas
            self.sizer_CA.Layout()
            self.manoSeleccionada = self.croupier.manos[0]
        
            self.manoSeleccionada.panel.SetBackgroundColour(wx.Colour(196, 201, 28))
            self.manoSeleccionada.panel.Refresh()
            self.contadorCroupier.Start(1000)

    def boton_doblar(self, event):  # wxGlade: MyFrame.<event_handler>
        nuevaCarta = self.mazo.reparte()
        
        self.manoSeleccionada.cartas.append(nuevaCarta)
        self.manoSeleccionada.establecerApuesta(self.manoSeleccionada.apuesta * 2)
        self.manoSeleccionada.establecerEstado("CERRADA")
        
        if self.manoSeleccionada.obtenerValor() > 21:
            self.manoSeleccionada.establecerEstado("PASADA")
        
        self.manoSeleccionada.sizer.Add(wx.StaticBitmap(self.manoSeleccionada.panel, wx.ID_ANY, nuevaCarta.imagen), 0, wx.ALL, 0)
        
        self.manoSeleccionada.actualizarTexto(self.jugador)
        self.manoSeleccionada.actualizarColor()
        
        self.manoSeleccionada = None
        self.boton_P.Disable()
        self.boton_D.Disable()
        self.boton_C.Disable()
        self.boton_S.Disable()
        
        self.reiniciarCA()
        
        if not self.jugador.esCroupier and not self.jugador.algunaManoActiva():
            self.contador.Stop()
            self.num_cuenta_atras.SetLabel("-")
            self.sizer_CA.Layout()
            self.manoSeleccionada = self.croupier.manos[0]
        
            self.manoSeleccionada.panel.SetBackgroundColour(wx.Colour(196, 201, 28))
            self.manoSeleccionada.panel.Refresh()
            self.contadorCroupier.Start(1000)

    def boton_cerrar(self, event):  # wxGlade: MyFrame.<event_handler>
        self.manoSeleccionada.establecerEstado("CERRADA")
        
        self.manoSeleccionada.actualizarTexto(self.jugador)
        self.manoSeleccionada.actualizarColor()
        
        self.manoSeleccionada = None
        self.boton_P.Disable()
        self.boton_D.Disable()
        self.boton_C.Disable()
        self.boton_S.Disable()
        
        self.reiniciarCA()
        if not self.jugador.esCroupier and not self.jugador.algunaManoActiva(): # Si el jugador no es el croupier y no tiene ninguna mano activa
            self.contador.Stop()
            self.num_cuenta_atras.SetLabel("-")
            self.sizer_CA.Layout()
            self.manoSeleccionada = self.croupier.manos[0]
        
            self.manoSeleccionada.panel.SetBackgroundColour(wx.Colour(196, 201, 28))
            self.manoSeleccionada.panel.Refresh()
            self.contadorCroupier.Start(1000)

    def boton_separar(self, event):  # wxGlade: MyFrame.<event_handler>
        self.agregarManoTablero(self.jugador, cartas = [self.manoSeleccionada.cartas.pop()])
        self.manoSeleccionada.recargarMano(self.jugador, self.seleccionarMano)
        self.sizer_division_manos.Layout()
        
        self.reiniciarCA()
        
        if not self.jugador.esCroupier and not self.jugador.algunaManoActiva():
            self.boton_P.Disable()
            self.boton_D.Disable()
            self.boton_C.Disable()
            self.boton_S.Disable()
            self.contador.Stop()
            self.num_cuenta_atras.SetLabel("-")
            self.sizer_CA.Layout()
            self.manoSeleccionada = self.croupier.manos[0]
        
            self.manoSeleccionada.panel.SetBackgroundColour(wx.Colour(196, 201, 28))
            self.manoSeleccionada.panel.Refresh()
            if not self.jugador.todasPasadas():
                self.contadorCroupier.Start(1000)
            else:
                self.croupier.manos[0].establecerEstado("CERRADA")
                self.croupier.manos[0].actualizarTexto(self.croupier)	
                self.croupier.manos[0].actualizarColor()
                self.mostrarResultados()
    
    def turnoCroupier(self, event): # Método para el turno del croupier
        
        if self.manoSeleccionada.obtenerValor() < 17:
            nuevaCarta = self.mazo.reparte()
            self.manoSeleccionada.cartas.append(nuevaCarta)
            self.manoSeleccionada.sizer.Add(wx.StaticBitmap(self.manoSeleccionada.panel, wx.ID_ANY, nuevaCarta.imagen), 0, wx.ALL, 0)
            self.manoSeleccionada.actualizarTexto(self.croupier)
            self.manoSeleccionada.sizer.Layout()
        else:
            self.manoSeleccionada.establecerEstado("CERRADA")
            self.manoSeleccionada.actualizarTexto(self.croupier)
            self.manoSeleccionada.actualizarColor()
        
            if self.manoSeleccionada.obtenerValor() > 21:
                self.manoSeleccionada.establecerEstado("PASADA")
                self.manoSeleccionada.actualizarTexto(self.croupier)
                self.manoSeleccionada.actualizarColor()
            
            self.contadorCroupier.Stop()
            self.manoSeleccionada = None
            self.mostrarResultados() # Muestra los resultados de la partida
        
    def mostrarResultados(self): # Método para mostrar los resultados de la partida
        for mano in self.jugador.manos:
            if mano.obtenerEstado() == "PASADA":
                if self.croupier.manos[0].obtenerEstado() != "PASADA":
                    self.balancePartida -= mano.obtenerApuesta()
                    mano.panel.SetBackgroundColour(wx.Colour(200, 0, 0))
                else:
                    mano.panel.SetBackgroundColour(wx.Colour(215, 215, 0))
            
            elif mano.obtenerEstado() == "CERRADA":
                if mano.obtenerValor() > self.croupier.manos[0].obtenerValor() or self.croupier.manos[0].obtenerEstado() == "PASADA":
                    self.balancePartida += mano.obtenerApuesta()
                    mano.panel.SetBackgroundColour(wx.Colour(0, 200, 0))
                    
                elif mano.obtenerValor() < self.croupier.manos[0].obtenerValor() and self.croupier.manos[0].obtenerEstado() != "PASADA":
                    self.balancePartida -= mano.obtenerApuesta()
                    mano.panel.SetBackgroundColour(wx.Colour(200, 0, 0))
                elif mano.obtenerValor() == self.croupier.manos[0].obtenerValor():
                    mano.panel.SetBackgroundColour(wx.Colour(215, 215, 0))    
            mano.panel.Refresh()
        
        signoBalanceActual = "" # Variable para almacenar el signo del balance de la partida
        
        if self.balancePartida >= 0:
            signoBalanceActual = "+" 
            self.balance_actual.SetForegroundColour(wx.Colour(134, 179, 44))
        else:
            self.balance_actual.SetForegroundColour(wx.Colour(200, 0, 0))
        
        self.balance_actual.SetLabel(f"{signoBalanceActual}{self.balancePartida} €")
        self.sizer_BPA.Layout()
        
        self.balanceGlobal += self.balancePartida
        signoBalanceGlobal = ""
        
        if self.balanceGlobal >= 0:
            signoBalanceGlobal = "+" 
            self.sum_balance_global.SetForegroundColour(wx.Colour(134, 179, 44))
        else:
            self.sum_balance_global.SetForegroundColour(wx.Colour(200, 0, 0))
            
        self.sum_balance_global.SetLabel(f"{signoBalanceGlobal}{self.balanceGlobal} €") 
        self.sizer_BG.Layout()
    
    def agregarManoTablero(self, jugador, texto = "", cartas = None): # Método para añadir una mano al tablero

        panel_mano = wx.Panel(self.tablero, wx.ID_ANY)
        self.sizer_division_manos.Add(panel_mano, 0, wx.ALL | wx.EXPAND, 10)

        sizer_mano = wx.BoxSizer(wx.HORIZONTAL)

        texto_mano = wx.StaticText(panel_mano, wx.ID_ANY, texto, style=wx.ALIGN_CENTER_HORIZONTAL)
        texto_mano.SetForegroundColour(wx.Colour(255, 255, 255))
        texto_mano.SetFont(wx.Font(20, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        texto_mano.Bind(wx.EVT_LEFT_DOWN, lambda event: self.seleccionarMano(event, jugador, nuevaMano))
        sizer_mano.Add(texto_mano, 0, wx.ALL, 10)

        for carta in cartas:
            bitmap = wx.StaticBitmap(panel_mano, wx.ID_ANY, carta.imagen)
            bitmap.Bind(wx.EVT_LEFT_DOWN, lambda event: self.seleccionarMano(event, jugador, nuevaMano))
            sizer_mano.Add(bitmap, 0, wx.ALL, 0)

        panel_mano.SetSizer(sizer_mano) 
        
        
        if jugador == self.jugador:
            nuevaMano = Mano(sizer_mano, panel_mano, texto_mano, self.apuestaElegida, cartas)
        else:
            nuevaMano = Mano(sizer_mano, panel_mano, texto_mano, 0, cartas)
            
        panel_mano.Bind(wx.EVT_LEFT_DOWN, lambda event: self.seleccionarMano(event, jugador, nuevaMano))
        
        jugador.agregarMano(nuevaMano)
        
        jugador.manos[-1].actualizarTexto(jugador)
        
        self.tablero.Layout()
    
    def seleccionarMano(self, event, jugador, mano): # Método para seleccionar una mano
        if jugador.esCroupier:
            return

        if mano.obtenerEstado() != "ACTIVA":
            return
        
        if self.manoSeleccionada == mano:
            return
        
        mano.panel.SetBackgroundColour(wx.Colour(196, 201, 28))
        
        if self.manoSeleccionada:
            self.manoSeleccionada.panel.SetBackgroundColour(wx.NullColour)
            self.manoSeleccionada.panel.Refresh()
        
        
        
        self.boton_P.Enable()
        self.boton_D.Enable()
        self.boton_C.Enable()
        
        if len(mano.cartas) == 2 and mano.cartas[0].valor == mano.cartas[1].valor:
            self.boton_S.Enable()
        else:
            self.boton_S.Disable()
        
        mano.panel.Refresh()
        
        self.manoSeleccionada = mano

# end of class MyFrame

class PreguntaApuesta(wx.Dialog): # Clase para representar la ventana de la pregunta de la apuesta
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((200, 173))
        self.SetTitle("Nueva Partida")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 0, wx.ALL | wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Elija Apuesta"), wx.VERTICAL)
        sizer_3.Add(sizer_4, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)

        self.apuesta_2 = wx.RadioButton(self, wx.ID_ANY, u"2 €")
        self.apuesta_2.SetValue(1) # Establece el valor del botón de radio a 1(2€) por defecto
        self.apuesta_2.Bind(wx.EVT_RADIOBUTTON, self.apuestaBaja)
        
        sizer_4.Add(self.apuesta_2, 1, wx.ALL | wx.EXPAND, 0)

        self.apuesta_10 = wx.RadioButton(self, wx.ID_ANY, u"10 €")
        self.apuesta_10.Bind(wx.EVT_RADIOBUTTON, self.apuestaMedia)
        sizer_4.Add(self.apuesta_10, 1, wx.ALL | wx.EXPAND, 0)
        

        self.apuesta_50 = wx.RadioButton(self, wx.ID_ANY, u"50 €")
        self.apuesta_50.Bind(wx.EVT_RADIOBUTTON, self.apuestaAlta)
        sizer_4.Add(self.apuesta_50, 1, wx.ALL | wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, u"¿Quiere seguir jugando?")
        label_1.SetMinSize((200, 16))
        sizer_3.Add(label_1, 0, wx.ALL | wx.EXPAND, 3)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 0)

        self.button_YES = wx.Button(self, wx.ID_YES, "")
        self.button_YES.SetBackgroundColour(wx.Colour(188, 188, 188))
        self.button_YES.SetDefault()
        sizer_2.AddButton(self.button_YES)

        self.button_NO = wx.Button(self, wx.ID_NO, "")
        self.button_NO.SetBackgroundColour(wx.Colour(188, 188, 188))
        sizer_2.AddButton(self.button_NO)

        sizer_2.Realize() 

        self.SetSizer(sizer_1)

        self.SetAffirmativeId(self.button_YES.GetId())

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.boton_yes, self.button_YES)
        self.Bind(wx.EVT_BUTTON, self.boton_no, self.button_NO)
        # end wxGlade

    def apuestaBaja(self, event): # Método para establecer la apuesta baja
        self.GetParent().apuestaElegida = 2
        
    def apuestaMedia(self, event): # Método para establecer la apuesta media
        self.GetParent().apuestaElegida = 10
        
    def apuestaAlta(self, event): # Método para establecer la apuesta alta
        self.GetParent().apuestaElegida = 50

    def boton_yes(self, event):  # wxGlade: MyDialog.<event_handler>
        self.EndModal(wx.ID_YES)

    def boton_no(self, event):  # wxGlade: MyDialog.<event_handler>
        self.EndModal(wx.ID_NO)

# end of class MyDialog

class MyDialog1(wx.Dialog): # Clase para representar la ventana de la victoria(BlackJack)
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog1.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((800, 552))
        self.SetTitle("dialog")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        bj_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("./fotosPAR/BJ.png", wx.BITMAP_TYPE_ANY))
        sizer_3.Add(bj_1, 0, 0, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, u"Ha ganado 15 €")
        label_1.SetForegroundColour(wx.Colour(255, 0, 0))
        label_1.SetFont(wx.Font(17, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_3.Add(label_1, 0, wx.ALL, 10)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetBackgroundColour(wx.Colour(188, 188, 188))
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.SetAffirmativeId(self.button_OK.GetId())

        self.Layout()
        # end wxGlade

# end of class MyDialog1

class Juego(wx.App): # Clase para representar el juego
    def OnInit(self): # Método para inicializar el juego
        self.mazo = Mazo(Carta, None)
        self.jugador = Jugador()
        self.croupier = Jugador(esCroupier=True)

        self.ventana = MyFrame(None, wx.ID_ANY, "", self.croupier, self.jugador, self.mazo)
        
        self.preguntaApuesta = PreguntaApuesta(self.ventana, wx.ID_ANY, "")
        self.preguntaApuesta.Center()

        respuesta = self.preguntaApuesta.ShowModal() # Muestra la ventana de la pregunta de la apuesta

        if respuesta != wx.ID_YES:
            self.ventana.Close()
            
        else:
            self.ventana.Show()
            self.ventana.CenterOnScreen()
            self.ventana.contador.Start(1000) # Inicia el temporizador de la cuenta atrás


        self.ventana.agregarManoTablero(self.croupier, cartas = [self.mazo.reparte()])
        
        self.ventana.agregarManoTablero(self.jugador, cartas = [self.mazo.reparte(), self.mazo.reparte(), self.mazo.reparte()])
        self.ventana.agregarManoTablero(self.jugador, cartas = [self.mazo.reparte(), self.mazo.reparte()])


        return True

    

# end of class Juego

if __name__ == "__main__": 
    mijuego = Juego(0) 
    mijuego.MainLoop() 
