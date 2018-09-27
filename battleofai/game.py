import requests
from .enums import GameState
from .utils import generate_get_uri


class Game:
    API_ENDPOINT = "https://games.battleofai.net/api/games/"

    def __init__(self):
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
        return self._players

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

    def pull(self, game_id: int):
        resp = requests.get(self.API_ENDPOINT + str(game_id))

        assert resp.status_code == 200

        info = resp.json()

        self._id = game_id
        self._name = info["game_name"]
        self._state = info["game_state"]
        self._open_slots = info["open_slots"]
        self._players = info["players"]
        self._active_player = info["active_player"]
        self._history = info["history"]
        self._winning_player = info["winning_player"]

    def update(self):
        if self.id is not None:
            self.pull(self.id)

    @classmethod
    def create(cls, game_name: str):
        """
        creates a game
        :param game_name: The name of the game (e.g. 'Core')
        :return: the game
        """
        url = cls.API_ENDPOINT + "createGame"

        resp = requests.post(url, json={"game_name": game_name})
        assert resp.status_code == 200

        game_id = int(resp.text)

        return cls.get(game_id)

    @classmethod
    def get(cls, game_id: int):
        game = cls()
        game.pull(game_id)
        return game

    @classmethod
    def list(cls, **kwargs):
        resp = requests.get(generate_get_uri(cls.API_ENDPOINT, **kwargs))

        assert resp.status_code == 200

        return [cls.get(g['id']) for g in resp.json()['games']]

    def make_turn(self, data: dict):
        return requests.post(self.API_ENDPOINT + str(self.id) + "/makeTurn", json=data)

    def __repr__(self):
        return f"<Game id={self.id}>"
