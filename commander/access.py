import asyncio
import discord


class access(object):

    def __init__(self):
        self.description = 'Used to gain access to special roles or channels.'
        self.permissions = []
        self.Owner = True
        self.bOwner = False
        self.name = 'access'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!access help (args)``\n' +
                'For Example: ``e!access help help`` - shows this message.',
            'config':
                'Chanes the config for access.\n' +
                'How to use this command: ``e!access config {"argument":{"role":"id"}}``' +
                'For Example: ``e!access config {"book":{"channel":"12345678"}}',
            'show':
                'Displays the config for this server.\n' +
                'How to use this command: ``e!access show``\n' +
                'For Example: ``e!access show``.',
            
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
                        if arg.lower() in data.servers[msg.server.id].custom_data['access']:
                            a_arg = data.servers[msg.server.id].custom_data['access'][arg.lower()]
                            for aType in a_arg:
                                if aType == 'role':
                                    r = discord.utils.find(lambda m: m.id == a_arg[aType], msg.server.roles)
                                    if r is None:
                                        r = discord.utils.find(lambda m: m.name == a_arg[aType], msg.server.roles)
                                    if r is not None:
                                        if r not in msg.author.roles:
                                            client.add_role(r, msg.author)
                                            results.append([
                                                '',
                                                data.embedder([[
                                                    'Granted role:',
                                                    'Granted ' + r.name + ' for ' + msg.author.display_name
                                                ]]),
                                                msg.channel
                                            ])
                                        else:
                                            client.remove_roles(msg.author, r)
                                            results.append([
                                                '',
                                                data.embedder([[
                                                    'Removed role:',
                                                    'Removed ' + r.name + ' from ' + msg.author.display_name
                                                ]]),
                                                msg.channel
                                            ])
                                    else:
                                        results.append([
                                            '', 
                                            data.embedder([['Couldn\'t find role:', a_arg[aType]]]), 
                                            msg.channel
                                        ])
                                if aType == 'channel':
                                    c = discord.utils.find(lambda m: m.id == a_arg[aType], msg.server.channels)
                                    if c is None:
                                        c = discord.utils.find(lambda m: m.name == a_arg[aType], msg.server.channels)
                                    if c is not None:
                                        if c.overwrites_for(msg.author).is_empty():
                                            overwrite = discord.PermissionOverwrite()
                                            overwrite.read_messages = True
                                            overwrite.send_messages = True
                                            overwrite.add_reactions = True
                                            overwrite.embed_links = True
                                            overwrite.attach_files = True
                                            overwrite.read_message_history = True
                                            overwrite.external_emojis = True
                                            overwrite.connect = True
                                            overwrite.speak = True
                                            overwrite.use_voice_activation = True
                                            yield from client.edit_channel_permissions(
                                                c, msg.author, overwrite=overwrite
                                            )
                                            results.append([
                                                '',
                                                data.embedder([[
                                                    'Granted channel:', c.name + ' for ' + msg.author.display_name
                                                ]]),
                                                msg.channel
                                            ])
                                        else:
                                            overwrite = discord.PermissionOverwrite()
                                            overwrite.read_messages = None
                                            overwrite.send_messages = None
                                            overwrite.add_reactions = None
                                            overwrite.embed_links = None
                                            overwrite.attach_files = None
                                            overwrite.read_message_history = None
                                            overwrite.external_emojis = None
                                            overwrite.connect = None
                                            overwrite.speak = None
                                            overwrite.use_voice_activation = None
                                            yield from client.edit_channel_permissions(
                                                c, msg.author, overwrite=overwrite
                                            )
                                            results.append([
                                                '',
                                                data.embedder([[
                                                    'Removed channel:', c.name + ' from ' + msg.author.display_name
                                                ]]),
                                                msg.channel
                                            ])
                                    else:
                                        results.append([
                                            '', 
                                            data.embedder([['Couldn\'t find channel:', a_arg[aType]]]), 
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
                    if arg.lower() == 'show':
                        cd = data.servers[msg.server.id].custom_data
                        if 'access' in cd:
                            m = ''
                            for key in cd['access']:
                                m += '```https\n' + key
                                for key2 in cd['access'][key]:
                                    m += '\n\ttype: ' + key2 + '\n\tid: ' + cd['access'][key][key2]
                                m += '```\n'
                            results.append([
                                '', data.embedder([[
                                    '**Access Data:**', 
                                    m
                                ]]), 
                                msg.channel]
                            )
                        else:
                            results.append([
                                '', 
                                data.embedder([['**Access Data:**', 'No custom data yet.']]), 
                                msg.channel
                            ])
                    ##########################
                    if arg.lower() == 'config':
                        skip = len(args[argpos:])
                        n_args = args[argpos + 1:]
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
                            emb, res = data.json(n_args, msg)
                            if emb is not None:
                                data.servers[msg.server.id].custom_data['access'] = emb
                                data.servers[msg.server.id].update(client)
                                results.append([
                                    '',
                                    data.embedder([[
                                        '**Access Data:**',
                                        str(data.servers[msg.server.id].custom_data['access']).replace("'", '"')]]),
                                    msg.channel
                                ])
                            else:
                                for r in res:
                                    results.append(r)
                    ##########################
##############################################################################
                argpos += 1
            yield from data.messager(msg, results)
