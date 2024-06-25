main :: IO ()
main = do
  putStrLn $ show $ suma 30 12
  putStrLn $ show $ resta 30 12
  putStrLn $ show $ division 30 12
  putStrLn $ show $ mult 30 12
  putStrLn $ show $ elevar 9 0.5
  putStrLn $ show $ factorial 5
  putStrLn $ show $ factorialConGuardas 5
  putStrLn $ show $ orPropio False True
  putStrLn $ show $ andPropio False True
  recorrerCadena "hola"
  putStrLn $ show $ obtenerDiscriminante 2 5 2
  putStrLn $ show $ obtenerSoluciones2oGrado 2 5 2
  putStrLn $ show $ comprobarNumeros "60140a3658"
  putStrLn $ show $ comprobarNumerosConFunciones "601403658"
  putStrLn $ "La media armonica de 1, 2, 3, 4, 5 es: " ++ (show $ obtenerMediaArmonica [1, 2, 3, 4, 5])
  putStrLn $ show $ sumarUno [1, 2, 3]
  putStrLn $ show $ menorQueTres [1, 2, 3]
  putStrLn $ show $ quitarUltimo [1, 2, 3]
  

suma :: Double -> Double -> Double
suma x y = x + y

resta :: Double -> Double -> Double
resta x y = x - y

division :: Double -> Double -> Double
division x y = x / y

mult :: Double -> Double -> Double
mult x y = x * y

elevar :: Double -> Double -> Double
elevar x y = x ** y

-- `div` y `mod` -> 2 enteros y devuelven 1 entero
-- / 2 double y devuelven 1 double

-- Ternaria: if condicion then valor1 else valor2

factorial :: Int -> Int
factorial 0 = 1
factorial x = if x == 1 then 1 else x * factorial (x - 1)

-- Guardas: | CONDICION = VALOR_RETORNO
factorialConGuardas :: Int -> Int
factorialConGuardas x
  | x < 1 = 1
  | otherwise = x * factorialConGuardas (x - 1)

orPropio :: Bool -> Bool -> Bool
orPropio False False = False
orPropio _ _ = True

andPropio :: Bool -> Bool -> Bool
andPropio True True = True
andPropio _ _ = False


recorrerCadena :: String -> IO () -- Si no devuelve nada ponemos IO ()
recorrerCadena [] = return () -- Cuando la cadena llega a estar vacia, finaliza
recorrerCadena (primeValor:resto) = do
  putStrLn [primeValor]
  recorrerCadena resto
  
  
obtenerDiscriminante :: Double -> Double -> Double -> Double
obtenerDiscriminante a b c = 
    let -- Como el where
      bCuadrado = b ** 2
      d = bCuadrado - 4 * a * c
    in d


obtenerSoluciones2oGrado :: Double -> Double -> Double -> (Double, Double)
obtenerSoluciones2oGrado a b c = if raiz /= -1 then (solucion1, solucion2) else error "Error, el discriminante es menor que 0"
  where
    bCuadrado = b ** 2
    discrimante = bCuadrado - 4 * a * c
    raiz = if discrimante >= 0 then sqrt discrimante else -1
    solucion1 = (b + raiz) / (2 * a)
    solucion2 = (b - raiz) / (2 * a)


{-
Crear un función que reciba una cadena de texto y devuelva un valor booleano indicando si todos sus
caracteres son dígitos (Para todo carácter c, c >= ‘0’ && c <= ‘9’). Resuélvalo primero usando
recursividad y luego usando map y/o filter y/o folder.
-}

comprobarNumeros :: String -> Bool
comprobarNumeros [] = True
comprobarNumeros (primerCaracter:restoCadena) = 
  if primerCaracter >= '0' && primerCaracter <= '9'
  then comprobarNumeros restoCadena
  else False

comprobarNumerosConFunciones :: String -> Bool
comprobarNumerosConFunciones entrada = if length array == 0 then True else False -- Tambien (null array) devuelve True si el array está vacio, False en caso contrario
  where
    array = filter (\valor -> valor < '0' || valor > '9') entrada

sumPropio :: [Double] -> Double
sumPropio [] = 0
sumPropio (primerValor:restoArray) = primerValor + (sumPropio restoArray)


obtenerMediaArmonica :: [Double] -> Double
obtenerMediaArmonica datos = mediaArmonica
  where
    inversaDeDatos = map (1/) datos -- Se le aplica la funcion 1/ a todos los elementos de array
    sumaDeInversas = sumPropio inversaDeDatos
    mediaArmonica = fromIntegral (length datos) / sumaDeInversas -- fromIntegral convierte de entero a numero real

sumarUno :: [Double] -> [Double]
sumarUno datos = map (+1) datos

menorQueTres :: [Double] -> ([Bool], [Double])
menorQueTres datos = (map (<3) datos, filter (<3) datos)


quitarUltimo :: [a] -> [a]
quitarUltimo [x] = []
quitarUltimo (x:xs) = x : quitarUltimo xs



