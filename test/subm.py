import sys
sys.path.append('src')

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import config
import submitter
import message
from models import Investor, Investment
import mock_praw
from unittest.mock import Mock, MagicMock

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
        engine = create_engine(config.DB)
        self.Session = scoped_session(sessionmaker(bind=engine))
        sess = self.Session()
        sess.query(Investment).delete()
        sess.query(Investor).delete()
        sess.commit()
        self.submitter = submitter
        self.submitter.time.sleep = sleep_func()
        self.reddit = mock_praw.Reddit()
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
        submission = self.reddit.subreddit().stream.submissions()[0]
        replies = submission.replies
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.invest_no_fee('u/' + submission.author.name))

    def test_sticky(self):
        submission = mock_praw.Submission('stickiedid')
        submission.stickied = True
        self.reddit.subreddit = MagicMock(return_value=MagicMock(stream=MagicMock(submissions=MagicMock(return_value=[submission]))))
        try:
            self.submitter.main()
        except DoneException:
            pass
        submission = self.reddit.subreddit().stream.submissions()[0]
        replies = submission.replies
        self.assertEqual(len(replies), 0)

    def test_old(self):
        submission = mock_praw.Submission('stickiedid')
        submission.created_utc = submission.created_utc - 100000
        self.reddit.subreddit = MagicMock(return_value=MagicMock(stream=MagicMock(submissions=MagicMock(return_value=[submission]))))
        try:
            self.submitter.main()
        except DoneException:
            pass
        submission = self.reddit.subreddit().stream.submissions()[0]
        print('aaaa', submission.stickied)
        replies = submission.replies
        self.assertEqual(len(replies), 0)
