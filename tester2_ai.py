import random
def main():
    print("multi\n"
          "line\n"
          "nonesense")

    column = random.randint(1,10)

    random_color = random.randint(1, 2)

    if random_color == 1:
        color = "r"
    else:
        color = "g"

    print(color + "," + str(column))

main()