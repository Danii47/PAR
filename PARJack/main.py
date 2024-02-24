from externo import Mazo, CartaBase, Estrategia

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

class Carta(CartaBase):
  def __init__(self, ind):
    self.ind = ind

  def toString(self):
    return CARDS_DICTIONARY[self.ind % 13 + 1]
  
  def getType(self):
    return CARD_TYPE_DICTIONARY[self.ind // 13 + 1]

  def drawCard(self) -> None:
    print(f"╭───╮\n│{self.toString().rjust(3)}│\n│{self.getType().ljust(3)}│\n╰───╯", end="")



class Hand():
  """
  Esta es la clase Hand. Esta clase representa la mano de un jugador en el juego.
  """

  def __init__(self, cards=[], bet=0, state="ABIERTA", id=""):
    """
    Inicializa un nuevo objeto Hand.
    """
    self.cards = cards
    self.state = state
    self.bet = bet
    self.id = id
  
  def getCard(self, carta: Carta):
    """
    Añade una carta a la mano del jugador.

    Args:
        carta (Carta): La carta a añadir.
    """
    self.cards.append(carta)

  def setState(self, state: str):
    self.state = state

  def setBet(self, bet: int):
    self.bet = bet

  def getValue(self):
    handValue = 0
    for card in self.cards:
      if (card.valor == 1) and (handValue + 11 <= 21):
        handValue += 11
      else:
        handValue += card.valor
    return handValue

  def split(self, player, handNumber: int):
    handToSplit = player.hands[handNumber]
    player.hands.append(Hand([handToSplit.cards.pop()], handToSplit.bet, "ABIERTA", handToSplit.id + "B"))
    handToSplit.id = handToSplit.id + "A"
    

  
  

class Player():
  """
  Esta es la clase Player. Esta clase representa a un jugador en el juego.
  """

  def __init__(self, name, crupier=False):
    """
    Inicializa un nuevo objeto Player.

    Args:
        name (str): El nombre del jugador.
    """

    self.name = name
    self.crupier = crupier
    self.balance = 0
    self.hands = [Hand()]
  
  def startMatch(self, mazo: Mazo):
    """
    Inicia una nueva partida para el jugador, repartiendo una o dos cartas dependiendo de si es crupier o no.
    """
    if (self.crupier):
      self.hands[0].getCard(mazo.reparte())
    else:
      self.hands[0].getCard(mazo.reparte())
      self.hands[0].getCard(mazo.reparte())

  def showHands(self):
    lines = [[], [], [], []]
    for hand in self.hands:
      
      lines[0].append(f"Mano {hand.id}".ljust(8))
      lines[1].append(f"({hand.getValue()})".ljust(8))
      lines[2].append(f"{hand.bet}".ljust(8))
      lines[3].append(f"{hand.state}".ljust(8))
      for card in hand.cards:
        lines[0].append("╭───╮")
        lines[1].append(f"│{card.toString().rjust(3)}│")
        lines[2].append(f"│{card.getType().ljust(3)}│")
        lines[3].append("╰───╯")
    for line in lines:
      print(" ".join(line))
    print()

      
estrategia = Estrategia(Mazo.NUM_BARAJAS)

mazo = Mazo(Carta)
player = Player("Daniel")
player.startMatch(mazo)
# print(player.hands)
# player.hands[0].split(player, 0)
# print(player.hands)
player.hands[0].split(player, 0)
player.showHands()

