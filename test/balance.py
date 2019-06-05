from test import Test
import message

class TestBalance(Test):
    def test_balance(self):
        self.command('!create')

        replies = self.command('!saldo')
        self.assertEqual(replies[0].body, message.modify_balance(1000, 1000))

        self.set_balance(1234)

        replies = self.command('!saldo')
        self.assertEqual(replies[0].body, message.modify_balance(1234, 1234))

    def test_invested(self):
        self.command('!create')

        replies = self.command('!investi 100')

        replies = self.command('!saldo')
        self.assertEqual(replies[0].body, message.modify_balance(900, 1000))