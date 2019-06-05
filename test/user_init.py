from test import Test
import config
import message


class TestUserInit(Test):
    def test_create(self):
        replies = self.command('!create')
        self.assertEqual(len(replies), 1)
        self.assertEqual(
            replies[0].body,
            message.modify_create('testuser', 1000)
        )

    def test_crea(self):
        replies = self.command('!crea')
        self.assertEqual(len(replies), 1)
        self.assertEqual(
            replies[0].body,
            message.modify_create('testuser', 1000)
        )

    def test_already_created(self):
        replies = self.command('!create')
        replies = self.command('!create')
        self.assertEqual(len(replies), 1)
        self.assertEqual(
            replies[0].body,
            message.CREATE_EXISTS_ORG
        )

    def test_autocreate(self):
        replies = self.command('!saldo')
        self.assertEqual(len(replies), 2)
        self.assertEqual(
            replies[0].body,
            message.modify_create('testuser', config.STARTING_BALANCE)
        )
        self.assertEqual(
            replies[1].body,
            message.modify_balance(config.STARTING_BALANCE, config.STARTING_BALANCE)
        )
