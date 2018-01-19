import asyncio
import discord
import sys

class bf(object):

    def __init__(self):
        self.description = "Used to execute brainfuck code.";
        self.permissions = ['administrator'];
        self.Owner = False;
        self.bOwner = False;
        self.name = 'bf';
        self.tick = False;
        self.react = False;
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!bf help (args)\n' +
                'For Example: e!bf help help - shows this message.'
        };
        self.actions = 0;
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
        
    def evaluate(self, code):
        bracemap = self.buildbracemap(code)

        cells, codeptr, cellptr = [0], 0, 0

        res = '';

        while codeptr < len(code):
            command = code[codeptr]

            if command == '>':
                cellptr += 1
                if cellptr == len(cells):
                    if len(cells) < 300:
                        cells.append(0)
                    else:
                        cellptr -= 1

            if command == '<':
                cellptr = 0 if cellptr <= 0 else cellptr - 1

            if command == '+':
                cells[cellptr] = cells[cellptr] + 1 if cells[cellptr] < 255 else 0

            if command == '-':
                cells[cellptr] = cells[cellptr] -1 if cells[cellptr] > 0 else 255

            if command == '[' and cells[cellptr] == 0: codeptr = bracemap[codeptr]
            if command == ']' and cells[cellptr] != 0: codeptr = bracemap[codeptr]
            if command == '.': res += chr(cells[cellptr])
            if command == ',': 
                cells[cellptr] = ord(code[codeptr + 1])
                codeptr += 1
            codeptr += 1
            self.actions += 1
            if self.actions == 99999:
                return cells, 'Code execution took too long.'
        return cells, res

    def buildbracemap(self, code):
        temp_bracestack, bracemap = [], {}

        for position, command in enumerate(code):
            if command == '[': temp_bracestack.append(position)
            if command == ']':
                start = temp_bracestack.pop()
                bracemap[start] = position
                bracemap[position] = start
        return bracemap

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
                    else:
                        skip = len(args[argpos:]);
                        nArgs = args[argpos:];
                        code = '';
                        for nArg in nArgs:
                           code += nArg + ' ';
                        cells, res = self.evaluate(code);
                        results.append(['', data.embedder([['**Executed code:**', "'" + code + "'" ]]), msg.channel]);
                        results.append(['', data.embedder([['**Results of code execution:**', 'Cells:\n' + str(cells)]]), msg.channel]);
                        results.append(['', data.embedder([['Text output:', "'" + res + "'"]]), msg.channel]);
#############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
