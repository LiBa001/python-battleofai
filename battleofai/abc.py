from abc import ABCMeta, abstractmethod
from .game import Game, GameState
from .http import HTTPClient
from typing import AsyncGenerator
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
    def __init__(self, http_client: HTTPClient, callback: callable):
        """
        :param callback: The function to call when it's your turn.
        """
        self.callback: callable = callback
        self._game: Game = None
        self._http: HTTPClient = http_client

    @property
    def game(self) -> Game:
        return self._game

    @property
    def is_active(self):
        if self.game is not None:
            return self.game.players[self.game.active_player] == self._http.user_id

    @property
    def won(self):
        game = self.game

        if game is not None:
            winning_player = game.winning_player

            if winning_player is not None:
                return game.players[winning_player] == self._http.user_id

    @property
    def opponents(self) -> tuple:
        if self.game is not None:
            players = self.game.players
            players.remove(self._http.user_id)
            return tuple(players)

    @property
    def ready(self) -> bool:
        game_not_none = self.game is not None
        game_is_ongoing = False

        if game_not_none:
            state = self.game.state
            game_is_ongoing = (state == GameState.WAITING) or (state == GameState.STARTED)

        return game_not_none and game_is_ongoing

    @classmethod
    def open_games(cls, http_client: HTTPClient) -> AsyncGenerator:
        return Game.get_all(http_client, game_name=cls.__game_name__, game_state=GameState.WAITING.value)

    async def join_game(self, game: Game=None, *, join_own_games: bool=False):
        """
        Registers the player for a match

        :param game:

            The match to register on

        :param join_own_games:

            Indicates if you'd like to join a `GameState.WAITING` game against yourself.

        """
        if game is None:
            open_games = self.open_games(self._http)
            async for game in open_games:
                if self._http.user_id in game.players and not join_own_games:
                    continue

                registered = await self._http.register_player(game.id)
                if registered:
                    logger.info(f"Found a game: {game.id}")
                    break

            if game is None:
                game = await self.create_game(self._http)
                logger.info(f"Created a game: {game.id}")
                assert await self._http.register_player(game.id)

        else:
            if self._http.user_id not in game.players:
                assert await self._http.register_player(game.id)
            elif join_own_games:
                await self._http.register_player(game.id)

        self._game = game

    async def rejoin_ongoing_game(self):
        """
        Rejoins the latest ongoing game that the client left.
        :return: None
        """
        left_games_ids = await self._http.get_games(
            game_name=self.__game_name__, game_state=GameState.STARTED.value, player_ids=self._http.user_id
        )
        game = await Game.get(self._http, left_games_ids[-1])
        return await self.join_game(game)

    @classmethod
    async def create_game(cls, http_client: HTTPClient):
        """
        creates a game
        :return: the game
        """
        return await Game.create(http_client, cls.__game_name__)

    @abstractmethod
    async def make_turn(self):
        assert self.game is not None
        await self.game.update()

        await self.callback()

    @abstractmethod
    async def play(self, turn_interval: int=5, matchmaking_interval: int=5):
        """
        Plays the game.
        :return: True if you won, else False
        """
        pass
