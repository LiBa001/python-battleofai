from abc import ABCMeta, abstractmethod
from .game import Game, GameState
import logging


logger = logging.getLogger(__name__)


class GameType(ABCMeta):
    def __init__(cls, *args, **kwargs):
        cls.__game_name__ = cls.__name__

        super().__init__(*args, **kwargs)

    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)

        return cls


class Match(metaclass=GameType):
    def __init__(self, callback: callable):
        """
        :param callback: The function to call when it's your turn.
        """
        self.callback = callback
        self._game = None
        self._client = None

    @property
    def game(self):
        return self._game

    @property
    def is_active(self):
        if self.game is not None:
            return self.game.players[self.game.active_player]["id"] == self._client.user_id

    @property
    def won(self):
        game = self.game

        if game is not None:
            winning_player = game.winning_player

            if winning_player is not None:
                return game.players[winning_player]["id"] == self._client.user_id

    @classmethod
    def open_games(cls):
        return Game.list(game_name=cls.__game_name__, game_state=GameState.WAITING.value)

    def join_game(self, client, game: Game=None):
        """
        Registers the player for a match
        :param client: The client to register
        :param game: The match to register on
        """
        if game is None:
            open_games = self.open_games()
            for g in open_games:
                registered = client.register(g)
                if registered:
                    game = g
                    logger.info(f"Found a game: {game.id}")
                    break

            if game is None:
                game = Game.create(self.__game_name__)
                logger.info(f"Created a game: {game.id}")
                assert client.register(game)

        else:
            assert client.register(game)

        self._game = game
        self._client = client

    def rejoin_game(self, client):
        """
        Rejoins the latest ongoing game that the client left.
        :param client: The client to register and which left.
        :return: None
        """
        left_games = Game.list(
            game_name=self.__game_name__, game_state=GameState.STARTED.value, player_ids=client.user_id
        )
        return self.join_game(client, left_games[-1])

    @classmethod
    def create_game(cls):
        """
        creates a game
        :return: the game
        """
        return Game.create(cls.__game_name__)

    @abstractmethod
    def make_turn(self):
        assert self.game is not None
        self.game.update()

        self.callback()

    @abstractmethod
    def play(self, turn_interval: int=5, matchmaking_interval: int=5):
        """
        Plays the game.
        :return: True if you won, else False
        """
        pass
