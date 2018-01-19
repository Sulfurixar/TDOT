import os
import asyncio
from importlib import import_module

class commands(object):

    def __init__(self):
        self.path = os.getcwd();
        self.cmddir = os.path.join(self.path, 'commands');
        self.getCommands();
        return super().__init__();

    def getCommands(self):
        self.commands = {};
        for cmd in os.listdir(self.cmddir):
            name = cmd.split('.')[0];
            m = import_module('commands.' + name);
            a = getattr(m, name);
            executor = getattr(a, name);
            self.commands.update({name, executor});
        return

    @asyncio.coroutine
    def execute(self, client, cmd):
        execute = yield from self.commands[cmd].execute(client, cmd);
