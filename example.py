def hash(x):
    seed = 23;
    diccionario = "adefijnoprsuv";
    for i in x :
        index = diccionario.index(i)
        seed = (seed * 19 + index )
    return seed;

def unhash(target):
    diccionario = "adefijnoprsuv"
    letras = []

    for _ in range(10):
        index = target % 19
        letras.append(diccionario[index])
        target = target // 19

    # Al invertir el orden porque fuimos de atrás hacia adelante:
    print("".join(reversed(letras)))  # Resultado: "perseverar"
    
    
    
if __name__ == "__main__":
    target = 143638514475224
    unhash(target)
    posibles = ["perseverar"]
    for word in posibles:
        result = hash(word)
        print(f"{word} {result} {result == 143638514475224}")
        print(f"{word} {result - 143638514475224}")    
    