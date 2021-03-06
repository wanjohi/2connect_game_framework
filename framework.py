import datetime
import os
import re
from subprocess import run, TimeoutExpired

class Framework:

    def __init__(self, player_1, player_2, working_directory):
        '''
        Initialization method. It creates a new board, receives the execution code for the two players.
        :return: None
        '''

        # Create a board of 10 x 8
        self.board_columns = 10
        self.board_rows = 8

        self.board = ['.'] * self.board_columns * self.board_rows

        # Set up the players
        self.players = [working_directory + player_1["filename"], working_directory + player_2["filename"]]
        self.working_directory = working_directory

        # Set up next turn where 0 is player 1 and 1 is player 2
        self.whos_turn = 0

        # Create a log file for the current game
        now = datetime.datetime.now()
        self.log_file_name = working_directory + now.strftime("%Y-%m-%d-%H-%M") + "-"+ player_1["filename"] + "-" + \
                             player_2["filename"] +  ".log"

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

        # Write who's playing into log
        self.write_to_log(current_player)

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

        # Write commands into log
        self.write_to_log("call: " + command)

        # Execute the ai
        try:
            self.turn_results = run(command, cwd=self.working_directory, timeout=10, capture_output=True, shell=True,
                                    text=True)
        except TimeoutExpired:
            self.write_to_log("Player timed out!")
            return

        # Write output to log file
        self.write_to_log("output: " + self.turn_results.stdout)
        self.write_to_log(self.turn_results.stderr)

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
        players_move = self.turn_results.stdout.splitlines()[-1]

        # Make sure the string structure is correct
        if not re.search('^(r|b|g),\d\d?$', players_move):
            return False

        players_column = int(players_move.split(",")[1]) - 1 # make it an array index
        players_color = players_move.split(",")[0]

        # Make sure the move is within the board limits
        if players_column > self.board_columns - 1 or players_column < 0:
            return False

        # Make sure the move is with the right color
        if players_color != self.prev_players_color and players_color != "g":
            return False

        # Check if column player want to play in is full
        if self.board[players_column] is not ".":
            return False

        # Play the move, find an empty spot and play the players move
        for row in range(self.board_rows,0,-1):
            index = (row * self.board_columns) - self.board_columns
            if self.board[players_column + index] is ".":
                self.board[players_column + index] = players_color
                break

        # Draw board into log
        self.write_to_log(self.print_board())
        return True

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
                    if players_regex.search(cells):
                        # found a winner!
                        self.write_to_log("Horizontal win on column: " + str(index%10))
                        return cells

                # Check upwards
                if index - 30 > 0:
                    cells = ''.join(self.board[index-30:index+10:10])
                    if players_regex.search(cells):
                        # found a winner!
                        self.write_to_log("Vertical win on column: " + str(index%10))
                        return cells

                # Check forward diagonal
                if index > 29 and index % 10 < self.board_columns - 3:
                    cells = self.board[index-27] + self.board[index-18] + self.board[index-9] + self.board[index]
                    if players_regex.search(cells):
                        # found a winner!
                        self.write_to_log("Forward diagonal win on column: " + str(index%10))
                        return cells

                # Check backward diagonal
                if index > 29 and index % 10 > 2:
                    cells = self.board[index - 33] + self.board[index - 22] + self.board[index - 11] + \
                            self.board[index]
                    if players_regex.search(cells):
                        # found a winner!
                        self.write_to_log("Backward diagonal win on column: " + str(index%10))
                        return cells


        # Check if board has been filled
        if '.' not in self.board:
            return 'draw'

        return None

    def print_board(self):
        '''
        prints out the board
        :return:
        '''

        board_buffer = ''
        for index, cell in enumerate(self.board):
            if index % 10 == 0:
                if index is not 0:
                    board_buffer = board_buffer + "| \n"
                board_buffer = board_buffer + "| "
            board_buffer = board_buffer + self.board[index] + " "
        board_buffer = board_buffer + "| \n"

        print(board_buffer)
        return board_buffer

    def write_to_log(self, buffer):
        '''
        Writes buffer into the log file
        :param buffer: buffer to write
        :return: None
        '''

        self.log_file.write("\n")
        self.log_file.write(buffer)
        self.log_file.write("\n")



def main():
    player_1 = {}
    player_2 = {}

    player_1['filename'] = "simba"
    player_2['filename'] = "simba1"
    ai_list = [player_1,player_2]

    for index, first_ai in enumerate(ai_list):
        for second_ai in ai_list[index:]:
            if first_ai != second_ai:
                run_game(first_ai,second_ai)


def run_game(first_ai, second_ai):
    game = Framework(first_ai, second_ai, os.getcwd() + "/")
    print(game.log_file_name)

    while True:
        # Play the next turn and exit loop if ai makes bad move
        if not game.run_next_turn():
            print("end turn")
            game.write_to_log("Failed to run")
            game.write_to_log(game.players[game.whos_turn] + " loses!!")

            break # player loses for failed execution

        # Add move to board
        if not game.play_players_move():
            print('bad move')
            game.write_to_log("Bad move!")
            game.write_to_log(game.players[game.whos_turn] + " wins!!")
            break # player loses for bad move

        # print board so i can see
        # game.print_board()

        # Judge current board
        judgement = game.judge_board()

        if judgement is None:
            pass
        elif judgement == 'draw':
            game.write_to_log("It was a draw!")
            break # it was a draw
        elif 'b' in judgement:
            print("Result:", judgement)
            game.write_to_log("Result: " + judgement)
            print("Player 1 wins!!")
            game.write_to_log("Player 1 wins!!")
            break
        elif 'r' in judgement:
            print("Result:",judgement)
            game.write_to_log("Result: " + judgement)
            print("Player 2 wins!!")
            game.write_to_log("Player 2 wins!!")
            break



if __name__ == "__main__":
    main()