DNI_LETTERS = {
  0: 'T',
  1: 'R',
  2: 'W',
  3: 'A',
  4: 'G',
  5: 'M',
  6: 'Y',
  7: 'F',
  8: 'P',
  9: 'D',
  10: 'X',
  11: 'B',
  12: 'N',
  13: 'J',
  14: 'Z',
  15: 'S',
  16: 'Q',
  17: 'V',
  18: 'H',
  19: 'L',
  20: 'C',
  21: 'K',
  22: 'E'
}

def dni_posibilities(DNI):
  DNIInterrogantsPositions = []
  for i, letter in enumerate(DNI):
    if letter == "?":
      DNIInterrogantsPositions.append(i)
      DNI = DNI[:i] + "0" + DNI[i + 1:]
  print(DNI)
  counter = 0
  for i in DNIInterrogantsPositions:
    for j in range(1, 10):
      if DNI_LETTERS[int(DNI[:8]) % 23] == DNI[8]:
        counter += 1
      DNI = DNI[:i] + str(j) + DNI[i + 1:]

dni_posibilities("12?74?27D")

