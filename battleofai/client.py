import requests
from .config import Config
from .game import Game
from .abc import GameType
import logging


logger = logging.getLogger(__name__)


class Client:
    ACCOUNT_API_ENDPOINT = "https://iam.battleofai.net/api/"

    def __init__(self, credentials: tuple=None):
        self.user_id = None
        self.user_token = None
        self.session_token = None
        self.config = Config()

        if credentials is not None:
            self.config["username"] = credentials[0]
            self.config["password"] = credentials[1]

        self._callbacks = {}

    @property
    def token(self):
        return str([self.user_token, self.session_token])

    def register(self, game: Game):
        """
        Registers the player for a match by id
        :param game: The match to register on
        """
        url = game.API_ENDPOINT + str(game.id) + "/registerPlayer"
        resp = requests.post(url, json={"id": self.user_id, "token": self.token})
        assert resp.status_code == 200, f"StatusCode: {resp.status_code}"

        return 'true' in resp.text

    def login(self):
        """
        Logs a user in with credentials of the registration for obtaining valid credentials for playing a game.
        :return: A tuple containing player_id and login token. Credentials are valid for 1 day.
        """
        login_data = {
            "username": self.config.username,
            "password": self.config.password
        }
        resp = requests.post(Client.ACCOUNT_API_ENDPOINT + "iam/login", json=login_data)
        if not resp.status_code == 200:
            exit("Account Management temporarily unavailable")

        if resp.json()["userid"] is None or resp.json()["token"] is None or resp.json()["session_token"] is None:
            exit("Invalid login credentials")

        self.user_id = resp.json()["userid"]
        self.user_token = resp.json()["token"]
        self.session_token = resp.json()["session_token"]

    def check_and_update_token(self):
        data = {
            "userid": self.user_id,
            "token": self.user_token,
            "session_token": self.session_token
        }
        resp = requests.post(Client.ACCOUNT_API_ENDPOINT + "iam/validateToken", json=data)
        if not resp.status_code == 200 or not resp.json()["success"]:
            self.login()

    def callback(self, game_type: GameType=None):
        def decorator(callback: callable):
            self._callbacks[game_type.__game_name__ if game_type is not None else game_type] = callback

        return decorator

    def get_callback(self, game_type: GameType):
        callback = self._callbacks.get(game_type.__game_name__)

        if callback is None:
            callback = self._callbacks.get(None)

            if callback is not None:
                logger.warning("Using callback with undefined game_type.")

        return callback

    def play(self, game_type: GameType, callback: callable=None, rejoin_ongoing_games=False,
             turn_interval: int=5, matchmaking_interval: int=5):
        self.login()

        if callback is None:
            callback = self.get_callback(game_type)
            assert callback is not None, "Need to specify callback function!"

        match = game_type(callback=callback)

        if rejoin_ongoing_games:
            match.rejoin_game(self)

        match.join_game(self)

        won = match.play(turn_interval=turn_interval, matchmaking_interval=matchmaking_interval)

        logger.info(f"{'won' if won else 'lost'} game {match.game.id}")

        return won
