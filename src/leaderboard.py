# TODO: add docstrin here
import logging
import time

import praw
from sqlalchemy import and_, create_engine, desc, func
from sqlalchemy.orm import sessionmaker

import config
import utils
from models import Investment, Investor
from utils import formatNumber

logging.basicConfig(level=logging.INFO)
localtime = time.strftime('{%Y-%m-%d %H:%M:%S}')
sidebar_text_org = """
/r/BancaDelMeme è un posto dove si puoi comprare, vendere, condividere, fare e investire sui meme liberamente.

*****

**Migliori utenti:**

%TOP_USERS%  


**Migliori autori di OC:**

%TOP_OC%  

Ultimo aggiornamento: %LOCALTIME%



^(Questo sub non è ***solo*** per templates. È rivolto a tutti i meme (in italiano), il tutto arricchito con un po' di sano gioco dei mercati)

###***[Inviaci dei suggerimenti!](https://www.reddit.com/message/compose?to=%2Fr%2FBancaDelMeme)***

&nbsp;

***

**Subreddit ai quali potresti essere interessato:**

/r/italy

***
***
"""


# TODO: add docstring
def main():
    logging.info("Starting leaderboard...")
    logging.info("Sleeping for 8 seconds. Waiting for the database to turn on...")
    time.sleep(8)

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    reddit = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

    # We will test our reddit connection here
    if not config.TEST and not utils.test_reddit_connection(reddit):
       exit()

    sess = session_maker()

    top_users = sess.query(
            Investor.name,
            func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth')).\
            outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
        group_by(Investor.name).\
        order_by(desc('networth')).\
        limit(10).\
        all()

    top_users_text = ".|Utente|Patrimonio\n"
    top_users_text += ":-:|:-:|:-:\n"
    for i, user in enumerate(top_users):
        top_users_text += f"{i + 1}|/u/{user.name}|{formatNumber(user.networth)} M€\n"

    top_users_text += """

[Classifica completa](/r/BancaDelMeme/wiki/leaderboardbig)"""

    sidebar_text = sidebar_text_org.\
        replace("%TOP_USERS%", top_users_text).\
        replace("%LOCALTIME%", localtime)

    # redesign
    if not config.TEST:
        for subreddit in config.SUBREDDITS:
            for widget in reddit.subreddit(subreddit).widgets.sidebar:
                if isinstance(widget, praw.models.TextArea):
                    if widget.shortName.lower().replace(" ", "") == 'top10':
                        widget.mod.update(text=top_users_text)
                        break

    top_poster = sess.execute("""
    SELECT  name,
            SUM(oc) AS coc,
            SUM(CASE OC WHEN 1 THEN final_upvotes ELSE 0 END) AS soc
    FROM "Buyables"
    WHERE done = 1 AND time > :since
    GROUP BY name
    ORDER BY coc DESC, soc DESC
    LIMIT :limit""", {"since": 1579020536, "limit": 5})

    top_poster_text = "Autore|#OC|Karma|\n"
    top_poster_text += ":-:|:-:|:-:|:-:|:-:\n"
    for poster in top_poster:
        top_poster_text += f"/u/{poster[0]}|{poster[1]}|{poster[2]}\n"
    top_poster_text += """

[Classifica completa](/r/BancaDelMeme/wiki/leaderboardocbig)"""
    sidebar_text = sidebar_text.\
        replace("%TOP_OC%", top_poster_text)
    if not config.TEST:
    # redesign
        for subreddit in config.SUBREDDITS:
            for widget in reddit.subreddit(subreddit).widgets.sidebar:
                if isinstance(widget, praw.models.TextArea):
                    if widget.shortName.lower() == 'migliori autori':
                        widget.mod.update(text=top_poster_text)
                        break

    # Sidebar update
    logging.info(" -- Updating sidebar text to:")
    logging.info(sidebar_text)
    if not config.TEST:
        for subreddit in config.SUBREDDITS:
            reddit.subreddit(subreddit).mod.update(description=sidebar_text)

    sess.commit()

    # Report the Reddit API call stats
    rem = int(reddit.auth.limits['remaining'])
    res = int(reddit.auth.limits['reset_timestamp'] - time.time())
    logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

    sess.close()


if __name__ == "__main__":
    main()
