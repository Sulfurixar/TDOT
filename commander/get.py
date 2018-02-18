import asyncio
import discord


class get(object):

    def __init__(self):
        self.description = 'Used to retrieve various kinds of information.'
        self.permissions = ['administrator']
        self.Owner = True
        self.bOwner = False
        self.name = 'get'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!get help (args)``\n' +
                'For Example: ``e!get help help`` - shows this message.',
            'server':
                'Displays data about this server.\n' +
                'How to use this command: ``e!get server``',
            'channels':
                'Displays all the channels in this server.\n' +
                'How to use this command: ``e!get channels``',
            'roles':
                'Displays all the roles in this server.\n' +
                'How to use this command: ``e!get roles``',
            'users':
                'Displays all the users in this server.\n' +
                'How to use this command: ``e!get users``',
            'user':
                'Displays all the user\'s data in this server.\n' +
                'How to use this command: ``e!get user (user)``'
        }

    def unlist(self, lists, t=-1):
        s = ''
        if type(lists) == type({}):
            t += 1
            for e in lists:
                c = 0
                if t > c:
                    while t > c:
                        s += '\t'
                        c += 1
                s += '' + e + ': ' + self.unlist(lists[e], t=t) + '\n'
        elif type(lists) == type([]):
            lists.reverse()
            c = 0
            t += 1
            if t > c:
                while t > c:
                    s += '\t'
                    c += 1
            for e in lists:
                s += '' + self.unlist(e, t=t) + '\n'
        else:
            return lists
        return s

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
                    if arg.lower() == 'server':
                        if not (msg.server.id in data.servers):
                            results.append(['', data.embedder([
                                [
                                    '**Server Data:**',
                                    'Server Name: ``' +
                                    msg.server.name +
                                    '``\n' +
                                    'Server ID: ``' +
                                    msg.server.id +
                                    '``\n'
                                ]
                            ]), msg.channel
                                            ])
                        else:
                            s = data.servers[str(msg.server.id)]
                            name = msg.server.name
                            auth_roles = ''
                            for role in s.auth_roles:
                                auth_roles = auth_roles + "``" + role + ";`` "
                            res = ''
                            if len(s.perms) > 0:
                                for perm in s.perms:
                                    if len(perm) > 0:
                                        for entry in perm:
                                            if entry == 'name':
                                                res += 'Name: ``' + perm[entry] + '``\n'
                                            if entry == 'names':
                                                if len(perm[entry]) > 0:
                                                    res += 'Names: \n'
                                                    for ID in perm[entry]:
                                                        res += perm[entry][ID] + ':' + ID + '\n'
                                            if entry == 'roles':
                                                if len(perm[entry]) > 0:
                                                    res += 'Roles: \n'
                                                    for ID in perm[entry]:
                                                        res += perm[entry][ID] + ':' + ID + '\n'
                                            if entry == 'cmds':
                                                if len(perm[entry]) > 0:
                                                    res += 'Commands: \n'
                                                    for cmd in perm[entry]:
                                                        res += cmd + '\n'
                            if res == '':
                                res = 'N/A'
                            results.append([
                                '',
                                data.embedder([[
                                    '**Server Data:**',
                                    "Server name: ``" + name + "``\n" +
                                    "Server ID: ``" + s.c_id + "``\n" +
                                    "Server Config Active: ``" + str(s.active) + "``\n" +
                                    "Server Authentication: ``" + str(s.auth) + "``\n" +
                                    "Server Command Logging: ``" + str(s.command_logging) + "``\n" +
                                    "Server Message Deletion Logging: ``" + str(s.message_delete_logging) + "``\n" +
                                    "Server Message Edit Logging: ``" + str(s.message_edit_logging) + "``\n" +
                                    "Server Give Authentication Roles: ``" + str(s.give_roles) + "``\n" +
                                    "Server Question: ``'" + s.question + "'``\n" +
                                    "Server Answer: ``'" + s.answer + "'``\n" +
                                    "Server Authentication Roles: " + auth_roles + "\n" +
                                    "Server Debug Channel: ``" + str(s.debug_channel[0]) + ":" +
                                    str(s.debug_channel[1]) + "``\n" +
                                    "Server Welcome Channel: ``" + str(s.welcome_channel[0]) + ":" +
                                    str(s.welcome_channel[1]) + "``\n" +
                                    "Server Joining Channel: ``" + str(s.join_channel[0]) + ":" +
                                    str(s.join_channel[1]) + "``\n" +
                                    "Server Leaving Channel: ``" + str(s.leave_channel[0]) + ":" +
                                    str(s.leave_channel[1]) + "``\n" +
                                    "User Welcoming: ``" + str(s.welcoming) + "``\n" +
                                    "Server Command Channel: ``" + str(s.command_channel[0]) + ":" +
                                    str(s.command_channel[1]) + "``\n" +
                                    "Server Message Edit Checking Channel: ``" + str(s.edit_channel[0]) + ':' +
                                    str(s.edit_channel[1]) + "``\n" +
                                    "Server Message Deletion Recovery Channel: ``" +
                                    str(s.delete_channel[0]) + ':' + str(s.delete_channel[1]) + "``\n"
                                ]]),
                                msg.channel
                            ])
                            results.append([
                                '',
                                data.embedder([
                                    ["**Server Permissions:**", res],
                                    ["**Custom Data**:", str(s.custom_data)],
                                    ["User Welcoming Message:", "``" + str(s.welcome_message) + "``"]
                                ]),
                                msg.channel
                            ])
                    ##########################
                    if arg.lower() == 'channels':
                        channels = ['']
                        c = 1
                        d = 0
                        for channel in msg.server.channels:
                            channels[-1] += str(c) + ') ``' + channel.name + '|' + channel.id + '`` \n'
                            c += 1
                            d += 1
                            if d == 10:
                                channels.append('')
                                d = 0
                        c = 1
                        for channel in channels:
                            results.append([
                                '',
                                data.embedder([["**Server Channels(" + str(c) + "):**", channels[c - 1]]]),
                                msg.channel
                            ])
                            c += 1
                    ###############
                    if arg.lower() == 'roles':
                        roles = ['']
                        c = 1
                        d = 0
                        for role in msg.server.roles:
                            roles[-1] += str(c) + ') ``' + role.name + "|" + role.id + '`` \n'
                            c += 1
                            d += 1
                            if d == 10:
                                roles.append('')
                                d = 0
                        c = 1
                        for role in roles:
                            results.append([
                                '',
                                data.embedder([['**Server Roles(' + str(c) + '):**', roles[c - 1]]]),
                                msg.channel
                            ])
                            c += 1
                    ####
                    if arg.lower() == 'users':
                        users = ['']
                        c = 1
                        d = 0
                        for user in msg.server.members:
                            users[-1] += str(c) + ') ``' + user.display_name + "|" + user.id + '`` \n'
                            c += 1
                            d += 1
                            if d == 10:
                                users.append('')
                                d = 0
                        c = 1
                        for user in users:
                            results.append([
                                '',
                                data.embedder([['**Server Users(' + str(c) + '):**', users[c - 1]]]),
                                msg.channel
                            ])
                            c += 1
                    ####
                    if arg.lower() == 'user':
                        users = []
                        try:
                            n_args = args[argpos + 1:]
                            skip = len(n_args)
                            for name in n_args:
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
                                    users.append(user)
                        except IndexError:
                            results.append([
                                '',
                                data.embedder(
                                    [['**Error:**', 'No users were specified!']]
                                ),
                                msg.channel
                            ])
                        for user in users:
                            w = [['User Data:', '``' + str(user.display_name) + ': ' + str(user.id) + '``']]
                            data.c.set_user_data(user)
                            u_data = data.c.get_user_data(user)
                            for key in u_data:
                                if u_data[key] is not None and u_data[key] != '':
                                    w.append([key.replace('_', ' '), '``' + str(self.unlist(u_data[key])) + '``'])
                            w = data.embedder(w)
                            results.append([
                                '',
                                w,
                                msg.channel
                            ])
                    ####
                ##############################################################################
                argpos += 1
            yield from data.messager(msg, results)