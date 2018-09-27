from .abc import Match
from .enums import GameState
import logging
import time

logger = logging.getLogger(__name__)


class Core(Match):
    def make_turn(self):
        assert self.game is not None
        self.game.update()

        assert self.game.state == GameState.STARTED
        assert self.is_active

        board = self.game.current_board
        symbol = self.symbol

        x_pos, y_pos = self.callback(board, symbol)

        logger.info(f"MOVING TO ({str(x_pos)}, {str(y_pos)})")

        resp = None
        status_code = 401
        while status_code == 401:
            self._client.check_and_update_token()

            data = {"player": {"id": self._client.user_id, "token": self._client.token}, "turn": str([x_pos, y_pos])}

            resp = self.game.make_turn(data)

            status_code = resp.status_code

        return resp

    def play(self, turn_interval: int=5, matchmaking_interval: int=5):
        game = self.game

        assert game is not None

        game.update()

        counter = 0
        while game.state == GameState.WAITING:
            logger.info(f"WAITING FOR OTHER PLAYERS ({counter} sec.)")
            time.sleep(matchmaking_interval)
            counter += matchmaking_interval
            game.update()

        # check everything
        registered = False
        for counter, i in enumerate(self.game.players):
            if i['id'] == self._client.user_id:
                registered = True
                break

        assert registered
        assert game.name == self.__game_name__
        assert game.state == GameState.STARTED
        assert game.open_slots == 0

        # PLAY
        is_ongoing = True

        logger.info("PLAYING THE GAME " + str(game.id))

        while is_ongoing:
            game.update()

            if not game.state == GameState.STARTED:
                break

            if self.is_active:
                resp = self.make_turn()

                if resp.status_code == 200 and 'false' in resp.text:
                    is_ongoing = False

            time.sleep(turn_interval)

        # evaluate result
        game.update()

        return self.won

    @staticmethod
    def get_symbol(active_player):
        return 'XO'[active_player]

    @property
    def symbol(self):
        if self.game is not None:
            return self.get_symbol(self.game.active_player)
