import os
import sys
import asyncio
import importlib


class update(object):

    def __init__(self):
        self.path = os.getcwd()
        self.cmddir = os.path.join(self.path, 'commander')
        self.description = 'Updates the commands and permissions file.'
        self.permissions = ['administrator']
        self.Owner = True
        self.bOwner = True
        self.name = 'update'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!get help (args)\n' +
                'For Example: e!get help help - shows this message.'
        }

    @asyncio.coroutine
    def execute(self, client, msg, data, args):
        if not data.can_use(self, msg):
            yield from data.messager(msg, [['', data.error(self, msg), msg.channel]])
            return
        results = []

        commands = {}
        for cmd in os.listdir(self.cmddir):
            if '.py' in cmd:
                name = str(cmd.split('.')[0])
                del sys.modules['commander.' + name]
                m = __import__('commander.' + name)
                m = importlib.reload(m)
                a = getattr(m, name)
                executor = getattr(a, name)
                commands.update({name: executor})
        data.cmds = commands
        te = {}
        re = {}
        for cmd in data.cmds:
            if data.cmds[cmd]().tick:
                te.update({cmd: data.cmds[cmd]})
            if data.cmds[cmd]().react:
                re.update({cmd: data.cmds[cmd]})
        data.tickEvents = te
        data.reactEvents = re
        del sys.modules['checkPermissions']
        m = __import__('checkPermissions')
        m = importlib.reload(m)
        a = getattr(m, 'CheckPermissions')
        data.perms = a(client)
        
        cmds = ''
        c = 1
        for cmd in data.cmds:
            cmds += '``' + cmd + '`` '
            c += 1
        results.append(['', data.embedder([["**Commands updated!**", cmds]]), msg.channel])

        yield from data.messager(msg, results)
