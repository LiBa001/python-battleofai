Quickstart
==========

Some things you need to get started quickly.

Install
-------

Latest stable version:

.. code:: sh

  python3.6 -m pip install battleofai


This branch (Alpha state):

.. code:: sh

  python3.6 -m pip install -U git+https://github.com/LiBa001/python-battleofai@async

.. note::

  This requires `git`_ to be installed.

.. _`git`: https://git-scm.com/

A short summary of the basic features.
--------------------------------------

Configure your client easily.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from battleofai import Client

    client = Client(credentials=('username', 'password'))

    # if you want to export your config
    client.config.from_python_file('config.py')

    # or use json
    client.config.from_json_file('config.json')


Play games automatically.
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

Play multiple games concurrently.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

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
