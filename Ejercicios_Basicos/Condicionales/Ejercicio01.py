
# ? CONDICIONALES
# * if, elif, else

# ? if
# * Si se cumple la condición, se ejecuta el bloque de código

# ? elif (else if)
# * Si no se cumple la condición del if, se evalua la condición del elif

# ? else
# * Si no se cumple la condición del if o del elif, se ejecuta el bloque de código del else


# ? Escribir un programa que pregunte al usuario su edad y muestre por pantalla si es mayor de edad o no.

edad = int(input("Dime tu edad: "))

if edad >= 18:
  print("Eres mayor de edad")
elif 0 <= edad < 18:
  print("Eres menor de edad")
else:
  print("La edad introducida no es válida")