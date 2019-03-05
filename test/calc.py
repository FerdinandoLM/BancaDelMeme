import sys
sys.path.append('src')
import os
import signal

import unittest
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import calculator
import config
from models import Base, Investor, Firm, Investment
from mock_praw import Comment, Submission, Reddit
from unittest.mock import Mock

class DoneException(BaseException):
    pass

def sleep_once(time):
    if time < 10:
        return
    raise DoneException()

class CalculatorTest(unittest.TestCase):
    def setUp(self):
        # create sqlite db
        engine = create_engine('sqlite:///.testenv/test.db')
        self.Session = session_maker = scoped_session(sessionmaker(bind=engine))
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()
        self.calculator = calculator
        self.calculator.time.sleep = sleep_once
        self.reddit = Reddit()
        self.calculator.praw.Reddit = Mock(return_value=self.reddit)
        self.calculator.create_engine = Mock(return_value=engine)

    def tearDown(self):
        # remove db file
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()

    def create_investment(self, amount, start_upvotes, end_upvotes):
        submission = Submission('sid1')
        comment = Comment('cid1', 'investor1', 'dummy', submission)
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
        investor = Investor(name='investor1')
        investment.time = int(time.time()) - config.INVESTMENT_DURATION - 1
        submission.ups = end_upvotes
        sess = self.Session()
        sess.add(investor)
        sess.add(investment)
        sess.commit()
        return investor, investment

    def test_base(self):
        try:
            investor, _ = self.create_investment(100, 0, 100)
            self.calculator.main()
        except DoneException:
            pass
        self.assertTrue(investor.balance != config.STARTING_BALANCE)        
