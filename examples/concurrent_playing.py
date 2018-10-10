from battleofai import Client, Core, GameSession


client = Client(credentials=('username', 'password'))


@client.callback(Core)
async def turn(board, symbol):
    """
    :param board: Contains the current state of the game
    :param symbol: Contains your symbol on the board - either X if you are the first player or O if you are the 2nd.
    :return: x_pos, y_pos where your AI wants to place a stone
    """
    for x_pos, columns in enumerate(board):
        for y_pos, field in enumerate(columns):
            if field == '#':  # if position is free
                return x_pos, y_pos  # set my stone


@client.on_ready
async def main():
    # play multiple games concurrently
    session_1 = GameSession(Core, rejoin_ongoing_games=False, turn_interval=0.5, join_own_games=True)
    session_2 = GameSession(Core, rejoin_ongoing_games=False, turn_interval=0.5, join_own_games=False)

    session_1.register_client(client)
    session_1.run()

    session_2.register_client(client)
    session_2.run()

    print(session_1.name, session_1.match, session_1.match.game)
    print(session_2.name, session_2.match, session_2.match.game)

    await session_1.task
    await session_2.task


client.run()
