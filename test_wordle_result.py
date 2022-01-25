from wordle_result import WordleResult
from datetime import datetime, timedelta, date as datetime_date
from unittest.mock import Mock
from os import environ

CHANNEL = environ['wordle_bot_channel']

class Object():
    pass

def w_s(day, score):
    return f"Wordle {day} {score}/6"

class FakeMessage():
    def __init__(self, channel=CHANNEL, message=w_s(1, 2)):
        self.channel = Object()
        self.channel.name = channel
        self.content = message
        self.author = Object()
        self.author.id = 123
        self.author.nick = "nick"

def test_is_wordle_wrong_channel():
    wr = WordleResult(FakeMessage(channel="not correct"))
    assert not wr.is_wordle_message()

    wr = WordleResult(FakeMessage(channel=""))
    assert not wr.is_wordle_message()

    wr = WordleResult(FakeMessage(channel=None))
    assert not wr.is_wordle_message()

def test_is_wordle_right_channel():
    wr = WordleResult(FakeMessage(channel=CHANNEL))
    assert wr.is_wordle_message()

def test_is_wordle_wrong_mesage():
    wr = WordleResult(FakeMessage(message="not a wordle message"))
    assert not wr.is_wordle_message()

    wr = WordleResult(FakeMessage(message=""))
    assert not wr.is_wordle_message()

    wr = WordleResult(FakeMessage(message=None))
    assert not wr.is_wordle_message()

def test_is_wordle_right_message():
    wr = WordleResult(FakeMessage(message=w_s(1, 1)))
    assert wr.is_wordle_message()

def test_parse_days():
    wr = WordleResult(FakeMessage(message=w_s(196, 1)))
    wr.parse_result()

    assert wr.day == 196
    assert wr.actual_date == datetime.fromisoformat("2022-01-01")

    wr = WordleResult(FakeMessage(message=w_s(1, 1)))
    wr.parse_result()

    assert wr.day == 1
    assert wr.actual_date == (datetime.fromisoformat("2022-01-01") - timedelta(days=195))

    wr = WordleResult(FakeMessage(message=w_s(1000, 1)))
    wr.parse_result()

    assert wr.day == 1000
    assert wr.actual_date == (datetime.fromisoformat("2022-01-01") + timedelta(days=804))

def test_parse_score():
    for i in range(1, 7):
        wr = WordleResult(FakeMessage(message=w_s(1, i)))
        wr.parse_result()

        assert wr.score == i
        assert wr.modified_score == 7 - i

    wr = WordleResult(FakeMessage(message=w_s(1, 0)))
    wr.parse_result()
    assert wr.score == 0
    assert wr.modified_score <= 0

def test_parse_score_x():
    wr = WordleResult(FakeMessage(message=w_s(1, 'X')))
    wr.parse_result()

    assert wr.score == 7
    assert wr.modified_score == 0

def test_apply_score(mocker):

    wr = WordleResult(FakeMessage(message=w_s(1, 3)))
    wr.parse_result()

    def check_inputs(user_id, nickname, date, score):
        assert user_id == wr.author.id
        assert nickname == wr.author.nick
        assert date == wr.actual_date
        assert score == wr.modified_score

        assert isinstance(user_id, int)
        assert isinstance(date, datetime_date)
        assert isinstance(score, int)

    m = Mock(wraps=check_inputs)
    mocker.patch("wordle_store.WordleStore.add_or_update_score", m)
    mocker.patch("wordle_store.WordleStore.__init__", return_value=None)

    wr.apply_score()

    m.assert_called()

