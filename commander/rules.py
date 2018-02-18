import asyncio


class rules(object):
    
    def __init__(self):
        self.description = 'Used to show rules.'
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'rules'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!rules help (args)\n' +
                'For Example: ``e!rules help help`` - shows this message.',
            'show':
                'Displays the rules, but will delete them on the next command execution.\n' +
                'How to use this command: ``e!rules show``\n' +
                'For Example: ``e!rules show`` - shows the rules.',
            'permanent':
                'Pastes the rules permanently.\n' +
                'How to use this command: ``e!rules permanent``\n' +
                'For Example: ``e!rules permanent`` - pastes the rules permanently.'
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
                                colour=data.embed_error
                            ), msg.channel
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
                    if arg.lower() == 'show':
                        if msg.server.id not in data.servers:
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        '**Error:**',
                                        'No server config exists for this server yet, as such there are no set rules.'
                                    ]],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                        else:
                            s = data.servers[msg.server.id]
                            for rule in s.rules:
                                results.append(['', rule[1], msg.channel])
                    ###############################################################
                    if arg.lower() == 'permanent':
                        if not (msg.author.id == msg.server.owner.id or msg.author.id == data.id):
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        '**Error:**',
                                        'Insufficient permissions: You need to be the owner of ``' + msg.server.name +
                                        "`` or owner of this Bot to use this command."
                                    ]],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                        else:
                            if msg.server.id not in data.servers:
                                results.append([
                                    '',
                                    data.embedder(
                                        [[
                                            '**Error:**',
                                            'No server config exists for this server yet,' +
                                            ' as such there are no set rules.'
                                        ]],
                                        colour=data.embed_error
                                    ),
                                    msg.channel
                                ])
                            else:
                                s = data.servers[msg.server.id]
                                for rule in s.rules:
                                    yield from client.send_message(msg.channel, rule[0], embed=rule[1])
#############################################################################
                argpos += 1
            yield from data.messager(msg, results)
