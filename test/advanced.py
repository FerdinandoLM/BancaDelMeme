from test import Test
import message

class TestAdvanced(Test):
    def test_sell(self):
        self.command('!create')
        replies = self.command('!investi 200')
        self.assertEqual(len(replies), 1)
        replies = self.command('!vendi')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_sell_investment(1))

    def test_sell_void(self):
        self.command('!create')
        replies = self.command('!vendi')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_sell_investment(0))

    def test_allin(self):
        self.command('!create')
        replies = self.command('!investi 200', post='testpost1')
        self.assertEqual(len(replies), 1)
        replies = self.command('!investitutto', post='testpost2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_invest(800, 100, 0))

    def test_allin_low(self):
        self.command('!create')
        replies = self.command('!investi 1000', post='testpost1')
        self.assertEqual(len(replies), 1)
        replies = self.command('!investitutto', post='testpost2')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.MIN_INVEST_ORG)
