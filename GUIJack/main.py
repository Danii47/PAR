# PRÁCTICA 2 - PARADIGMAS DE PROGRAMACIÓN # -*- coding: utf-8 -*-
#


# region Imports
from externo import CartaBase, Mazo, Estrategia
import wx
import winsound
import random
# endregion

# region Constants
class SOUNDS:
    GIVE_CARD = "./utils/sounds/giveCard.wav"
    START_GAME = "./utils/sounds/startGame3CardsSound.wav"
    CHEERS = "./utils/sounds/cheers.wav"

class COLOURS:
    SELECTED = wx.Colour(236, 247, 181)
    PASSED = wx.Colour(255, 105, 97)
    CLOSED = wx.Colour(60, 60, 60)
    WHITE = wx.Colour(250, 250, 250)
    BLACK = wx.Colour(10 ,10, 10)
    WON = wx.Colour(48, 194, 48)
    LOST = wx.Colour(255, 105, 97)
    DRAW = wx.Colour(215, 215, 0)
    LOW_COUNTDOWN = wx.Colour(255, 22, 0)
    BACKGROUND = wx.Colour(237, 237, 237)
    NULL = wx.NullColour

class HAND_STATES:
    ACTIVE = "ACTIVA"
    PASSED = "PASADA"
    CLOSED = "CERRADA"
    DECLINED = "RENUNCIADA"

class GAME_MODES:
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATICO"

# endregion

# region Card
class Card(CartaBase):
    def __init__(self, ind: int) -> None:
        super().__init__(ind)
        self.ind = ind
        self.img = wx.Bitmap()
        self.img.LoadFile(f"./utils/imgs/cards/m{ind:02d}.png")

    def getCardBitmap(self):
        return self.img
    
# endregion

