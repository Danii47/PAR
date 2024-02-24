# Programa en Python que solicite la edad de una persona hasta que sea mayor de edad
# Quiero saber cuantos números menores de edad se han introducido

age = int(input("Introduce tu edad: "))
ageLess18 = 0
agesLess18 = []
ageLess0 = 0

while age < 18:
  age = int(input("Introduce tu edad: "))

  if (age < 0):
    ageLess0 += 1
  else:
    ageLess18 += 1
    agesLess18.append(age)



print("El usuario tiene ", age, " años, es mayor de edad. Se ha introducido ", ageLess18, " edades menores de 18 años.")
for i in agesLess18:
  print(i, end=" ")
