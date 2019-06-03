# TODO: add docstrin here
import time
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, desc, and_
import praw

import config
import utils
import formula
import message
from kill_handler import KillHandler
from models import Investment, Investor, Firm
from stopwatch import Stopwatch
from calculator import BALANCE_CAP, EmptyResponse, edit_wrap

logging.basicConfig(level=logging.INFO)


# TODO: rethink how to structure this main
# TODO: add docstring
def close_active():
    logging.info("Starting Close active investments for season...")

    killhandler = KillHandler()

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

    logging.info("Monitoring active investments...")

    while not killhandler.killed:
        sess = session_maker()

        investment = sess.query(Investment).\
            filter(Investment.done == 0).\
            order_by(Investment.time.asc()).\
            first()

        if not investment:
            return ()

        duration = stopwatch.measure()

        investor = sess.query(Investor).filter(Investor.name == investment.name).one()
        # net_worth = sess.\
        #     query(func.sum(Investment.amount)).\
        #     filter(and_(Investment.name == investor.name, Investment.done == 0)).\
        #     scalar()\
        #     + investor.balance
        net_worth = 0

        logging.info("Investment: %s", investment.comment)
        logging.info(" -- by %s", investor.name)

        # Retrieve the post the user invested in (lazily, no API call)
        post = reddit.submission(investment.post)

        # Retrieve the post's current upvote count (triggers an API call)
        upvotes_now = post.ups
        investment.final_upvotes = upvotes_now

        # Updating the investor's balance
        factor = formula.calculate(upvotes_now, investment.upvotes, net_worth)
        amount = investment.amount
        balance = investor.balance

        new_balance = int(balance + (amount * factor))
        change = new_balance - balance
        profit = change - amount
        percent_str = f"{int((profit/amount)*100)}%"
        # FORCE best strategy
        if factor < 1:
            new_balance = int(balance + (amount * 1))
            change = amount
            profit = change - amount
            percent_str = f"{int((profit/amount)*100)}% - FORZATO"

        # Updating the investor's variables
        investor.completed += 1

        # Retrieve the bot's original response (lazily, no API call)
        if investment.response != "0":
            response = reddit.comment(id=investment.response)
        else:
            response = EmptyResponse()

        firm_profit = 0
        if new_balance < BALANCE_CAP:
            # If investor is in a firm and he profits,
            # 15% goes to the firm
            firm_name = ''
            if investor.firm != 0 and profit >= 0:
                firm = sess.query(Firm).\
                    filter(Firm.id == investor.firm).\
                    first()
                firm_name = firm.name

                user_profit = int(profit * ((100 - firm.tax) / 100))
                investor.balance += user_profit + amount

                firm_profit = int(profit * (firm.tax / 100))
                firm.balance += firm_profit
            else:
                investor.balance = new_balance

            # Edit the bot's response (triggers an API call)
            if profit > 0:
                logging.info(" -- profited %s", profit)
            elif profit == 0:
                logging.info(" -- broke even")
            else:
                logging.info(" -- lost %s", profit)

            edited_response = message.modify_invest_return(investment.amount, investment.upvotes,
                                                           upvotes_now, change, profit, percent_str,
                                                           investor.balance)
            if investor.firm != 0:
                edited_response += message.modify_firm_tax(firm_profit, firm_name)

            response.edit_wrap(edited_response)
        else:
            # This investment pushed the investor's balance over the cap
            investor.balance = BALANCE_CAP

            # Edit the bot's response (triggers an API call)
            logging.info(" -- profited %s but got capped", profit)
            response.edit_wrap(
                message.modify_invest_capped(investment.amount, investment.upvotes, upvotes_now,
                                             change, profit, percent_str, investor.balance))

        investment.success = (profit > 0)
        investment.profit = profit
        investment.done = True

        sess.commit()

        # Measure how long processing took
        duration = stopwatch.measure()
        logging.info(" -- processed in %.2fs", duration)

        # Report the Reddit API call stats
        rem = int(reddit.auth.limits['remaining'])
        res = int(reddit.auth.limits['reset_timestamp'] - time.time())
        logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

        sess.close()


def reset_balances():
    logging.info("Starting resetting balances...")

    killhandler = KillHandler()

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)
    sess = session_maker()

    stopwatch = Stopwatch()

    logging.info("Fetching investors...")
    stopwatch.measure()

    investors = sess.query(Investor).filter(Investor.balance != config.STARTING_BALANCE).all()
    duration = stopwatch.measure()
    logging.info(" -- processed in %.2fs", duration)

    for investor in investors:
        logging.info("%s | %d | %d | %d -> %d", investor.name, investor.completed, investor.broke,
                     investor.balance, config.STARTING_BALANCE)
        investor.balance = config.STARTING_BALANCE
        sess.commit()

        # Measure how long processing took
        duration = stopwatch.measure()
        logging.info(" -- processed in %.2fs", duration)

    sess.close()

def leaderboard():
    logging.info("Starting Wiki leaderboard...")
    stopwatch = Stopwatch()
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

    logging.info("Fetching investors...")
    stopwatch.measure()

    top_users = sess.query(
            Investor.name,
            func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth')).\
            outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
        group_by(Investor.name).\
        order_by(desc('networth')).\
        all()

    duration = stopwatch.measure()
    logging.info(" -- processed in %.2fs", duration)
    logging.info("Creating page content...")

    top_users_text = "Rank|User|Net Worth\n"
    top_users_text += ":-:|:-:|:-:\n"
    for i, user in enumerate(top_users):
        top_users_text += f"{i + 1}|/u/{user.name}|{formatNumber(user.networth)} M€\n"

    logging.info(" -- processed in %.2fs", duration)
    logging.info("Uploading page...")

    wiki_text = "# Stagione 1\n\nClassifica definitiva della stagione 1\n\n" + top_users_text

    wikipage = reddit.subreddit('bancadelmeme').wiki.create('stagione001', wiki_text)
    logging.info(" -- processed in %.2fs", duration)

    # Report the Reddit API call stats
    rem = int(reddit.auth.limits['remaining'])
    res = int(reddit.auth.limits['reset_timestamp'] - time.time())
    logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

    sess.close()

def formatNumber(n):
    suffixes = {
        6: 'M',
        9: 'B',
        12: 'T',
        15: 'Q'
    }
    digits = len(str(n))
    if digits <= 6:
        return '{:,}'.format(n)
    exponent = (digits - 1) - ((digits - 1) % 3)
    mantissa = n / (10 ** exponent)
    suffix = suffixes.get(exponent)
    return '{:.2f}{}'.format(mantissa, suffix)

if __name__ == "__main__":
    close_active()
    leaderboard()
    reset_balances()
