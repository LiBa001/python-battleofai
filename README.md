
[![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/LiBa001/python-battleofai/blob/master/LICENSE)


# Battle of AI - Python library

[![GitHub stars](https://img.shields.io/github/stars/LiBa001/python-battleofai.svg?style=social&label=Stars)](https://github.com/LiBa001/python-battleofai/stargazers)


[![PyPI version](https://badge.fury.io/py/battleofai.svg)](https://badge.fury.io/py/battleofai)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/battleofai.svg)](https://pypi.org/project/battleofai/)
[![Build Status](https://travis-ci.org/LiBa001/python-battleofai.svg?branch=async)](https://travis-ci.org/LiBa001/python-battleofai)

Object-oriented, asynchronous, easy2use solution for interacting with https://battleofai.net/ \'s APIs.

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

client = Client(credentials=('username', 'password'))

@client.callback(Core)
async def turn(board, symbol):
    for x_pos, columns in enumerate(board):
        for y_pos, field in enumerate(columns):
            if field == '#':  # if position is free
                return x_pos, y_pos  # set my stone


@client.on_ready
async def main():
    # called when the client logged in and finished up
    
    session = client.create_session(Core)  # create and register a new game session

    await session.run()  # find a match and play the game


client.run()
```

#### Play multiple games concurrently.
```python
from battleofai import Client, Core, GameSession

client = Client()

# setup callback like above

@client.on_ready
async def main():
    # play multiple games concurrently
    session_1 = GameSession(Core, rejoin_ongoing_games=False, turn_interval=0.5, join_own_games=True)
    session_2 = GameSession(Core, rejoin_ongoing_games=False, turn_interval=0.5, join_own_games=False)

    session_1.register_client(client)
    session_1.run()

    session_2.register_client(client)
    session_2.run()

    await session_1.task
    await session_2.task


client.run()
```
