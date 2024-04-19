import wx

class MiVentana(wx.Frame):
  def __init__(self):
    super(MiVentana, self).__init__(None, title='Vent. pulsador', size=(300, 300))
    self.InitUI()

    return None
  
  def InitUI(self):
    panel = wx.Panel(self)
    self.button = wx.Button(panel, label="Pulsa", pos=(100, 75), size=(100, 100))
    self.exitButton = wx.Button(panel, label="Salir", pos=(100, 200), size=(100, 100))
    self.button.Bind(wx.EVT_BUTTON, self.onClick)
    self.exitButton.Bind(wx.EVT_BUTTON, self.onExit)
    self.count = 0
    return None
  
  def onClick(self, event):
    self.count += 1
    self.button.SetLabel(str(self.count))
    return None
  
  def onExit(self, event):
    self.Close()
    return None
  
  
def main():
  app = wx.App()
  ventana = MiVentana()
  ventana.Show()
  app.MainLoop()
  return None
if __name__ == '__main__':
  main()