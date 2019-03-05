import sys
sys.path.append('src')
import os
import signal

import unittest
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import submitter
import config
from models import Base, Investor, Firm, Investment
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

class SubmitterTest(unittest.TestCase):
    def setUp(self):
        # create sqlite db
        engine = create_engine('sqlite:///.testenv/test.db')
        self.Session = session_maker = scoped_session(sessionmaker(bind=engine))
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()
        self.submitter = submitter
        self.submitter.time.sleep = sleep_func()
        self.reddit = Reddit()
        self.submitter.praw.Reddit = Mock(return_value=self.reddit)
        self.submitter.create_engine = Mock(return_value=engine)

    def tearDown(self):
        # remove db file
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()

    def test_base(self):
        try:
            self.submitter.main()
        except DoneException:
            pass
        replies = self.reddit.subreddit().stream.submissions()[0].replies
        self.assertEqual(len(replies), 1)
