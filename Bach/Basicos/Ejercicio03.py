
# ? TIPOS DE DATOS EN PYTHON
# * String - str (Cadena de texto) -> "Hola mundo!", "20", "3.14159"
# * Integer - int (Entero) -> 20
# * Float - float (Decimal) -> 3.14159
# * Boolean - bool (Booleano) -> True, False
# * List - list (Lista) -> [10, "Hola mundo!", 20.3, False]

# ? DEFINIR VARIABLES
# * nombre = "Juan" -> Variable de tipo String
# * edad = 20 -> Variable de tipo Integer
# * altura = 1.75 -> Variable de tipo Float
# * es_estudiante = True -> Variable de tipo Boolean
# * lista = [10, "Hola mundo!", 20.3, False] -> Variable de tipo List

# ? FUNCIONES PREDEFINIDAS DE PYTHON
# * print(arg1) -> Imprimir en consola o terminal | arg1: Mensaje a mostrar
# * input(arg1) -> Capturar datos del usuario por consola o terminal hasta que el usuario presione el Enter | arg1: Mensaje a mostrar al usuario
# * int(arg1) -> Convertir un valor a entero | arg1: Valor a convertir (debe ser un número en formato de texto)
# * float(arg1) -> Convertir un valor a decimal | arg1: Valor a convertir (debe ser un número en formato de texto)

# ? OPERADORES MATEMÁTICOS
# * Suma -> + (en cadenas de texto es concatenación)
# * Resta -> -
# * Multiplicación -> *
# * División -> /
# * Módulo (Resto) -> %
# * Potencia -> **
# * División entera -> //

# ? Pies y pulgadas a cm. Escriba un programa que pida una distancia en pies
# ? y pulgadas y que escriba esa distancia en centímetros.
# ? Un pie son doce pulgadas y una pulgada son 2,54 cm.

distanciaEnPies = float(input("Dime la distancia en pies: "))
distanciaEnPulgadas = float(input("Dime la distancia en pulgadas: "))

piesEnCentimetros = distanciaEnPies * 12 * 2.54
pulgadasEnCentimetros = distanciaEnPulgadas * 2.54

print(f"\n{distanciaEnPies} pies son {piesEnCentimetros}cm\n{distanciaEnPulgadas} pulgadas son {pulgadasEnCentimetros}cm\n")