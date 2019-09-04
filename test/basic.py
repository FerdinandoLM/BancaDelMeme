from test import Test
import message
import help_info
import utils

class TestBasic(Test):
    def test_non_command(self):
        replies = self.command('saldo')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.cmd_sconosciuto())

    def test_ignore(self):
        replies = self.command('!ignora')
        self.assertEqual(len(replies), 0)

    def test_ignorato(self):
        replies = self.command('!nonesiste')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.cmd_sconosciuto())

    def test_help(self):
        replies = self.command('!aiuto')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.HELP_ORG)

    def test_help_detail(self):
        replies = self.command('!aiuto investi')
        self.assertEqual(len(replies), 1)
        self.assertTrue(help_info.help_dict['investi'] in replies[0].body)

    def test_version(self):
        replies = self.command('!versione')
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].body, message.modify_deploy_version(utils.DEPLOY_DATE))
