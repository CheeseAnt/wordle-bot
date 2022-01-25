from wordle.wordle_store import WordleStore
from datetime import datetime, timedelta
from os import remove
from os.path import join
import pytest


@pytest.fixture()
def w(tmp_path):
    p = join(tmp_path, "test_db.db")
    yield WordleStore(db=p)
    try:
        remove(p)
    except:
        pass


def test_wordle_store_create(w):
    pass


def test_add_score(w):
    d = datetime.now()
    w.add_score(1, "nick", d, 1)
    w.add_score(2, "nick2", d, 2)
    w.add_score(3, "nick3", d, 3)

    r = w.get_weekly_leaderboard()
    print(r)

    assert len(r) == 3
    assert r.user_id[0] == 1
    assert r.nickname[0] == "nick"
    assert r.score[0] == 1
    assert r.date[0] == d


def test_update_score(w):
    d = datetime.now()
    w.add_score(3, "nickn", d, 2)

    r = w.get_weekly_leaderboard()

    assert len(r) == 1
    assert r.user_id[0] == 3
    assert r.nickname[0] == "nickn"
    assert r.score[0] == 2
    assert r.date[0] == d

    w.update_score(3, "nickn2", d, 5)

    r = w.get_weekly_leaderboard()

    assert len(r) == 1
    assert r.user_id[0] == 3
    assert r.nickname[0] == "nickn2"
    assert r.score[0] == 5
    assert r.date[0] == d


def test_add_or_update_score(w):
    d = datetime.now()
    w.add_or_update_score(3, "nic", d, 2)

    r = w.get_weekly_leaderboard()

    assert len(r) == 1
    assert r.user_id[0] == 3
    assert r.nickname[0] == "nic"
    assert r.score[0] == 2
    assert r.date[0] == d

    w.add_or_update_score(3, "nic2", d, 5)

    r = w.get_weekly_leaderboard()

    assert len(r) == 1
    assert r.user_id[0] == 3
    assert r.nickname[0] == "nic2"
    assert r.score[0] == 5
    assert r.date[0] == d


def test_weekly_leaderboard(w):
    d = datetime.today().date()

    def t(i=0):
        return d - timedelta(days=i)

    w.add_score(1, "n", t(), 0)
    w.add_score(1, "n", t(1), 1)
    w.add_score(1, "n", t(2), 2)
    w.add_score(1, "n", t(3), 3)
    w.add_score(1, "n", t(4), 4)
    w.add_score(1, "n", t(5), 5)
    w.add_score(1, "n", t(6), 6)
    w.add_score(1, "n", t(7), 7)

    r = w.get_weekly_leaderboard()
    print(r.date)

    assert len(r) == d.weekday() + 1
    assert set(r.nickname) == {"n"}
    assert set(r.score) == set(list(range(d.weekday() + 1)))


def test_weekly_leaderboard_markdown(w):
    d = datetime.today().date()

    def t(i=0):
        return d - timedelta(days=i)

    w.add_score(1, "n", t(), 4)
    w.add_score(1, "n", t(2), 3)
    w.add_score(1, "n", t(3), 2)
    w.add_score(1, "n", t(5), 1)
    w.add_score(1, "n", t(6), 0)
    w.add_score(1, "n", t(7), 5)

    r = w.get_markdown_leaderboard()

    assert isinstance(r, str)

    print(r)
