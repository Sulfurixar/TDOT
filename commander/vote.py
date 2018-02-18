import asyncio
from server import Server
import discord


class vote(object):

    def __init__(self):
        self.description = 'Used to vote during events.'
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'vote'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!vote help (args)``\n' +
                'For Example: ``e!vote help help`` - shows this message.',
            'channel':
                'Sets a custom channel for voting output.\n' +
                "How to use this command: ``e!vote channel (exact channel name or it's corresponding id')``\n" +
                'For Example: ``e!vote channel 271336104735539200``',
            'make':
                'Sends your vote to the voting channel.\n' +
                'How to use this command: ``e!vote make (args)``\n' +
                'For Example: ``e!vote make This is my vote.``'
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
                        skip = len(args[argpos:])
                        if 'vote' not in data.servers[msg.Server.id].custom_data:
                            results.append([
                               '',
                               data.embedder(
                                   [[
                                        "**Error:**",
                                        "The 'vote' command has not yet been set up for this Server." +
                                        " Set a channel for votes output via ``vote channel (channel)``."
                                   ]],
                                   colour=data.embed_error
                               ),
                               msg.channel
                            ])
                        else:
                            if 'channel' not in data.servers[msg.Server.id].custom_data['vote']:
                                results.append([
                                    '',
                                    data.embedder(
                                        [[
                                            "**Error:**",
                                            "No channel was found in vote command, rerun ``vote channel (channel)``."
                                        ]],
                                        colour=data.embed_error
                                    ),
                                    msg.channel
                                ])
                            else:
                                channel = discord.utils.find(
                                    lambda m: m.id == data.servers[msg.Server.id].custom_data['vote']['channel'],
                                    msg.Server.channels
                                )
                                if channel is None:
                                    results.append([
                                        '',
                                        data.embedder(
                                            [[
                                                "**Error:**",
                                                "Couldn't find channel set in config in this Server," +
                                                " rerun ``vote channel (channel)``."
                                            ]],
                                            colour=data.embed_error
                                        ),
                                        msg.channel
                                    ])
                                else:
                                    s = ''
                                    for word in args[argpos:]:
                                        s += word + " "
                                    yield from client.send_message(
                                        channel,
                                        '',
                                        embed=data.embedder([
                                            ["**Vote:**", s + " "],
                                            ["**Author:**", msg.author.display_name + ":" + msg.author.id +
                                             ":<@" + msg.author.id + ">"]
                                        ])
                                    )
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
                    if arg.lower() == 'channel':
                        skip = 1
                        if not (msg.author.id == msg.Server.owner.id or msg.author.id == data.id):
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        '**Error:**', 'Insufficient permissions: You need to be the owner of ``' +
                                        msg.Server.name + "`` or owner of this Bot to use this command."
                                    ]],
                                    colour=data.embed_error
                                ),
                                msg.channel])
                        else:
                            channel = discord.utils.find(lambda m: m.name == args[argpos + 1], msg.Server.channels)
                            if channel is None:
                                channel = discord.utils.find(lambda m: m.id == args[argpos + 1], msg.Server.channels)
                            if channel is None:
                                results.append([
                                    '',
                                    data.embedder(
                                        [["**Error:**", "Specified channel: ``" + arg + "``, does not exist."]],
                                        colour=data.embed_error
                                    ),
                                    msg.channel
                                ])
                            else:
                                if channel.Server.id not in data.servers:
                                    s = Server(client, msg.Server.id)
                                    data.Server.append({msg.Server.id: s})
                                    data.Server[msg.Server.id].update(client)
                                data.servers[msg.Server.id].custom_data['vote'] = {'channel': channel.id}
                                data.servers[msg.Server.id].update(client)
                                results.append(
                                    [
                                        '',
                                        data.embedder(
                                            [[
                                                "**Voting Channel:**",
                                                "Set voting channel for this Server as ``" + channel.name + ":" +
                                                channel.id + "``."
                                            ]]
                                        ),
                                        msg.channel
                                    ]
                                )
                    #################
                    if arg.lower() == 'make':
                        skip = len(args[argpos + 1:])
                        if 'vote' not in data.servers[msg.Server.id].custom_data:
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        "**Error:**",
                                        "The 'vote' command has not yet been set up for this Server. Set a channel" +
                                        " for votes output via ``vote channel (channel)``."
                                    ]],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                        else:
                            if 'channel' not in data.servers[msg.Server.id].custom_data['vote']:
                                results.append([
                                    '',
                                    data.embedder(
                                        [[
                                            "**Error:**",
                                            "No channel was found in vote command, rerun" +
                                            " ``vote channel (channel)``."
                                        ]],
                                        colour=data.embed_error
                                    ),
                                    msg.channel
                                ])
                            else:
                                channel = discord.utils.find(
                                    lambda m: m.id == data.servers[msg.Server.id].custom_data['vote']['channel'],
                                    msg.Server.channels
                                )
                                if channel is None:
                                    results.append([
                                        '',
                                        data.embedder(
                                            [[
                                                "**Error:**",
                                                "Couldn't find channel set in config in this Server, rerun" +
                                                " ``vote channel (channel)``."
                                            ]],
                                            colour=data.embed_error
                                        ),
                                        msg.channel
                                    ])
                                else:
                                    s = ''
                                    for word in args[argpos + 1:]:
                                        s += word + " "
                                    yield from client.send_message(
                                        channel,
                                        '',
                                        embed=data.embedder(
                                            [
                                                ["**Vote:**", s + " "],
                                                [
                                                    "**Author:**",
                                                    msg.author.display_name + ":" + msg.author.id + ":<@" +
                                                    msg.author.id + ">"
                                                ]
                                            ]
                                        )
                                    )
                    ######################################
#############################################################################
                argpos += 1
            yield from data.messager(msg, results)
