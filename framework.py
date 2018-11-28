import datetime
from subprocess import run

class Framework:

    def __init__(self, player_1_exec, player_2_exec):
        '''
        Initialization method. It creates a new board, receives the execution code for the two players.
        :return: None
        '''

        # Create a board of 10 x 8
        self.board = ['.'] * 80

        # Set up the players
        self.players = [player_1_exec, player_2_exec]

        # Set up next turn where 0 is player 1 and 1 is player 2
        self.whos_turn = 0

        # Create a log file for the current game
        now = datetime.datetime.now()
        self.log_file_name = now.strftime("%Y-%m-%d-%H-%M") + ".log"

        self.log_file = open(self.log_file_name, "a")



    def run_next_turn(self):
        '''
        Executes the current players executable with the board game and returns the results to the judge
        :return: -1 if error or CompletedProcess if sucessful
        '''

        # Prepare data for subprocess call
        current_player = str(self.players[self.whos_turn])
        current_board = ','.join(self.board)

        results = run([current_player,current_board], timeout=5, capture_output=True)

        # Write output to log file
        self.log_file.write(results.stdout)

        # Player looses if the return code is not 0
        if results.returncode is not 0:
            return -1

        # Set the next players turn
        self.whos_turn = (self.whos_turn + 1) % 2

        return results
