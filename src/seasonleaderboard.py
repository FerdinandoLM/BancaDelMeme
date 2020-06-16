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

    with open('stagione03.txt', 'wt') as oo:
        oo.write(top_users_text)

    sess.close()


if __name__ == "__main__":
    main()
