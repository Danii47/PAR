
# ? CONDICIONALES
# * if, elif, else

# ? if
# * Si se cumple la condición, se ejecuta el bloque de código

# ? elif (else if)
# * Si no se cumple la condición del if, se evalua la condición del elif

# ? else
# * Si no se cumple la condición del if o del elif, se ejecuta el bloque de código del else

# ? Escribir un programa que determine si un número ingresado por el usuario es positivo,
# ? negativo o cero. Si es positivo, mostrará si es par o impar

numero = int(input("Dime un número: "))

if numero > 0:
  print("El número es positivo")
  if numero % 2 == 0:
    print("El número es par")
  else:
    print("El número es impar")

elif numero < 0:
  print("El número es negativo")
else:
  print("El número es 0")