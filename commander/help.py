import asyncio


class help(object):

    def __init__(self):
        self.description = 'Used to retrieve various kinds of information.'
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'help'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!help (args)\n' +
                'For Example: e!help help - shows this message.'
        }

    @asyncio.coroutine
    def execute(self, client, msg, data, args):
        if not data.can_use(self, msg):
            yield from data.messager(msg, [['', data.error(self, msg), msg.channel]])
            return

        if len(args) == 0:
            yield from data.messager(msg, data.help(msg, self))
            return
        else:
            results = []
            argpos = 0
            for arg in args:
                    if not (arg.lower() in self.commands or arg.lower() in data.cmds):
                        results.append([
                            '',
                            data.embedder(
                                [['**Error:**', "Couldn't recognise ``" + arg + '``.']],
                                colour=data.embed_error), msg.channel
                        ])
                        argpos += 1
                        continue
#############################################################################
                    if arg.lower() in self.commands:
                        n = data.help(msg, self, [arg.lower()])
                        for h in n:
                            results.append(h)
                    if arg.lower() in data.cmds:
                        n = data.help(msg, data.cmds[arg.lower()]())
                        for h in n:
                            results.append(h)
#############################################################################
            yield from data.messager(msg, results)