# region Hand
class Hand():
    def __init__(self, panel, sizer, staticText, cards: list[Card] = None, bet = 0, state = HAND_STATES.ACTIVE) -> None:
        self.sizer = sizer
        self.staticText = staticText
        self.panel = panel
        self.bet = bet
        self.cards = [] if not cards else cards
        self.state = state

    def getValue(self) -> int:

        handValue: int = 0
        countOfAces: int = 0

        for card in self.cards:
            handValue += card.valor
            if card.valor == 1:
                countOfAces += 1
        
        if countOfAces > 0 and handValue + 10 <= 21:
            handValue += 10

        return handValue
    
    def giveCard(self, player, deck, amount, selectPanel):

        for _ in range(amount):
            cardToAdd = deck.reparte()
            self.cards.append(cardToAdd)
            if self.getValue() > 21:
                self.state = HAND_STATES.PASSED
            

            cardBitmap = self.cards[-1].getCardBitmap()
            staticBitMap = wx.StaticBitmap(self.getPanel(), wx.ID_ANY, cardBitmap)
            staticBitMap.Bind(wx.EVT_LEFT_DOWN, lambda event: selectPanel(event, player, self))

            self.sizer.Add(staticBitMap, 0, 0, 0)

        self.updateText(player)
        self.updateColor()
        self.panel.Layout()

    def updateColor(self):
        if self.getState() == HAND_STATES.PASSED:
            self.panel.SetBackgroundColour(COLOURS.PASSED)
        elif self.getState() == HAND_STATES.CLOSED:
            self.panel.SetBackgroundColour(COLOURS.CLOSED)
        elif self.getState() == HAND_STATES.DECLINED:
            self.panel.SetBackgroundColour(COLOURS.PASSED)

        self.panel.Refresh()

    def updateText(self, player):
        self.staticText.SetLabel(f"{"CROUPIER" if player.isCroupier else f"({self.getValue()})"}\n{f"({self.getValue()})" if player.isCroupier else f"{self.getBet()}€"}\n{self.getState()}")

        if self.getState() == HAND_STATES.PASSED or self.getState() == HAND_STATES.CLOSED or self.getState() == HAND_STATES.DECLINED:
            self.staticText.SetForegroundColour(COLOURS.WHITE)


    def renderHandPanel(self, player, selectPanel):

        self.panel.DestroyChildren()
        self.updateColor()

        self.staticText = wx.StaticText(self.panel, wx.ID_ANY, f"{"CROUPIER" if player.isCroupier else f"({self.getValue()})"}\n{f"({self.getValue()})" if player.isCroupier else f"{self.getBet()}€"}\n{self.getState()}", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.staticText.SetMinSize((145, 200))
        self.staticText.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        
        self.staticText.Bind(wx.EVT_LEFT_DOWN, lambda event: selectPanel(event, player, self))

        self.sizer.Add(self.staticText, 0, wx.ALL, 10)

        for card in self.cards:
            cardBitmap = card.getCardBitmap()
            staticBitMap = wx.StaticBitmap(self.panel, wx.ID_ANY, cardBitmap)
            staticBitMap.Bind(wx.EVT_LEFT_DOWN, lambda event: selectPanel(event, player, self))
            
            self.sizer.Add(staticBitMap, 0, 0, 0)

        self.panel.Refresh()
        self.sizer.Layout()

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

    def getBet(self):
        return self.bet
    
    def setBet(self, bet):
        self.bet = bet

    def getPanel(self):
        return self.panel
    
    def getSizer(self):
        return self.sizer
    
# endregion


# region Player
class Player():
    def __init__(self, hands: list[Hand] = None, isCroupier = False):
        self.hands = [] if not hands else hands
        self.isCroupier = isCroupier

    def getIsCroupier(self):
        return self.isCroupier

    def addHand(self, hand):
        self.hands.append(hand)

    def anyHandOpen(self):
        return any(hand.getState() == HAND_STATES.ACTIVE for hand in self.hands)
    
    def allHandsPassed(self):
        return all(hand.getState() == HAND_STATES.PASSED for hand in self.hands)
    
# endregion


# region MainWindow
class MainWindow(wx.Frame):
    DEFAULT_COUNTDOWN = 10

    def __init__(self, parent, id, title, croupier, player, deck, strategy):

        self.selectedBet = 2
        self.handSelected = None
        self.playerSelected = player
        self.croupier = croupier
        self.player = player
        self.deck = deck
        self.gameMode = GAME_MODES.MANUAL
        self.gameCounter = 0
        self.globalBalance = 0
        self.gameBalance = 0
        self.countdown = MainWindow.DEFAULT_COUNTDOWN
        self.delayActions = 1000
        self.chooseBetWindow = None
        self.strategy = strategy
        self.automaticHandCount = 0

        wx.Frame.__init__(self, parent, id, title)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.handleTimer, self.timer)
        
        self.croupierTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.croupierTurn, self.croupierTimer)

        self.automaticTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.automaticAction, self.automaticTimer)

        self.selectBetAutomaticTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.selectBetAutomatic, self.selectBetAutomaticTimer)

        self.SetTitle("Blackjack - PARADIGMAS DE PROGRAMACIÓN - GRUPO 3 - 2024")
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.statusBar = self.CreateStatusBar(2)
        self.statusBar.SetStatusWidths([-1, 0])

        statusBar_fields = ["Selecciona jugada", ""]
        for i in range(len(statusBar_fields)):
            self.statusBar.SetStatusText(statusBar_fields[i], i)

        gameSizer = wx.BoxSizer(wx.HORIZONTAL)

        gameOptionsSizer = wx.BoxSizer(wx.VERTICAL)
        gameSizer.Add(gameOptionsSizer, 10, wx.EXPAND, 0)

        gameModeSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Modo de juego"), wx.HORIZONTAL)
        gameOptionsSizer.Add(gameModeSizer, 7, wx.ALL | wx.EXPAND, 9)

        self.manualButton = wx.RadioButton(self, wx.ID_ANY, "Manual")
        self.manualButton.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        gameModeSizer.Add(self.manualButton, 60, wx.ALIGN_CENTER_VERTICAL, 0)

        self.automaticButton = wx.RadioButton(self, wx.ID_ANY, u"Automático")
        self.automaticButton.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        gameModeSizer.Add(self.automaticButton, 40, wx.ALIGN_CENTER_VERTICAL, 0)

        gameDelaySizer = wx.BoxSizer(wx.HORIZONTAL)
        gameOptionsSizer.Add(gameDelaySizer, 6, wx.ALL | wx.EXPAND, 9)

        delayText = wx.StaticText(self, wx.ID_ANY, "Retardo:")
        delayText.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        gameDelaySizer.Add(delayText, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)

        self.delayInput = wx.TextCtrl(self, wx.ID_ANY, f"{self.delayActions}", style=wx.TE_CENTRE | wx.TE_PROCESS_ENTER)
        self.delayInput.SetMinSize((65, 23))
        self.Bind(wx.EVT_TEXT_ENTER, self.handleDelayInput, self.delayInput)
        
        gameDelaySizer.Add(self.delayInput, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)

        msText = wx.StaticText(self, wx.ID_ANY, "ms.")
        msText.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        gameDelaySizer.Add(msText, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        gameActionSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Acción"), wx.VERTICAL)
        gameOptionsSizer.Add(gameActionSizer, 17, wx.ALL | wx.EXPAND, 9)

        self.askButton = wx.Button(self, wx.ID_ANY, "PEDIR")
        self.askButton.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.askButton.Disable()

        gameActionSizer.Add(self.askButton, 25, wx.ALL | wx.EXPAND, 2)

        self.doubleButton = wx.Button(self, wx.ID_ANY, "DOBLAR")
        self.doubleButton.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.doubleButton.Disable()

        gameActionSizer.Add(self.doubleButton, 25, wx.ALL | wx.EXPAND, 2)

        self.closeButton = wx.Button(self, wx.ID_ANY, "CERRAR")
        self.closeButton.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.closeButton.Disable()

        gameActionSizer.Add(self.closeButton, 25, wx.ALL | wx.EXPAND, 2)

        self.splitButton = wx.Button(self, wx.ID_ANY, "SEPARAR")
        self.splitButton.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.splitButton.Disable()

        gameActionSizer.Add(self.splitButton, 25, wx.ALL | wx.EXPAND, 2)

        self.declineButton = wx.Button(self, wx.ID_ANY, "RENUNCIAR")
        self.declineButton.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.declineButton.Disable()

        gameActionSizer.Add(self.declineButton, 25, wx.ALL | wx.EXPAND, 2)

        self.separatorPanel = wx.Panel(self, wx.ID_ANY)
        gameOptionsSizer.Add(self.separatorPanel, 15, wx.EXPAND, 0)

        self.gameCounterSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Partida"), wx.HORIZONTAL)
        gameOptionsSizer.Add(self.gameCounterSizer, 7, wx.ALL | wx.EXPAND, 9)

        self.gameCounterText = wx.StaticText(self, wx.ID_ANY, f"{self.gameCounter}", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.gameCounterText.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.gameCounterSizer.Add(self.gameCounterText, 100, wx.ALIGN_CENTER_VERTICAL, 0)

        self.gameGlobalBalanceSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Balance global"), wx.HORIZONTAL)
        gameOptionsSizer.Add(self.gameGlobalBalanceSizer, 7, wx.ALL | wx.EXPAND, 9)

        self.globalBalanceText = wx.StaticText(self, wx.ID_ANY, f"+{self.globalBalance} €", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.globalBalanceText.SetForegroundColour(COLOURS.WON)
        self.globalBalanceText.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.gameGlobalBalanceSizer.Add(self.globalBalanceText, 100, wx.ALIGN_CENTER_VERTICAL, 0)

        self.gameBalanceSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Balance partida actual"), wx.HORIZONTAL)
        gameOptionsSizer.Add(self.gameBalanceSizer, 7, wx.ALL | wx.EXPAND, 9)

        self.gameBalaneText = wx.StaticText(self, wx.ID_ANY, f"+{self.gameBalance} €", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.gameBalaneText.SetForegroundColour(COLOURS.WON)
        self.gameBalaneText.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.gameBalanceSizer.Add(self.gameBalaneText, 100, wx.ALIGN_CENTER_VERTICAL, 0)

        self.gameCountdownSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Cuenta atrás"), wx.HORIZONTAL)
        gameOptionsSizer.Add(self.gameCountdownSizer, 7, wx.ALL | wx.EXPAND, 9)

        self.countDownText = wx.StaticText(self, wx.ID_ANY, f"{self.countdown}", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.countDownText.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.gameCountdownSizer.Add(self.countDownText, 100, wx.ALIGN_CENTER_VERTICAL, 0)

        self.gamePanel = wx.ScrolledWindow(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.gamePanel.SetBackgroundColour(COLOURS.BACKGROUND)
        self.gamePanel.SetScrollRate(10, 10)
        gameSizer.Add(self.gamePanel, 90, wx.EXPAND, 0)

        self.gamePanelSizer = wx.BoxSizer(wx.VERTICAL)


        self.gamePanel.SetSizer(self.gamePanelSizer)

        self.SetSizer(gameSizer)
        gameSizer.Fit(self)
        gameSizer.SetSizeHints(self)

        self.Layout()
        self.Centre()

        self.Bind(wx.EVT_RADIOBUTTON, self.handleClickManualButton, self.manualButton)
        self.Bind(wx.EVT_RADIOBUTTON, self.handleClickAutomaticButton, self.automaticButton)
        self.Bind(wx.EVT_BUTTON, self.handleClickAskButton, self.askButton)
        self.Bind(wx.EVT_BUTTON, self.handleClickDoubleButton, self.doubleButton)
        self.Bind(wx.EVT_BUTTON, self.handleClickCloseButton, self.closeButton)
        self.Bind(wx.EVT_BUTTON, self.handleClickSplitButton, self.splitButton)
        self.Bind(wx.EVT_BUTTON, self.handleClickDeclineButton, self.declineButton)

    def handleClickDeclineButton(self, _):
        for hand in self.player.hands:
            if hand.getState() == HAND_STATES.ACTIVE:
                hand.setState(HAND_STATES.DECLINED)
                hand.updateColor()
                hand.updateText(self.player)
        self.gamePanelSizer.Layout()
        self.croupier.hands[0].setState(HAND_STATES.CLOSED)
        self.croupier.hands[0].updateColor()
        self.croupier.hands[0].updateText(self.croupier)

        self.timer.Stop()
        self.resetTimer("-")

        self.showResults()


    def handleDelayInput(self, _):

        if self.delayInput.GetValue() == "":
            self.delayInput.SetValue(f"{self.delayActions}")

        if not self.delayInput.GetValue().isdigit():
            return
        
        self.delayActions = int(self.delayInput.GetValue())

        if self.croupierTimer.IsRunning():
            self.croupierTimer.Stop()
            self.croupierTimer.Start(self.delayActions)

        if self.automaticTimer.IsRunning():
            self.automaticTimer.Stop()
            self.automaticTimer.Start(self.delayActions)



    def canSplit(self, hand):
        return len(hand.cards) == 2 and hand.cards[0].valor == hand.cards[1].valor and len(self.player.hands) < 4

    def croupierTurn(self, _):

        if self.croupier.hands[0].getValue() < 17:
            winsound.PlaySound(SOUNDS.GIVE_CARD, winsound.SND_ASYNC)
            self.handSelected.giveCard(self.croupier, self.deck, 1, self.selectPanel)


        else:
            if self.croupier.hands[0].getState() != HAND_STATES.PASSED:
                self.croupier.hands[0].setState(HAND_STATES.CLOSED)
                self.croupier.hands[0].updateColor()
                self.croupier.hands[0].updateText(self.croupier)

            self.croupierTimer.Stop()
            self.showResults()

    def automaticAction(self, _):
        handsOpen = list(filter(lambda hand: hand.getState() == HAND_STATES.ACTIVE, self.player.hands))
        self.automaticHandCount = self.automaticHandCount + 1 if self.automaticHandCount < len(handsOpen) - 1 else 0
        
        hand = handsOpen[self.automaticHandCount]
        self.handSelected = hand

        play = self.strategy.jugada(self.croupier.hands[0].cards[0], hand.cards)

        if play == "P":
            self.handleClickAskButton(None)
        elif play == "D":
            self.handleClickDoubleButton(None)
        elif play == "C":
            self.handleClickCloseButton(None)
        elif play == "S":
            self.handleClickSplitButton(None)
            self.automaticAction -= 1
        

    def showResults(self):
        for hand in self.player.hands:
            if hand.getState() == HAND_STATES.PASSED or hand.getState() == HAND_STATES.DECLINED:
                if self.croupier.hands[0].getState() != HAND_STATES.PASSED:
                    self.gameBalance -= int(hand.getBet() * (0.5 if hand.getState() == HAND_STATES.DECLINED else 1))
                    hand.panel.SetBackgroundColour(COLOURS.LOST)
                else:
                    hand.panel.SetBackgroundColour(COLOURS.DRAW)
            
            elif hand.getState() == HAND_STATES.CLOSED:
                if hand.getValue() > self.croupier.hands[0].getValue() or self.croupier.hands[0].getState() == HAND_STATES.PASSED:
                    self.gameBalance += int(hand.getBet() * (1 if not self.blackJack else 1.5))
                    hand.panel.SetBackgroundColour(COLOURS.WON)
                    
                elif hand.getValue() < self.croupier.hands[0].getValue() and self.croupier.hands[0].getState() != HAND_STATES.PASSED:
                    self.gameBalance -= hand.getBet()
                    hand.panel.SetBackgroundColour(COLOURS.LOST)
                elif hand.getValue() == self.croupier.hands[0].getValue():
                    hand.panel.SetBackgroundColour(COLOURS.DRAW)    
            hand.panel.Refresh()
        
        gameBalanceSign = ""
        
        if self.gameBalance >= 0:
            gameBalanceSign = "+" 
            self.gameBalaneText.SetForegroundColour(COLOURS.WON)
        else:
            self.gameBalaneText.SetForegroundColour(COLOURS.LOST)
        
        self.gameBalaneText.SetLabel(f"{gameBalanceSign}{self.gameBalance} €")
        self.gameBalanceSizer.Layout()
        
        self.globalBalance += self.gameBalance
        globalBalanceSign = ""
        
        if self.globalBalance >= 0:
            globalBalanceSign = "+" 
            self.globalBalanceText.SetForegroundColour(COLOURS.WON)
        else:
            self.globalBalanceText.SetForegroundColour(COLOURS.LOST)
            
        self.globalBalanceText.SetLabel(f"{globalBalanceSign}{self.globalBalance} €") 
        self.gameGlobalBalanceSizer.Layout()

        if not self.blackJack:
            if self.gameMode == GAME_MODES.MANUAL:
                self.chooseBetWindow.ShowModal()
            else:
                self.selectedBet = self.strategy.apuesta(2, 10, 50)
            

                self.chooseBetWindow.Show()

                self.selectBetAutomaticTimer.Start(self.delayActions)

    def selectBetAutomatic(self, _):
        self.selectBetAutomaticTimer.Stop()

        self.chooseBetWindow.Hide()
        self.restartGameData()

        if self.blackJack:
            self.isBlackjack()


    def changeToCroupierTurn(self):
        self.playerSelected = self.croupier
        self.handSelected = self.croupier.hands[0]

        self.handSelected.getPanel().SetBackgroundColour(COLOURS.SELECTED)
        self.handSelected.getPanel().Refresh()

        self.askButton.Disable()
        self.doubleButton.Disable()
        self.closeButton.Disable()
        self.splitButton.Disable()
        self.declineButton.Disable()
        
        self.timer.Stop()
        self.resetTimer("-")
        self.automaticTimer.Stop()
        self.gameCountdownSizer.Layout()

        if not self.player.allHandsPassed():
            self.croupierTimer.Start(self.delayActions)
        else:
            self.croupier.hands[0].setState(HAND_STATES.CLOSED)
            self.croupier.hands[0].updateColor()
            self.croupier.hands[0].updateText(self.croupier)
            self.showResults()


    def handleTimer(self, _):
        self.countdown -= 1
        self.countDownText.SetLabel(f"{self.countdown}")
        
        if self.countdown <= 3:
            self.countDownText.SetForegroundColour(COLOURS.LOW_COUNTDOWN)
            

        if self.countdown < 0:
            self.selectRandomAction()
            self.resetTimer()
            if not self.playerSelected.anyHandOpen():
                self.timer.Stop()

        self.gameCountdownSizer.Layout()

    def resetTimer(self, newTime = None):
        self.countdown = MainWindow.DEFAULT_COUNTDOWN if newTime is None else newTime
        self.countDownText.SetLabel(f"{self.countdown}")
        self.countDownText.SetForegroundColour(COLOURS.BLACK)
        self.gameCountdownSizer.Layout()


    def selectRandomAction(self):
        options = ["PEDIR", "DOBLAR", "CERRAR"]
        
        possibleHands = list(filter(lambda hand: hand.getState() == HAND_STATES.ACTIVE, self.playerSelected.hands))

        self.handSelected = possibleHands[random.randint(0, len(possibleHands) - 1)]
        
        if self.canSplit(self.handSelected):
            options.append("SEPARAR")

        randomAction = random.choice(options)

        if randomAction == "PEDIR":
            self.handleClickAskButton(None)
        elif randomAction == "DOBLAR":
            self.handleClickDoubleButton(None)
        elif randomAction == "CERRAR":
            self.handleClickCloseButton(None)
        elif randomAction == "SEPARAR":
            self.handleClickSplitButton(None)

    def handleClickManualButton(self, _):
        self.gameMode = GAME_MODES.MANUAL

        if not self.playerSelected.getIsCroupier():
            self.resetTimer()
            self.removeHandSelected()
            self.automaticTimer.Stop()
            self.timer.Start(1000)


    def handleClickAutomaticButton(self, _):
        self.gameMode = GAME_MODES.AUTOMATIC
        if not self.playerSelected.getIsCroupier():
            self.removeHandSelected()
            self.automaticTimer.Start(self.delayActions)
            self.timer.Stop()

    # BOTÓN DE PEDIR CARTA
    def handleClickAskButton(self, _):
        winsound.PlaySound(SOUNDS.GIVE_CARD, winsound.SND_ASYNC)

        self.handSelected.giveCard(self.playerSelected, self.deck, 1, self.selectPanel)
        
        if self.canSplit(self.handSelected):
            self.splitButton.Enable()

        if self.handSelected.getState() == HAND_STATES.PASSED:
            self.removeHandSelected()

        self.resetTimer()
        if not self.playerSelected.anyHandOpen():
            self.changeToCroupierTurn()


    # BOTÓN DE DOBLAR APUESTA
    def handleClickDoubleButton(self, _):
        winsound.PlaySound(SOUNDS.GIVE_CARD, winsound.SND_ASYNC)

        self.handSelected.setBet(self.handSelected.getBet() * 2)
        self.handSelected.setState(HAND_STATES.CLOSED)

        self.handSelected.giveCard(self.playerSelected, self.deck, 1, self.selectPanel)

        self.removeHandSelected()

        self.resetTimer()
        
        if not self.playerSelected.anyHandOpen() and not self.playerSelected.getIsCroupier():
            self.changeToCroupierTurn()

    # BOTÓN DE CERRAR MANO
    def handleClickCloseButton(self, _):
        self.handSelected.setState(HAND_STATES.CLOSED)

        self.handSelected.updateColor()
        self.handSelected.updateText(self.playerSelected)

        self.removeHandSelected()

        if not self.playerSelected.getIsCroupier():
            self.resetTimer()
            if not self.playerSelected.anyHandOpen():
                self.changeToCroupierTurn()

    # BOTÓN DE SEPARAR MANO
    def handleClickSplitButton(self, _):

        self.handSelected.getPanel().SetBackgroundColour(COLOURS.NULL)
        self.handSelected.getPanel().Refresh()

        self.addHandToGamePanel(self.playerSelected, bet = self.handSelected.getBet(), cards = [self.handSelected.cards.pop()])

        self.handSelected.renderHandPanel(self.playerSelected, self.selectPanel)
        self.playerSelected.hands[-1].updateText(self.playerSelected)

        self.removeHandSelected()

        if not self.playerSelected.getIsCroupier():
            self.resetTimer()
            if not self.playerSelected.anyHandOpen():
                self.changeToCroupierTurn()

    def removeHandSelected(self):
        self.askButton.Disable()
        self.doubleButton.Disable()
        self.closeButton.Disable()
        self.splitButton.Disable()
        self.handSelected = None

    def addHandToGamePanel(self, player, bet = 0, cards = None):

        handPanel = wx.Panel(self.gamePanel, len(player.hands), style=wx.TAB_TRAVERSAL, size=wx.Size(0, 120))
        newSizer = wx.BoxSizer(wx.HORIZONTAL)
        handPanel.SetSizer(newSizer)

        self.gamePanelSizer.Add(handPanel, 0, wx.EXPAND, 0)

        newSizerText = wx.StaticText(handPanel, wx.ID_ANY, "", style=wx.ALIGN_CENTER_HORIZONTAL)
        newSizerText.SetMinSize((145, 200))
        newSizerText.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        newSizerText.SetForegroundColour(COLOURS.BLACK)

        newSizerText.Bind(wx.EVT_LEFT_DOWN, lambda event: self.selectPanel(event, player, newHand))
        newSizer.Add(newSizerText, 0, wx.ALL, 10)

        newHand = Hand(handPanel, newSizer, newSizerText, cards = cards, bet = bet)

        if cards is not None:
            for card in cards:

                cardBitmap = card.getCardBitmap()
                staticBitMap = wx.StaticBitmap(handPanel, wx.ID_ANY, cardBitmap)
                staticBitMap.Bind(wx.EVT_LEFT_DOWN, lambda event: self.selectPanel(event, player, newHand))

                newSizer.Add(staticBitMap, 0, 0, 0)

            newHand.updateText(player)
            
        handPanel.Bind(wx.EVT_LEFT_DOWN, lambda event: self.selectPanel(event, player, newHand))

        player.addHand(newHand)

        self.gamePanel.Layout()
        

    
    def selectPanel(self, _, player, hand):
        if self.gameMode == GAME_MODES.AUTOMATIC:
            return

        if player.isCroupier:
            return

        if hand.getState() == HAND_STATES.PASSED or hand.getState() == HAND_STATES.CLOSED:
            return

        self.askButton.Enable()
        self.doubleButton.Enable()
        self.closeButton.Enable()

        if self.canSplit(hand):
            self.splitButton.Enable()
        else:
            self.splitButton.Disable()

        if self.handSelected:
            self.handSelected.getPanel().SetBackgroundColour(COLOURS.NULL)
            self.handSelected.getPanel().Refresh()

        hand.getPanel().SetBackgroundColour(COLOURS.SELECTED)
        hand.getPanel().Refresh()

        self.handSelected = hand

    def isBlackjack(self):

        winsound.PlaySound(SOUNDS.CHEERS, winsound.SND_ASYNC)

        if self.gameMode == GAME_MODES.AUTOMATIC:
            self.automaticTimer.Stop()

        blackJackPopUp = BlackJackPopUp(self, wx.ID_ANY, "")

        self.player.hands[0].setState(HAND_STATES.CLOSED)
        self.player.hands[0].updateColor()
        self.player.hands[0].updateText(self.player)

        self.showResults()

        self.timer.Stop()

        if self.gameMode == GAME_MODES.MANUAL:
            blackJackPopUp.ShowModal()
        else:
            
            self.selectedBet = self.strategy.apuesta(2, 10, 50)
            blackJackPopUp.Show()
            blackJackPopUp.handlePressOk(None)
            self.selectBetAutomaticTimer.Start(self.delayActions)


    def getSelectedBet(self):
        return self.selectedBet
    
    def startGame(self):

        winsound.PlaySound(SOUNDS.START_GAME, winsound.SND_ASYNC)

        self.addHandToGamePanel(self.croupier, cards = [self.deck.reparte()])

        self.addHandToGamePanel(self.player, bet = self.selectedBet, cards = [self.deck.reparte(), self.deck.reparte(), self.deck.reparte()])


        if self.player.hands[0].getValue() == 21:
            self.blackJack = True

        elif self.croupier.hands[0].cards[0].valor == 1:
            self.declineButton.Enable()


    def restartGameData(self):
        self.player.hands = []
        self.croupier.hands = []
        self.blackJack = False

        self.gamePanel.DestroyChildren()
        self.gamePanelSizer.Clear()

        self.gamePanelSizer.Layout()
        self.gamePanel.Refresh()
        
        self.Show()
        self.CenterOnScreen()

        self.resetTimer()

        self.gameCounter += 1
        self.gameBalance = 0

        self.gameCounterText.SetLabel(f"{self.gameCounter}")
        self.gameCounterSizer.Layout()

        self.gameBalaneText.SetLabel(f"+{self.gameBalance} €")
        self.gameBalaneText.SetForegroundColour(COLOURS.WON)
        self.gameBalanceSizer.Layout()

        self.handSelected = None
        self.playerSelected = self.player

        self.startGame()

        if self.gameMode == GAME_MODES.AUTOMATIC:
            self.automaticHandCount = 0
            self.automaticTimer.Start(self.delayActions)
        else:
            self.timer.Start(1000)

        self.gamePanel.Layout()

# endregion


# region ChooseBet
class ChooseBet(wx.Dialog):
    def __init__(self, parent, id):

        wx.Dialog.__init__(self, parent, id, "")

        self.SetSize((220, 250))
        self.SetTitle("Nueva partida")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        chooseBetSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Elija su apuesta"), wx.VERTICAL)
        sizer_1.Add(chooseBetSizer, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.TOP, 17)

        self.lowBet = wx.RadioButton(self, 2, u"2€ ")
        chooseBetSizer.Add(self.lowBet, 33, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.mediumBet = wx.RadioButton(self, 10, u"10€")
        chooseBetSizer.Add(self.mediumBet, 33, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.highBet = wx.RadioButton(self, 50, u"50€")
        chooseBetSizer.Add(self.highBet, 33, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        if self.GetParent().selectedBet == 2:
            self.lowBet.SetValue(1)
        elif self.GetParent().selectedBet == 10:
            self.mediumBet.SetValue(1)
        elif self.GetParent().selectedBet == 50:
            self.highBet.SetValue(1)

        label_1 = wx.StaticText(self, wx.ID_ANY, u"¿Quiere seguir jugando?")
        sizer_1.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 2)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        self.acceptBet = wx.Button(self, wx.ID_YES, "")
        sizer_2.AddButton(self.acceptBet)

        self.denyBet = wx.Button(self, wx.ID_NO, "")
        sizer_2.AddButton(self.denyBet)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.Layout()
        self.Centre()

        self.Bind(wx.EVT_RADIOBUTTON, self.setSelectedBet, self.lowBet)
        self.Bind(wx.EVT_RADIOBUTTON, self.setSelectedBet, self.mediumBet)
        self.Bind(wx.EVT_RADIOBUTTON, self.setSelectedBet, self.highBet)
        self.Bind(wx.EVT_BUTTON, self.handleYesButton, self.acceptBet)
        self.Bind(wx.EVT_BUTTON, self.handleNoButton, self.denyBet)


    def setSelectedBet(self, event):
        self.GetParent().selectedBet = event.GetId()

    def handleYesButton(self, _):
        if self.GetParent().gameMode == GAME_MODES.AUTOMATIC:
            return
 
        self.EndModal(0)
        self.GetParent().restartGameData()

        if self.GetParent().blackJack:
            self.GetParent().isBlackjack()


    def handleNoButton(self, _):
        if self.GetParent().gameMode == GAME_MODES.AUTOMATIC:
            return

        self.EndModal(0)
        self.GetParent().Close()

# endregion

# region BlackJackPopUp
class BlackJackPopUp(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: BlackJackPopUp.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((550, 400))
        self.SetTitle("BLACKJACK")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("./utils/imgs/blackjack.jpeg", wx.BITMAP_TYPE_ANY))
        sizer_1.Add(bitmap_1, 1, 0, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALL, 8)

        label_1 = wx.StaticText(self, wx.ID_ANY, f"¡Enhorabuena has hecho blackjack has ganado {int(self.GetParent().getSelectedBet() * 1.5)}€!", style=wx.ALIGN_CENTER_HORIZONTAL)
        label_1.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_2.Add(label_1, 90, wx.ALIGN_CENTER_VERTICAL, 0)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        self.button_OK.Bind(wx.EVT_BUTTON, self.handlePressOk)
        sizer_2.AddButton(self.button_OK)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.SetAffirmativeId(self.button_OK.GetId())

        self.Layout()
        self.Centre()

    def handlePressOk(self, event):


        if self.GetParent().gameMode == GAME_MODES.AUTOMATIC:
            self.GetParent().selectedBet = self.GetParent().strategy.apuesta(2, 10, 50)


        self.GetParent().chooseBetWindow = ChooseBet(self.GetParent(), wx.ID_ANY)


        if self.GetParent().gameMode == GAME_MODES.MANUAL:
            self.EndModal(event.GetId())
            self.GetParent().chooseBetWindow.ShowModal()
        else:
            self.Close()
            self.GetParent().chooseBetWindow.Show()

# endregion

# region Game
class Game(wx.App):
    DECKS_NUM = 2

    def OnInit(self):
        self.player = Player()
        self.croupier = Player(isCroupier = True)
        self.strategy = Estrategia(Game.DECKS_NUM)
        self.deck = Mazo(Card, self.strategy)

        self.mainWindow = MainWindow(None, wx.ID_ANY, "", self.croupier, self.player, self.deck, self.strategy)
        self.chooseBetWindow = ChooseBet(self.mainWindow, wx.ID_ANY)

        self.mainWindow.chooseBetWindow = self.chooseBetWindow

        self.chooseBetWindow.ShowModal()

        return True
    
# endregion

if __name__ == "__main__":

    GUIJack = Game(0)
    GUIJack.MainLoop()
