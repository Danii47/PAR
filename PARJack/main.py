from externo import Estrategia
import time
import os
import random

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


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
  1: f"{bcolors.OKBLUE}♠{bcolors.ENDC}",
  2: f"{bcolors.FAIL}♥{bcolors.ENDC}",
  3: f"{bcolors.OKBLUE}♣{bcolors.ENDC}",
  4: f"{bcolors.FAIL}♦{bcolors.ENDC}"
}

HAND_STATE_DICTIONARY = {
  "ABIERTA": "ABIERTA",
  "CERRADA": "CERRADA",
  "PASADA": "PASADA"
}

class Card():
  def __init__(self, ind: int) -> None:
    self.ind = ind

  def getValue(self) -> int:
    return min(10, self.ind % 13 + 1)

  def toString(self) -> str:
    return CARDS_DICTIONARY[self.ind % 13 + 1]
  
  def getType(self) -> str:
    return CARD_TYPE_DICTIONARY[self.ind // 13 + 1]

class Deck():

  DECKS_NUM = 2

  def __init__(self, cardClass: type[Card], strategy: Estrategia | None = None) -> None:

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
      self.strategy.cuenta_carta(cardToDrop)

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
    while bet != 2 and bet != 10 and bet != 50:

      try:
        bet = input(f"\n¿Apuesta de {self.name}? [2] [10] [50]: ")

        if bet == "": 
          bet = 10
        else:
          bet = int(bet)

        if (bet != 2 and bet != 10 and bet != 50):
          print("Apuesta no válida.\n")
      except ValueError:
        print("Apuesta no válida.\n")

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
    # TODO: SEGUIR TIPANDO
    for i, hand in enumerate(self.hands):
      handNameLength = len(self.getName()) + len(hand.getId()) if (len(self.getName()) + len(hand.getId()) >= 8) else 8
      
      lines[0].append(f"{self.name}{hand.id}:".rjust(handNameLength + 1))
      lines[1].append(f"({hand.getValue()})".rjust(handNameLength + 1))

      if not self.isCroupier:
        lines[2].append(f"{hand.bet}€".rjust(handNameLength + 1))

      if self.isCroupier:
        lines[2].append(f"{hand.state}".rjust(handNameLength + 1))
        lines[3].append("".rjust(handNameLength + 1))
      else:
        lines[3].append(f"{hand.state}".rjust(handNameLength + 1))

      for card in hand.cards:
        lines[0].append("╭───╮")
        lines[1].append(f"│{card.toString().rjust(3)}│")
        lines[2].append(f"│{card.getType().ljust(3)}│")
        lines[3].append("╰───╯")
      
      if (i < len(self.hands) - 1):

        for line in lines:
          line.append("│")

    for line in lines:
      print(" ".join(line))
    print()

  def splitHand(self, handNumber: int):
    handToSplit = self.hands[handNumber]
    self.hands.append(Hand([handToSplit.cards.pop()], HAND_STATE_DICTIONARY["ABIERTA"], handToSplit.bet, handToSplit.getId() + "B"))
    handToSplit.setId(handToSplit.getId() + "A")


class Hand():
  """
  Esta es la clase Hand. Esta clase representa la mano de un jugador en el juego.
  """

  def __init__(self, cards: list[Card] | None = None, state: str = HAND_STATE_DICTIONARY["ABIERTA"], bet: int = 0, id: str = ""):
    """
    Inicializa un nuevo objeto Hand.
    """
    self.cards = [] if cards is None else cards
    self.state = state
    self.bet = bet
    self.id = id
  
  def getBet(self):
    return self.bet
    
  def getState(self):
    return self.state

  def getId(self):
    return self.id

  def setId(self, id: str):
    self.id = id

  def setState(self, state: str):
    self.state = state

  def setBet(self, bet: int):
    self.bet = bet

  def giveCard(self, deck: Deck, amount: int = 1):
    for _ in range(amount):
      self.cards.append(deck.dropCard())
      

  def getValue(self):
    handValue: int = 0
    for card in self.cards:
      if (card.getValue() == 1) and (handValue + 11 <= 21):
        handValue += 11
      else:
        handValue += card.getValue()
    return handValue
  

class Game():
  """
  Esta es la clase Game. Esta clase representa el juego en sí.
  """

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
    self.areAllHandsPassed = False
    self.gameBlackjack = False
    self.gameNumber = 1
  
  def startGame(self):
    """
    Inicia una nueva partida.
    """
    os.system("cls")
    self.croupier.giveHand(self.deck)
    for player in self.players:
      print(f"--- INICIO DE LA PARTIDA #{self.gameNumber} --- BALANCE = {"+" if player.getBalance() > 0 else ""}{player.getBalance()} €")
      player.setInitialBet(player.askBet())
      os.system("cls")

      print(f"╭────────────────────────────╮\n│         BARAJEANDO         │\n╰────────────────────────────╯")
      time.sleep(2)
      os.system("cls")

      player.giveHand(self.deck)
      if player.hands[0].getValue() == 21:
        player.setIsBlackjack(True)
        self.gameBlackjack = True


    print("REPARTO INICIAL")
    self.showTable()
    time.sleep(2)
    os.system("cls")

  def showTable(self):
    self.croupier.showHands()
    for player in self.players:
      player.showHands()

  def showTablePlayersTurn(self, playerName: str):
    os.system("cls")
    print(f"TURNO DE {playerName.upper()}")
    self.showTable()

  def playersTurn(self):

    if not self.gameBlackjack:
      for player in self.players:

        for i, hand in enumerate(player.hands):

          while hand.state == "ABIERTA":
            self.showTablePlayersTurn(playerName = player.name)
            canSplitHand: bool = len(hand.cards) == 2 and hand.cards[0].getValue() == hand.cards[1].getValue()
            action: str = input(f"{player.name}{hand.id}: ¿Qué quieres hacer? [P]edir [D]oblar [C]errar{" [S]eparar:" if canSplitHand else ":"} ").upper()
            if action == "P" or action == "":
              hand.giveCard(self.deck)
              if (hand.getValue() > 21):
                hand.setState(HAND_STATE_DICTIONARY["PASADA"])
                self.showTablePlayersTurn(playerName = player.name)

            elif action == "D":
              hand.giveCard(self.deck)
              hand.setBet(hand.bet * 2)


              if (hand.getValue() > 21):
                hand.setState(HAND_STATE_DICTIONARY["PASADA"])
              
              else:
                hand.setState(HAND_STATE_DICTIONARY["CERRADA"])

              self.showTablePlayersTurn(playerName = player.name)

            elif action == "C":
              hand.setState(HAND_STATE_DICTIONARY["CERRADA"])
              self.showTablePlayersTurn(playerName = player.name)
            
            elif action == "S" and canSplitHand:
                player.splitHand(i)
                
            else:
              print("Acción no válida. Inténtalo de nuevo.\n")
            
      self.setAreAllHandsPassed()

  # TODO: Preguntar si se permite más de un return en un método
  def setAreAllHandsPassed(self):
    allHandsPassed = True
    for player in self.players:
      for hand in player.hands:
        if hand.getState() != HAND_STATE_DICTIONARY["PASADA"]:
          allHandsPassed = False

    self.areAllHandsPassed = allHandsPassed

  def croupierTurn(self):
    if not self.gameBlackjack:
      time.sleep(3)
      os.system("cls")
      print("TURNO DEL CROUPIER")
      if not self.areAllHandsPassed:

        while self.croupier.hands[0].getValue() < 17:
          self.showTable()
          time.sleep(2)
          os.system("cls")
          self.croupier.hands[0].giveCard(self.deck)

          if self.croupier.hands[0].getValue() > 21:
            self.croupier.hands[0].setState(HAND_STATE_DICTIONARY["PASADA"])
          print("TURNO DEL CROUPIER")


      if self.croupier.hands[0].getState() == HAND_STATE_DICTIONARY["ABIERTA"]:
        self.croupier.hands[0].setState(HAND_STATE_DICTIONARY["CERRADA"])

      self.showTable()
      time.sleep(3)
      
  def warnBlackjack(self):
    for player in self.players:
      if player.getIsBlackjack():
        print(f"\n*** BLACKJACK DE {player.getName().upper()} ***")
        player.hands[0].setBet(int(player.hands[0].getBet() * (3 / 2)))
        player.hands[0].setState(HAND_STATE_DICTIONARY["CERRADA"])

  def showFinalTable(self):
    os.system("cls")
    print("TABLERO FINAL")
    if self.gameBlackjack:
      self.croupier.hands[0].setState(HAND_STATE_DICTIONARY["CERRADA"])
      for player in self.players:
        player.hands[0].setState(HAND_STATE_DICTIONARY["CERRADA"])

    self.showTable()
    
    if self.gameBlackjack:
      self.warnBlackjack()
      
    time.sleep(3)

  def countResult(self):
    os.system("cls")
    for player in self.players:
      print(f"CONTABILIZACIÓN DE RESULTADOS {player.name}")
      totalProfit: str = 0
      for hand in player.hands:
        resultOfBet = hand.getBet()

        if (self.croupier.hands[0].getState() != HAND_STATE_DICTIONARY["PASADA"] and hand.getState() == HAND_STATE_DICTIONARY["PASADA"]) or (self.croupier.hands[0].getState() != HAND_STATE_DICTIONARY["PASADA"] and self.croupier.hands[0].getValue() > hand.getValue()):
          resultOfBet = -hand.getBet()
        elif (self.croupier.hands[0].getState() == HAND_STATE_DICTIONARY["PASADA"] and hand.getState() == HAND_STATE_DICTIONARY["PASADA"]) or (self.croupier.hands[0].getValue() == hand.getValue()) or (self.gameBlackjack and not player.getIsBlackjack()):
          resultOfBet = 0

        totalProfit += resultOfBet

        print(f"* {self.croupier.getName()}: {self.croupier.hands[0].getValue()}, {player.getName()}{hand.getId()}: {hand.getValue()} -> {"+" if resultOfBet > 0 else ""}{resultOfBet}€")
      
      print(f"\nResultado de la partida: {"+" if totalProfit > 0 else ""}{totalProfit}€ {"(BLACKJACK)" if self.gameBlackjack and player.getIsBlackjack() else ""}")
      player.addBalance(totalProfit)

  def restartGame(self):
    print("\n\n¿Quieres jugar otra partida?")
    action = input("[S]í [N]o: ").upper()
    if action == "S" or action == "":
      os.system("cls")
      self.gameNumber += 1
      self.gameBlackjack = False
      self.croupier.resetPlayer()
      for player in self.players:
        player.resetPlayer()
      self.deck.resetDeck()
    else:
      print("\n¡Hasta la próxima!")

    return True if action == "S" or action == "" else False


def main():
  os.system("cls")

  deck: Deck = Deck(Card)

  print("\n\n♠ ♥ ♦ ♣ BLACKJACK - PARADIGMAS DE PROGRAMACIÓN 2023/24 ♠ ♥ ♦ ♣\n\n")
  print("¿Modo de ejecución? [J]uego [A]nálisis: J\n")


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

  
# TODO: Tipar todos los métodos
# TODO: Enmarcar tablero con los signos de las cartas (hacer método)
# TODO: Hacer una cartera con la que empieces con X dinero (ej: 100€)


