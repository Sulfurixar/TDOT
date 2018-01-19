import asyncio
from server import server
import discord
import json

class suggestion(object):

    def __init__(self):
        self.description = 'Used to make private suggestions to the server administration.';
        self.permissions = [];
        self.Owner = False;
        self.bOwner = False;
        self.name = 'suggestion';
        self.tick = False;
        self.react = False;
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
        };
        return super().__init__();

    def error(self, data, msg):
        message = 'Insufficient permissions. ';
        if len(self.permissions) > 0:
            message += 'You must have: ';
            for perm in self.permissions:
                message += '``' + perm + '`` '
            message += '; permissions by default.'
        if self.Owner and not self.bOwner:
            message += ' This command can be run by the Owner of ``' + msg.server.name + '`` or ``Bot``.';
        elif self.bOwner:
            message += ' This command can be run only by the Owner of the ``Bot``.';
        return data.embedder([['**Error:**', message]], colour=data.embed_error);
        

    def check(self, data, msg):
        r = False;
        if msg.server.id in data.servers:
            p = data.servers[msg.server.id].perms;
            for entry in p:
                if msg.author.id in entry['names']:
                    if self.name in entry['cmds']:
                        return True;
                for role in entry['roles']:
                    r = discord.utils.find(lambda m: m.id == role, msg.author.roles);
                    print(r.name)
                    if r != None:
                        if self.name in entry['cmds']:
                            return True;
        return False

    #@asyncio.coroutine
    def can_use(self, data, msg):
        use = True;
        for perm in self.permissions:
            #not (has perm or is me) // if has perm = True -> False, if is me = True -> False, if has perm and is me == False -> True
            #val = (data.perms._user(data, msg.author, [msg.channel, perm]) or msg.author.id == data.id or self.check(data, msg));
            a = data.perms._user(data, msg.author, [msg.channel, perm]);
            if msg.author.id == data.id:
                b = True
            else:
                b = False
            c = self.check(data, msg)
            print(perm)
            print(str(a) + '|' + str(b) + '|' + str(c))
            if (True not in [a, b, c]):
                use = False;
        print('1)' + str(use))
        # not ((reqOwner and is Owner) or is me)
        if self.Owner:
            if msg.author.id != msg.server.owner.id:
                if msg.author.id != data.id:
                    use = False;
        print('2)' + str(use))
        if self.bOwner and msg.author.id != data.id:
            use = False;
        print('3)' + str(use))
        #if not use:
            #yield from data.messager(msg, [['', self.error(data, msg), msg.channel]]);
        return use


    @asyncio.coroutine
    def execute(self, client, msg, data, args):
        if not self.can_use(data, msg):
            yield from data.messager(msg, [['', self.error(data, msg), msg.channel]]);
            return;

        if len(args) == 0:
            yield from data.messager(msg, data.help(msg, self));
            return;
        else:
            results = [];
            skip = 0;
            argpos = 0;
            for arg in args:
                if skip > 0:
                    skip -= 1;
                    argpos += 1;
                    continue;
                else:
                    if arg.lower() not in self.commands:
                        skip = len(args[argpos:]);
                        if not 'suggestions' in data.servers[msg.server.id].customData:
                           results.append(['', data.embedder([["**Error:**", "The 'suggestion' command has not yet been set up for this server. Set a channel for suggestions output via ``suggestion channel (channel)``."]], colour=data.embed_error), msg.channel]);
                        else:
                            if not 'channel' in data.servers[msg.server.id].customData['suggestions']:
                                results.append(['', data.embedder([["**Error:**", "No channel was found in suggestions' command, rerun ``suggestion channel (channel)``."]], colour=data.embed_error), msg.channel]);
                            else:
                                channel = discord.utils.find(lambda m: m.id == data.servers[msg.server.id].customData['suggestions']['channel'], msg.server.channels);
                                if channel is None:
                                    result.append(['', data.embedder([["**Error:**", "Couldn't find channel set in config in this server, rerun ``suggestion channel (channel)``."]], colour=data.embed_error), msg.channel]);
                                else:
                                    s = '';
                                    for word in args[argpos:]:
                                        s += word + " ";
                                    yield from client.send_message(channel, '', embed=data.embedder([["**Suggestion:**", s + " "], ["**Author:**", msg.author.display_name + ":" + msg.author.id + ":<@" + msg.author.id + ">"]]));
                        argpos += 1;
                        continue;
#############################################################################
                    if arg.lower() == 'help':
                        help = [];
                        if len(args[argpos + 1:]) > 0:
                            help = data.help(msg, self, args[argpos + 1:]);
                            skip = len(args[argpos + 1:]);
                        else:
                            help = data.help(msg, self);
                        for h in help:
                            results.append(h);
                    ##########################
                    if arg.lower() == 'channel':
                        skip = 1;
                        if not (msg.author.id == msg.server.owner.id or msg.author.id == data.id):
                            results.append(['', data.embedder([['**Error:**', 'Insufficient permissions: You need to be the owner of ``' + msg.server.name + "`` or owner of this Bot to use this command."]], colour=data.embed_error), msg.channel]);
                        else:
                            channel = discord.utils.find(lambda m: m.name == args[argpos + 1], msg.server.channels);
                            if channel is None:
                                channel = discord.utils.find(lambda m: m.id == args[argpos + 1], msg.server.channels);
                            if channel is None:
                                results.append(['', data.embedder([["**Error:**", "Specified channel: ``" + arg + "``, does not exist."]], colour=data.embed_error), msg.channel]);
                            else:
                                if not channel.server.id in data.servers:
                                    s = server(client, msg.server.id);
                                    data.server.append({msg.server.id: s});
                                    data.server[msg.server.id].update(client);
                                data.servers[msg.server.id].customData['suggestions'] = {'channel': channel.id}; 
                                data.servers[msg.server.id].update(client);
                                results.append(['', data.embedder([["**Suggestion Channel:**", "Set suggestion' channel for this server as ``" + channel.name + ":" + channel.id + "``."]]), msg.channel]);
                    #################
                    if arg.lower() == 'make':
                        skip = len(args[argpos + 1:]);
                        if not 'suggestions' in data.servers[msg.server.id].customData:
                           results.append(['', data.embedder([["**Error:**", "The 'suggestion' command has not yet been set up for this server. Set a channel for suggestions output via ``suggestion channel (channel)``."]], colour=data.embed_error), msg.channel]);
                        else:
                            if not 'channel' in data.servers[msg.server.id].customData['suggestions']:
                                results.append(['', data.embedder([["**Error:**", "No channel was found in suggedtions command, rerun ``suggestion channel (channel)``."]], colour=data.embed_error), msg.channel]);
                            else:
                                channel = discord.utils.find(lambda m: m.id == data.servers[msg.server.id].customData['suggestions']['channel'], msg.server.channels);
                                if channel is None:
                                    result.append(['', data.embedder([["**Error:**", "Couldn't find channel set in config in this server, rerun ``suggestion channel (channel)``."]], colour=data.embed_error), msg.channel]);
                                else:
                                    s = '';
                                    for word in args[argpos + 1:]:
                                        s += word + " ";
                                    yield from client.send_message(channel, '', embed=data.embedder([["**Suggestion:**", s + " "], ["**Author:**", msg.author.display_name + ":" + msg.author.id + ":<@" + msg.author.id + ">"]]));
                    ######################################
#############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
