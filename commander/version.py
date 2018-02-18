import asyncio


class version(object):

    def __init__(self):
        self.description = "Displays current Elybot version."
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'version'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!version help (args)``\n' +
                'For Example: ``e!version help help`` - shows this message.',
            'show':
                'Displays current version name.\n' +
                'How to use this command: ``e!version show``\n' +
                'For Example: ``e!version show`` - shows the current version.'
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
                    if arg.lower() == 'show':
                        results.append(['', data.embedder([['**Current Version: **', data.version]]), msg.channel])
                    ##########################
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
