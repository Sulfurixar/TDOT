import asyncio
from server import server
import discord
import json
import traceback

class setup(object):
    def __init__(self):
        self.description = 'Used to set up server specific details.';
        self.permissions = ['administrator'];
        self.Owner = True;
        self.bOwner = False;
        self.name = 'setup';
        self.tick = False;
        self.react = False;
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!setup help (args)``\n' +
                'For Example: ``e!setup help help`` - shows this message.',
            'commandchannel':
                "Sets this server's command channel as the channel specified.\n" +
                "How to use this command: ``e!setup commandChannel (exact channel name or its id)``\n" +
                'For Example: ``e!setup commandChannel 271336104735539200``',
            'joinchannel':
                "Sets this server's user join logging channel.\n" +
                "How to use this command: `e!setup joinChannel (exactl channel name or its id)\n`" +
                "For Example: ``e!setup joinChannel 271336104735539200``",
            'leavechannel':
                "Sets this server's user leaving logging channel.\n" +
                "How to use this command: `e!setup leaveChannel (exactl channel name or its id)\n`" +
                "For Example: ``e!setup leaveChannel 271336104735539200``",
            'authentication':
                "Enables or disables the bot's security question inquiry before giving roles.\n" +
                'How to use this command: ``e!setup authentication (true/false)``\n' +
                'For Example: ``e!setup authentication True``',
            'update':
                "Updates this server's server config - or creates one if it doesn't exist yet.\n" +
                'How to use this command: ``e!setup update``\n' +
                'For Example: ``e!setup update``',
            'giveroles':
                "Enables or disables the bot's ability to give roles on authentication.\n" +
                'How to use this command: ``e!setup giveRoles (true/false)``\n' +
                'For Example: ``e!setup giveRoles True``',
            'cmdlog':
                "Enables or disables command logging for this server.\n" +
                "How to use this command: ``e!setup cmdlog (true/false)``\n" +
                "For Example: ``e!setup cmdlog True``",
            'active':
                "Enables or disables config activity for this server.\n" +
                "How to use this command: ``e!setup active (true/false)``\n" +
                "For Example: ``e!setup active True``",
            'msgdellog':
                'Enables or disables message delete logging for this server.\n' +
                "How to use this command: ``e!setup msgdellog (true/false)``\n" +
                "For Example: ``e!setup msgdellog True``",
            'msgdelchannel':
                "Sets this server's message deletion recovery channel as the channel specified.\n" +
                "How to use this command: ``e!setup msgdelChannel (exact channel name or its id)``\n" +
                'For Example: ``e!setup msgdelChannel 271336104735539200``',
            'msgeditlog':
                'Enables or disables message edit logging for this server.\n' +
                "How to use this command: ``e!setup msgeditlog (true/false)``\n" +
                "For Example: ``e!setup msgeditlog True``",
            'msgeditchannel':
                "Sets this server's message edit checking channel as the channel specified.\n" +
                "How to use this command: ``e!setup msgeditChannel (exact channel name or its id)``\n" +
                'For Example: ``e!setup msgeditChannel 271336104735539200``',
            'welcomemsg':
                "Sets this server's user welcoming message in their private messages.\n" +
                "How to use this command: ``e!setup welcomemsg {'name':'Header', 'value': 'Text'}\n" +
                "For Example: ``e!setup welcomemsg {'name': 'Welcome!', 'value': 'Welcome to our server!'}",
            'welcoming':
                'Enables or disables welcome messages for users.\n' +
                "How to use this command: ``e!setup welcoming (true/false)``\n" +
                "For Example: ``e!setup welcoming True``",
            'permissions':
                "Manages permissions for roles to not have to rely on 'administrator'.\n" +
                "How to use this command: ``e!setup permissions (args)``\n" +
                "For Example: ``e!setup permissions show``",
            'setgiveroles':
                "Sets this server's roles that it gives upon users joining.\n" +
                "How to use this command: ``e!setup setgiveroles {\"rolename\":\"roleid\"}``\n" +
                "For Example: ``e!setup setgiveroles {\"Members\":\"199659930892894208\"}``"
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
        

    def makeValue(self, emb):
        name = '';
        value = '';
        if 'name' in emb:
            name = emb['name'];
        if 'value' in emb:
            value = emb['value'];

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
        
    def channeler(self, data, msg, client, info, name):
        channel = discord.utils.find(lambda m: m.name == info, msg.server.channels);
        if channel is None:
            channel = discord.utils.find(lambda m: m.id == info, msg.server.channels);
        if channel is None:
            return None, ['', data.embedder([["**Error:**", "Specified channel: ``" + info + "``, does not exist on this server."]]), msg.channel];
        else:
            if not channel.server.id in data.servers:
                s = server(client, msg.server.id);
                data.servers[msg.server.id] = server(client, msg.server.id);
                data.servers[msg.server.id].update(client);
            return channel, ['', data.embedder([["**" + name + ":**", "Set command channel for this server as ``" + channel.name + ":" + channel.id + "``."]]), msg.channel];


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
                    if arg.lower() == 'commandchannel':
                        skip = 1;
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "Command Channel");
                        if channel != None:
                            data.servers[msg.server.id].commandChannel = [channel.name, channel.id, channel];
                            data.servers[msg.server.id].update(client);
                        results.append(res);
                    ##########################
                    if arg.lower() == 'msgdelchannel':
                        skip = 1;
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "Delete Channel");
                        if channel != None:
                            data.servers[msg.server.id].deleteChannel = [channel.name, channel.id, channel];
                            data.servers[msg.server.id].update(client);
                        results.append(res);
                    #########################
                    if arg.lower() == 'msgeditchannel':
                        skip = 1;
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "Message Edit Channel");
                        if channel != None:
                            data.servers[msg.server.id].editChannel = [channel.name, channel.id, channel];
                            data.servers[msg.server.id].update(client);
                        results.append(res);
                    #########################
                    if arg.lower() == 'joinchannel':
                        skip = 1;
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "User Join Channel");
                        if channel != None:
                            data.servers[msg.server.id].joinChannel = [channel.name, channel.id, channel];
                            data.servers[msg.server.id].update(client);
                        results.append(res);
                    #########################
                    if arg.lower() == 'leavechannel':
                        skip = 1;
                        channel, res = self.channeler(data, msg, client, args[argpos + 1], "User Leaving Channel");
                        if channel != None:
                            data.servers[msg.server.id].leaveChannel = [channel.name, channel.id, channel];
                            data.servers[msg.server.id].update(client);
                        results.append(res);
                    #################
                    if arg.lower() == 'authentication':
                        skip = 1;
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.server.id].auth = True;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Authentication:**', 'Set authentication for this server to True.']]), msg.channel]);
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.server.id].auth = False;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Authentication:**', 'Set authentication for this server to False.']]), msg.channel]);
                        else:
                            results.append(['', data.embedder([['**Error:**', 'Invalid argument: ``' + args[argpos + 1] + '``.']], colour=data.embed_error), msg.channel]);
                    #############################################################
                    if arg.lower() == 'giveroles':
                        skip = 1;
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.server.id].giveRoles = True;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**GiveRoles:**', 'Set giveRoles for this server to True.']]), msg.channel]);
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.server.id].giveRoles = False;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**GiveRoles:**', 'Set giveRoles for this server to False.']]), msg.channel]);
                        else:
                            results.append(['', data.embedder([['**Error:**', 'Invalid argument: ``' + args[argpos + 1] + '``.']], colour=data.embed_error), msg.channel]);
                    ############################################################
                    if arg.lower() == 'cmdlog':
                        skip = 1;
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.server.id].commandLogging = True;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Command Logging:**', 'Set command logging for this server to True.']]), msg.channel]);
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.server.id].commandLogging = False;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Command Logging:**', 'Set command logging for this server to False.']]), msg.channel]);
                    ############################################################
                    if arg.lower() == 'active':
                        skip = 1;
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.server.id].active = True;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Config Activity:**', 'Set config activity for this server to True.']]), msg.channel]);
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.server.id].active = False;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Config Activity:**', 'Set config activity for this server to False.']]), msg.channel]);
                    ############################################################
                    if arg.lower() == 'msgdellog':
                        skip = 1;
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.server.id].messageDeleteLogging = True;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Message Delete Logging:**', 'Set message delete logging for this server to True.']]), msg.channel]);
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.server.id].messageDeleteLogging = False;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Message Delete Logging:**', 'Set message delete logging for this server to False.']]), msg.channel]);
                    ##########################################################
                    if arg.lower() == 'msgeditlog':
                        skip = 1;
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.server.id].messageEditLogging = True;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Message Edit Logging:**', 'Set message edit logging for this server to True.']]), msg.channel]);
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.server.id].messageEditLogging = False;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Message Edit Logging:**', 'Set message edit logging for this server to False.']]), msg.channel]);
                    ##########################################################
                    if arg.lower() == 'welcoming':
                        skip = 1;
                        if args[argpos + 1].lower() == 'true':
                            data.servers[msg.server.id].welcoming = True;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Welcoming:**', 'Set welcoming for this server to True.']]), msg.channel]);
                        elif args[argpos + 1].lower() == 'false':
                            data.servers[msg.server.id].welcoming = False;
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Welcoming:**', 'Set welcoming for this server to False.']]), msg.channel]);
                    ##########################################################
                    if arg.lower() == 'welcomemsg':
                        skip = len(args[argpos:]);
                        nArgs = args[argpos + 1:];
                        emb, res = data.json(nArgs);
                        if emb != None:
                            data.servers[msg.server.id].welcomeMessage = emb;
                            data.servers[msg.server.id].update(client);
                            results.append(['**Set welcome message to:**', data.embedder([[emb['name'], emb['value']]]), msg.channel]);
                        else:
                            for r in res:
                                results.append(r);
                    ##########################################################
                    if arg.lower() == 'permissions':
                        skip = len(args[argpos:]);
                        nSkip = 0;
                        nArgs = args[argpos + 1:];
                        nArgpos = 0;
                        subargs = ['show', 'set'];
                        if len(nArgs) > 0:
                            for nArg in nArgs:
                                if nSkip > 0:
                                    nSkip -= 1;
                                else:
                                    #
                                    if nArg.lower() not in subargs:
                                        print('Not in subargs... (' + nArg.lower() + ')');
                                        results.append(['', data.embedder([['**Error:**', "Couldn't recognize '" + nArg + "'."]]), msg.channel]);
                                    else:
                                        a = '';
                                        b = '';
                                        c = True;
                                        if '=' in nArg:
                                            t = nArg.split('=');
                                            if t[0].lower() in subargs:
                                                a = t[0].lower();
                                                b = t[1];
                                            else:
                                                c = False;
                                        else:
                                            a = nArg.lower();
                                        if c:
                                            #######################
                                            if a == 'show':
                                                results.append(['',data.embedder([['**Server Permissions:**', str(data.servers[msg.server.id].perms).replace("'",'"')]]), msg.channel]);
                                            #######################
                                            if a == 'set':
                                                nSkip = len(nArgs[nArgpos:]);
                                                bArgs = nArgs[nArgpos + 1:];
                                                emb, res = data.json(bArgs);
                                                if emb != None:
                                                    data.servers[msg.server.id].perms = emb;
                                                    data.servers[msg.server.id].update(client);
                                                    results.append(['', data.embedder([['**Server Permissions:**', 'Set server permissions to: ``' + str(emb) + '``.']]), msg.channel]);
                                                else:
                                                    for r in res:
                                                        results.append(r);
                                            #######################
                                    #
                                nArgpos += 1;
                        else:
                            results.append(['',data.embedder([['**Server Permissions:**', str(data.servers[msg.server.id].perms).replace("'",'"')]]), msg.channel]);
                    ##########################################################
                    if arg.lower() == 'setgiveroles':
                        skip = len(args[argpos:]);
                        nArgs = args[argpos + 1:];
                        emb, res = data.json(nArgs);
                        roles = {};
                        if emb != None:
                            for role in emb:
                                r = discord.utils.find(lambda m: m.id == emb[role], msg.server.roles);
                                if r == None:
                                    r = discord.utils.find(lambda m: m.name == role, msg.server.roles);
                                if r == None:
                                    results.append(['', data.embedder([['**Error:**', 'Could not find specified role: ``' + role + ':' + emb[role]]]), msg.channel]);
                                else:
                                    roles[r.name] = r.id;
                            #print(str(data.servers[msg.server.id].authRoles));
                            data.servers[msg.server.id].authRoles = roles;
                            #print(str(data.servers[msg.server.id].authRoles));
                            data.servers[msg.server.id].update(client);
                            results.append(['', data.embedder([['**Set giveroles to:**', '``' + str(roles) + '``']]), msg.channel]);
                        else:
                            for r in res:
                                results.append(r);
                    ##########################################################
                    if arg.lower() == 'update':
                        if msg.server.id in data.servers:
                            data.servers[msg.server.id].update(client);
                        else:
                            s = server(client, msg.server.id);
                            data.server.append({msg.server.id: s});
                            data.server[msg.server.id].update(client);
                        results.append(['', data.embedder([['**Updated ``' + msg.server.name + "``**", 'Update complete.']]), msg.channel]);
                    ##########################################
#############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
