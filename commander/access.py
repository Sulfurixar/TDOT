import asyncio
import discord

class access(object):

    def __init__(self):
        self.description = 'Used to gain access to special roles or channels.';
        self.permissions = [];
        self.Owner = True;
        self.bOwner = False;
        self.name = 'get';
        self.tick = False;
        self.react = False;
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
                'How to use this command: ``e!access show``' +
                'For Example: ``e!access show``.',
            
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
                        if arg.lower() in data.servers[msg.server.id].customData['access']:
                            aArg = aType in data.servers[msg.server.id].customData['access'][arg.lower()];
                            for aType in aArg:
                                if aType == 'role':
                                    r = discord.utils.find(lambda m: m.id == aArg[aType], msg.server.roles);
                                    if r == None:
                                        r = discord.utils.find(lambda m: m.name == aArg[aType], msg.server.roles);
                                    if r != None:
                                        client.add_role(r, msg.author);
                                        results.append(['', data.embedder([['Granted role:', r.name]]), msg.channel]);
                                    else:
                                        results.append(['', data.embedder([['Couldn\'t find role:', aArg[aType]]]), msg.channel]);
                                if aType == 'channel':
                                    c = discord.utils.find(lambda m: m.id == aArg[aType], msg.server.channels);
                                    if c == None:
                                        c = discord.utils.find(lambda m: m.name == aArg[aType], msg.server.channels);
                                    if c != None:
                                        overwrite = discord.PermissionOverwrite();
                                        overwrite.read_messages = True;
                                        overwrite.send_messages = True;
                                        overwrite.add_reactions = True;
                                        overwrite.embed_links = True;
                                        overwrite.attach_files = True;
                                        overwrite.read_message_history = True;
                                        overwrite.external_emojis = True;
                                        overwrite.connect = True;
                                        overwrite.speak = True;
                                        overwrite.use_voice_activation = True;
                                        yield from client.edit_channel_permissions(c, msg.author, overwrite=overwrite);
                                        results.append(['', data.embedder([['Granted channel:', c.name]]), msg.channel]);
                                    else:
                                        results.append(['', data.embedder([['Couldn\'t find channel:', aArg[aType]]]), msg.channel])
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
                    if arg.lower() == 'show':
                        if 'access' in data.servers[msg.server.id].customData:
                            results.append(['', data.embedder([['**Access Data:**', str(data.servers[msg.server.id].customData['access']).replace("'", '"')]]), msg.channel]);
                        else:
                            results.append(['', data.embedder([['**Access Data:**', 'No custom data yet.']]), msg.channel]);
                    ##########################
                    if arg.lower() == 'config':
                        skip = len(args[argpos:]);
                        nArgs = args[argpos + 1:];
                        emb, res = data.json(nArgs);
                        if emb != None:
                            data.servers[msg.server.id].customData['access'] = emb;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Access Data:**', str(data.servers[msg.server.id].customData['access']).replace("'", '"')]]), msg.channel]);
                        else:
                            for r in res:
                                results.append(r);
                    ##########################
##############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
