import asyncio


class mute(object):

    def __init__(self):
        self.description = 'Used to mute people!'
        self.permissions = ['administrator']
        self.Owner = False
        self.bOwner = False
        self.name = 'mute'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!get help (args)``\n' +
                'For Example: ``e!get help help`` - shows this message.\n'
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
            skip = 0
            argpos = 0
            for arg in args:
                if skip > 0:
                    skip -= 1
                    argpos += 1
                    continue
                else:
                    if arg.lower() not in self.commands:
                        results.append([
                            '',
                            data.embedder(
                                [['**Error:**', "Couldn't recognise ``" + arg + '``.']],
                                colour=data.embed_error), msg.channel
                        ])
                        argpos += 1
                        continue
                    #############################################################################
                    if arg.lower() == 'help':
                        if len(args[argpos + 1:]) > 0:
                            _help = data.help(msg, self, args[argpos + 1:])
                            skip = len(args[argpos + 1:])
                        else:
                            _help = data.help(msg, self)
                        for h in _help:
                            results.append(h)
                    ##########################
                ##############################################################################
                argpos += 1
            yield from data.messager(msg, results)