import asyncio
import datetime


class ping(object):

    def __init__(self):
        self.description = 'Used to measure and test the internet connection between the server and Ely.'
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'ping'
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

        if len(args) == 0:
            t1 = datetime.datetime.now()
            m1 = yield from client.send_message(msg.channel, 'Pong! ``' + t1.strftime("%Y-%m-%d %H:%M:%S") + '``')
            yield from client.delete_message(m1)
            t2 = datetime.datetime.now()
            pt = t2 - t1
            ms = (pt.seconds*1000 + pt.microseconds/1000)/2
            yield from data.messager(
                msg,
                [[
                    '',
                    data.embedder([['**Ping results:**', 'Mean average connection speed: ``' + str(ms) + 'ms``.']]),
                    msg.channel
                ]]
            )
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
                        t1 = datetime.datetime.now()
                        m1 = yield from client.send_message(
                            msg.channel, 'Pong! ``' + t1.strftime("%Y-%m-%d %H:%M:%S") + '``'
                        )
                        yield from client.delete_message(m1)
                        t2 = datetime.datetime.now()
                        pt = t2 - t1
                        ms = (pt.seconds*1000 + pt.microseconds/1000)/2
                        results.append([
                            '',
                            data.embedder([[
                                '**Ping results:**',
                                'Mean average connection speed: ``' + str(ms) +
                                'ms``.'
                            ]]),
                            msg.channel
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
##############################################################################
                argpos += 1
            yield from data.messager(msg, results)