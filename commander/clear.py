import asyncio
import discord

class clear(object):

    def __init__(self):
        self.description = 'Clears the reversible results of your commands.';
        self.permissions = [];
        self.Owner = False;
        self.bOwner = False;
        self.name = 'clear';
        self.tick = False;
        self.react = False;
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!clear help (args)\n' +
                'For Example: e!clear help help - shows this message.',
            'all':
                'Deletes all the messages sent by this bot during this session.\n' +
                'How to use this command: e!clear all\n' +
                'For Example: e!clear all - deletes all messages sent by Ely,not including embeds, during this session.'
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
            # Edit
            #yield from data.messager(msg, data.help(msg, self));
            c = 0;
            if msg.author.id in data.messages:
                for message in data.messages[msg.author.id]:
                    if data.perms.checkPerms(data, client, [message.channel, 'manage messages']):
                        try:
                            yield from client.delete_message(message);
                            c += 1;
                        except:
                            pass
                data.messages[msg.author.id] = [];
            yield from data.messager(msg, [['', data.embedder([['**Cleared your messages.**', 'Cleared a total of: ``' + str(c) + '`` messages.']]), msg.channel]]);
            yield from asyncio.sleep(10.0);
            for message in data.messages[msg.author.id]:
                    if data.perms.checkPerms(data, client, [message.channel, 'manage messages']):
                        try:
                            yield from client.delete_message(message);
                        except:
                            pass
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
                        results.append(['', 
                            data.embedder([
                                ['**Error:**', "Couldn't recognise ``" + arg + '``.']
                            ], colour=data.embed_error), msg.channel
                        ]);
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
                    if arg.lower() == 'all':
                        if not (msg.author.id == data.id):
                            results.append(['', data.embedder([['**Error:**', 'Insufficient permissions: You need to be the owner of this Bot to use this command.']], colour=data.embed_error), msg.channel]);
                        else:
                            c = 0;
                            if len(data.messages) > 0:
                                for entry in data.messages:
                                    for message in data.messages[entry]:
                                        if data.perms._user(data, client.user, [message.channel, 'manage messages']):
                                            try:
                                                yield from client.delete_message(message);
                                                c += 1;
                                            except:
                                                pass
                                data.messages = {};
                            yield from data.messager(msg, [['', data.embedder([['**Cleared your messages.**', 'Cleared a total of: ``' + str(c) + '`` messages.']]), msg.channel]]);
                            yield from asyncio.sleep(5.0);
                            for message in data.messages[msg.author.id]:
                                if data.perms._user(data, client.user, [message.channel, 'manage messages']):
                                    try:
                                        yield from client.delete_message(message);
                                    except:
                                        pass
                    ########################
#############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
