import os
import asyncio
from importlib import import_module


class Commands(object):

    def __init__(self):
        self.path = os.getcwd()
        self.cmddir = os.path.join(self.path, 'commands')
        self.commands = {}
        self.get_commands()

    def get_commands(self):
        for cmd in os.listdir(self.cmddir):
            name = str(cmd.split('.')[0])
            m = import_module('commands.' + name)
            a = getattr(m, name)
            executor = getattr(a, name)
            self.commands.update({name, executor})
        return

    @asyncio.coroutine
    def execute(self, client, cmd):
        yield from self.commands[cmd].execute(client, cmd)
