import sys
sys.path.append('src')

import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import config
from comment_worker import CommentWorker
from models import Base, Investor, Firm, Investment
from mock_praw import Comment, Submission

class Test(unittest.TestCase):
    def setUp(self):
        # create sqlite db
        engine = create_engine(config.DB)
        self.Session = session_maker = scoped_session(sessionmaker(bind=engine))
        Base.metadata.create_all(engine)
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()

        self.worker = CommentWorker(session_maker)

    def tearDown(self):
        # remove db file
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()

    def command(self, command, username='testuser', post='testpost'):
        comment = Comment(post + '/id', username, command, Submission(post))
        self.worker(comment)
        return comment.replies

    def set_balance(self, balance, username='testuser'):
        sess = self.Session()
        investor = sess.query(Investor)\
            .filter(Investor.name == username)\
            .first()
        investor.balance = balance
        sess.commit()

    def set_firm_balance(self, firm_name, balance):
        sess = self.Session()
        firm = sess.query(Firm)\
            .filter(Firm.name == firm_name)\
            .first()
        firm.balance = balance
        sess.commit()
