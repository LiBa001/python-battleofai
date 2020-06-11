[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Battle of AI - Python library

[![PyPI version](https://badge.fury.io/py/battleofai.svg)](https://badge.fury.io/py/battleofai)
[![Build Status](https://travis-ci.org/LiBa001/python-battleofai.svg?branch=master)](https://travis-ci.org/LiBa001/python-battleofai)

> **DEPRECATED:** The Battle of AI has been taken offline by it's creators

Object-oriented easy2use solution for interacting with https://battleofai.net/ \'s API.

A short summary of the basic features.

#### Configure your client easily.

```python
from battleofai import Client

client = Client(credentials=('username', 'password'))

# if you want to export your config
client.config.from_python_file('config.py')

# or use json
client.config.from_json_file('config.json')

```

#### Play games automatically.
```python
from battleofai import Client, Core


client = Client()  # specify credentials


@client.callback()
def turn(board, symbol):
    for x_pos, columns in enumerate(board):
        for y_pos, field in enumerate(columns):
            if field == '#':  # if position is free
                return x_pos, y_pos  # set my stone


client.play(Core)

```

#### Play games manually.
```python
from battleofai import Client, Core, GameState
import time


client = Client()  # specify credentials


def turn(board, symbol):
    for x_pos, columns in enumerate(board):
        for y_pos, field in enumerate(columns):
            if field == '#':  # if position is free
                return x_pos, y_pos  # set my stone


game = Core.create_game()

client.login()

my_match = Core(callback=turn)
my_match.join_game(client, game)

# then either
my_match.play()

# or even something like this
playing = True
while playing:
    game.update()

    if not game.state == GameState.STARTED:
        break
    
    if my_match.is_active:
        resp = my_match.make_turn()

        if resp.status_code == 200 and 'false' in resp.text:
            playing = False
    
    time.sleep(5)

```

#### Manage games.
```python
from battleofai import Game, GameState, Core

my_game = Game.get(game_id=100)
print(my_game.players)

open_games = Game.list(game_state=GameState.WAITING)

new_game = Game.create(Core.__game_name__)

```
