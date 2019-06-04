import sys
sys.path.append('src')

import unittest
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import calculator
import config
from models import Investor, Investment
from mock_praw import Comment, Submission, Reddit
from unittest.mock import Mock

class DoneException(BaseException):
    pass

def sleep_func():
    done = False
    def sleep(_):
        nonlocal done
        if not done:
            done = True
            return
        raise DoneException()
    return sleep

class CalculatorTest(unittest.TestCase):
    def setUp(self):
        # create sqlite db
        engine = create_engine(config.DB)
        self.Session = scoped_session(sessionmaker(bind=engine))
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()
        self.calculator = calculator
        self.calculator.time.sleep = sleep_func()
        self.reddit = Reddit()
        self.calculator.praw.Reddit = Mock(return_value=self.reddit)
        self.calculator.create_engine = Mock(return_value=engine)

    def tearDown(self):
        # remove db file
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()

    def create_investment(self, amount, start_upvotes, end_upvotes, iid='0'):
        investor = Investor(name='investor' + iid)
        submission = Submission('sid' + iid)
        comment = Comment('cid' + iid, investor.name, 'dummy', submission)
        self.reddit.add_submission(submission)
        investment = Investment(
            post=comment.submission.id,
            upvotes=start_upvotes,
            comment=comment.id,
            name=comment.author.name,
            amount=amount,
            response="0",
            done=False,
        )
        investment.time = int(time.time()) - config.INVESTMENT_DURATION - 1
        submission.ups = end_upvotes
        sess = self.Session()
        sess.add(investor)
        sess.add(investment)
        sess.commit()
        return investor, investment

    def test_base(self):
        try:
            investor, _ = self.create_investment(100, 0, 100, '0')
            self.create_investment(100, 100, 100, '1')
            self.create_investment(100, 100, 169, '2')
            self.create_investment(calculator.BALANCE_CAP, 0, 100, 'top')
            self.calculator.main()
        except DoneException:
            pass
        sess = self.Session()
        investor = sess.query(Investor).\
            filter(Investor.name == investor.name).\
            one()
        self.assertTrue(investor.balance != config.STARTING_BALANCE)
