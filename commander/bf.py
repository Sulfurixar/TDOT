import asyncio


class bf(object):

    def __init__(self):
        self.description = "Used to execute brainfuck code."
        self.permissions = ['administrator']
        self.Owner = False
        self.bOwner = False
        self.name = 'bf'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!bf help (args)\n' +
                'For Example: e!bf help help - shows this message.'
        }
        self.actions = 0

    def evaluate(self, code):
        bracemap = self.buildbracemap(code)

        cells, codeptr, cellptr = [0], 0, 0

        res = ''

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
                cells[cellptr] = cells[cellptr] - 1 if cells[cellptr] > 0 else 255

            if command == '[' and cells[cellptr] == 0:
                codeptr = bracemap[codeptr]
            if command == ']' and cells[cellptr] != 0:
                codeptr = bracemap[codeptr]
            if command == '.':
                res += chr(cells[cellptr])
            if command == ',':
                cells[cellptr] = ord(code[codeptr + 1])
                codeptr += 1
            codeptr += 1
            self.actions += 1
            if self.actions == 99999:
                return cells, 'Code execution took too long.'
        return cells, res

    @staticmethod
    def buildbracemap(code):
        temp_bracestack, bracemap = [], {}

        for position, command in enumerate(code):
            if command == '[':
                temp_bracestack.append(position)
            if command == ']':
                start = temp_bracestack.pop()
                bracemap[start] = position
                bracemap[position] = start
        return bracemap

    @asyncio.coroutine
    def execute(self, client, msg, data, args):
        if not data.can_use(self, msg):
            yield from data.messager(msg, [['', data.error(self, msg), msg.channel]])
            return

        if len(args) == 0:
            yield from data.messager(msg, data.help(msg, self))
            return
        else:
            results = []
            skip = 0
            argpos = 0
            for arg in args:
                if skip > 0:
                    skip -= 1
                    argpos += 1
                    continue
                else:
                    #############################################################################
                    if arg.lower() == 'help':
                        if len(args[argpos + 1:]) > 0:
                            _help = data.help(msg, self, args[argpos + 1:])
                            skip = len(args[argpos + 1:])
                        else:
                            _help = data.help(msg, self)
                        for h in _help:
                            results.append(h)
                    ##########################
                    else:
                        skip = len(args[argpos:])
                        n_args = args[argpos:]
                        code = ''
                        for nArg in n_args:
                            code += nArg + ' '
                        cells, res = self.evaluate(code)
                        results.append(['', data.embedder([['**Executed code:**', "'" + code + "'"]]), msg.channel])
                        results.append([
                            '',
                            data.embedder([['**Results of code execution:**', 'Cells:\n' + str(cells)]]),
                            msg.channel
                        ])
                        results.append(['', data.embedder([['Text output:', "'" + res + "'"]]), msg.channel])
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
