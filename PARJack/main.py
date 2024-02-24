from externo import Mazo, CartaBase, Estrategia
import time
import os

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

class Carta(CartaBase):
  def __init__(self, ind):
    self.ind = ind

  def toString(self):
    return CARDS_DICTIONARY[self.ind % 13 + 1]
  
  def getType(self):
    return CARD_TYPE_DICTIONARY[self.ind // 13 + 1]

  def drawCard(self) -> None:
    print(f"╭───╮\n│{self.toString().rjust(3)}│\n│{self.getType().ljust(3)}│\n╰───╯", end="")


class Player():
  """
  Esta es la clase Player. Esta clase representa a un jugador en el juego.
  """

  def __init__(self, name, bet: int = 0, isCroupier: bool = False):
    """
    Inicializa un nuevo objeto Player.

    Args:
        name (str): El nombre del jugador.
    """

    self.name = name
    self.isCroupier = isCroupier
    self.balance = 0
    self.hands = [Hand([], bet=bet)]
  
  def getName(self):
    return self.name

  def getBalance(self):
    return self.balance

  def addBalance(self, balance):
    self.balance = self.balance + balance

  def startMatch(self, deck: Mazo):
    """
    Inicia una nueva partida para el jugador, repartiendo una o dos cartas dependiendo de si es croupier o no.
    """
    if (self.isCroupier):
      self.hands[0].getCard(deck)
    else:
      self.hands[0].getCard(deck)
      self.hands[0].getCard(deck)

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

  def __init__(self, cards: list[Carta], state: str = HAND_STATE_DICTIONARY["ABIERTA"], bet: int = 0, id: str = ""):
    """
    Inicializa un nuevo objeto Hand.
    """
    self.cards = cards
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


  def getCard(self, mazo: Mazo):
    """
    Añade una carta a la mano del jugador.

    Args:
        carta (Carta): La carta a añadir.
    """
    self.cards.append(mazo.reparte())



  def getValue(self):
    handValue = 0
    for card in self.cards:
      if (card.valor == 1) and (handValue + 11 <= 21):
        handValue += 11
      else:
        handValue += card.valor
    return handValue
  
  def blackjack(self):
    return self.getValue() == 21

  
    
class Game():
  """
  Esta es la clase Game. Esta clase representa el juego en sí.
  """

  def __init__(self, players: list[Player], croupier: Player, deck: Mazo):
    """
    Inicializa un nuevo objeto Game.

    Args:
        players (list[Player]): La lista de jugadores.
        deck (Mazo): El mazo de cartas.
    """
    self.players = players
    self.croupier = croupier
    self.deck = deck
  
  def startGame(self):
    """
    Inicia una nueva partida.
    """
    self.croupier.startMatch(self.deck)
    for player in self.players:
      player.startMatch(self.deck)
    self.showTable()
  
  def showTable(self):
    self.croupier.showHands()
    for player in self.players:
      player.showHands()

  def playersTurn(self):
    for player in self.players:

      if not player.hands[0].blackjack():
        print(f"TURNO DEL JUGADOR ({player.getName()})")

      for i, hand in enumerate(player.hands):
        if hand.blackjack():
          hand.setBet(int(hand.bet * (3 / 2)))
          player.addBalance(hand.bet)
          print("*****************\n*** BLACKJACK ***\n*****************\n")

        else:
          
          while hand.state == "ABIERTA":
            print()
            canSplitHand = len(hand.cards) == 2 and hand.cards[0].valor == hand.cards[1].valor
            textSplit = " [S]eparar:" if canSplitHand else ":"
            action = input(f"{player.name}{hand.id}: ¿Qué quieres hacer? [P]edir [D]oblar [C]errar{textSplit} ")

            if action == "P":
              hand.getCard(self.deck)
              if (hand.getValue() > 21):
                hand.setState(HAND_STATE_DICTIONARY["PASADA"])
              player.showHands()

            elif action == "D":
              hand.getCard(self.deck)
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
  
  def croupierTurn(self):
    print("TURNO DEL CROUPIER")
    while (self.croupier.hands[0].getValue() < 17):
      self.croupier.showHands()
      time.sleep(1)
      self.croupier.hands[0].getCard(self.deck)

      if (self.croupier.hands[0].getValue() > 21):
        self.croupier.hands[0].setState(HAND_STATE_DICTIONARY["PASADA"])


    if self.croupier.hands[0].getState() == HAND_STATE_DICTIONARY["ABIERTA"]:
      self.croupier.hands[0].setState(HAND_STATE_DICTIONARY["CERRADA"])

    self.croupier.showHands()
    time.sleep(2)
    os.system("cls")
    print("TABLERO FINAL")
    self.showTable()
    

  def countResult(self):
    for player in self.players:
      print(f"CONTABILIZACIÓN DE RESULTADOS {player.name}")
      totalProfit = 0
      for hand in player.hands:
        resultOfBet = hand.getBet()

        if (self.croupier.hands[0].getState() != HAND_STATE_DICTIONARY["PASADA"] and hand.getState() == HAND_STATE_DICTIONARY["PASADA"]) or (self.croupier.hands[0].getState() != HAND_STATE_DICTIONARY["PASADA"] and self.croupier.hands[0].getValue() > hand.getValue()):
          resultOfBet = -hand.getBet()
        elif (self.croupier.hands[0].getState() == HAND_STATE_DICTIONARY["PASADA"] and hand.getState() == HAND_STATE_DICTIONARY["PASADA"]) or (self.croupier.hands[0].getValue() == hand.getValue()):
          resultOfBet = 0

        betSymbol = "+" if resultOfBet > 0 else ""
        totalProfit += resultOfBet

        print(f"* {self.croupier.getName()}: {self.croupier.hands[0].getValue()}, {player.getName()}{hand.getId()}: {hand.getValue()} -> {betSymbol}{resultOfBet}€")
      totalProfitSymbol = "+" if totalProfit > 0 else ""
      print(f"Resultado de la partida: {totalProfitSymbol}{totalProfit}€")
      player.addBalance(totalProfit)
    

def askBet():
  bet = 0
  while bet != 2 and bet != 10 and bet != 50:

    try:

      bet = int(input("¿Apuesta? [2] [10] [50]: "))
      if (bet != 2 and bet != 10 and bet != 50):
        print("Apuesta no valida.\n")
    except ValueError:
      print("Apuesta no valida.\n")

  return bet

# estrategia = Estrategia(Mazo.NUM_BARAJAS)

deck = Mazo(Carta)

croupier = Player("Croupier", isCroupier=True)



bet = askBet()

player = Player("Huguito", bet)


game = Game([player], croupier, deck)
game.startGame()

print("*** BLACKJACK - PARADIGMAS DE PROGRAMACIÓN 2023/24 ***")
print("¿Modo de ejecución? [J]uego [A]nálisis: J")

print("\nREPARTO INICIAL")

game.showTable()


game.playersTurn()
game.croupierTurn()
game.countResult()
# TODO: Si hay blackjack no juega el crupier, cambiar de clase el metodo blackjack()
#print("\nTURNO DEL JUGADOR")

