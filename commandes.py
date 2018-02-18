import os
import asyncio


class Commandes(object):

    def __init__(self):
        self.path = os.getcwd()
        self.cmddir = os.path.join(self.path, 'commander')
        self.commands = {}
        self.get_commands()

    def get_commands(self):
        for cmd in os.listdir(self.cmddir):
            if '.py' in cmd:
                name = str(cmd.split('.')[0])
                m = __import__('commander.' + name)
                a = getattr(m, name)
                executor = getattr(a, name)
                self.commands.update({name: executor})
        return

    def get_events(self):
        ticks = {}
        reacts = {}
        for cmd in self.commands:
            if self.commands[cmd]().tick:
                ticks.update({cmd: self.commands[cmd]})
            if self.commands[cmd]().react:
                reacts.update({cmd: self.commands[cmd]})
        return ticks, reacts
        
    @asyncio.coroutine
    def execute(self, client, msg, data, args, cmd):
        print(data.cmds[cmd])
        executer = data.cmds[cmd]()
        yield from executer.execute(client, msg, data, args)

    @asyncio.coroutine
    def tick(self, client, data, cmd):
        print(data.cmds[cmd])
        executer = data.cmds[cmd]()
        yield from executer.ticker(client, data)
        
    @asyncio.coroutine
    def react(self, client, reaction, user, data, cmd):
        print(data.cmds[cmd])
        executer = data.cmds[cmd]()
        yield from executer.reactor(client, reaction, user, data)
