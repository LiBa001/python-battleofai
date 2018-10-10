from battleofai import Client, Core
import os


client = Client(credentials=(os.environ['BOAI_username'], os.environ['BOAI_password']))


async def turn(board, symbol):
    for x_pos, columns in enumerate(board):
        for y_pos, field in enumerate(columns):
            if field == '#':  # if position is free
                return x_pos, y_pos  # set my stone


@client.on_ready
async def main():
    match = Core(client.http, turn)
    game = await match.create_game(client.http)

    await match.join_game(game)
    await match.join_game(game, join_own_games=True)  # join a second time

    await game.update()

    session = client.create_session(Core, "test against myself", turn_interval=0.5)
    session.set_match(match)

    await session.run()


client.run()
