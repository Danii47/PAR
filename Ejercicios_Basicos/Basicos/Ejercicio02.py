
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

# ? TIPOS DE FORMA DE ESCRIBIR
# * Pascal Case -> MiPalabra
# * Camel Case -> miPalabra
# * Snake Case -> mi_palabra

# ? Índice de Masa Corporal. Escriba un programa que pida el peso (en kilogramos) y la altura (en metros)
# ? de una persona y que calcule su índice de masa corporal (imc).
# ? IMC se calcula con la fórmula imc = peso / altura 2

peso = float(input("Dime tu peso: "))
altura = float(input("Dime tu altura: "))

imc = peso / altura ** 2

print(f"Tu indice de masa corporal es: {imc}")