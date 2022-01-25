import re
import os
from datetime import datetime, timedelta
from wordle_store import WordleStore

EMOJIS = {
    0: "0️⃣",
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣"
}

class WordleResult():
    def __init__(self, message):
        """
        Args:
            message (str): Message to check
        """
        self._message = message
        self.author = message.author

    def is_wordle_message(self):
        """
        Checks whether this message is a wordle message
        Sets the day and score attributes
        Returns:
            (bool): world or not
        """
        if self._message.channel.name != os.environ['wordle_bot_channel']:
            return False

        return self.parse_result()

    def parse_result(self):
        """
        Parses the result of the message
        Results:
            (bool): Whether a wordle string was parsed or not
        """
        try:
            result = re.search("Wordle (?P<day>\d+) (?P<score>[\dX])/6", self._message.content)
        except TypeError:
            return False

        if result:
            self.day = int(result.group('day'))
            try:
                self.score = int(result.group('score'))
            except ValueError:
                self.score = 7

            return True

        return False

    @property
    def modified_score(self):
        """
        7 - Score
        Returns:
            (int): Modified score
        """
        if self.score == 0:
            return -69

        return 7 - self.score

    @property
    def actual_date(self):
        """
        Get the actual date from the wordle day count
        Returns:
            (datetime): Datetime of the wordle day
        """
        return datetime.fromisoformat("2022-01-01") + timedelta(days=(self.day-196))

    def apply_score(self):
        """
        Apply the score for the given day
        """
        ws = WordleStore()
        ws.add_or_update_score(self.author.id, self.author.nick or self.author.name, self.actual_date, self.modified_score)

    async def show(self):
        """
        Perform an emoji on the user's message that shows it has been counted
        """

        emoji = EMOJIS.get(self.modified_score)

        await self._message.add_reaction(emoji)

