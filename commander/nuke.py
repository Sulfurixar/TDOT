import asyncio


class nuke(object):

    def __init__(self):
        self.description = 'Some people jut wish to see the world burn!'
        self.permissions = []
        self.Owner = False
        self.bOwner = True
        self.name = 'nuke'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!ping help (args)``\n' +
                'For Example: ``e!get help help`` - shows this message.'
        }

    @asyncio.coroutine
    def execute(self, client, msg, data, args):
        if not data.can_use(self, msg):
            yield from data.messager(msg, [['', data.error(self, msg), msg.channel]])
            return
        return
