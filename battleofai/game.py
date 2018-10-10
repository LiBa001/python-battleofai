from .enums import GameState
from .http import HTTPClient


class Game:
    def __init__(self, http_client: HTTPClient):
        self._http = http_client

        self._id = None
        self._name = None
        self._state = None
        self._open_slots = None
        self._players = None
        self._active_player = None
        self._history = None
        self._winning_player = None

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return GameState(self._state)

    @property
    def open_slots(self):
        return self._open_slots

    @property
    def players(self):
        return [player["id"] for player in self._players]

    @property
    def active_player(self):
        return self._active_player

    @property
    def history(self):
        return self._history

    @property
    def current_board(self):
        if self.history is not None:
            return self.history[-1]["board"]

    @property
    def winning_player(self):
        return self._winning_player

    async def pull(self, game_id: int):
        info = await self._http.get_game(game_id)

        self._id = game_id
        self._name = info["game_name"]
        self._state = info["game_state"]
        self._open_slots = info["open_slots"]
        self._players = info["players"]
        self._active_player = info["active_player"]
        self._history = info["history"]
        self._winning_player = info["winning_player"]

    async def update(self):
        if self.id is not None:
            await self.pull(self.id)

    @classmethod
    async def create(cls, http_client: HTTPClient, game_name: str):
        """
        creates a game
        :param game_name: The name of the game (e.g. 'Core')
        :param http_client: The client to use for registration
        :return: the game
        """
        game_id = await http_client.create_game(game_name)
        return await cls.get(http_client, game_id)

    @classmethod
    async def get(cls, http_client: HTTPClient, game_id: int):
        game = cls(http_client)
        await game.pull(game_id)
        return game

    @classmethod
    async def get_all(cls, http_client: HTTPClient, **criteria):
        game_ids = await http_client.get_games(**criteria)

        for game_id in game_ids:
            game = await cls.get(http_client, game_id)
            yield game

    @classmethod
    async def list(cls, http_client: HTTPClient, **criteria):
        return [game async for game in cls.get_all(http_client, **criteria)]

    async def make_turn(self, turn_data: tuple) -> bool:
        return await self._http.make_turn(self.id, turn_data)

    def __repr__(self):
        return f"<Game id={self.id}>"
