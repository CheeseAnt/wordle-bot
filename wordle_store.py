import sqlite3
import pandas as pd
from datetime import datetime, date as datetime_date, timedelta

class WordleStore():
    def __init__(self, db='wordle.db'):
        self.con = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cur = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Create the Wordle tables in the DB
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS wordle_scores
                (user_id integer, nickname text, date timestamp, score integer, PRIMARY KEY (user_id, date))
        """)
        self.con.commit()

    def assert_inputs(self, user_id, nickname, date, score):
        assert isinstance(user_id, int)
        assert isinstance(score, int)
        assert isinstance(nickname, str)
        if isinstance(date, datetime_date) and not isinstance(date, datetime):
            date = datetime.combine(date, datetime.min.time())
        assert isinstance(date, datetime)

        return date

    def add_score(self, user_id, nickname, date, score):
        """
        Add a score for a given user id at the date
        Args:
            user_id (int): Integer discord User ID
            nickname (str): String last known nickname for this user
            date (datetime): Datetime date object
            score (int): User's score for the date
        """
        date = self.assert_inputs(user_id, nickname, date, score)

        self.cur.execute(f"""
            INSERT INTO wordle_scores VALUES
                ('{user_id}', '{nickname}', '{date}', '{score}');
        """)
        self.con.commit()

    def update_score(self, user_id, nickname, date, score):
        """
        Update a score for a given user id at the date
        Args:
            user_id (int): Integer discord User ID
            nickname (str): String last known nickname for this user
            date (datetime): Datetime date object
            score (int): User's score for the date
        """
        date = self.assert_inputs(user_id, nickname, date, score)

        self.cur.execute(f"""
            UPDATE wordle_scores
            SET score = '{score}',
                nickname = '{nickname}'
            WHERE user_id = '{user_id}'
            AND date = '{date}';
        """)
        self.con.commit()

    def add_or_update_score(self, user_id, nickname, date, score):
        """
        Add or update the score if it already exists
        Args:
            user_id (int): Integer discord User ID
            nickname (str): String last known nickname for this user
            date (datetime): Datetime date object
            score (int): User's score for the date
        """
        try:
            self.add_score(user_id, nickname, date, score)
            print(f"Added score {score} to user {nickname}")
        except sqlite3.IntegrityError:
            self.update_score(user_id, nickname, date, score)
            print(f"Updated score {score} to user {nickname}") 

    def get_last_sunday(self):
        """
        Gets the date of last sunday
        Returns:
            (datetime): Last sunday
        """
        today = datetime.today()
        sunday = today.date() - timedelta(days=today.weekday()+1)

        return datetime.combine(sunday, datetime.min.time())

    def get_weekly_leaderboard(self, offset=0):
        """
        Get the leaderboard for the week
        Args:
           offset (int): Offset (backwards) in weeks 
        Returns:
            (pd.DataFrame): This week's stats
        """
        last_sunday = self.get_last_sunday()

        if offset:
            last_sunday = last_sunday - timedelta(days= 7 * abs(offset))

        next_sunday = last_sunday + timedelta(days=7)

        res = self.cur.execute(f"""
            SELECT * from wordle_scores
            WHERE date > '{last_sunday}'
            AND date <= '{next_sunday}'
        """).fetchall()

        df = pd.DataFrame(res, columns=('user_id', 'nickname', 'date', 'score'))
        df.sort_values(inplace=True, by=['score', 'nickname'], axis=0, ascending=False)

        return df

    def get_top_three(self, offset=0):
        """
        Get the top three scores
        Args:
            offset (int): Weekly offset to get top three from
        Returns
            (str): String of top three scores
        """
        df = self.get_weekly_leaderboard(offset=offset)
        names = {r.user_id:r.nickname for r in df.itertuples()}
        df = df.groupby('user_id').sum()
        df.index = [names[d] for d in df.index]
        scores = list(set(df.score))
        scores.sort(reverse=True)

        top_three = ""

        def join_people(people):
            part = ", ".join(people[:-1])

            if part:
                part += f" and {people[-1]}"
            else:
                part = people[0]

            return part

        if len(scores) > 0:
            people = list(df.loc[df.score==scores[0]].index)
            top_three = "👑 " + join_people(people) + "\n"

        if len(scores) > 1:
            people = list(df.loc[df.score==scores[1]].index)
            top_three += "🏆 " + join_people(people) + "\n"

        if len(scores) > 2:
            people = list(df.loc[df.score==scores[2]].index)
            top_three += "🎖" + join_people(people) + "\n"

        return top_three
    
    def get_user_list(self):
        """
        Returns the list of user ids for this week
        Returns:
            (list): List of integer user ids 
        """
        return self.get_weekly_leaderboard().user_id

    def get_markdown_leaderboard(self, offset=0):
        """
        Get the leaderboard for the week, returning it as markdown
        Args:
           offset (int): Offset (backwards) in weeks 
        Returns:
            (str): This week's stats as a markdown string
        """
        dat = self.get_weekly_leaderboard(offset)

        if dat.empty:
            return "All outta scores"
        
        # get all unique days
        dates = list(dat.date.unique())
        dates.sort()
        
        # convert to day names (monday, tuesday etc)
        dates = pd.Series(dates).dt.day_name()
        dat.index=dat.date.dt.day_name()
 
        dat = dat.groupby('user_id')

        # assign columns and count totals
        table = pd.DataFrame()
        table.index = dates
        totals = list()
        for user, df in dat:
            table[df.nickname[-1]] = df.score.astype('str')
            totals.append(df.score.sum())

        # fill NaNs and make shorten column names
        table.fillna("", inplace=True)
        table = table.transpose()
        table.columns = [c[:3] for c in table.columns]

        # assign totals and do namewise sorting, then scorewise sorting
        table["totals"] = totals
        table.sort_index(inplace=True)
        table.sort_values(by="totals", ascending=False, inplace=True)
        table.rename(columns={"totals":""}, inplace=True)
        table.index.name = "UsEr"

        return f"`{table.to_markdown(index=True,tablefmt='pretty')}`"

    def __del__(self):
        try:
            self.con.close()
        except Exception:
            pass

