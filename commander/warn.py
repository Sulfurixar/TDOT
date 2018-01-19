import discord
import asyncio
import datetime

class warn(object):

    def __init__(self):
        self.description = "Used to warn people of their mischievous actions.";
        self.permissions = ['administrator'];
        self.Owner = False;
        self.bOwner = False;
        self.name = 'warn';
        self.tick = True;
        self.react = False;
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!warn help (args)``\n' +
                'For Example: ``e!warn help help`` - shows this message.',
            'show':
                'Displays the warnings that are currently active.\n' +
                'How to use this command: ``e!warn show``\n' +
                'For Example: ``e!warn show`` - shows the active warnings.'
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
    def ticker(self, client, data):
        print("Executed!")
        for server in data.servers:
            #print("1")
            if 'warnings' in data.servers[server].customData:
                #print("2")
                w = data.servers[server].customData['warnings'];
                #print("3")
                if len(w) > 0:
                    #print("4")
                    for user in w:
                        #print("5")
                        nWarnings = [];
                        #print("6")
                        if len(w[user]) > 0:
                            #print("7")
                            for entry in w[user]:
                                #print("8")
                                date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S.%f');
                                #print("9")
                                curDate = datetime.datetime.now();
                                #print("10")
                                diff = (date.year - curDate.year) * 12 + date.month - curDate.month;
                                #print("11")
                                if diff < 3:
                                    #print("12")
                                    nWarnings.append(warning);
                                    #print("13")
                            w[user] = nWarnings;
                            #print("14")
                            
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
                    # Edit
                    #if arg.lower() not in self.commands:
                    #    results.append(['', 
                    #        data.embedder([
                    #            ['**Error:**', "Couldn't recognise ``" + arg + '``.']
                    #        ], colour=data.embed_error), msg.channel
                    #    ]);
                    #    argpos += 1;
                    #    continue;
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
                        nArgs = args[argpos + 1];
                        if type(nArgs) != type([]):
                            nArgs = [nArgs];
                        skip = len(nArgs);
                        whitelist = [];
                        for name in nArgs:
                            user = None;
                            if '@' in name:
                                name = name[2:len(name)-1];
                                if name[0] == '!':
                                    name = name[1:];
                                user = msg.server.get_member(name);
                            else:
                                user = discord.utils.find(lambda m: m.display_name == name[1:], msg.server.members);
                            if user == None:
                                user = discord.utils.find(lambda m: m.id == name, msg.server.members);
                            if user == None:
                                results.append(['', data.embedder([['**Error:**', 'Specified user: ``' + name + '`` could not be found.']]), msg.channel]);
                            else:
                                whitelist.append(user);
                        if 'warnings' in data.servers[msg.server.id].customData:
                            if len(data.servers[msg.server.id].customData['warnings']) > 0:
                                users = {};
                                for user in data.servers[msg.server.id].customData['warnings']:
                                    if len(data.servers[msg.server.id].customData['warnings'][user]) > 0:
                                        d = '<@' + user + '>\n';
                                        c = 0;
                                        for entry in data.servers[msg.server.id].customData['warnings'][user]:
                                            d += str(c) + ') ' + entry['reason'] + ' - ``' + entry['date'] + '``.\n';
                                            c += 1;
                                        users[user] = d;
                                for user in users:
                                    ID = user;
                                    name = discord.utils.find(lambda m: m.id == user, msg.server.members);
                                    if name != None:
                                        user = name.display_name + ':' + name.id;
                                    else:
                                        user = ':' + user;
                                    if len(whitelist) > 0:
                                        for entry in whitelist:
                                            if ID == entry.id:
                                                results.append(['', data.embedder([['Warnings for: ' + user, users[ID]]]), msg.channel]);
                                    else:
                                        results.append(['', data.embedder([['Warnings for: ' + user, users[ID]]]), msg.channel]);
                    ##########################
                    if arg.lower() not in self.commands:
                        name = arg;
                        skip = len(args[argpos + 1:]);
                        message = ' '.join(args[argpos + 1:]);
                        user = None;
                        if '@' in name:
                            user = msg.mentions[0];
                        else:
                            user = discord.utils.find(lambda m: m.display_name == name[1:], msg.server.members);
                        if user == None:
                            user = discord.utils.find(lambda m: m.id == name, msg.server.members);
                        if user == None:
                            results.append(['', data.embedder([['**Error:**', 'Specified user: ``' + arg + '`` could not be found.']]), msg.channel]);
                        else:
                            warnings = {};
                            if 'warnings' in data.servers[msg.server.id].customData:
                                warnings = data.servers[msg.server.id].customData['warnings'];
                            if user.id in warnings:
                                warnings[user.id].append({'date': str(datetime.datetime.now()), 'reason': message});
                            else:
                                warnings[user.id] = [{'date': str(datetime.datetime.now()), 'reason': message}];
                            nWarnings = [];
                            for warning in warnings[user.id]:
                                date = datetime.datetime.strptime(warning['date'], '%Y-%m-%d %H:%M:%S.%f');
                                curDate = datetime.datetime.now();
                                diff = (date.year - curDate.year) * 12 + date.month - curDate.month;
                                if diff < 3:
                                    nWarnings.append(warning);
                            warnings[user.id] = nWarnings;
                            if len(warnings[user.id]) >= 3:
                                if data.servers[msg.server.id].debugChannel != ['','']:
                                    wr = '';
                                    c = 0;
                                    for warning in warnings[user.id]:
                                        wr += str(c) + ') ' + warning['reason'] + ' - ' + warning['date'] + '\n';
                                        c += 1;
                                    yield from client.send_message(data.servers[msg.server.id].commandChannel[2], '', embed=data.embedder([['**WARNING:**', 'User ``' + user.display_name + ':' + user.id + '`` <@' + user.id + '>:\n' + wr]]));
                            data.servers[msg.server.id].customData['warnings'] = warnings;
                            data.servers[msg.server.id].update(client);
                            results.append(['Warning placed!', data.embedder([['User', user.display_name + ':' + user.id + ' - <@' + user.id + '>'],['Reason:', message]]), msg.channel]);
                    ##########################
#############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
