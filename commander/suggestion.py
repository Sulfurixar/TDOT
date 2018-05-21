import asyncio
from server import Server
import discord


class suggestion(object):

    def __init__(self):
        self.description = 'Used to make private suggestions to the Server administration.'
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'suggestion'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!suggestion help (args)``\n' +
                'For Example: ``e!suggestion help help`` - shows this message.',
            'channel':
                'Sets a custom channel for suggestion output.\n' +
                "How to use this command: ``e!suggestion channel (exact channel name or it's corresponding id')``\n" +
                'For Example: ``e!suggestion channel 271336104735539200``',
            'make':
                'Makes an suggestion to the suggestion channel.\n' +
                'How to use this command: ``e!suggestion make (args)``\n' +
                'For Example: ``e!suggestion make This is my suggestion.``'
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
                        if 'suggestions' not in data.servers[msg.server.id].custom_data:
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        "**Error:**",
                                        "The 'suggestion' command has not yet been set up for this Server. " +
                                        "Set a channel for suggestions output via ``suggestion channel (channel)``."
                                    ]],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                        else:
                            if 'channel' not in data.servers[msg.server.id].custom_data['suggestions']:
                                results.append([
                                    '',
                                    data.embedder(
                                        [[
                                            "**Error:**",
                                            "No channel was found in suggestions' command, rerun " +
                                            "``suggestion channel (channel)``."
                                        ]],
                                        colour=data.embed_error
                                    ),
                                    msg.channel
                                ])
                            else:
                                channel = discord.utils.find(
                                    lambda m: m.id == data.servers[msg.server.id].custom_data['suggestions']['channel'],
                                    msg.server.channels
                                )
                                if channel is None:
                                    results.append([
                                        '',
                                        data.embedder(
                                            [[
                                                "**Error:**",
                                                "Couldn't find channel set in config in this Server, rerun " +
                                                "``suggestion channel (channel)``."
                                            ]],
                                            colour=data.embed_error), msg.channel
                                    ])
                                else:
                                    s = ''
                                    for word in args[argpos:]:
                                        s += word + " "
                                    yield from client.send_message(
                                        channel,
                                        '',
                                        embed=data.embedder([
                                            ["**Suggestion:**", s + " "],
                                            [
                                                "**Author:**",
                                                msg.author.display_name + ":" + msg.author.id + ":<@" +
                                                msg.author.id + ">"
                                            ]
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
                        if not (msg.author.id == msg.server.owner.id or msg.author.id == data.id):
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        '**Error:**',
                                        'Insufficient permissions: You need to be the owner of ``' + msg.server.name +
                                        "`` or owner of this Bot to use this command."
                                    ]],
                                    colour=data.embed_error),
                                msg.channel
                            ])
                        else:
                            channel = discord.utils.find(lambda m: m.name == args[argpos + 1], msg.server.channels)
                            if channel is None:
                                channel = discord.utils.find(lambda m: m.id == args[argpos + 1], msg.server.channels)
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
                                if channel.server.id not in data.servers:
                                    s = Server(client, msg.server.id)
                                    data.servers.append({msg.server.id: s})
                                    data.servers[msg.server.id].update(client)
                                data.servers[msg.server.id].custom_data['suggestions'] = {'channel': channel.id}
                                data.servers[msg.server.id].update(client)
                                results.append([
                                    '',
                                    data.embedder([[
                                        "**Suggestion Channel:**",
                                        "Set suggestion' channel for this Server as ``" + channel.name + ":" +
                                        channel.id + "``."
                                    ]]),
                                    msg.channel
                                ])
                    #################
                    if arg.lower() == 'make':
                        skip = len(args[argpos + 1:])
                        if 'suggestions' not in data.servers[msg.server.id].custom_data:
                            results.append([
                               '',
                               data.embedder(
                                   [[
                                       "**Error:**",
                                       "The 'suggestion' command has not yet been set up for this Server. " +
                                       "Set a channel for suggestions output via ``suggestion channel (channel)``."
                                   ]],
                                   colour=data.embed_error
                               ),
                               msg.channel
                            ])
                        else:
                            if 'channel' not in data.servers[msg.server.id].custom_data['suggestions']:
                                results.append([
                                    '',
                                    data.embedder(
                                        [[
                                            "**Error:**",
                                            "No channel was found in suggedtions command, rerun " +
                                            "``suggestion channel (channel)``."
                                        ]],
                                        colour=data.embed_error
                                    ),
                                    msg.channel
                                ])
                            else:
                                channel = discord.utils.find(
                                    lambda m: m.id == data.servers[msg.server.id].custom_data['suggestions']['channel'],
                                    msg.Server.channels
                                )
                                if channel is None:
                                    results.append([
                                        '',
                                        data.embedder(
                                            [[
                                                "**Error:**",
                                                "Couldn't find channel set in config in this Server, rerun " +
                                                "``suggestion channel (channel)``."
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
                                        embed=data.embedder([
                                            ["**Suggestion:**", s + " "],
                                            [
                                                "**Author:**",
                                                msg.author.display_name + ":" + msg.author.id + ":<@" +
                                                msg.author.id + ">"
                                            ]
                                        ])
                                    )
                    ######################################
#############################################################################
                argpos += 1
            yield from data.messager(msg, results)
