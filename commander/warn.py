import discord
import asyncio
import datetime


class warn(object):

    def __init__(self):
        self.description = "Used to warn people of their mischievous actions."
        self.permissions = ['administrator']
        self.Owner = False
        self.bOwner = False
        self.name = 'warn'
        self.tick = True
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!warn help (args)``\n' +
                'For Example: ``e!warn help help`` - shows this message.',
            'show':
                'Displays the warnings that are currently active.\n' +
                'How to use this command: ``e!warn show``\n' +
                'For Example: ``e!warn show`` - shows the active warnings.'
        }

    @asyncio.coroutine
    def ticker(self, client, data):
        for server in data.servers:
            if 'warnings' in data.servers[server].custom_data:
                w = data.servers[server].custom_data['warnings']
                if len(w) > 0:
                    for user in w:
                        nwarnings = []
                        if len(w[user]) > 0:
                            for entry in w[user]:
                                date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S.%f')
                                curdate = datetime.datetime.now()
                                diff = (date.year - curdate.year) * 12 + date.month - curdate.month
                                if diff < 3:
                                    nwarnings.append(entry)
                            w[user] = nwarnings

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
                        whitelist = []
                        skip = 0
                        try:
                            n_args = args[argpos + 1:]
                            skip = len(n_args)
                            for name in n_args:
                                user = None
                                if '@' in name:
                                    name = name[2:len(name) - 1]
                                    if name[0] == '!':
                                        name = name[1:]
                                    user = msg.server.get_member(name)
                                else:
                                    user = discord.utils.find(lambda m: m.display_name == name[1:], msg.server.members)
                                if user is None:
                                    user = discord.utils.find(lambda m: m.id == name, msg.server.members)
                                if user is None:
                                    results.append([
                                        '',
                                        data.embedder(
                                            [['**Error:**', 'Specified user: ``' + name + '`` could not be found.']]
                                        ),
                                        msg.channel
                                    ])
                                else:
                                    whitelist.append(user)
                        except IndexError:
                            pass
                        if 'warnings' in data.servers[msg.server.id].custom_data:
                            if len(data.servers[msg.server.id].custom_data['warnings']) > 0:
                                users = {}
                                for user in data.servers[msg.server.id].custom_data['warnings']:
                                    if len(data.servers[msg.server.id].custom_data['warnings'][user]) > 0:
                                        d = '<@' + user + '>\n'
                                        c = 0
                                        for entry in data.servers[msg.server.id].custom_data['warnings'][user]:
                                            d += str(c) + ') ' + entry['reason'] + ' - ``' + entry['date'] + '``.\n'
                                            c += 1
                                        users[user] = d
                                for user in users:
                                    _id = user
                                    name = discord.utils.find(lambda m: m.id == user, msg.server.members)
                                    if name is not None:
                                        user = name.display_name + ':' + name.id
                                    else:
                                        user = ':' + user
                                    if len(whitelist) > 0:
                                        for entry in whitelist:
                                            if _id == entry.id:
                                                results.append([
                                                    '',
                                                    data.embedder([['Warnings for: ' + user, users[_id]]]),
                                                    msg.channel
                                                ])
                                    else:
                                        results.append([
                                            '',
                                            data.embedder([['Warnings for: ' + user, users[_id]]]), msg.channel
                                        ])
                    ##########################
                    if arg.lower() not in self.commands:
                        name = arg
                        skip = len(args[argpos + 1:])
                        message = ' '.join(args[argpos + 1:])
                        user = None
                        if '@' in name:
                            user = msg.mentions[0]
                        else:
                            user = discord.utils.find(lambda m: m.display_name == name[1:], msg.server.members)
                        if user is None:
                            user = discord.utils.find(lambda m: m.id == name, msg.server.members)
                        if user is None:
                            results.append([
                                '',
                                data.embedder([['**Error:**', 'Specified user: ``' + arg + '`` could not be found.']]),
                                msg.channel
                            ])
                        else:
                            warnings = {}
                            if 'warnings' in data.servers[msg.server.id].custom_data:
                                warnings = data.servers[msg.server.id].custom_data['warnings']
                            if user.id in warnings:
                                warnings[user.id].append({'date': str(datetime.datetime.now()), 'reason': message})
                            else:
                                warnings[user.id] = [{'date': str(datetime.datetime.now()), 'reason': message}]
                            nwarnings = []
                            for warning in warnings[user.id]:
                                date = datetime.datetime.strptime(warning['date'], '%Y-%m-%d %H:%M:%S.%f')
                                curdate = datetime.datetime.now()
                                diff = (date.year - curdate.year) * 12 + date.month - curdate.month
                                if diff < 3:
                                    nwarnings.append(warning)
                            warnings[user.id] = nwarnings
                            if len(warnings[user.id]) >= 3:
                                if data.servers[msg.server.id].debugChannel != ['', '']:
                                    wr = ''
                                    c = 0
                                    for warning in warnings[user.id]:
                                        wr += str(c) + ') ' + warning['reason'] + ' - ' + warning['date'] + '\n'
                                        c += 1
                                    yield from client.send_message(
                                        data.servers[msg.server.id].command_channel[2], '',
                                        embed=data.embedder([[
                                            '**WARNING:**', 'User ``' + user.display_name + ':' + user.id + '`` <@' +
                                                            user.id + '>:\n' + wr
                                        ]]))
                            data.servers[msg.server.id].custom_data['warnings'] = warnings
                            data.servers[msg.server.id].update(client)
                            results.append([
                                'Warning placed!',
                                data.embedder([
                                    ['User', user.display_name + ':' + user.id + ' - <@' + user.id + '>'],
                                    ['Reason:', message]
                                ]),
                                msg.channel
                            ])
                    ##########################
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
