from .abc import Match
from .enums import GameState
from .game import Game
import logging
import asyncio

logger = logging.getLogger(__name__)


class Core(Match):
    async def make_turn(self) -> bool:
        game: Game = self.game
        assert game is not None
        await game.update()

        assert game.state == GameState.STARTED
        assert self.is_active

        board = game.current_board
        symbol = self.symbol

        turn_data = await self.callback(board, symbol)
        is_ongoing = await game.make_turn(turn_data)

        logger.info(f"MOVING TO {', '.join(str(td) for td in [turn_data])}")

        return is_ongoing

    async def play(self, turn_interval: int=5, matchmaking_interval: int=5) -> bool:
        game: Game = self.game

        assert game is not None

        await game.update()

        counter = 0
        while game.state == GameState.WAITING:
            logger.info(f"WAITING FOR OTHER PLAYERS ({counter} sec.)")
            await asyncio.sleep(matchmaking_interval)
            counter += matchmaking_interval
            await game.update()

        # check everything
        my_id = self._http.user_id

        assert my_id in game.players
        assert game.name == self.__game_name__
        assert game.state == GameState.STARTED
        assert game.open_slots == 0

        # PLAY
        is_ongoing = True

        logger.info(f"PLAYING THE GAME {game.id} ({my_id} vs. {', '.join([str(opp_id) for opp_id in self.opponents])})")

        while is_ongoing:
            await game.update()

            if not game.state == GameState.STARTED:
                break

            if self.is_active:
                is_ongoing = await self.make_turn()

            await asyncio.sleep(turn_interval)

        # evaluate result
        await game.update()

        return self.won

    @staticmethod
    def get_symbol(active_player):
        return 'XO'[active_player]

    @property
    def symbol(self):
        if self.game is not None:
            return self.get_symbol(self.game.active_player)
