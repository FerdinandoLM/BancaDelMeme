"""Script to write a txt file with the full leaderboard a the and of a season"""
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

# TODO: add docstring
def main():
    logging.info("Starting leaderboard...")

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    reddit = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

    # We will test our reddit connection here
    if not utils.test_reddit_connection(reddit):
        exit()

    sess = session_maker()

    top_users = sess.query(
            Investor.name,
            func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth')).\
            outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
        group_by(Investor.name).\
        order_by(desc('networth')).\
        all()

    top_users_text = "Rank|User|Net Worth\n"
    top_users_text += ":-:|:-:|:-:\n"
    for i, user in enumerate(top_users):
        top_users_text += f"{i + 1}|/u/{user.name}|{formatNumber(user.networth)} M€\n"

    with open('stagione02.txt', 'wt') as oo:
        oo.write(top_users_text)

    sess.commit()

    # Report the Reddit API call stats
    rem = int(reddit.auth.limits['remaining'])
    res = int(reddit.auth.limits['reset_timestamp'] - time.time())
    logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

    sess.close()


if __name__ == "__main__":
    main()
