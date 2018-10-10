import asyncio
from .errors import Unauthorized
from .abc import GameType, Match
import logging

logger = logging.getLogger(__name__)


class GameSession:
    """ Represents a client's game session. (The client playing a match.) """

    def __init__(self, game_type: GameType, name: str=None, callback: callable=None, *,
                 rejoin_ongoing_games=False, join_own_games=False, turn_interval=1, matchmaking_interval=5):
        """
        :param game_type: The game type to play e.g. :cls:`battleofai.Core`
        :param callback: The function to call on every turn
        :param rejoin_ongoing_games: Bool indicating if the client should rejoin ongoing games
        :param turn_interval: Indicating how long to wait for the opponent to make his turn
        :param matchmaking_interval: Indicating how often to check for new players joined
        :return: Bool indicating if you have won the game.
        """

        self._task: asyncio.Task = None
        self._match: Match = None
        self._client = None

        self.name = name
        self.game_type = game_type
        self.callback = callback
        self.rejoin_ongoing_games = rejoin_ongoing_games
        self.join_own_games = join_own_games
        self.turn_interval = turn_interval
        self.matchmaking_interval = matchmaking_interval

    @property
    def task(self):
        return self._task

    @property
    def match(self):
        return self._match

    @property
    def client(self):
        return self._client

    @property
    def result(self):
        if self._task is not None:
            return self._task.result()

    def register_client(self, client):
        assert self._client is None, "A client is already registered."
        self._client = client

        if self.name is None:
            self.name = f"Session #{len(client.sessions) + 1}"

    def set_match(self, match: Match):
        assert self._client is not None
        assert match.ready, "This match is not ready to play."
        assert self._client.http.user_id in match.game.players, "You don't participate in this match."

        self._match = match

    def setup(self, client, match: Match):
        self.register_client(client)
        self.set_match(match)

    async def find_match(self):
        assert self._client is not None
        assert self._match is None, "Already joined a match."

        game_type = self.game_type
        callback = self.callback
        client = self._client

        if callback is None:
            callback = client.get_callback(game_type)
            assert callback is not None, "Need to specify callback function!"

        match: Match = game_type(client.http, callback=callback)

        if self.rejoin_ongoing_games:
            await match.rejoin_ongoing_game()

        await match.join_game(join_own_games=self.join_own_games)

        self._match: Match = match
        return match

    async def run_match(self):
        match = self._match

        if match is None:
            match = await self.find_match()

        client = self._client

        won = None
        finished = False
        while not finished:
            try:
                won = await match.play(turn_interval=self.turn_interval, matchmaking_interval=self.matchmaking_interval)
                finished = True
            except Unauthorized:
                await client.check_and_update_token()
            except asyncio.CancelledError:
                logger.info("Received signal to cancel execution.")
                raise asyncio.CancelledError

        logger.info(f"{self.name}: {'won' if won else 'lost'} game {match.game.id}")

        return won

    def run(self):
        assert not self.is_running, "A task is still pending."

        self._task: asyncio.Task = self._client.loop.create_task(self.run_match())
        self._task.add_done_callback(self._done_callback)

        return self.task

    def run_for_client(self, client):
        self.register_client(client)
        self.run()

    @property
    def is_running(self):
        task = self._task
        if task is not None:
            if not task.done():
                return True
        return False

    async def cancel(self):
        if self.is_running:
            self._task.cancel()

    def _done_callback(self, future: asyncio.Future):
        if future.cancelled():
            logger.debug(f"{self.name}: Future has been cancelled.")
        else:
            logger.info(f"{self.name} is done: {future.exception() or future.result()}")
