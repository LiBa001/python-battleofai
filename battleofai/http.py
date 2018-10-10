import aiohttp
import asyncio
from . import __version__
from .errors import HTTPException, Unauthorized, Forbidden, NotFound, LoginFailure
from urllib.parse import quote as _uriquote
import sys
import json
import logging
from enum import Enum


logger = logging.getLogger(__name__)


class Method(Enum):
    GET = "GET"
    POST = "POST"


class Route:
    BASE = ''
    MAJOR_PARAMS = []

    def __init__(self, method: Method, path, **parameters):
        self.path = path
        self.method = method.value
        url = (self.BASE + self.path)
        if parameters:
            self.url = url.format(**{k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        else:
            self.url = url

        for param in self.MAJOR_PARAMS:
            setattr(self, param, parameters.get(param))

    @property
    def bucket(self):
        # the bucket is just method + path w/ major parameters
        bucket_values = [self.method]
        bucket_values.extend([str(getattr(self, p)) for p in self.MAJOR_PARAMS])
        bucket_values.append(self.path)

        return ':'.join(bucket_values)


class GamesRoute(Route):
    BASE = 'https://games.battleofai.net/api/games'
    MAJOR_PARAMS = ['game_id']


class IAMRoute(Route):
    BASE = 'https://iam.battleofai.net/api/iam'
    MAJOR_PARAMS = ['user_id']


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the BOAI APIs."""

    def __init__(self, connector=None, *, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.connector = connector
        self._session = aiohttp.ClientSession(connector=connector, loop=self.loop)
        self.user_id = None
        self.user_token = None
        self.session_token = None

        user_agent = 'GameAI (https://github.com/LiBa001/python-battleofai {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    @property
    def token(self):
        return str([self.user_token, self.session_token])

    @property
    def player_auth(self) -> dict:
        return {"id": self.user_id, "token": self.token}

    async def close(self):
        await self._session.close()

    async def request(self, route, **kwargs) -> dict or str:
        method = route.method
        url = route.url

        # header creation
        headers = {
            'User-Agent': self.user_agent,
        }

        # some checking if it's a JSON request
        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs.pop('json'))

        kwargs['headers'] = headers

        async with self._session.request(method, url, **kwargs) as r:
            logger.debug(f"{method} {url} with {kwargs.get('data')} has returned {r.status}")

            if r.headers['content-type'] == 'application/json':
                data = await r.json(encoding='utf-8')
            else:
                data = await r.text(encoding='utf-8')

            # the request was successful so just return the text/json
            if 300 > r.status >= 200:
                logger.debug(f'{method} {url} has received {data}')
                return data

            else:
                message = data.get('message') if isinstance(data, dict) else data

                if r.status == 401:
                    raise Unauthorized(r, message)
                elif r.status == 403:
                    raise Forbidden(r, message)
                elif r.status == 404:
                    raise NotFound(r, message)
                else:
                    raise HTTPException(r, message)

    async def login(self, username: str, password: str):
        """
        Logs a user in with credentials of the registration for obtaining valid credentials for playing a game.
        :return: A tuple containing player_id and login token. Credentials are valid for 1 day.
        """
        route = IAMRoute(Method.POST, '/login')

        login_data = {
            "username": username,
            "password": password
        }
        content: dict = await self.request(route, json=login_data)

        if content["userid"] is None or content["token"] is None or content["session_token"] is None:
            raise LoginFailure()

        self.user_id = content["userid"]
        self.user_token = content["token"]
        self.session_token = content["session_token"]

        return self.user_id, self.token

    async def validate_token(self) -> bool:
        route = IAMRoute(Method.POST, '/validateToken')

        data = {
            "userid": self.user_id,
            "token": self.user_token,
            "session_token": self.session_token
        }
        content: dict = await self.request(route, json=data)

        return content["success"]

    async def get_games(self, **criteria) -> [int]:
        """
        Gets a list of all existing games meeting the given criteria.
        :param criteria: Select games meeting specific criteria e.g. game_state='WAITING'
        :return: List of game IDs
        """

        route = GamesRoute(Method.GET, '/')

        content: dict = await self.request(route, params=criteria)

        games = content["games"]
        return [g["id"] for g in games]

    async def create_game(self, game_name: str) -> int:
        """
        Creates a new game.
        :param game_name: The name of the game (e.g. 'Core')
        :return: The game id
        """

        route = GamesRoute(Method.POST, '/createGame')

        content: str = await self.request(route, json={'game_name': game_name})

        game_id = int(content)
        return game_id

    async def get_game(self, game_id) -> dict:
        """
        Gets all info about the given game.
        :param game_id: The ID of the game.
        :return: A dict containing all info about the game.
        """

        route = GamesRoute(Method.GET, '/{game_id}', game_id=game_id)

        game: dict = await self.request(route)

        return game

    async def make_turn(self, game_id, turn_data: tuple) -> bool:
        data = {
            "player": self.player_auth,
            "turn": json.dumps(turn_data)
        }
        route = GamesRoute(Method.POST, '/{game_id}/makeTurn', game_id=game_id)

        resp: bool = await self.request(route, json=data)

        return resp

    async def register_player(self, game_id) -> bool:
        """
        Registers the player for a match by id
        :param game_id: The match to register on
        :return: True -> success; False -> failure
        """
        route = GamesRoute(Method.POST, '/{game_id}/registerPlayer', game_id=game_id)

        resp: bool = await self.request(route, json=self.player_auth)

        return resp
