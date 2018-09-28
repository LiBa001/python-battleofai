from battleofai import Client, Core
import os


client = Client(credentials=(os.environ['BOAI_username'], os.environ['BOAI_password']))


@client.callback()
def turn(board, symbol):
    for x_pos, columns in enumerate(board):
        for y_pos, field in enumerate(columns):
            if field == '#':  # if position is free
                return x_pos, y_pos  # set my stone


client.play(Core, turn_interval=1)
