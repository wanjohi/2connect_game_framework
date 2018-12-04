import random
import sys

def main():

    if len(sys.argv) != 3:
        print("Wrong Usage!")
        print("Correct Usage: python main.py color board")
        return 0

    player_color = sys.argv[1]
    board = (sys.argv[2]).split(',')

    column = random.randint(1, 10)
    while(board[column-1] != '.'):
        column = random.randint(1, 10)

    random_color = random.randint(1,2)

    if random_color == 1:
        color = player_color
    else:
        color = "g"

    print(color +"," + str(column))

main()