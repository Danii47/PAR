from externo import CartaBase, Mazo, Estrategia
import time
import os

class TERMINAL_COLORS:
  RED = '\033[91m'
  BLACK = '\033[2;37m'
  RESTART = '\033[0m'

class HAND_STATES:
  ABIERTA = "ABIERTA"
  CERRADA = "CERRADA"
  PASADA = "PASADA"

class GAME_MODES:
  JUEGO = "J"
  ANALISIS = "A"

CARDS_DICTIONARY = {
  1: "A",
  2: "2",
  3: "3",
  4: "4",
  5: "5",
  6: "6",
  7: "7",
  8: "8",
  9: "9",
  10: "10",
  11: "J",
  12: "Q",
  13: "K",
}

CARD_TYPE_DICTIONARY = {
  1: "♠",
  2: "♥",
  3: "♣",
  4: "♦"
}


class Card(CartaBase):
  def __init__(self, ind: int) -> None:
    self.ind = ind

  def getValue(self) -> int:
    return min(10, self.ind % 13 + 1)

  def toString(self) -> str:
    return CARDS_DICTIONARY[self.ind % 13 + 1]
  
  def getType(self) -> str:
    return CARD_TYPE_DICTIONARY[self.ind // 13 + 1]
  
  def getTypeId(self) -> int:
    return self.ind // 13 + 1


class Player():
  """
  Esta es la clase Player. Esta clase representa a un jugador en el juego.
  """

  def __init__(self, name: str | None = None, isCroupier: bool = False) -> None:
    """
    Inicializa un nuevo objeto Player.

    Args:
        name (str): El nombre del jugador.
    """

    self.name = name if name is not None else self.askName()
    self.isCroupier = isCroupier
    self.balance = 0
    self.hands = [Hand()]
    self.isBlackjack = False
  
  def askName(self) -> str:
    """
    Pregunta al usuario el nombre del jugador y devuelve el nombre ingresado.

    Retorna:
        str: El nombre del jugador.
    """

    name: str = ""
    while name == "":
      name = input("¿Cuál es tu nombre?: ")
      if name == "":
        print("Nombre no válido. Inténtalo de nuevo.\n")

    return name

  def getHandsLength(self) -> int:
    return len(self.hands)

  def getName(self) -> str:
    return self.name

  def getBalance(self) -> int:
    return self.balance

  def getIsBlackjack(self) -> bool:
    return self.isBlackjack
  
  def setIsBlackjack(self, isBlackjack: bool) -> None:
    self.isBlackjack = isBlackjack

  def addBalance(self, balance: int) -> None:
    self.balance = self.balance + balance

  def resetPlayer(self) -> None:
    self.isBlackjack = False
    self.resetHands()

  def resetHands(self) -> None:
    self.hands = [Hand()]

  def setInitialBet(self, bet: int) -> None:
    self.hands[0].setBet(bet)

  def askBet(self) -> int:
    bet: int = 0
    while bet not in [Game.LOW_BET, Game.MEDIUM_BET, Game.HIGH_BET]:

      try:
        bet = input(f"\n¿Apuesta de {self.name}? [{Game.LOW_BET}] [{Game.MEDIUM_BET}] [{Game.HIGH_BET}]: ")

        if bet == "": 
          bet = Game.MEDIUM_BET
        else:
          bet = int(bet)

        if bet not in [Game.LOW_BET, Game.MEDIUM_BET, Game.HIGH_BET]:
          print("Apuesta no válida.")
      except ValueError:
        print("Apuesta no válida.")

    return bet

  def giveHand(self, deck: Mazo) -> None:
    """
    Inicia una nueva partida para el jugador, repartiendo una o dos cartas dependiendo de si es croupier o no.
    """
    if (self.isCroupier):
      self.hands[0].giveCard(deck)
      
    else:
      self.hands[0].giveCard(deck, 2)
      # self.hands[0].cards = [Card(0), Card(9)] # ? Para iniciar con blackjack
    

  def showHands(self) -> None:

    lines: list[list[str]] = [[] for _ in range(4 if Game.CARD_STYLE == 1 else 7)]


    for i, hand in enumerate(self.hands):

      handNameLength: int = len(self.getName()) + len(hand.getId())
      handShift: int = handNameLength if handNameLength >= 8 else 8 # 8 es la longitud de "Croupier", que es el nombre más largo
      
      lines[0].append(f"{self.name}{hand.id}:".rjust(handShift + 1))
      lines[1].append(f"({hand.getValue()})".rjust(handShift + 1))

      if not self.isCroupier:
        lines[2].append(f"{hand.getBet()}€".rjust(handShift + 1))

      if self.isCroupier:
        lines[2].append(f"{hand.getState()}".rjust(handShift + 1))
        lines[3].append("".rjust(handShift + 1))
      else:
        lines[3].append(f"{hand.getState()}".rjust(handShift + 1))
      

      if Game.CARD_STYLE == 1:
        for card in hand.cards:
          cardColor: TERMINAL_COLORS = TERMINAL_COLORS.RED if card.getTypeId() in [2, 4] else TERMINAL_COLORS.BLACK
          lines[0].append(f"{cardColor if Game.COLORED_CARDS else ""}╭───╮{TERMINAL_COLORS.RESTART}")
          lines[1].append(f"{cardColor if Game.COLORED_CARDS else ""}│{cardColor}{card.toString().ljust(3)}{TERMINAL_COLORS.RESTART if not Game.COLORED_CARDS else ""}│{TERMINAL_COLORS.RESTART}")
          lines[2].append(f"{cardColor if Game.COLORED_CARDS else ""}│{cardColor}{card.getType().rjust(3)}{TERMINAL_COLORS.RESTART if not Game.COLORED_CARDS else ""}│{TERMINAL_COLORS.RESTART}")
          lines[3].append(f"{cardColor if Game.COLORED_CARDS else ""}╰───╯{TERMINAL_COLORS.RESTART}")
      
      elif Game.CARD_STYLE == 2:
        for i in range(4, 7):
          lines[i].append(" " * (handShift + 1))

        for card in hand.cards:
          cardColor: TERMINAL_COLORS = TERMINAL_COLORS.RED if card.getTypeId() in [2, 4] else TERMINAL_COLORS.BLACK
          lines[0].append(f"{cardColor if Game.COLORED_CARDS else ""}╭───────╮{TERMINAL_COLORS.RESTART}")
          lines[1].append(f"{cardColor if Game.COLORED_CARDS else ""}│{cardColor}{card.toString().ljust(7)}{TERMINAL_COLORS.RESTART if not Game.COLORED_CARDS else ""}│{TERMINAL_COLORS.RESTART}")
          lines[2].append(f"{cardColor if Game.COLORED_CARDS else ""}│{"".center(7)}│{TERMINAL_COLORS.RESTART}")
          lines[3].append(f"{cardColor if Game.COLORED_CARDS else ""}│{cardColor}{card.getType().center(7)}{TERMINAL_COLORS.RESTART if not Game.COLORED_CARDS else ""}│{TERMINAL_COLORS.RESTART}")
          lines[4].append(f"{cardColor if Game.COLORED_CARDS else ""}│{"".center(7)}│{TERMINAL_COLORS.RESTART}")
          lines[5].append(f"{cardColor if Game.COLORED_CARDS else ""}│{cardColor}{card.toString().rjust(7)}{TERMINAL_COLORS.RESTART if not Game.COLORED_CARDS else ""}│{TERMINAL_COLORS.RESTART}")
          lines[6].append(f"{cardColor if Game.COLORED_CARDS else ""}╰───────╯{TERMINAL_COLORS.RESTART}")

      if (i < len(self.hands) - 1):

        for line in lines:
          line.append("│")

    for line in lines:
      print(" ".join(line))
    print()


  def splitHand(self, handNumber: int):
    handToSplit: Hand = self.hands[handNumber]
    self.hands.append(Hand(cards = [handToSplit.cards.pop()], state = HAND_STATES.ABIERTA, bet = handToSplit.bet, id = handToSplit.getId() + "B"))
    handToSplit.setId(handToSplit.getId() + "A")


class Hand():
  """
  Representa una mano de cartas en el juego de PARJack (Blackjack).

  Atributos de instancia:
  - cards (list[Card]): Una lista de objetos Card que representan las cartas en la mano.
  - state (str): El estado actual de la mano.
  - bet (int): La cantidad de apuesta realizada en la mano.
  - id (str): El identificador único de la mano.

  Métodos:
  - __init__(self, cards: list[Card] | None = None, state: str = HAND_STATES.ABIERTA, bet: int = 0, id: str = ""): Inicializa una nueva mano con las cartas, el estado, la apuesta y el identificador únicos dados.
  - getBet() -> int: Devuelve la cantidad de apuesta realizada en la mano.
  - getState() -> str: Devuelve el estado actual de la mano.
  - getId() -> str: Devuelve el identificador único de la mano.
  - setId(id: str) -> None: Establece el identificador único de la mano.
  - setState(state: str) -> None: Establece el estado actual de la mano.
  - setBet(bet: int) -> None: Establece la cantidad de apuesta realizada en la mano.
  - giveCard(deck: Mazo, amount: int = 1) -> None: Agrega una o varias cartas a la mano desde un mazo.
  - getValue() -> int: Calcula y devuelve el valor total de la mano.
  """

  def __init__(self, cards: list[Card] | None = None, state: str = HAND_STATES.ABIERTA, bet: int = 0, id: str = ""):
    self.cards = [] if cards is None else cards
    self.state = state
    self.bet = bet
    self.id = id
  
  def getBet(self) -> int:
    """
    Devuelve la cantidad de apuesta realizada en la mano.

    Retorna:
      int: La cantidad de apuesta realizada en la mano.
    """
    return self.bet
  
  def getState(self) -> str:
    """
    Devuelve el estado actual de la mano.

    Retorna:
      str: El estado actual de la mano.
    """
    return self.state

  def getId(self) -> str:
    """
    Devuelve el identificador único de la mano.

    Retorna:
      str: El identificador único de la mano.
    """
    return self.id

  def setId(self, id: str) -> None:
    """
    Establece el identificador único de la mano.

    Args:
      id (str): El identificador único de la mano.
    """
    self.id = id

  def setState(self, state: str) -> None:
    """
    Establece el estado actual de la mano.

    Args:
      state (str): El estado actual de la mano.
    """
    self.state = state

  def setBet(self, bet: int) -> None:
    """
    Establece la cantidad de apuesta realizada en la mano.

    Args:
      bet (int): La cantidad de apuesta realizada en la mano.
    """
    self.bet = bet

  def giveCard(self, deck: Mazo, amount: int = 1) -> None:
    """
    Agrega una o varias cartas a la mano desde un mazo.

    Args:
      deck (Mazo): El mazo del cual se obtendrán las cartas.
      amount (int, optional): La cantidad de cartas a agregar. Por defecto es 1.
    """
    for _ in range(amount):
      self.cards.append(deck.reparte())

  def getValue(self) -> int:
    """
    Calcula y devuelve el valor total de la mano.

    Retorna:
      int: El valor total de la mano.
    """
    handValue: int = 0
    countOfAces: int = 0

    for card in self.cards:
      handValue += card.valor
      if card.valor == 1:
        countOfAces += 1
    
    if countOfAces > 0 and handValue + 10 <= Game.MAX_CARDS_VALUE:
      handValue += 10

    return handValue
  

class Game():
  """
  La clase Game representa un juego de PARJack (Blackjack).
  Administra los jugadores, el crupier, la baraja y el flujo del juego.

  Atributos de clase:
  - MAX_CARDS_VALUE: El valor máximo de las cartas en una mano (por defecto: 21)
  - MIN_CROUPIER_CARDS: El valor mínimo de las cartas que debe tener el crupier antes de detenerse (por defecto: 17)
  - CARD_STYLE: El estilo de las cartas (1: Cartas en 4 líneas, 2: Cartas en 7 líneas) (por defecto: 1)
  - COLORED_CARDS: Si las cartas se muestran en color (por defecto: False)
  - LOW_BET: La cantidad de apuesta baja (por defecto: 2)
  - MEDIUM_BET: La cantidad de apuesta media (por defecto: 10)
  - HIGH_BET: La cantidad de apuesta alta (por defecto: 50)
  - LOW_DELAY: El tiempo de espera bajo en segundos (por defecto: 1)
  - MEDIUM_DELAY: El tiempo de espera medio en segundos (por defecto: 2)
  - HIGH_DELAY: El tiempo de espera alto en segundos (por defecto: 3)

  Atributos de instancia:
  - players (list[Player]): Una lista de objetos Player que representan a los jugadores en el juego.
  - croupier (Player): Un objeto Player que representa al crupier.
  - deck (Mazo): Un objeto Mazo que representa la baraja de cartas.
  - gameBlackjack (bool): Si el juego tiene un blackjack.
  - gameNumber (int): El número de la partida actual.
  - gameMode (str): El modo de juego (Juego o Análisis).
  - gamesAmount (int): El número de juegos a jugar en el modo de análisis.
  
  Métodos:
  - __init__(self, players: list[Player], croupier: Player, deck: Mazo): Inicializa un nuevo juego con los jugadores, el crupier y la baraja dados.
  - askGameMode(self) -> str: Pregunta al usuario el modo de juego (Juego o Análisis) y devuelve el modo seleccionado.
  - askGamesAmount(self) -> int: Pregunta al usuario el número de juegos a jugar en el modo de análisis y devuelve la cantidad seleccionada.
  - startGame(self) -> None: Inicia el juego inicializando las manos, estableciendo las apuestas iniciales y barajando la baraja.
  - showTable(self) -> None: Muestra el estado actual de la mesa, incluyendo la mano del crupier y las manos de los jugadores.
  - showTablePlayersTurn(self, playerName: str) -> None: Muestra el estado actual de la mesa durante el turno de un jugador.
  - playersTurn(self) -> None: Administra los turnos de los jugadores, permitiéndoles tomar decisiones (pedir, doblar, cerrar, separar).
  - areAllHandsPassed(self) -> bool: Verifica si todas las manos en la mesa se han pasado (superado 21).
  - croupierTurn(self) -> None: Administra el turno del crupier, permitiéndole tomar cartas hasta alcanzar el valor mínimo.
  - warnBlackjack(self) -> None: Verifica si algún jugador tiene un blackjack y ajusta su apuesta en consecuencia.
  - showFinalTable(self) -> None: Muestra el estado final de la mesa después de que se hayan jugado todos los turnos.
  - countResult(self) -> None: Calcula y muestra los resultados del juego para cada jugador.
  - restartGame(self) -> bool: Pregunta al usuario si desea jugar otra partida y devuelve True si lo desea, False en caso contrario.
  """

  MAX_CARDS_VALUE = 21
  MIN_CROUPIER_CARDS = 17
  CARD_STYLE = 2
  COLORED_CARDS = False
  LOW_BET = 2
  MEDIUM_BET = 10
  HIGH_BET = 50
  LOW_DELAY = 1
  MEDIUM_DELAY = 2
  HIGH_DELAY = 3

  def __init__(self, players: list[Player], croupier: Player, deck: Mazo):
    """
    Inicializa un nuevo juego con los jugadores, el crupier y la baraja dados.

    Parámetros:
    - players (list[Player]): Una lista de objetos Player que representan a los jugadores en el juego.
    - croupier (Player): Un objeto Player que representa al crupier.
    - deck (Mazo): Un objeto Mazo que representa la baraja de cartas.
    """
    self.players = players
    self.croupier = croupier
    self.deck = deck
    self.gameBlackjack = False
    self.gameNumber = 1
    self.gameMode = self.askGameMode()
    self.gamesAmount = self.askGamesAmount() if self.gameMode == GAME_MODES.ANALISIS else 0

  def askGameMode(self) -> str:
    """
    Pregunta al usuario el modo de juego (Juego o Análisis) y devuelve el modo seleccionado.

    Retorna:
    - str: El modo de juego seleccionado.
    """

    gameMode: str = ""
    while gameMode not in [GAME_MODES.JUEGO, GAME_MODES.ANALISIS]:
      gameMode = input("¿Qué modo de juego quieres? [J]uego [A]nálisis: ").upper()
      if gameMode == "":
        gameMode = GAME_MODES.JUEGO

      if gameMode not in [GAME_MODES.JUEGO, GAME_MODES.ANALISIS]:
        print("Modo no válido. Inténtalo de nuevo.\n")
    return gameMode

  def askGamesAmount(self) -> int:
    """
    Pregunta al usuario el número de juegos a jugar en el modo de análisis y devuelve la cantidad seleccionada.

    Retorna:
    - int: El número de juegos seleccionado.
    """

    gamesAmount: int = 0
    while gamesAmount <= 0:
      try:
        gamesAmount = int(input("¿Cuántas partidas quieres jugar?: "))
        if gamesAmount <= 0:
          print("Número no válido. Inténtalo de nuevo.\n")
      except ValueError:
        print("Número no válido. Inténtalo de nuevo.\n")
    return gamesAmount

  def startGame(self) -> None:
    """
    Inicia el juego inicializando las manos, estableciendo las apuestas iniciales y barajando la baraja.
    """

    clearScreen()
    self.croupier.giveHand(self.deck)
    for player in self.players:
      print(f"--- INICIO DE LA PARTIDA #{self.gameNumber} --- BALANCE = {"+" if player.getBalance() > 0 else ""}{player.getBalance()} €")

      if self.gameMode == GAME_MODES.JUEGO:
        player.setInitialBet(player.askBet())
      else:
        bestBet: int = self.deck.estrategia.apuesta(apu_lo = Game.LOW_BET, apu_med = Game.MEDIUM_BET, apu_hi = Game.HIGH_BET)

        print(f"\n¿Apuesta de {player.getName()}? [{Game.LOW_BET}] [{Game.MEDIUM_BET}] [{Game.HIGH_BET}]: ", end="")
        time.sleep(Game.LOW_DELAY)
        print(bestBet)
        time.sleep(Game.LOW_DELAY)
        player.setInitialBet(bestBet)

      clearScreen()

      player.giveHand(self.deck)
      if player.hands[0].getValue() == Game.MAX_CARDS_VALUE:
        player.setIsBlackjack(True)
        self.gameBlackjack = True

    print(f"╭────────────────────────────╮\n│         BARAJEANDO         │\n╰────────────────────────────╯")
    time.sleep(Game.MEDIUM_DELAY)
    clearScreen()

    print("REPARTO INICIAL")
    self.showTable()
    time.sleep(Game.MEDIUM_DELAY)

  def showTable(self) -> None:
    """
    Muestra el estado actual de la mesa, incluyendo la mano del crupier y las manos de los jugadores.
    """

    self.croupier.showHands()
    for player in self.players:
      player.showHands()

  def showTablePlayersTurn(self, playerName: str) -> None:
    """
    Muestra el estado actual de la mesa durante el turno de un jugador.

    Parámetros:
    - playerName (str): El nombre del jugador cuyo turno se está mostrando.
    """

    clearScreen()
    print(f"TURNO DE {playerName.upper()}")
    self.showTable()

  def playersTurn(self) -> None:
    """
    Administra los turnos de los jugadores, permitiéndoles tomar decisiones (pedir, doblar, cerrar, separar).
    """

    if not self.gameBlackjack:
      for player in self.players:
        for i, hand in enumerate(player.hands):
          while hand.state == "ABIERTA":
            self.showTablePlayersTurn(playerName = player.getName())

            canSplitHand: bool = len(hand.cards) == 2 and hand.cards[0].valor == hand.cards[1].valor and player.getHandsLength() < 4
            action: str = ""

            if self.gameMode == GAME_MODES.JUEGO:
              action = input(f"{player.getName()}{hand.getId()}: ¿Qué quieres hacer? [P]edir [D]oblar [C]errar{" [S]eparar" if canSplitHand else ""}: ").upper()
            else:
              action = self.deck.estrategia.jugada(self.croupier.hands[0].cards[0], hand.cards)
              time.sleep(Game.LOW_DELAY)
              print(f"\n¿Qué quieres hacer? [P]edir [D]oblar [C]errar{" [S]eparar" if canSplitHand else ""}: ", end="")
              time.sleep(Game.LOW_DELAY)
              print(action)
              time.sleep(Game.LOW_DELAY)

            if action in ["P", ""]:
              hand.giveCard(self.deck)
              if hand.getValue() > Game.MAX_CARDS_VALUE:
                hand.setState(HAND_STATES.PASADA)
                self.showTablePlayersTurn(playerName = player.getName())

            elif action == "D":
              hand.giveCard(self.deck)
              hand.setBet(hand.bet * 2)

              if hand.getValue() > Game.MAX_CARDS_VALUE:
                hand.setState(HAND_STATES.PASADA)
              else:
                hand.setState(HAND_STATES.CERRADA)

              self.showTablePlayersTurn(playerName = player.name)

            elif action == "C":
              hand.setState(HAND_STATES.CERRADA)
              self.showTablePlayersTurn(playerName = player.name)

            elif action == "S" and canSplitHand:
              player.splitHand(i)

            else:
              print("Acción no válida. Inténtalo de nuevo.\n")

  def areAllHandsPassed(self) -> bool:
    """
    Verifica si todas las manos en la mesa se han pasado (superado 21).

    Retorna:
    - bool: True si todas las manos se han pasado, False en caso contrario.
    """

    for player in self.players:
      for hand in player.hands:
        if hand.getState() != HAND_STATES.PASADA:
          return False

    return True

  def croupierTurn(self) -> None:
    """
    Administra el turno del crupier, permitiéndole tomar cartas hasta alcanzar el valor mínimo.
    """

    if not self.gameBlackjack:
      time.sleep(Game.HIGH_DELAY)
      clearScreen()
      print("TURNO DEL CROUPIER")
      if not self.areAllHandsPassed():
        while self.croupier.hands[0].getValue() < Game.MIN_CROUPIER_CARDS:
          self.showTable()
          time.sleep(Game.MEDIUM_DELAY)
          clearScreen()
          self.croupier.hands[0].giveCard(self.deck)

          if self.croupier.hands[0].getValue() > Game.MAX_CARDS_VALUE:
            self.croupier.hands[0].setState(HAND_STATES.PASADA)
          print("TURNO DEL CROUPIER")

      if self.croupier.hands[0].getState() == HAND_STATES.ABIERTA:
        self.croupier.hands[0].setState(HAND_STATES.CERRADA)

      self.showTable()
      time.sleep(Game.HIGH_DELAY)
      clearScreen()

  def warnBlackjack(self) -> None:
    """
    Verifica si algún jugador tiene un blackjack y ajusta su apuesta en consecuencia.
    """

    for player in self.players:
      if player.getIsBlackjack():
        print(f"\n*** BLACKJACK DE {player.getName().upper()} ***")
        player.hands[0].setBet(int(player.hands[0].getBet() * (3 / 2)))
        player.hands[0].setState(HAND_STATES.CERRADA)

  def showFinalTable(self) -> None:
    """
    Muestra el estado final de la mesa después de que se hayan jugado todos los turnos.
    """
    
    clearScreen()
    print("TABLERO FINAL")
    if self.gameBlackjack:
      self.croupier.hands[0].setState(HAND_STATES.CERRADA)
      for player in self.players:
        player.hands[0].setState(HAND_STATES.CERRADA)

    self.showTable()

    if self.gameBlackjack:
      self.warnBlackjack()

    time.sleep(Game.HIGH_DELAY)
    clearScreen()

  def countResult(self) -> None:
    """
    Calcula y muestra los resultados del juego para cada jugador.
    """

    for player in self.players:
      print(f"CONTABILIZACIÓN DE RESULTADOS {player.name.upper()}")
      totalProfit: int = 0
      for hand in player.hands:

        resultOfBet: int = hand.getBet()

        if (self.croupier.hands[0].getState() != HAND_STATES.PASADA and hand.getState() == HAND_STATES.PASADA) or (self.croupier.hands[0].getState() != HAND_STATES.PASADA and self.croupier.hands[0].getValue() > hand.getValue()):
          resultOfBet = -hand.getBet()
        elif (self.croupier.hands[0].getState() == HAND_STATES.PASADA and hand.getState() == HAND_STATES.PASADA) or (self.croupier.hands[0].getValue() == hand.getValue()) or (self.gameBlackjack and not player.getIsBlackjack()):
          resultOfBet = 0

        totalProfit += resultOfBet

        print(f"* {self.croupier.getName()}: {self.croupier.hands[0].getValue()}, {player.getName()}{hand.getId()}: {hand.getValue()} -> {"+" if resultOfBet > 0 else ""}{resultOfBet}€")
      print(f"Resultado de la partida: {"+" if totalProfit > 0 else ""}{totalProfit}€ {"(BLACKJACK)" if self.gameBlackjack and player.getIsBlackjack() else ""}\n")
      player.addBalance(totalProfit)

  def restartGame(self) -> bool:
    """
    Pregunta al usuario si desea jugar otra partida y devuelve True si lo desea, False en caso contrario.
    """

    action: str = ""

    if self.gameMode == GAME_MODES.JUEGO:
      action = input(f"\n\n¿{"Quieres" if len(self.players) == 1 else "Quereis"} jugar otra partida? [S]í [N]o: ").upper()
    else:

      self.gamesAmount -= 1

      if self.gamesAmount > 0:
        action = "S" # CONTROLAR CUANTAS PARTIDAS QUIERE JUGAR EN EL MODO ANALISIS
      else:
        action = "N"

      print(f"\n\n¿{"Quieres" if len(self.players) == 1 else "Queréis"} jugar otra partida? [S]í [N]o: ", end="")
      time.sleep(Game.LOW_DELAY)
      print(action)
      time.sleep(Game.LOW_DELAY)

    if action in ["S", ""]:
      clearScreen()
      self.gameNumber += 1
      self.gameBlackjack = False
      self.croupier.resetPlayer()
      for player in self.players:
        player.resetPlayer()

    else:
      clearScreen()
      print("REGISTRO FINAL DE BALANCE\n")
      for player in self.players:
        print(f"{player.getName()} -> {"+" if player.getBalance() > 0 else ""}{player.getBalance()}€")
      print("\n¡Hasta la próxima!")

    return True if action == "S" or action == "" else False

def clearScreen() -> None:
  """
  Limpia la pantalla de la consola.
  """

  if os.name == "nt":
    # * Windows
    os.system("cls")
  else:
    # * Linux / Mac
    os.system("clear")

def main() -> None:
  """
  La función principal del juego. Inicializa el juego y administra el flujo del juego.
  """

  clearScreen()

  strategy: Estrategia = Estrategia(num_barajas = Mazo.NUM_BARAJAS)
  deck: Mazo = Mazo(clase_carta = Card, estrategia = strategy)

  print("♠ ♥ ♦ ♣ BLACKJACK - PARADIGMAS DE PROGRAMACIÓN 2023/24 ♠ ♥ ♦ ♣\n\n")

  croupier: Player = Player(name = "Croupier", isCroupier = True)
  player: Player = Player(name = "Mano")

  game: Game = Game(players = [player], croupier = croupier, deck = deck)

  continuePlaying: bool = True

  while continuePlaying:
    game.startGame()
    game.playersTurn()
    game.croupierTurn()
    game.showFinalTable()
    game.countResult()
    continuePlaying = game.restartGame()

if __name__ == "__main__":
  main()

