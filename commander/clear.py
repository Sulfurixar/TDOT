import asyncio


class clear(object):

    def __init__(self):
        self.description = 'Clears the reversible results of your commands.'
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'clear'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!clear help (args)\n' +
                'For Example: e!clear help help - shows this message.',
            'all':
                'Deletes all the messages sent by this bot during this session.\n' +
                'How to use this command: e!clear all\n' +
                'For Example: e!clear all - deletes all messages sent by Ely,not including embeds, during this session.'
        }

    @asyncio.coroutine
    def execute(self, client, msg, data, args):
        if not data.can_use(self, msg):
            yield from data.messager(msg, [['', data.error(self, msg), msg.channel]])
            return

        if len(args) == 0:
            c = 0
            if msg.author.id in data.messages:
                for message in data.messages[msg.author.id]:
                    if data.perms._user(data, client.user, [message.channel, 'manage messages']):
                        try:
                            yield from client.delete_message(message)
                            c += 1
                        except Exception as e:
                            print(repr(e))
                data.messages[msg.author.id] = []
            yield from data.messager(
                msg,
                [[
                    '',
                    data.embedder([['**Cleared your messages.**', 'Cleared a total of: ``' + str(c) + '`` messages.']]),
                    msg.channel
                ]]
            )
            yield from asyncio.sleep(10.0)
            for message in data.messages[msg.author.id]:
                    if data.perms._user(data, client.user, [message.channel, 'manage messages']):
                        try:
                            yield from client.delete_message(message)
                        except Exception as e:
                            print(repr(e))
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
                            '', data.embedder(
                                [['**Error:**', "Couldn't recognise ``" + arg + '``.']],
                                colour=data.embed_error
                            ),
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
                    ##########################
                    if arg.lower() == 'all':
                        if not (msg.author.id == data.id):
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        '**Error:**',
                                        'Insufficient permissions: ' +
                                        'You need to be the owner of this Bot to use this command.'
                                    ]],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                        else:
                            c = 0
                            if len(data.messages) > 0:
                                for entry in data.messages:
                                    for message in data.messages[entry]:
                                        if data.perms._user(data, client.user, [message.channel, 'manage messages']):
                                            try:
                                                yield from client.delete_message(message)
                                                c += 1
                                            except Exception as e:
                                                print(repr(e))
                                data.messages = {}
                            yield from data.messager(
                                msg,
                                [[
                                    '',
                                    data.embedder([[
                                        '**Cleared your messages.**', 'Cleared a total of: ``' + str(c) + '`` messages.'
                                    ]]),
                                    msg.channel
                                ]]
                            )
                            yield from asyncio.sleep(5.0)
                            for message in data.messages[msg.author.id]:
                                if data.perms._user(data, client.user, [message.channel, 'manage messages']):
                                    try:
                                        yield from client.delete_message(message)
                                    except Exception as e:
                                        print(repr(e))
                    ########################
#############################################################################
                argpos += 1
            yield from data.messager(msg, results)
