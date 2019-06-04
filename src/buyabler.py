# TODO: add docstrin here
import logging
import time

import praw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import message
import utils
from models import Buyable, Investor, Investment
from stopwatch import Stopwatch
from utils import BALANCE_CAP, EmptyResponse, edit_wrap

logging.basicConfig(level=logging.INFO)


# TODO: rethink how to structure this main
# TODO: add docstring
def main():
    logging.info("Starting buyable...")

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

    praw.models.Comment.edit_wrap = edit_wrap

    stopwatch = Stopwatch()

    logging.info("Fetching active buyable...")

    sess = session_maker()

    then = int(time.time()) - config.INVESTMENT_DURATION
    buyables = sess.query(Buyable).\
        filter(Buyable.done == 0).\
        filter(Buyable.time < then).\
        order_by(Buyable.time.asc())

    for buyable in buyables:
        duration = stopwatch.measure()

        logging.info("New mature investment: %s", buyable.post)
        logging.info(" -- by %s", buyable.name)
        # Retrieve the post
        submission = reddit.submission(id=buyable.post)
        buyable.final_upvotes = submission.ups
        buyable.oc = (submission.link_flair_text == 'OC')
        if submission.deleted or submission.removed:
            logging.info(" -- deleted or removed")
            buyable.done = True
            sess.commit()
            duration = stopwatch.measure()
            logging.info(" -- processed in %.2fs", duration)
            continue
        if not buyable.oc:
            logging.info(" -- not OC")
            buyable.done = True
            sess.commit()
            duration = stopwatch.measure()
            logging.info(" -- processed in %.2fs", duration)
            continue

        # Retrieve OP
        investor = sess.query(Investor).filter(Investor.name == buyable.name).first()
        if not investor:
            logging.info(" -- OP not investor")
            buyable.done = True
            sess.commit()
            duration = stopwatch.measure()
            logging.info(" -- processed in %.2fs", duration)
            continue
        balance = investor.balance

        # Retrieve the post investments
        investments = sess.query(Investment)\
            .filter(Investment.post == buyable.post)\
            .filter(Investment.name != buyable.name)
        profit = 0
        net_worth = investor.networth(sess)
        for investment in investments:
            profit = min(int(investment.amount / 100), net_worth)

        # Updating the investor's balance
        new_balance = int(balance + profit)

        # Retrieve the bot's original response (lazily, no API call)
        if buyable.response != "0":
            response = reddit.comment(id=buyable.response)
        else:
            response = EmptyResponse()

        if new_balance < BALANCE_CAP:
            investor.balance = new_balance

            # Edit the bot's response (triggers an API call)
            logging.info(" -- profited %d", profit)

            response.edit_wrap(response.body + message.modify_oc_return(profit))
        else:
            # This investment pushed the investor's balance over the cap
            investor.balance = BALANCE_CAP

            # Edit the bot's response (triggers an API call)
            logging.info(" -- profited %d but got capped", profit)
            response.edit_wrap(response.body + message.modify_oc_capped())

        buyable.profit = profit
        buyable.done = True

        sess.commit()

        # Measure how long processing took
        duration = stopwatch.measure()
        logging.info(" -- processed in %.2fs", duration)

        # Report the Reddit API call stats
        rem = int(reddit.auth.limits['remaining'])
        res = int(reddit.auth.limits['reset_timestamp'] - time.time())
        logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

    sess.close()


if __name__ == "__main__":
    utils.keep_up(main)
