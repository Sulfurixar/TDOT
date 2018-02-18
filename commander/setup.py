import asyncio
from server import Server
import discord


class setup(object):
    def __init__(self):
        self.description = 'Used to set up Server specific details.'
        self.permissions = ['administrator']
        self.Owner = True
        self.bOwner = False
        self.name = 'setup'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!setup help (args)``\n' +
                'For Example: ``e!setup help help`` - shows this message.',
            'commandchannel':
                "Sets this Server's command channel as the channel specified.\n" +
                "How to use this command: ``e!setup commandChannel (exact channel name or its id)``\n" +
                'For Example: ``e!setup commandChannel 271336104735539200``',
            'joinchannel':
                "Sets this Server's user join logging channel.\n" +
                "How to use this command: `e!setup joinChannel (exactl channel name or its id)\n`" +
                "For Example: ``e!setup joinChannel 271336104735539200``",
            'leavechannel':
                "Sets this Server's user leaving logging channel.\n" +
                "How to use this command: `e!setup leaveChannel (exactl channel name or its id)\n`" +
                "For Example: ``e!setup leaveChannel 271336104735539200``",
            'authentication':
                "Enables or disables the bot's security question inquiry before giving roles.\n" +
                'How to use this command: ``e!setup authentication (true/false)``\n' +
                'For Example: ``e!setup authentication True``',
            'update':
                "Updates this Server's Server config - or creates one if it doesn't exist yet.\n" +
                'How to use this command: ``e!setup update``\n' +
                'For Example: ``e!setup update``',
            'giveroles':
                "Enables or disables the bot's ability to give roles on authentication.\n" +
                'How to use this command: ``e!setup giveRoles (true/false)``\n' +
                'For Example: ``e!setup giveRoles True``',
            'cmdlog':
                "Enables or disables command logging for this Server.\n" +
                "How to use this command: ``e!setup cmdlog (true/false)``\n" +
                "For Example: ``e!setup cmdlog True``",
            'active':
                "Enables or disables config activity for this Server.\n" +
                "How to use this command: ``e!setup active (true/false)``\n" +
                "For Example: ``e!setup active True``",
            'msgdellog':
                'Enables or disables message delete logging for this Server.\n' +
                "How to use this command: ``e!setup msgdellog (true/false)``\n" +
                "For Example: ``e!setup msgdellog True``",
            'msgdelchannel':
                "Sets this Server's message deletion recovery channel as the channel specified.\n" +
                "How to use this command: ``e!setup msgdelChannel (exact channel name or its id)``\n" +
                'For Example: ``e!setup msgdelChannel 271336104735539200``',
            'msgeditlog':
                'Enables or disables message edit logging for this Server.\n' +
                "How to use this command: ``e!setup msgeditlog (true/false)``\n" +
                "For Example: ``e!setup msgeditlog True``",
            'msgeditchannel':
                "Sets this Server's message edit checking channel as the channel specified.\n" +
                "How to use this command: ``e!setup msgeditChannel (exact channel name or its id)``\n" +
                'For Example: ``e!setup msgeditChannel 271336104735539200``',
            'welcomemsg':
                "Sets this Server's user welcoming message in their private messages.\n" +
                "How to use this command: ``e!setup welcomemsg {'name':'Header', 'value': 'Text'}\n" +
                "For Example: ``e!setup welcomemsg {'name': 'Welcome!', 'value': 'Welcome to our Server!'}",
            'welcoming':
                'Enables or disables welcome messages for users.\n' +
                "How to use this command: ``e!setup welcoming (true/false)``\n" +
                "For Example: ``e!setup welcoming True``",
            'permissions':
                "Manages permissions for roles to not have to rely on 'administrator'.\n" +
                "How to use this command: ``e!setup permissions (args)``\n" +
                "For Example: ``e!setup permissions show``",
            'setgiveroles':
                "Sets this Server's roles that it gives upon users joining.\n" +
                "How to use this command: ``e!setup setgiveroles {\"rolename\":\"roleid\"}``\n" +
                "For Example: ``e!setup setgiveroles {\"Members\":\"199659930892894208\"}``"
        }

    @staticmethod
    def channeler(data, msg, client, info, name):
        channel = discord.utils.find(lambda m: m.name == info, msg.Server.channels)
        if channel is None:
            channel = discord.utils.find(lambda m: m.id == info, msg.Server.channels)
        if channel is None:
            return None, [
                '',
                data.embedder([["**Error:**", "Specified channel: ``" + info + "``, does not exist on this Server."]]),
                msg.channel
            ]
        else:
            if channel.Server.id not in data.servers:
                data.servers[msg.Server.id] = Server(client, msg.Server.id)
                data.servers[msg.Server.id].update(client)
            return channel, [
                '',
                data.embedder([[
                    "**" + name + ":**",
                    "Set command channel for this Server as ``" + channel.name + ":" + channel.id + "``."
                ]]),
                msg.channel
            ]

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
                            data.embedder([
                                ['**Error:**', "Couldn't recognise ``" + arg + '``.']
                            ], colour=data.embed_error), msg.channel
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
                    if arg.lower() == 'commandchannel':
                        skip = 1
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "Command Channel")
                        if channel is not None:
                            data.servers[msg.Server.id].command_channel = [channel.name, channel.id, channel]
                            data.servers[msg.Server.id].update(client)
                        results.append(res)
                    ##########################
                    if arg.lower() == 'msgdelchannel':
                        skip = 1
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "Delete Channel")
                        if channel is not None:
                            data.servers[msg.Server.id].delete_channel = [channel.name, channel.id, channel]
                            data.servers[msg.Server.id].update(client)
                        results.append(res)
                    #########################
                    if arg.lower() == 'msgeditchannel':
                        skip = 1
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "Message Edit Channel")
                        if channel is not None:
                            data.servers[msg.Server.id].edit_channel = [channel.name, channel.id, channel]
                            data.servers[msg.Server.id].update(client)
                        results.append(res)
                    #########################
                    if arg.lower() == 'joinchannel':
                        skip = 1
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "User Join Channel")
                        if channel is not None:
                            data.servers[msg.Server.id].join_channel = [channel.name, channel.id, channel]
                            data.servers[msg.Server.id].update(client)
                        results.append(res)
                    #########################
                    if arg.lower() == 'leavechannel':
                        skip = 1
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "User Leaving Channel")
                        if channel is not None:
                            data.servers[msg.Server.id].leave_channel = [channel.name, channel.id, channel]
                            data.servers[msg.Server.id].update(client)
                        results.append(res)
                    #################
                    if arg.lower() == 'authentication':
                        skip = 1
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.Server.id].auth = True
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([['**Authentication:**', 'Set authentication for this Server to True.']]),
                                msg.channel
                            ])
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.Server.id].auth = False
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([[
                                    '**Authentication:**', 'Set authentication for this Server to False.'
                                ]]),
                                msg.channel
                            ])
                        else:
                            results.append([
                                '',
                                data.embedder(
                                    [['**Error:**', 'Invalid argument: ``' + args[argpos + 1] + '``.']],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                    #############################################################
                    if arg.lower() == 'giveroles':
                        skip = 1
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.Server.id].give_roles = True
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([['**GiveRoles:**', 'Set giveRoles for this Server to True.']]),
                                msg.channel
                            ])
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.Server.id].give_roles = False
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([['**GiveRoles:**', 'Set giveRoles for this Server to False.']]),
                                msg.channel
                            ])
                        else:
                            results.append([
                                '',
                                data.embedder(
                                    [['**Error:**', 'Invalid argument: ``' + args[argpos + 1] + '``.']],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                    ############################################################
                    if arg.lower() == 'cmdlog':
                        skip = 1
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.Server.id].command_logging = True
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder(
                                    [['**Command Logging:**', 'Set command logging for this Server to True.']]
                                ),
                                msg.channel
                            ])
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.Server.id].command_logging = False
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([[
                                    '**Command Logging:**', 'Set command logging for this Server to False.'
                                ]]),
                                msg.channel
                            ])
                    ############################################################
                    if arg.lower() == 'active':
                        skip = 1
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.Server.id].active = True
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([[
                                    '**Config Activity:**', 'Set config activity for this Server to True.'
                                ]]),
                                msg.channel
                            ])
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.Server.id].active = False
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([[
                                    '**Config Activity:**', 'Set config activity for this Server to False.'
                                ]]),
                                msg.channel
                            ])
                    ############################################################
                    if arg.lower() == 'msgdellog':
                        skip = 1
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.Server.id].message_delete_logging = True
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([[
                                    '**Message Delete Logging:**', 'Set message delete logging for this Server to True.'
                                ]]),
                                msg.channel
                            ])
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.Server.id].message_delete_logging = False
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([[
                                    '**Message Delete Logging:**',
                                    'Set message delete logging for this Server to False.'
                                ]]),
                                msg.channel
                            ])
                    ##########################################################
                    if arg.lower() == 'msgeditlog':
                        skip = 1
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.Server.id].message_edit_logging = True
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([[
                                    '**Message Edit Logging:**', 'Set message edit logging for this Server to True.'
                                ]]),
                                msg.channel
                            ])
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.Server.id].message_edit_logging = False
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '', 
                                data.embedder([[
                                    '**Message Edit Logging:**', 
                                    'Set message edit logging for this Server to False.'
                                ]]), 
                                msg.channel
                            ])
                    ##########################################################
                    if arg.lower() == 'welcoming':
                        skip = 1
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.Server.id].welcoming = True
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '', 
                                data.embedder([['**Welcoming:**', 'Set welcoming for this Server to True.']]), 
                                msg.channel
                            ])
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.Server.id].welcoming = False
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '', 
                                data.embedder([['**Welcoming:**', 'Set welcoming for this Server to False.']]), 
                                msg.channel
                            ])
                    ##########################################################
                    if arg.lower() == 'welcomemsg':
                        skip = len(args[argpos:])
                        n_args = args[argpos + 1:]
                        emb, res = data.json(n_args, msg)
                        if emb is not None:
                            data.servers[msg.Server.id].welcome_message = emb
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '**Set welcome message to:**', 
                                data.embedder([[emb['name'], emb['value']]]), 
                                msg.channel
                            ])
                        else:
                            for r in res:
                                results.append(r)
                    ##########################################################
                    if arg.lower() == 'permissions':
                        skip = len(args[argpos:])
                        n_skip = 0
                        n_args = args[argpos + 1:]
                        n_argpos = 0
                        subargs = ['show', 'set']
                        if len(n_args) > 0:
                            for nArg in n_args:
                                if n_skip > 0:
                                    n_skip -= 1
                                else:
                                    #
                                    if nArg.lower() not in subargs:
                                        results.append([
                                            '', 
                                            data.embedder([['**Error:**', "Couldn't recognize '" + nArg + "'."]]), 
                                            msg.channel
                                        ])
                                    else:
                                        a = ''
                                        c = True
                                        if '=' in nArg:
                                            t = nArg.split('=')
                                            if t[0].lower() in subargs:
                                                a = t[0].lower()
                                            else:
                                                c = False
                                        else:
                                            a = nArg.lower()
                                        if c:
                                            #######################
                                            if a == 'show':
                                                results.append([
                                                    '',
                                                    data.embedder([[
                                                        '**Server Permissions:**', 
                                                        str(data.servers[msg.Server.id].perms).replace("'", '"')
                                                    ]]), 
                                                    msg.channel
                                                ])
                                            #######################
                                            if a == 'set':
                                                n_skip = len(n_args[n_argpos:])
                                                b_args = n_args[n_argpos + 1:]
                                                emb, res = data.json(b_args, msg)
                                                if emb is not None:
                                                    data.servers[msg.Server.id].perms = emb
                                                    data.servers[msg.Server.id].update(client)
                                                    results.append([
                                                        '',
                                                        data.embedder([[
                                                            '**Server Permissions:**',
                                                            'Set Server permissions to: ``' + str(emb) + '``.'
                                                        ]]),
                                                        msg.channel
                                                    ])
                                                else:
                                                    for r in res:
                                                        results.append(r)
                                            #######################
                                n_argpos += 1
                        else:
                            results.append([
                                '',
                                data.embedder([[
                                    '**Server Permissions:**',
                                    str(data.servers[msg.Server.id].perms).replace("'", '"')
                                ]]),
                                msg.channel
                            ])
                    ##########################################################
                    if arg.lower() == 'setgiveroles':
                        skip = len(args[argpos:])
                        n_args = args[argpos + 1:]
                        emb, res = data.json(n_args, msg)
                        roles = {}
                        if emb is not None:
                            for role in emb:
                                r = discord.utils.find(lambda m: m.id == emb[role], msg.Server.roles)
                                if r is None:
                                    r = discord.utils.find(lambda m: m.name == role, msg.Server.roles)
                                if r is None:
                                    results.append([
                                        '',
                                        data.embedder([[
                                            '**Error:**', 'Could not find specified role: ``' + role + ':' + emb[role]
                                        ]]),
                                        msg.channel
                                    ])
                                else:
                                    roles[r.name] = r.id
                            data.servers[msg.Server.id].auth_roles = roles
                            data.servers[msg.Server.id].update(client)
                            results.append([
                                '',
                                data.embedder([['**Set giveroles to:**', '``' + str(roles) + '``']]),
                                msg.channel
                            ])
                        else:
                            for r in res:
                                results.append(r)
                    ##########################################################
                    if arg.lower() == 'update':
                        if msg.Server.id in data.servers:
                            data.servers[msg.Server.id].update(client)
                        else:
                            s = Server(client, msg.Server.id)
                            data.Server.append({msg.Server.id: s})
                            data.Server[msg.Server.id].update(client)
                        results.append([
                            '',
                            data.embedder([['**Updated ``' + msg.Server.name + "``**", 'Update complete.']]),
                            msg.channel
                        ])
                    ##########################################
#############################################################################
                argpos += 1
            yield from data.messager(msg, results)
