import time
from unittest.mock import MagicMock


class Redditor():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Submission():
    def __init__(self, submission_id, author=Redditor('submitter'), ups=100):
        self.id = submission_id
        self.author = author
        self.ups = ups
        self.replies = []
        self.stickied = False
        self.created_utc = int(time.time())
        self.link_flair_text = ''
        self.removed = False

    def __str__(self):
        return self.id

    def reply_wrap(self, body):
        comment = Comment(self.id + '/r', 'replyer', body, self)
        self.replies.append(comment)
        return comment


class Comment():
    def __init__(self, comment_id, author_name, body, submission):
        self.id = comment_id
        self.is_root = False
        self.author = Redditor(author_name)
        self.created_utc = time.time()
        self.body = body
        self.replies = []
        self.submission = submission
        self.edited = False
        self.stickied = False
        self.mod = MagicMock()

    def reply_wrap(self, body):
        comment = Comment(self.id + '/r', 'replyer', body, self.submission)
        self.replies.append(comment)
        return comment

    def edit_wrap(self, body):
        self.body = body
        self.edited = True

    def parent(self):
        parent = Comment(self.id + '/p', 'parentComment', 'body', self.submission)
        parent.stickied = True
        return parent

    def refresh(self):
        pass

    @property
    def is_submitter(self):
        return self.author.name == self.submission.author.name


class Reddit():
    def __init__(self, *args, **kwargs):
        self.user = MagicMock()
        self.submissions = {}
        self.auth = MagicMock()
        self.subreddit = MagicMock(return_value=Subreddit())

    def submission(self, id):
        return self.submissions.get(id, None)

    def comment(self, id):
        return Comment(id, 'commenter', '', 'sub_comment')

    def add_submission(self, submission):
        self.submissions[submission.id] = submission


class Subreddit():
    def __init__(self, *args, **kwargs):
        self.stream = MagicMock(submissions=MagicMock(return_value=[Submission('id')]))
