import os
import sys
import asyncio
import importlib
import discord

class update(object):

    def __init__(self):
        self.path = os.getcwd();
        self.cmddir = os.path.join(self.path, 'commander');
        self.description = 'Updates the commands and permissions file.';
        self.permissions = ['administrator'];
        self.Owner = True;
        self.bOwner = True;
        self.name = 'update';
        self.tick = False;
        self.react = False;
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!get help (args)\n' +
                'For Example: e!get help help - shows this message.'
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
        results = [];

        commands = {};
        for cmd in os.listdir(self.cmddir):
            if '.py' in cmd:
                name = cmd.split('.')[0];
                m = __import__('commander.' + name);
                del sys.modules['commander.' + name]
                m = __import__('commander.' + name);
                m = importlib.reload(m);
                a = getattr(m, name);
                executor = getattr(a, name);
                commands.update({name: executor});
        data.cmds = commands;
        te = {};
        re = {};
        for cmd in data.cmds:
            if data.cmds[cmd]().tick:
                te.update({cmd: data.cmds[cmd]});
            if data.cmds[cmd]().react:
                re.update({cmd: data.cmds[cmd]});
        data.tickEvents = te;
        data.reactEvents = re;
        print(data.cmds);
        m = __import__('checkPermissions');
        del sys.modules['checkPermissions']
        m = __import__('checkPermissions');
        m = importlib.reload(m);
        a = getattr(m, 'checkPermissions');
        #c = getattr(a, 'checkPermissions');
        data.perms = a(client);
        print(a);
        
        cmds = '';
        c = 1;
        for cmd in data.cmds:
            cmds += '``' + cmd + '`` ';
            c += 1;
        results.append(['', data.embedder([["**Commands updated!**", cmds]]), msg.channel]);

        yield from data.messager(msg, results);
        results = [];
