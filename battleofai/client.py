from .config import Config
from .abc import GameType
from .game_session import GameSession
from .http import HTTPClient
import logging
import asyncio


logger = logging.getLogger(__name__)


class Client:
    def __init__(self, username: str=None, password: str=None, *, credentials: tuple=None, loop=None, **options):
        self.loop = asyncio.get_event_loop() if loop is None else loop

        self.config = Config()

        self.set_credentials(username, password, credentials=credentials)

        self._callbacks = {}
        self._sessions = []
        self._ready_callback = None

        connector = options.pop('connector', None)
        self.http = HTTPClient(connector, loop=self.loop)

    def set_credentials(self, username: str=None, password: str=None, *, credentials: tuple=None):
        self.config["username"] = username
        self.config["password"] = password

        if credentials is not None:
            self.config["username"] = credentials[0]
            self.config["password"] = credentials[1]

    async def login(self, username: str=None, password: str=None, *, credentials: tuple=None):
        # update missing credentials
        self.set_credentials(
            username or self.config.username,
            password or self.config.password,
            credentials=credentials
        )

        return await self.http.login(self.config.username, self.config.password)

    async def check_and_update_token(self):
        valid = await self.http.validate_token()

        if not valid:
            logger.info("Token has expired; Requesting new one . . .")
            return await self.login()

    def register_callback(self, callback: callable, game_type: GameType=None) -> None:
        """
        This is to register a callback for a game type.
        :param callback: callable

            A callable used

        :param game_type: `battleofai.abc.GameType`

            The game type to use this callback for.
            If None it's used for any game type where no other callback is specified.
            Instance of :mcs:`battleofai.abc.GameType` (Subclass of :cls:`battleofai.abc.Match`)
                e.g. :cls:`battleofai.Core`.

        """
        self._callbacks[game_type.__game_name__ if game_type is not None else game_type] = callback

    def callback(self, game_type: GameType=None) -> callable:
        """
        Use this to decorate your callback functions.
        Alternative to :meth:`register_callback`.
        """
        def decorator(callback: callable):
            self.register_callback(callback, game_type)

        return decorator

    def get_callback(self, game_type: GameType):
        callback = self._callbacks.get(game_type.__game_name__)

        if callback is None:
            callback = self._callbacks.get(None)

            if callback is not None:
                logger.warning("Using callback with undefined game_type.")

        return callback

    def on_ready(self, func: callable):
        self._ready_callback = func

    @property
    def sessions(self):
        return self._sessions

    def register_session(self, session: GameSession):
        session.register_client(self)
        self._sessions.append(session)

    def create_session(self, game_type: GameType, name: str=None, callback: callable=None, **kwargs) -> GameSession:
        session = GameSession(game_type, name, callback, **kwargs)
        self.register_session(session)
        return session

    async def run_sessions(self):
        for session in self.sessions:
            session.run()

        await asyncio.gather(*[s.task for s in self.sessions])

    async def start(self, *args, **kwargs):
        await self.login(*args, **kwargs)

        if self._ready_callback is not None:
            on_ready = self.loop.create_task(self._ready_callback())
        else:
            on_ready = None

        await self.run_sessions()

        if on_ready is not None:
            await on_ready

    def run(self, *args, **kwargs):
        """
        A blocking call that abstracts away the `event loop` initialisation from you.
        If you want more control over the event loop then this
        function should not be used.

        Warning
        --------
        This function must be the last function to call due to the fact that it
        is blocking. That means that registration of events or anything being
        called after this function call will not execute until it returns.
        """

        loop = self.loop

        try:
            loop.run_until_complete(self.start(*args, **kwargs))
        except KeyboardInterrupt:
            logger.info('Received signal to terminate event loop.')
        finally:
            self.close()

    def close(self):
        self.loop.run_until_complete(self.http.close())
        self.loop.close()
