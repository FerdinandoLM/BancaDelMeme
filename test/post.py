from test import Test
from mock_praw import Comment, Submission
import message
import help_info
import utils


class TestPost(Test):
    def test_template(self):
        post = Submission('post')
        comment = Comment('1/id', post.author.name, '!template https://i.imgur.com/asdas.jps', post)
        self.worker(comment)
        self.assertEqual(len(comment.replies), 1)
        self.assertEqual(comment.replies[0].body, message.TEMPLATE_SUCCESS)

    def test_template_not_op(self):
        post = Submission('post')
        comment = Comment('1/id', 'commenter', '!template https://i.imgur.com/asdas.jps', post)
        self.worker(comment)
        self.assertEqual(len(comment.replies), 1)
        self.assertEqual(comment.replies[0].body, message.TEMPLATE_NOT_OP)
