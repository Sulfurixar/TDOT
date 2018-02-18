import discord
import asyncio
from urllib.parse import quote


class google(object):

    def __init__(self):
        self.description = "Used to educate people with the ways of google."
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'google'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!google help (args)``\n' +
                'For Example: ``e!google help help`` - shows this message.'
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
                    if arg.lower() not in self.commands:
                        skip = len(args)
                        s = ' '.join(args)
                        q = 'https://www.lmgtfy.com/?q=' + quote(s)
                        i = 'https://i.imgur.com/wymW7E9.png'
                        embed = discord.Embed()
                        embed.title = s
                        embed.color = data.embed_normal
                        embed.set_image(url=i)
                        embed.add_field(name='Let me google that for ya...', value=q)
                        results.append(['', embed, msg.channel])
                    ##########################
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
