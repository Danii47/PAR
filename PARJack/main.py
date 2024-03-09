from externo import Estrategia
import time
import os
import random

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


class Card():
  def __init__(self, cardIndex: int) -> None:
    self.cardIndex = cardIndex

  def getValue(self) -> int:
    return min(10, self.cardIndex % 13 + 1)

  def toString(self) -> str:
    return CARDS_DICTIONARY[self.cardIndex % 13 + 1]
  
  def getType(self) -> str:
    return CARD_TYPE_DICTIONARY[self.cardIndex // 13 + 1]
  
  def getTypeId(self) -> int:
    return self.cardIndex // 13 + 1

# TODO: preguntar (object)
class Strategy():
  """ Clase que representa una estrategia de juego para el Blackjack
      Basada en el libro que muestra Alan en Resacón en las Vegas
  """
  # Matrices de estrategia: Filas suma de valores de cartas del jugador (ases = 1), columnas valor carta del croupier
  # Matriz para jugadas con 2 cartas del mismo valor (inicio fila 2)
  MATD: list[str] = ['S' * 10, *['P' + 'S' * 6 + 'PPP'] * 2, 'P' * 4 + 'SS' + 'P' * 4, 'P' + 'D' * 8 + 'P',
                      'P' + 'S' * 6 + 'PPP', 'P' + 'S' * 7 + 'PP', 'S' * 10, 'C' + 'S' * 5 + 'CSSC', 'C' * 10]
  # Matriz para jugadas con algún as (inicio fila 3, suma debe dividirse por 2)
  MATA: list[str] = [*['P' * 4 + 'DD' + 'P' * 4] * 2, *['PPPDDD' + 'P' * 4] * 2, 'PP' + 'D' * 4 + 'P' * 4,
                      'PC' + 'D' * 4 + 'CCPP', *['C' * 10] * 3]
  # Matriz para jugadas sin ases ni duplicados (inicio fila 4)
  MATN: list[str] = [*['P' * 10] * 5, 'P' + 'D' * 5 + 'P' * 4, 'P' + 'D' * 8 + 'P', 'D' * 10,
                      'P' * 3 + 'C' * 3 + 'P' * 4, *['P' + 'C' * 5 + 'P' * 4] * 4, *['C' * 10] * 5]
  # Vector de estrategia de conteo
  CONT: list[int] = [-2, 2, 2, 2, 3, 2, 1, 0, -1, -2]

  def __init__(self, decksAmount: int) -> None:
    """ Crea e inicializa la estrategia
    :param decksAmount: Número de barajas del mazo utilizado en el juego
    """
    self.decksAmount = decksAmount
    self.cardsDropped = 0
    self.account = 0

  def registerDropCard(self, card: Card) -> None:
    """ Este método se llama automáticamente por el objeto Mazo cada vez
        que se reparte una carta
    :param card: La carta que se ha repartido
    """
    self.cardsDropped += 1
    if self.cardsDropped >= 52 * self.decksAmount:
      # Se ha cambiado el mazo
      self.cardsDropped = 1
      self.account = 0
    self.account += Strategy.CONT[card.getValue() - 1]

  def bestBet(self, lowBet: int, mediumBet: int, highBet: int) -> int:
    """ Indica la apuesta que se debe realizar dado el estado del juego.
        Elige entre 3 valores posibles (baja, media y alta)
    :param lowBet: El valor de la apuesta baja
    :param mediumBet: El valor de la apuesta media
    :param highBet: El valor de la apuesta alta
    :return: Uno de los 3 valores posibles de apuesta
    """
    remainingDecks: int = self.decksAmount - self.cardsDropped // 52
    trueCount: float = self.account / remainingDecks
    if trueCount > 1.0:
      return highBet
    elif trueCount < -1.0:
      return lowBet
    else:
      return mediumBet

  def bestPlay(self, firstCroupierCard: Card, playerHand: list[Card]) -> str:
    """ Indica la mejor opción dada la mano del croupier (que se supone que
        consta de una única carta) y la del jugador
    :param croupier: La carta del croupier
    :param jugador: La lista de cartas de la mano del jugador
    :return: La mejor opción: 'P' (pedir), 'D' (doblar), 'C' (cerrar) o 'S' (separar)
    """
    croupierHandValue = firstCroupierCard.getValue()
    playerHandValue = sum(playerCard.getValue() for playerCard in playerHand)

    if len(playerHand) == 2 and playerHand[0].getValue() == playerHand[1].getValue():
        
        return Strategy.MATD[playerHandValue // 2 - 1][croupierHandValue - 1]
    
    if any(card.getValue() == 1 for card in playerHand) and playerHandValue < 12:
        
        return Strategy.MATA[playerHandValue - 3][croupierHandValue - 1]
    
    return Strategy.MATN[playerHandValue - 4][croupierHandValue - 1]

class Deck():

  DECKS_NUM = 2

  def __init__(self, cardClass: type[Card], strategy: Strategy) -> None:

    self.cardClass = cardClass
    self.strategy = strategy
    self.cards = []

  def dropCard(self) -> Card:

    if len(self.cards) == 0:
      indexes: list[int] = list(range(52)) * Deck.DECKS_NUM
      random.shuffle(indexes)
      self.cards = [self.cardClass(i) for i in indexes]

    cardToDrop: Card = self.cards.pop()

    if self.strategy is not None:
      self.strategy.registerDropCard(cardToDrop)

    return cardToDrop

  def resetDeck(self) -> None:
    self.cards = []

class Player():
  """
  Esta es la clase Player. Esta clase representa a un jugador en el juego.
  """

  def __init__(self, name: str, isCroupier: bool = False) -> None:
    """
    Inicializa un nuevo objeto Player.

    Args:
        name (str): El nombre del jugador.
    """

    self.name = name
    self.isCroupier = isCroupier
    self.balance = 0
    self.hands = [Hand()]
    self.isBlackjack = False
  
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
    while bet != Game.LOW_BET and bet != Game.MEDIUM_BET and bet != Game.HIGH_BET:

      try:
        bet = input(f"\n¿Apuesta de {self.name}? [{Game.LOW_BET}] [{Game.MEDIUM_BET}] [{Game.HIGH_BET}]: ")

        if bet == "": 
          bet = Game.MEDIUM_BET
        else:
          bet = int(bet)

        if (bet != Game.LOW_BET and bet != Game.MEDIUM_BET and bet != Game.HIGH_BET):
          print("Apuesta no válida.")
      except ValueError:
        print("Apuesta no válida.")

    return bet

  def giveHand(self, deck: Deck) -> None:
    """
    Inicia una nueva partida para el jugador, repartiendo una o dos cartas dependiendo de si es croupier o no.
    """
    if (self.isCroupier):
      self.hands[0].giveCard(deck)
    else:
      self.hands[0].giveCard(deck, 2)
     # self.hands[0].cards = [Card(0), Card(9)] # ? Para iniciar con blackjack

  def showHands(self) -> None:

    lines: list[list[str]] = [[], [], [], []]

    for i, hand in enumerate(self.hands):

      handNameLength: int = len(self.getName()) + len(hand.getId())
      handShift: int = handNameLength if (handNameLength >= 8) else 8 # 8 es la longitud de "Croupier", que es el nombre más largo
      
      lines[0].append(f"{self.name}{hand.id}:".rjust(handShift + 1))
      lines[1].append(f"({hand.getValue()})".rjust(handShift + 1))

      if not self.isCroupier:
        lines[2].append(f"{hand.getBet()}€".rjust(handShift + 1))

      if self.isCroupier:
        lines[2].append(f"{hand.getState()}".rjust(handShift + 1))
        lines[3].append("".rjust(handShift + 1))
      else:
        lines[3].append(f"{hand.getState()}".rjust(handShift + 1))

      for card in hand.cards:
        lines[0].append(f"{TERMINAL_COLORS.RED if card.getTypeId() == 2 or card.getTypeId() == 4 else TERMINAL_COLORS.BLACK}╭───╮{TERMINAL_COLORS.RESTART}")
        lines[1].append(f"{TERMINAL_COLORS.RED if card.getTypeId() == 2 or card.getTypeId() == 4 else TERMINAL_COLORS.BLACK}│{card.toString().rjust(3)}│{TERMINAL_COLORS.RESTART}")
        lines[2].append(f"{TERMINAL_COLORS.RED if card.getTypeId() == 2 or card.getTypeId() == 4 else TERMINAL_COLORS.BLACK}│{card.getType().ljust(3)}│{TERMINAL_COLORS.RESTART}") # Debe dejar 2 espacios a la derecha. El cambio de color no afecta 
        lines[3].append(f"{TERMINAL_COLORS.RED if card.getTypeId() == 2 or card.getTypeId() == 4 else TERMINAL_COLORS.BLACK}╰───╯{TERMINAL_COLORS.RESTART}")
      
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
  Esta es la clase Hand. Esta clase representa la mano de un jugador en el juego.
  """

  def __init__(self, cards: list[Card] | None = None, state: str = HAND_STATES.ABIERTA, bet: int = 0, id: str = ""):
    """
    Inicializa un nuevo objeto Hand.
    """
    self.cards = [] if cards is None else cards
    self.state = state
    self.bet = bet
    self.id = id
  
  def getBet(self) -> int:
    return self.bet
    
  def getState(self) -> str:
    return self.state

  def getId(self) -> str:
    return self.id

  def setId(self, id: str) -> None:
    self.id = id

  def setState(self, state: str) -> None:
    self.state = state

  def setBet(self, bet: int) -> None:
    self.bet = bet

  def giveCard(self, deck: Deck, amount: int = 1) -> None:
    for _ in range(amount):
      self.cards.append(deck.dropCard())

  def getValue(self) -> int:
    handValue: int = 0
    countOfAces: int = 0

    for card in self.cards:
      handValue += card.getValue()
      if card.getValue() == 1:
        countOfAces += 1

    for _ in range(countOfAces):
      if handValue + 10 <= 21:
        handValue += 10  

    return handValue
  

class Game():
  """
  Esta es la clase Game. Esta clase representa el juego en sí.
  """

  MIN_CROUPIER_CARDS = 17
  LOW_BET = 2
  MEDIUM_BET = 10
  HIGH_BET = 50
  LOW_DELAY = 1
  MEDIUM_DELAY = 2
  HIGH_DELAY = 3

  def __init__(self, players: list[Player], croupier: Player, deck: Deck):
    """
    Inicializa un nuevo objeto Game.

    Args:
        players (list[Player]): La lista de jugadores.
        deck (Deck): El mazo de cartas.
    """
    self.players = players
    self.croupier = croupier
    self.deck = deck
    self.gameBlackjack = False
    self.gameNumber = 1
    self.gameMode = self.askGameMode()
    self.gamesAmount = self.askGamesAmount() if self.gameMode == GAME_MODES.ANALISIS else 0

  def askGameMode(self) -> str:
    gameMode: str = ""
    while gameMode != GAME_MODES.JUEGO and gameMode != GAME_MODES.ANALISIS:
      gameMode = input("¿Qué modo de juego quieres? [J]uego [A]nálisis: ").upper()
      if gameMode == "":
        gameMode = GAME_MODES.JUEGO
  
      if gameMode != GAME_MODES.JUEGO and gameMode != GAME_MODES.ANALISIS:
        print("Modo no válido. Inténtalo de nuevo.\n")
    return gameMode

  def askGamesAmount(self) -> int:
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
    Inicia una nueva partida.
    """
    os.system("cls")
    self.croupier.giveHand(self.deck)
    for player in self.players:
      print(f"--- INICIO DE LA PARTIDA #{self.gameNumber} --- BALANCE = {"+" if player.getBalance() > 0 else ""}{player.getBalance()} €")
      
      if self.gameMode == GAME_MODES.JUEGO:
        player.setInitialBet(player.askBet())
      else:
        bestBet: int = self.deck.strategy.bestBet(Game.LOW_BET, Game.MEDIUM_BET, Game.HIGH_BET)

        print(f"\n¿Apuesta de {player.getName()}? [{Game.LOW_BET}] [{Game.MEDIUM_BET}] [{Game.HIGH_BET}]: ", end="")
        time.sleep(Game.LOW_DELAY)
        print(bestBet)
        time.sleep(Game.LOW_DELAY)
        player.setInitialBet(bestBet) 
      
      os.system("cls")

      player.giveHand(self.deck)
      if player.hands[0].getValue() == 21:
        player.setIsBlackjack(True)
        self.gameBlackjack = True

    print(f"╭────────────────────────────╮\n│         BARAJEANDO         │\n╰────────────────────────────╯")
    time.sleep(Game.MEDIUM_DELAY)
    os.system("cls")

    print("REPARTO INICIAL")
    self.showTable()
    time.sleep(Game.MEDIUM_DELAY)


  def showTable(self) -> None:
    self.croupier.showHands()
    for player in self.players:
      player.showHands()

  def showTablePlayersTurn(self, playerName: str) -> None:
    os.system("cls")
    print(f"TURNO DE {playerName.upper()}")
    self.showTable()

  def playersTurn(self) -> None:

    if not self.gameBlackjack:
      for player in self.players:

        for i, hand in enumerate(player.hands):
          
          while hand.state == "ABIERTA":
            self.showTablePlayersTurn(playerName = player.getName())
            
            canSplitHand: bool = len(hand.cards) == 2 and hand.cards[0].getValue() == hand.cards[1].getValue() and player.getHandsLength() < 4
            action: str = ""
            if self.gameMode == GAME_MODES.JUEGO:
              action = input(f"{player.getName()}{hand.getId()}: ¿Qué quieres hacer? [P]edir [D]oblar [C]errar{" [S]eparar" if canSplitHand else ""}: ").upper()
            else:
              action = self.deck.strategy.bestPlay(self.croupier.hands[0].cards[0], hand.cards)
              time.sleep(Game.LOW_DELAY)
              print(f"\n¿Qué quieres hacer? [P]edir [D]oblar [C]errar{" [S]eparar" if canSplitHand else ""}: ", end="")
              time.sleep(Game.LOW_DELAY)
              print(action)
              time.sleep(Game.LOW_DELAY)

            if action == "P" or action == "":
              hand.giveCard(self.deck)
              if (hand.getValue() > 21):
                hand.setState(HAND_STATES.PASADA)
                self.showTablePlayersTurn(playerName = player.getName())

            elif action == "D":
              hand.giveCard(self.deck)
              hand.setBet(hand.bet * 2)


              if (hand.getValue() > 21):
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

    for player in self.players:
      for hand in player.hands:
        if hand.getState() != HAND_STATES.PASADA:
          return False

    return True

  def croupierTurn(self) -> None:
    if not self.gameBlackjack:
      time.sleep(Game.HIGH_DELAY)
      os.system("cls")
      print("TURNO DEL CROUPIER")
      if not self.areAllHandsPassed():

        while self.croupier.hands[0].getValue() < Game.MIN_CROUPIER_CARDS:
          self.showTable()
          time.sleep(Game.MEDIUM_DELAY)
          os.system("cls")
          self.croupier.hands[0].giveCard(self.deck)

          if self.croupier.hands[0].getValue() > 21:
            self.croupier.hands[0].setState(HAND_STATES.PASADA)
          print("TURNO DEL CROUPIER")


      if self.croupier.hands[0].getState() == HAND_STATES.ABIERTA:
        self.croupier.hands[0].setState(HAND_STATES.CERRADA)

      self.showTable()
      time.sleep(Game.HIGH_DELAY)
      os.system("cls")
      
  def warnBlackjack(self) -> None:
    for player in self.players:
      if player.getIsBlackjack():
        print(f"\n*** BLACKJACK DE {player.getName().upper()} ***")
        player.hands[0].setBet(int(player.hands[0].getBet() * (3 / 2)))
        player.hands[0].setState(HAND_STATES.CERRADA)

  def showFinalTable(self) -> None:
    os.system("cls")
    print("TABLERO FINAL")
    if self.gameBlackjack:
      self.croupier.hands[0].setState(HAND_STATES.CERRADA)
      for player in self.players:
        player.hands[0].setState(HAND_STATES.CERRADA)

    self.showTable()
    
    if self.gameBlackjack:
      self.warnBlackjack()
      
    time.sleep(Game.HIGH_DELAY)
    os.system("cls")

  def countResult(self) -> None:
    for player in self.players:
      print(f"CONTABILIZACIÓN DE RESULTADOS {player.name}")
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

    action: str = ""

    if self.gameMode == GAME_MODES.JUEGO:
      action = input(f"\n\n¿{"Quieres" if len(self.players) == 1 else "Quereis"} jugar otra partida? [S]í [N]o: ").upper()
    else:

      self.gamesAmount -= 1

      if self.gamesAmount > 0:
        action = "S" # CONTROLAR CUANTAS PARTIDAS QUIERE JUGAR EN EL MODO ANALISIS
      else:
        action = "N"

      print(f"\n\n¿{"Quieres" if len(self.players) == 1 else "Quereis"} jugar otra partida? [S]í [N]o: ", end="")
      time.sleep(Game.LOW_DELAY)
      print(action)
      time.sleep(Game.LOW_DELAY)

    if action == "S" or action == "":
      os.system("cls")
      self.gameNumber += 1
      self.gameBlackjack = False
      self.croupier.resetPlayer()
      for player in self.players:
        player.resetPlayer()
      self.deck.resetDeck()
    else:
      os.system("cls")
      print("REGISTRO FINAL DE BALANCE\n")
      for player in self.players:
        print(f"{player.getName()} -> {"+" if player.getBalance() > 0 else ""}{player.getBalance()}€")
      print("\n¡Hasta la próxima!")

    return True if action == "S" or action == "" else False


def main() -> None:
  os.system("cls")

  strategy: Strategy = Strategy(decksAmount = Deck.DECKS_NUM)
  deck: Deck = Deck(cardClass = Card, strategy = strategy)

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

# TODO: Cambiar color de los números de las cartas
# TODO: Controlar cuantas partidas juega en modo análisis