asignaturas = ["Matemáticas", "Física", "Química", "Historia", "Lengua"]

for asignatura in asignaturas:
  print("Yo estudio " + asignatura)

print()

notas = []

for asignatura in asignaturas:
  nota = float(input(f"¿Qué nota has sacado en {asignatura}? "))
  notas.append(nota)

print()

asignaturasAprobadas = []

for i in range(0, len(asignaturas)):
  print(f"En {asignaturas[i]} has sacado: {notas[i]}")
  if notas[i] >= 5:
    asignaturasAprobadas.append(asignaturas[i])

print()

for asignaturaAprobada in asignaturasAprobadas:
  asignaturas.remove(asignaturaAprobada)


for asignatura in asignaturas:
  print(f"Debes repetir el examen de {asignatura}")
