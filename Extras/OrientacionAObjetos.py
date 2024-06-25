# EJERCICIO CLASES Y OBJETOS

# Haz una clase Concesionario que tenga una lista de coches que contenga elementos de la clase Coche.
# El constructor de la clase Concesionario debe recibir la lista de coches, el nombre del concesionario y la dirección.
# La clase Concesionario debe tener de atributos la lista de coches, el nombre del concesionario, la dirección y el coche más barato
# La clase Concesionario debe tener un método que devuelva el coche más caro y otro que devuelva el coche más barato.

# El constructor de la clase Coche debe recibir la marca, el modelo y el precio.
# La clase Coche debe tener la marca, el modelo y el precio.
# La clase Coche debe tener un método que devuelva el precio del coche.

# Crea una lista de coches y un concesionario con esa lista de coches, además haz uso de los métodos de la clase Concesionario para mostrar el coche más caro y el coche más barato.

class Coche():

  def __init__(self, marca: str , modelo: str, precio: int):

    self.marca = marca
    self.modelo = modelo
    self.precio = precio

  def getMarca(self) -> str:
    return self.marca
  
  def getModelo(self) -> str:
    return self.modelo
  
  def getPrecio(self) -> int:
    return self.precio
  
  def mostrarCoche(self) -> None:
    print((f"COCHE {self.modelo.upper()}\n\t* Marca: {self.marca}\n\t* Modelo: {self.modelo}\n\t* Precio: {self.precio}\n"))
  


class Concesionario():

  def __init__(self, coches: list[Coche], nombre: str, direccion: str):
    self.coches = coches
    self.nobre = nombre
    self.direccion = direccion
    self.cocheMasBarato = self.buscarCocheMasBarato()

  def getCocheMasBarato(self) -> Coche:
    return self.cocheMasBarato

  def buscarCocheMasBarato(self) -> Coche:
    precioBarato: int = self.coches[0].getPrecio()

    cocheBarato: Coche = self.coches[0]
    
    for coche in self.coches:
      
      if coche.getPrecio() < precioBarato:
        cocheBarato = coche
        precioBarato = coche.getPrecio()
      
    return cocheBarato
  
  def getPrecioMasCaro(self) -> int:

    precioCaro: int = 0

    for coche in self.coches:


      if coche.getPrecio() > precioCaro:
        precioCaro = coche.getPrecio()

    return precioCaro


def main() -> None:
  arrayCoches: list[Coche] = []

  for i in range(10):
    coche = Coche (marca = "polla", modelo = f"enorme{i}", precio = (i+1)*100)
    arrayCoches.append(coche)

  concesionario = Concesionario(coches = arrayCoches, nombre = "pollalandia", direccion = "calle de las pollas")

  for coche in concesionario.coches:
    coche.mostrarCoche()

  print(f"\nEl coche mas barato es: {concesionario.getCocheMasBarato().getModelo().upper()}")
  print(f"\nEl precio del coche más caro es: {concesionario.getPrecioMasCaro()}\n")
  # Muéstrame la marca, modelo y precio de TODOS los coches dentro de un Concesionario
  # Después, muestrame el coche más barato del Concesionario y el más caro (habiendo creado el concesionario con los 10 coches)

if __name__ == "__main__":
  main()