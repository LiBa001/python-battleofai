from battleofai import Client, Core


client = Client(credentials=('username', 'password'))


@client.callback()
def turn(board, symbol):
    """
    :param board: Contains the current state of the game
    :param symbol: Contains your symbol on the board - either X if you are the first player or O if you are the 2nd.
    :return: x_pos, y_pos where your AI wants to place a stone
    """
    for x_pos, columns in enumerate(board):
        for y_pos, field in enumerate(columns):
            if field == '#':  # if position is free
                return x_pos, y_pos  # set my stone


client.play(Core)
