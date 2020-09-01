from test import Test
import config
import message

class TestAdvanced(Test):
    def test_sell(self):
        self.command('!create')
        replies = self.command('!investi 200')
        self.assertEqual(len(replies), 1)
        replies = self.command('!vendi')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_sell_investment(1, 0))

    def test_sell_taxes_max(self):
        INVESTMENT_DURATION = config.INVESTMENT_DURATION
        config.INVESTMENT_DURATION = 86400
        self.command('!create')
        replies = self.command('!investi 100')
        self.assertEqual(len(replies), 1)
        replies = self.command('!vendi')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_sell_investment(1, 99))
        config.INVESTMENT_DURATION = INVESTMENT_DURATION

    def test_sell_taxes(self):
        INVESTMENT_DURATION = config.INVESTMENT_DURATION
        config.INVESTMENT_DURATION = 16 * 60 * 60
        self.command('!create')
        replies = self.command('!investi 100')
        self.assertEqual(len(replies), 1)
        replies = self.command('!vendi')
        self.assertEqual(len(replies), 1)
        # 16^(1.5) = 64
        self.assertEqual(replies[0].body, message.modify_sell_investment(1, 64))
        config.INVESTMENT_DURATION = INVESTMENT_DURATION

    def test_sell_removed(self):
        INVESTMENT_DURATION = config.INVESTMENT_DURATION
        config.INVESTMENT_DURATION = 16 * 60 * 60
        self.command('!create')
        replies = self.command('!investi 100')
        self.assertEqual(len(replies), 1)
        replies = self.command('!vendi', lpost=lambda submission: setattr(submission, 'removed', True))
        self.assertEqual(len(replies), 1)
        # No taxes
        self.assertEqual(replies[0].body, message.modify_sell_investment(1, 0))
        config.INVESTMENT_DURATION = INVESTMENT_DURATION

    def test_sell_deleted(self):
        INVESTMENT_DURATION = config.INVESTMENT_DURATION
        config.INVESTMENT_DURATION = 16 * 60 * 60
        self.command('!create')
        replies = self.command('!investi 100')
        self.assertEqual(len(replies), 1)
        replies = self.command('!vendi')
        self.assertEqual(len(replies), 1)
        replies = self.command('!vendi', lpost=lambda submission: setattr(submission, 'author', None))
        # No taxes
        self.assertEqual(replies[0].body, message.modify_sell_investment(1, 0))
        config.INVESTMENT_DURATION = INVESTMENT_DURATION

    def test_sell_void(self):
        self.command('!create')
        replies = self.command('!vendi')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_sell_investment(0, 0))

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
        self.assertEqual(replies[0].body, message.modify_min_invest(0))
