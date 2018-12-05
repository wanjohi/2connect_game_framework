import sys
import os
import boto3
import botocore
import pymysql
from subprocess import run
from framework import Framework

# Get environment variables
mysql_host = os.environ["mysql_host"]
mysql_user = os.environ["mysql_user"]
mysql_pass = os.environ["mysql_pass"]
mysql_db = os.environ["mysql_db"]

s3 = boto3.resource("s3")

def lambda_handler(event, context):

    # Connect to mysql
    conn = mysql_connect()

    # S3
    bucket = os.environ["s3_bucket"]
    keys = []
    ais = {}

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT * FROM ais")
        ais = cur.fetchall()



    copy_ais_to_tmp(bucket, ais)
    coordinate_matches(conn, bucket, ais)


def mysql_connect():
    """
    Establish mysql connection
    :return: connection object
    """
    try:
        conn = pymysql.connect(mysql_host, user=mysql_user,
                               passwd=mysql_pass, db=mysql_db, connect_timeout=5)
    except:
        print("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()

    return conn


def copy_ais_to_tmp(bucket, ais):
    """
    Download ais
    :param bucket:
    :param keys:
    :return:
    """

    for ai in ais:
        try:
            local_file_name = "/tmp/" + ai["filename"]
            s3_file_name = 'ais/' + ai["filename"]
            print("Coping:", s3_file_name, "to:", local_file_name)
            s3.Bucket(bucket).download_file(s3_file_name, local_file_name)
            run("chmod 755 " + local_file_name, shell=True, text=True)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("Could not copy: ", s3_file_name)
                continue
            else:
                raise

def save_logs_to_s3(bucket, log_name):
    lambda_path = log_name
    s3_path = "logs/" + log_name.replace("/tmp/","")
    print("Saving:",lambda_path,"to:",s3_path)
    s3.Bucket(bucket).upload_file(lambda_path, s3_path, ExtraArgs={'ACL':'public-read'})
    return s3_path


def save_game_log_db(conn, won_id, lost_id, is_draw,log_link):


    s3_link = 'https://{}.s3.amazonaws.com/'.format(os.environ["s3_bucket"]) + log_link

    print("Saving data:", won_id, lost_id, is_draw, s3_link)

    sql = "INSERT INTO game_log (ai_won_id, ai_lost_id, is_draw, log_link) VALUES (%s, %s, %s, %s)"

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        try:
            cur.execute(sql,(won_id,lost_id,is_draw,s3_link))
            conn.commit()
        except:
            print(cur._last_executed)
            raise

def coordinate_matches(conn, bucket, ai_list):
    for index, first_ai in enumerate(ai_list):
        for second_ai in ai_list[index:]:
            if first_ai["id"] != second_ai["id"]:
                winner_ai, loser_ai, is_draw, log_file = run_game(first_ai,second_ai)

                s3_log = save_logs_to_s3(bucket, log_file)

                save_game_log_db(conn, int(winner_ai["id"]), int(loser_ai["id"]), is_draw, s3_log)


def run_game(first_ai, second_ai):
    """
    Run a game between two ais
    :param first_ai:
    :param second_ai:
    :return:
    """
    game = Framework(first_ai, second_ai, "/tmp/")

    while True:
        # Play the next turn and exit loop if ai makes bad move
        if not game.run_next_turn():
            game.write_to_log("Failed to run")
            game.write_to_log(game.players[game.whos_turn] + " loses!!")
            if(game.whos_turn == 0):
                loser = first_ai
                winner = second_ai
            else:
                loser = second_ai
                winner = first_ai
            draw = False
            break  # player loses for failed execution

        # Add move to board
        if not game.play_players_move():
            game.write_to_log("Bad move!")
            game.write_to_log(game.players[game.whos_turn] + " wins!!")
            if(game.whos_turn == 1):
                loser = first_ai
                winner = second_ai
            else:
                loser = second_ai
                winner = first_ai
            draw = False
            break  # player loses for bad move

        # print board so i can see
        game.print_board()

        # Judge current board
        judgement = game.judge_board()

        if judgement is None:
            pass
        elif judgement == "draw":
            game.write_to_log("It was a draw!")
            winner = first_ai
            loser = second_ai
            draw = True
            break
        elif "b" in judgement:
            game.write_to_log("Result: " + judgement)
            game.write_to_log("Player 1 wins!!")
            winner = first_ai
            loser = second_ai
            draw = False
            break
        elif "r" in judgement:
            game.write_to_log("Result: " + judgement)
            game.write_to_log("Player 2 wins!!")
            winner = second_ai
            loser = first_ai
            draw = False
            break

    return winner, loser, draw, game.log_file_name