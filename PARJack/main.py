from externo import CartaBase, Estrategia
import time
import os
import random

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
  3: "♦",
  4: "♣"
}

HAND_STATE_DICTIONARY = {
  "ABIERTA": "ABIERTA",
  "CERRADA": "CERRADA",
  "PASADA": "PASADA"
}

class Card(CartaBase):
  def __init__(self, ind):
    self.ind = ind

  def toString(self):
    return CARDS_DICTIONARY[self.ind % 13 + 1]
  
  def getType(self):
    return CARD_TYPE_DICTIONARY[self.ind // 13 + 1]

  def drawCard(self) -> None:
    print(f"╭───╮\n│{self.toString().rjust(3)}│\n│{self.getType().ljust(3)}│\n╰───╯", end="")

class Deck():

  DECKS_NUM = 2

  def __init__(self, cardClass: type[Card], strategy: Estrategia | None = None):

    self.cardClass = cardClass
    self.strategy = strategy
    self.cards = []

  def dropCard(self) -> Card:

    if len(self.cards) == 0:
      indexes = list(range(52)) * Deck.DECKS_NUM
      random.shuffle(indexes)
      self.cards = [self.cardClass(i) for i in indexes]

    cardToDrop: Card = self.cards.pop()

    if self.strategy is not None:
      self.strategy.cuenta_carta(cardToDrop)

    return cardToDrop

  def resetDeck(self):
    self.cards = []

class Player():
  """
  Esta es la clase Player. Esta clase representa a un jugador en el juego.
  """

  def __init__(self, name: str, isCroupier: bool = False):
    """
    Inicializa un nuevo objeto Player.

    Args:
        name (str): El nombre del jugador.
    """

    self.name = name
    self.isCroupier = isCroupier
    self.balance = 0
    self.hands = [Hand(bet = self.askBet() if not isCroupier else 0)]
    self.isBlackjack = False
  
  def getName(self):
    return self.name

  def getBalance(self):
    return self.balance

  def getIsBlackjack(self):
    return self.isBlackjack
  
  def setIsBlackjack(self, isBlackjack: bool):
    self.isBlackjack = isBlackjack

  def addBalance(self, balance: int):
    self.balance = self.balance + balance

  def resetPlayer(self):
    self.isBlackjack = False
    self.hands = [Hand(bet = self.askBet() if not self.isCroupier else 0)]


  def askBet(self):
    bet = 0
    while bet != 2 and bet != 10 and bet != 50:

      try:

        bet = input(f"¿Apuesta de {self.name}? [2] [10] [50]: ")

        if bet == "":
          bet = 10
        else:
          bet = int(bet)

        if (bet != 2 and bet != 10 and bet != 50):
          print("Apuesta no valida.\n")
      except ValueError:
        print("Apuesta no valida.\n")

    return bet

  def giveHand(self, deck: Deck):
    """
    Inicia una nueva partida para el jugador, repartiendo una o dos cartas dependiendo de si es croupier o no.
    """
    if (self.isCroupier):
      self.hands[0].giveCard(deck)
    else:
      self.hands[0].giveCard(deck, 2)
      # self.hands[0].giveCard(deck, 2)

  def showHands(self):
    lines = [[], [], [], []]

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

  def split(self, handNumber: int):
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
      if (card.valor == 1) and (handValue + 11 <= 21):
        handValue += 11
      else:
        handValue += card.valor
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
  
  def startGame(self):
    """
    Inicia una nueva partida.
    """
    os.system("cls")
    self.croupier.giveHand(self.deck)
    for player in self.players:
      player.giveHand(self.deck)

      if player.hands[0].getValue() == 21:
        player.setIsBlackjack(True)
        
        

    print("\nREPARTO INICIAL")
    self.showTable()
  
  def comprobateBlackjack(self):
    blackjack: bool = False

    for player in self.players:
      if player.getIsBlackjack():
        blackjack = True

    return blackjack

  def showTable(self):
    self.croupier.showHands()
    for player in self.players:
      player.showHands()

  def playersTurn(self):

    if not self.comprobateBlackjack():
      for player in self.players:

        for i, hand in enumerate(player.hands):

          while hand.state == "ABIERTA":
            print()
            canSplitHand = len(hand.cards) == 2 and hand.cards[0].valor == hand.cards[1].valor
            action = input(f"{player.name}{hand.id}: ¿Qué quieres hacer? [P]edir [D]oblar [C]errar{" [S]eparar:" if canSplitHand else ":"} ").upper()
            if action == "P" or action == "":
              hand.giveCard(self.deck)
              if (hand.getValue() > 21):
                hand.setState(HAND_STATE_DICTIONARY["PASADA"])
              player.showHands()

            elif action == "D":
              hand.giveCard(self.deck)
              hand.setBet(hand.bet * 2)
              if (hand.getValue() > 21):
                hand.setState(HAND_STATE_DICTIONARY["PASADA"])
              else:
                hand.setState(HAND_STATE_DICTIONARY["CERRADA"])
              player.showHands()

            elif action == "C":
              hand.setState(HAND_STATE_DICTIONARY["CERRADA"])
              player.showHands()

            
            elif action == "S" and canSplitHand:
                player.split(i)
                player.showHands()
                
            else:
              print("Acción no válida. Inténtalo de nuevo.\n")
    else:
      for player in self.players:
        if player.getIsBlackjack():
          print(f"\n*** BLACKJACK DE {player.getName().upper()} ***\n")
          player.hands[0].setBet(int(player.hands[0].getBet() * (3 / 2)))
          player.hands[0].setState(HAND_STATE_DICTIONARY["CERRADA"])

  
  # TODO: Preguntar si se permite más de un return en un método
  def getAllHandsPassed(self):
    allHandsPassed = True
    for player in self.players:
      for hand in player.hands:
        if hand.getState() != HAND_STATE_DICTIONARY["PASADA"]:
          allHandsPassed = False
    return allHandsPassed

  def croupierTurn(self):
    if not self.comprobateBlackjack():
      print("TURNO DEL CROUPIER")
      if not self.getAllHandsPassed():

        while self.croupier.hands[0].getValue() < 17:
          self.croupier.showHands()
          time.sleep(2)
          self.croupier.hands[0].giveCard(self.deck)

          if self.croupier.hands[0].getValue() > 21:
            self.croupier.hands[0].setState(HAND_STATE_DICTIONARY["PASADA"])


      if self.croupier.hands[0].getState() == HAND_STATE_DICTIONARY["ABIERTA"]:
        self.croupier.hands[0].setState(HAND_STATE_DICTIONARY["CERRADA"])

      self.croupier.showHands()
      time.sleep(3)
      
    
  def showFinalTable(self):
    os.system("cls")
    print("TABLERO FINAL")
    self.showTable()
    time.sleep(3)

  def countResult(self):
    for player in self.players:
      print(f"\nCONTABILIZACIÓN DE RESULTADOS {player.name}")
      totalProfit: str = 0
      for hand in player.hands:
        resultOfBet = hand.getBet()

        if (self.croupier.hands[0].getState() != HAND_STATE_DICTIONARY["PASADA"] and hand.getState() == HAND_STATE_DICTIONARY["PASADA"]) or (self.croupier.hands[0].getState() != HAND_STATE_DICTIONARY["PASADA"] and self.croupier.hands[0].getValue() > hand.getValue()):
          resultOfBet = -hand.getBet()
        elif (self.croupier.hands[0].getState() == HAND_STATE_DICTIONARY["PASADA"] and hand.getState() == HAND_STATE_DICTIONARY["PASADA"]) or (self.croupier.hands[0].getValue() == hand.getValue()) or (self.comprobateBlackjack() and not player.getIsBlackjack()):
          resultOfBet = 0

        totalProfit += resultOfBet

        print(f"* {self.croupier.getName()}: {self.croupier.hands[0].getValue()}, {player.getName()}{hand.getId()}: {hand.getValue()} -> {"+" if resultOfBet > 0 else ""}{resultOfBet}€")
      
      print(f"\nResultado de la partida: {"+" if totalProfit > 0 else ""}{totalProfit}€ {"(PARTIDA CON BLACKJACK)" if self.comprobateBlackjack() and not player.getIsBlackjack() else ""}\n")
      player.addBalance(totalProfit)

  def restartGame(self):
    print("\n\n¿Quieres jugar otra partida?")
    action = input("[S]í [N]o: ").upper()

    if action == "S":
      self.croupier.resetPlayer()
      for player in self.players:
        player.resetPlayer()
      self.deck.resetDeck()

    else:
      print("\n¡Hasta la próxima!")

    return True if action == "S" else False


# estrategia = Estrategia(Deck.NUM_BARAJAS)

if __name__ == "__main__":

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
  
# TODO: Tipar todos los métodos
# TODO: Mostrar balance al iniciar cada partida
# TODO: Añadir el mensaje de barajando (dar más feedback al usuario)
# TODO: Si hay blackjack no juega el crupier, cambiar de clase el metodo blackjack() ✅
# TODO: Si el jugador se ha pasado en todas sus manos, el crupier no pide carta ✅
# TODO: Solucionar lo del valor default de Hand de cards, hacerlo como el video de malas prácticas ✅
#print("\nTURNO DEL JUGADOR")

