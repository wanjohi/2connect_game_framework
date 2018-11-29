import datetime
import os
import re
from subprocess import run

class Framework:

    def __init__(self, player_1_exec, player_2_exec, working_directory):
        '''
        Initialization method. It creates a new board, receives the execution code for the two players.
        :return: None
        '''

        # Create a board of 10 x 8
        self.board_columns = 10
        self.board_rows = 8

        self.board = ['.'] * self.board_columns * self.board_rows

        # Set up the players
        self.players = [player_1_exec, player_2_exec]
        self.working_directory = working_directory

        # Set up next turn where 0 is player 1 and 1 is player 2
        self.whos_turn = 0

        # Create a log file for the current game
        now = datetime.datetime.now()
        self.log_file_name = now.strftime("%Y-%m-%d-%H-%M") + "-"+ player_1_exec + "-" + player_2_exec +  ".log"

        self.log_file = open(self.log_file_name, "a")



    def run_next_turn(self):
        '''
        Executes the current players executable with the board game and returns the results to the judge
        :return: False if error
        '''

        # Prepare data for subprocess call
        current_player = self.players[self.whos_turn]
        current_board = ','.join(self.board)
        players_color = 'b' if self.whos_turn is 0 else 'r'

        # Save color for playing the move
        self.prev_players_color = players_color

        # check file type
        type = current_player.split(".")[-1]

        # Handle a python script
        if type == "py":
            command = "python " + current_player + " " + players_color + " " + current_board
        # Handle a binary script
        else:
            command = current_player + " " + players_color + " " + current_board

        # Execute the ai
        self.turn_results = run(command, cwd=self.working_directory, timeout=5, capture_output=True, shell=True,
                                text=True)

        # Write output to log file
        self.log_file.write(self.turn_results.stdout)

        # Player looses if the return code is not 0
        if self.turn_results.returncode is not 0:
            return False

        # Player looses if they return nothing
        if self.turn_results.stdout is '':
            return False

        # Set the next players turn
        self.whos_turn = (self.whos_turn + 1) % 2

        return True


    def play_players_move(self):
        '''
        Adds the player's move to the board, making sure we stick within the board size
        :return: False if error
        '''

        # Get the players move
        print(self.turn_results.stdout)
        players_move = self.turn_results.stdout.splitlines()[-1]
        players_column = int(players_move.split(",")[1]) - 1 # make it an array index
        players_color = players_move.split(",")[0]

        # Make sure the move is within the board limits
        if players_column > self.board_columns:
            return False

        # Make sure the move is with the right color
        if players_color != self.prev_players_color:
            return False

        # Play the move, find an empty spot and play the players move
        for row in range(self.board_rows,0,-1):
            index = (row * self.board_columns) - self.board_columns
            print(index)
            if self.board[players_column + index] is ".":
                self.board[players_column + index] = players_color
                break
            # Check if player is playing on a completed column
            elif row is 0 and self.board[players_column * row] is not ".":
                return False

    def judge_board(self):
        '''
        Go through the board and see if there are any winners
        :return:
        '''
        players_regex = re.compile(r"(bbgg|ggbb|bgbg|gbgb|bggb|gbbg|rrgg|ggrr|rgrg|grgr|rggr|grrg)")

        for index, cell in enumerate(self.board):
            if self.board[index] is not ".":
                # Check backwards
                if index % 10 > 2:
                    cells = ''.join(self.board[index-3:index+1])
                    print(cells)
                    if players_regex.search(cells):
                        # found a winner!
                        return cells

                # Check upwards
                if index - 30 > 0:
                    cells = ''.join(self.board[index-30:index+1:10])
                    print(cells)
                    if players_regex.search(cells):
                        # found a winner!
                        return cells

                # Check forward diagonal
                if index > 29 and index % 10 < self.board_columns - 3:
                    cells = self.board[index-27] + self.board[index-18] + self.board[index-9] + self.board[index]
                    print(cells)
                    if players_regex.search(cells):
                        # found a winner!
                        return cells

                # Check backward diagonal
                if index > 29 and index % 10 > 3:
                    cells = self.board[index - 27] + self.board[index - 18] + self.board[index - 9] + \
                            self.board[index]
                    print(cells)
                    if players_regex.search(cells):
                        # found a winner!
                        return cells


        # Check if board has been filled
        if '.' not in self.board:
            return False

    def print_board(self):
        '''
        prints out the board
        :return:
        '''
        print("| ", end="")
        for _ in range(self.board_columns):
            print("- ",end="")
        for index, cell in enumerate(self.board):
            if index % 10 == 0:
                print("| ")
                print("| ",end="")
            print(self.board[index],"",end="")
        print("| ")
        print("| ", end="")
        for _ in range(self.board_columns):
            print("- ",end="")
        print("|")



def main():
    test_framework = Framework("tester_ai.py", "tester_ai.py",os.getcwd())
    test_framework.run_next_turn()
    test_framework.play_players_move()
    test_framework.print_board()
    print(test_framework.whos_turn)
    test_framework.judge_board()


if __name__ == "__main__":
    main()