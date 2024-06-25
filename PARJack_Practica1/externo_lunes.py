""" Paradigmas de Programación, curso 2023/24
    Código externo para la primera práctica
    Versión de las defensas del lunes
    (c) César Vaca
"""


class CartaBase(object):
    def __init__(self, ind):
        self.ind = ind

    @property
    def valor(self):
        return min(10, self.ind % 13 + 1)


class Estrategia(object):

    def __init__(self, num_barajas):
        self.cuenta = 0
        self.flag = False

    def cuenta_carta(self, carta):
        self.cuenta += 1

    def apuesta(self, apu_lo, apu_med, apu_hi):
        if self.cuenta % 3 == 0:
            return apu_hi
        elif self.cuenta % 3 == 1:
            return apu_med
        else:
            return apu_lo

    def jugada(self, croupier, jugador):
        vj = sum(c.valor for c in jugador)
        eqs = len(set(j.valor for j in jugador)) == 1
        if self.flag and len(jugador) > 1 and eqs:
            self.flag = False
            return 'S'
        if len(jugador) > 4 and eqs:
            self.flag = True
            return 'S'
        if vj == 11:
            return 'D'
        return 'P' if vj < 19 else 'C'


class Mazo(object):
    NUM_BARAJAS = 2

    def __init__(self, clase_carta, estrategia):
        self.clase = clase_carta
        self.estrategia = estrategia
        self.cartas = []

    def reparte(self):
        if len(self.cartas) == 0:
            # Se ha acabado el mazo: crear uno nuevo
            inds = [0,37,28,24,10,15,41,28,15,2,11]
            self.cartas = [self.clase(i) for i in inds]
        c = self.cartas.pop()
        if self.estrategia is not None:
            # Se informa a la estrategia de la carta que se reparte
            self.estrategia.cuenta_carta(c)
        return c