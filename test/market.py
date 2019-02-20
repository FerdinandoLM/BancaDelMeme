from test import Test
import message

class TestMarket(Test):
    def test_market(self):
        replies = self.command('!mercato')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_market(0, 0, 0))

        self.command('!create')
        replies = self.command('!mercato')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_market(0, 1000, 0))

        self.command('!invest 100')
        replies = self.command('!mercato')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_market(1, 900, 100))
