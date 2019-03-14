"""Script to collect taxes"""
import logging
import math

from sqlalchemy import and_, create_engine, desc, func
from sqlalchemy.orm import sessionmaker

import config
from models import Investment, Investor
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

NO_TAX = 2 * config.STARTING_BALANCE

RATES = [0, 23, 27, 38, 41, 43]
# Rates from https://it.wikipedia.org/wiki/Imposta_sul_reddito_delle_persone_fisiche


class TaxCollector():
    def __init__(self):
        engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
        session_maker = sessionmaker(bind=engine)

        self.sess = session_maker()

        logging.info("Calculating parameters...")
        stopwatch = Stopwatch()
        self.calc_tiers()
        duration = stopwatch.measure()

        logging.info("Rates : %s", RATES)
        logging.info("Tiers : %s", self.tiers)
        logging.info("Basics : %s", self.basics)
        logging.info(" -- calculated in %ss", duration)

    def collect(self):
        """Collect taxes"""
        logging.info("Fetching investors...")
        stopwatch = Stopwatch()
        investors = self.sess.query(Investor).\
            filter(Investor.completed > 0).\
            all()
        duration = stopwatch.measure()
        logging.info("Investors : %d", len(investors))
        logging.info(" -- fetched in %ss", duration)

        logging.info("Adjusting investors...")
        stopwatch.reset()
        for investor in investors:
            investor.balance = self.adjust_amount(investor)
        duration = stopwatch.measure()
        logging.info(" -- calculated in %ss", duration)

        logging.info("Committing ...")
        stopwatch.reset()
        self.sess.commit()
        self.sess.close()
        duration = stopwatch.measure()
        logging.info(" -- committed in %ss", duration)

    def calc_tiers(self):
        """"Calculate tiers and basics taxes"""
        top_tier_amunt = self.top_tier()
        logging.info("Top 1%% : %f", top_tier_amunt)
        deltas = (top_tier_amunt - NO_TAX) / (len(RATES) - 2)
        tiers = []
        basics = []
        for i, _ in enumerate(RATES):
            if i == 0:
                tiers.append(0)
                basics.append(0)
            elif i == 1:
                tiers.append(NO_TAX)
                basics.append(0)
            else:
                tiers.append(math.floor(tiers[-1] + deltas))
                basics.append(basics[-1] + math.floor((tiers[-1] - tiers[-2]) / 100 * RATES[i - 1]))
        self.basics = basics
        self.tiers = tiers

    def top_tier(self):
        """"Return the minimum amount to be in the top 1% of networth"""
        num_investors = self.sess.query(Investor).filter(Investor.completed != 0).count()
        top_users = self.sess.query(
            Investor.name,
            (func.coalesce(func.sum(Investment.amount), 0) + Investor.balance).label('networth')).\
            outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
            group_by(Investor.name).\
            order_by(desc('networth')).\
            limit(round(num_investors/100)).\
            all()
        return top_users[-1][1]

    def get_networth(self, investor):
        """Return the balance + invested amount"""
        investments = self.sess.query(Investment, \
                func.sum(Investment.amount)).\
                filter(Investment.done == 0).\
                filter(Investment.name == investor.name).\
                group_by(Investment.name).\
                first()
        if not investments:
            return investor.balance
        return investor.balance + investments[1]

    def adjust_amount(self, investor):
        """Change balance based on taxes"""
        networth = self.get_networth(investor)
        i = 0
        for i, tier in enumerate(self.tiers):
            if tier >= networth:
                i = i - 1
                break
        if i > 0:
            taxes = self.basics[i] + (networth - self.tiers[i]) / 100 * RATES[i]
            logging.info("Investor : %s (%d) - tier %d => -%d", investor.name, networth, i, taxes)
            return investor.balance - taxes
        return investor.balance


if __name__ == "__main__":
    COLLECTOR = TaxCollector()
    COLLECTOR.collect()
