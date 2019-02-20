import time

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

    def __str__(self):
        return self.id

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
