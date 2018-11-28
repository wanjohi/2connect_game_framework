import datetime
import os
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
        :return: -1 if error
        '''

        # Prepare data for subprocess call
        current_player = self.players[self.whos_turn]
        current_board = ','.join(self.board)
        players_color = 'b' if self.whos_turn is 0 else 'r'

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

        # Set the next players turn
        self.whos_turn = (self.whos_turn + 1) % 2

        return True

    def play_players_move(self):

        # Get the players move
        players_move = self.turn_results.stdout.splitlines()[-1]
        players_column = int(players_move.split(",")[1]) - 1 # make it an array index
        players_color = players_move.split(",")[0]

        # Make sure the move is within the board limits
        if players_column > self.board_columns:
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

        print(self.board)

def main():
    test_framework = Framework("tester_ai.py", "tester_ai.py",os.getcwd())
    test_framework.run_next_turn()
    test_framework.play_players_move()


if __name__ == "__main__":
    main()