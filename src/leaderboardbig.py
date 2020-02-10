"""Script to update wiki pages with investor and oc poster leaderboard."""
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
localtime = time.strftime("{%Y-%m-%d %H:%M:%S}")
wiki_lead_text_org = """
#Migliori utenti:

%TOP_USERS%  

Ultimo aggiornamento: %LOCALTIME%
"""

wiki_oc_text_org = """
#Migliori autori:

%TOP_OC%  

Ultimo aggiornamento: %LOCALTIME%
"""

# TODO: add docstring
def main():
    logging.info("Starting leaderboard...")

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    reddit = praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        username=config.USERNAME,
        password=config.PASSWORD,
        user_agent=config.USER_AGENT,
    )

    # We will test our reddit connection here
    if not config.TEST and not utils.test_reddit_connection(reddit):
        exit()

    sess = session_maker()

    top_users = (
        sess.query(
            Investor.name,
            func.coalesce(Investor.balance + func.sum(Investment.amount), Investor.balance).label(
                "networth"
            ),
        )
        .outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0))
        .group_by(Investor.name)
        .order_by(desc("networth"))
        .limit(500)
        .all()
    )

    top_users_text = ".|Utente|Patrimonio\n"
    top_users_text += ":-:|:-:|:-:\n"
    for i, user in enumerate(top_users):
        top_users_text += f"{i + 1}|/u/{user.name}|{formatNumber(user.networth)} M€\n"

    wiki_lead_text = wiki_lead_text_org.replace("%TOP_USERS%", top_users_text).replace(
        "%LOCALTIME%", localtime
    )

    logging.info(" -- Updating wiki text to:")
    logging.info(wiki_lead_text)
    if not config.TEST:
        wikipage = reddit.subreddit("BancaDelMeme").wiki["leaderboardbig"]
        wikipage.edit(wiki_lead_text)

    top_poster = sess.execute("""
    SELECT  name,
            SUM(oc) AS coc,
            SUM(CASE OC WHEN 1 THEN final_upvotes ELSE 0 END) AS soc,
            count(*) as ct,
            sum(final_upvotes) as st
    FROM "Buyables"
    WHERE done = 1 AND time > :since
    GROUP BY name
    ORDER BY coc DESC, soc DESC, ct DESC, st DESC""",
        {"since": 1579020536},
    )

    top_oc_text = "Autore|#OC|Karma OC|Post totali|Karma totali\n"
    top_oc_text += ":-:|:-:|:-:|:-:|:-:\n"
    for poster in top_poster:
        top_oc_text += f"/u/{poster[0]}|{poster[1]}|{poster[2]:,d}|{poster[3]}|{poster[4]:,d}\n"
    oc_text = wiki_oc_text_org.replace("%TOP_OC%", top_oc_text).replace("%LOCALTIME%", localtime)
    logging.info(" -- Updating wiki text to:")
    logging.info(oc_text)
    if not config.TEST:
        wikipage = reddit.subreddit("BancaDelMeme").wiki["leaderboardocbig"]
        wikipage.edit(oc_text)

    sess.commit()

    # Report the Reddit API call stats
    rem = int(reddit.auth.limits["remaining"])
    res = int(reddit.auth.limits["reset_timestamp"] - time.time())
    logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

    sess.close()


if __name__ == "__main__":
    main()
