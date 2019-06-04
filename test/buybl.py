import sys
sys.path.append('src')

import time
import unittest
from unittest.mock import Mock, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import buyabler
import config
from models import Investor, Investment, Buyable
from mock_praw import Comment, Submission, Reddit

class BuyableTest(unittest.TestCase):
    def setUp(self):
        # create sqlite db
        engine = create_engine(config.DB)
        sess_maker = scoped_session(sessionmaker(bind=engine))
        self.session = sess_maker()
        self.session.query(Buyable).delete()
        self.session.query(Investment).delete()
        self.session.query(Investor).delete()
        self.session.commit()
        self.buyabler = buyabler
        self.reddit = Reddit()
        self.buyabler.praw.Reddit = Mock(return_value=self.reddit)
        self.buyabler.create_engine = Mock(return_value=engine)

    def tearDown(self):
        # remove db file
        self.session.query(Buyable).delete()
        self.session.query(Investment).delete()
        self.session.query(Investor).delete()
        self.session.commit()
        self.session.close()

    def create_investment(self, amount, iid='0'):
        investor = Investor(name='investor' + iid)
        submission = Submission('sid' + iid)
        comment = Comment('cid' + iid, investor.name, 'dummy', submission)
        self.reddit.add_submission(submission)
        investment = Investment(
            post=comment.submission.id,
            upvotes=1,
            comment=comment.id,
            name=comment.author.name,
            amount=amount,
            response="0",
            done=False,
        )
        buyable = Buyable(post=submission.id, name=submission.author.name, response='brid' + iid)
        buyable.time = int(time.time()) - config.INVESTMENT_DURATION - 1
        sess = self.session
        sess.add(buyable)
        sess.add(investor)
        sess.add(investment)
        sess.commit()
        return investor, buyable, submission

    def test_not_oc(self):
        investor, _, submission = self.create_investment(100, iid='0')
        self.buyabler.main()
        sess = self.session
        investor = sess.query(Investor).\
            filter(Investor.name == investor.name).\
            one()
        self.assertTrue(investor.balance == config.STARTING_BALANCE)
        buyable = sess.query(Buyable).\
            filter(Buyable.post == submission.id).\
            one()
        self.assertTrue(buyable.done)
        self.assertTrue(not buyable.oc)
        self.assertEqual(buyable.profit, 0)

    def test_base(self):
        investor, buyable, submission = self.create_investment(1000, iid='1')
        submission.link_flair_text = 'OC'
        investor = Investor(name=submission.author.name)
        sess = self.session
        sess.add(investor)
        sess.commit()
        self.buyabler.main()
        investor = sess.query(Investor).\
            filter(Investor.name == submission.author.name).\
            one()
        self.assertTrue(investor.balance != config.STARTING_BALANCE)
        buyable = sess.query(Buyable).\
            filter(Buyable.post == submission.id).\
            one()
        self.assertTrue(buyable.done)
        self.assertTrue(buyable.oc)
        self.assertTrue(buyable.profit > 0)

    def test_not_investor(self):
        _, buyable, submission = self.create_investment(100, iid='2')
        submission.link_flair_text = 'OC'
        self.buyabler.main()
        sess = self.session
        buyable = sess.query(Buyable).\
            filter(Buyable.post == submission.id).\
            one()
        self.assertTrue(buyable.done)
        self.assertEqual(buyable.profit, 0)

    def test_deleted(self):
        investor, _, submission = self.create_investment(100, iid='3')
        submission.deleted = True
        investor = Investor(name=submission.author.name)
        sess = self.session
        sess.add(investor)
        sess.commit()
        self.buyabler.main()
        investor = sess.query(Investor).\
            filter(Investor.name == submission.author.name).\
            one()
        self.assertTrue(investor.balance == config.STARTING_BALANCE)
        buyable = sess.query(Buyable).\
            filter(Buyable.post == submission.id).\
            one()
        self.assertTrue(buyable.done)
        self.assertEqual(buyable.profit, 0)
