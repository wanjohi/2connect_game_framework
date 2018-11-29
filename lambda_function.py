import sys
import os
import boto3
import botocore
import pymysql
from framework import Framework

# Get environment variables
mysql_host = os.environ['mysql_host']
mysql_user = os.environ['mysql_user']
mysql_pass = os.environ['mysql_pass']
mysql_db = os.environ['mysql_db']

s3 = boto3.resource('s3')

def lambda_handler(event, context):

    # Connect to mysql
    conn = mysql_connect()

    # S3
    bucket = 'connect2'
    keys = []

    with conn.cursor() as cur:
        cur.execute("select 'filename' from ais")
        for row in cur:
            keys.append(row['filename'])



    copy_ais_to_tmp(bucket, keys)
    coordinate_matches(bucket, keys)


def mysql_connect():
    '''
    Establish mysql connection
    :return: connection object
    '''
    try:
        conn = pymysql.connect(mysql_host, user=mysql_user,
                               passwd=mysql_pass, db=mysql_db, connect_timeout=5)
    except:
        print("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()

    return conn


def copy_ais_to_tmp(bucket, keys):
    '''
    Download ais
    :param bucket:
    :param keys:
    :return:
    '''

    for key in keys:
        try:
            local_file_name = '/tmp/' + key
            s3.Bucket(bucket).download_file(key, local_file_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                continue
            else:
                raise

def save_logs_to_s3(bucket, log_name):
    lambda_path = "/tmp/" + log_name
    s3_path = "/logs/" + log_name
    s3.Bucket(bucket).upload_file(lambda_path, s3_path)


def coordinate_matches(bucket, ai_list):
    for index, first_ai in enumerate(ai_list):
        for second_ai in ai_list[index:]:
            if first_ai != second_ai:
                log_file = run_game(first_ai,second_ai)
                save_logs_to_s3(bucket, log_file)


def run_game(first_ai, second_ai):
    '''
    Run a game between two ais
    :param first_ai:
    :param second_ai:
    :return:
    '''
    game = Framework(first_ai, second_ai, "/tmp/")

    while True:
        # Play the next turn and exit loop if ai makes bad move
        if not game.run_next_turn():
            game.write_to_log("Failed to run")
            game.write_to_log(game.players[game.whos_turn] + " loses!!")

            break  # player loses for failed execution

        # Add move to board
        if not game.play_players_move():
            game.write_to_log("Bad move!")
            game.write_to_log(game.players[game.whos_turn] + " wins!!")
            break  # player loses for bad move

        # print board so i can see
        game.print_board()

        # Judge current board
        judgement = game.judge_board()

        if judgement is None:
            pass
        elif judgement == 'draw':
            game.write_to_log("It was a draw!")
            pass  # it was a draw
        elif 'b' in judgement:
            game.write_to_log("Result: " + judgement)
            game.write_to_log("Player 1 wins!!")
            break
        elif 'r' in judgement:
            game.write_to_log("Result: " + judgement)
            game.write_to_log("Player 2 wins!!")
            break

    return game.log_file_name