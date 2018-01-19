import asyncio
import discord

class get(object):

    def __init__(self):
        self.description = 'Used to retrieve various kinds of information.';
        self.permissions = ['administrator'];
        self.Owner = True;
        self.bOwner = False;
        self.name = 'get';
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
                'How to use this command: ``e!get users``'
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
                            ]);
                        else:
                            s = data.servers[str(msg.server.id)];
                            name = msg.server.name;
                            authRoles = '';
                            for role in s.authRoles:
                                authRoles = authRoles + "``" + role + ";`` ";
                            res = '';
                            if len(s.perms) > 0:
                                for perm in s.perms:
                                    print(perm)
                                    if len(perm) > 0:
                                        for entry in perm:
                                            print(entry)
                                            if entry == 'name':
                                                res += 'Name: ``' + perm[entry] + '``\n';
                                            if entry == 'names':
                                                if len(perm[entry]) > 0:
                                                    res += 'Names: \n';
                                                    for ID in perm[entry]:
                                                        res += perm[entry][ID] + ':' + ID + '\n';
                                            if entry == 'roles':
                                                if len(perm[entry]) > 0:
                                                    res += 'Roles: \n';
                                                    for ID in perm[entry]:
                                                        res += perm[entry][ID] + ':' + ID + '\n';
                                            if entry == 'cmds':
                                                if len(perm[entry]) > 0:
                                                    res += 'Commands: \n';
                                                    for cmd in perm[entry]:
                                                        res += cmd + '\n'
                            if res == '':
                                res = 'N/A';
                            results.append(['', data.embedder([
                                ['**Server Data:**', "Server name: ``" + name + "``\n" +
                            "Server ID: ``" + s.id + "``\n" +
                            "Server Config Active: ``" + str(s.active) + "``\n" +
                            "Server Authentication: ``" + str(s.auth) + "``\n" +
                            "Server Command Logging: ``" + str(s.commandLogging) + "``\n" +
                            "Server Message Deletion Logging: ``" + str(s.messageDeleteLogging) + "``\n" +
                            "Server Message Edit Logging: ``" + str(s.messageEditLogging) + "``\n" +
                            "Server Give Authentication Roles: ``" + str(s.giveRoles) + "``\n" +
                            "Server Question: ``" + s.question + "``\n" +
                            "Server Answer: ``" + s.answer + "``\n" +
                            "Server Authentication Roles: " + authRoles + "\n" +
                            "Server Debug Channel: ``" + str(s.debugChannel[0]) + ":" + str(s.debugChannel[1]) + "``\n" +
                            "Server Welcome Channel: ``" + str(s.welcomeChannel[0]) + ":" + str(s.welcomeChannel[1]) + "``\n" +
                            "User Welcoming: ``" + str(s.welcoming) + "``\n" +
                            "Server Command Channel: ``" + str(s.commandChannel[0]) + ":" + str(s.commandChannel[1]) + "``\n" +
                            "Server Message Edit Checking Channel: ``" + str(s.editChannel[0]) + ':' + str(s.editChannel[1]) + "``\n" +
                            "Server Message Deletion Recovery Channel: ``" + str(s.deleteChannel[0]) + ':' + str(s.deleteChannel[1]) + "``\n"]
                            ]), msg.channel]);
                            print(res)
                            print(str(s.customData))
                            print((s.welcomeMessage))
                            results.append(['', data.embedder([["**Server Permissions:**", res], ["**Custom Data**:", str(s.customData)],["User Welcoming Message:", "``" + str(s.welcomeMessage) + "``"]]), msg.channel]);
                    ##########################
                    if arg.lower() == 'channels':
                        channels = [''];
                        c = 1;
                        d = 0;
                        for channel in msg.server.channels:
                            channels[-1] += str(c) + ') ``' + channel.name + '|' + channel.id + '`` \n';
                            c += 1;
                            d += 1;
                            if d == 10:
                                channels.append('');
                                d = 0;
                        c = 1;
                        for channel in channels:
                            results.append(['', data.embedder([["**Server Channels(" + str(c) + "):**", channels[c-1]]]), msg.channel]);
                            c += 1;
                    ###############
                    if arg.lower() == 'roles':
                        roles = [''];
                        c = 1;
                        d = 0;
                        for role in msg.server.roles:
                            roles[-1] += str(c) + ') ``' + role.name + "|" + role.id + '`` \n';
                            c += 1;
                            d += 1;
                            if d == 10:
                                roles.append('');
                                d = 0;
                        c = 1;
                        for role in roles:
                            results.append(['', data.embedder([['**Server Roles(' + str(c) + '):**', roles[c-1]]]), msg.channel]);
                            c += 1;
                    ####
                    if arg.lower() == 'users':
                        users = [''];
                        c = 1;
                        d = 0;
                        for user in msg.server.members:
                            users[-1] += str(c) + ') ``' + user.display_name + "|" + user.id + '`` \n';
                            c += 1;
                            d += 1;
                            if d == 10:
                                users.append('');
                                d = 0;
                        c = 1;
                        for user in users:
                            results.append(['', data.embedder([['**Server Users(' + str(c) + '):**', users[c-1]]]), msg.channel]);
                            c += 1;
                    ####
##############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
