import asyncio
import os
import json


class cookie(object):

    def __init__(self):
        self.description = 'Used to give your buddies a cookie on a good day.'
        self.permissions = []
        self.Owner = False
        self.bOwner = False
        self.name = 'cookie'
        self.tick = True
        self.react = True
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: ``e!cookie help (args)``\n' +
                'For Example: ``e!cookie help help`` - shows this message.',
            'setcookie':
                'Sets the default cookie into the specified emoji.\n' +
                'How to use this command: ``e!cookie setcookie (args)``\n' +
                'For Example: ``e!cookie setcookie :cookie:`` - sets the default cookie into a cookie.'
        }
        self.userExample = {
            'active_cycles': 0,
            'inactive_cycles': 0,
            'get': {'total': 0, 'cycle': 0, 'average': 0},
            'give': {'total': 0, 'cycle': 0, 'average': 0},
            'custom': {},
            'previous_cycles': {}

        }
        self.configExample = {
            'default': '',
            "custom": {},
            "analytics": {
                "totalCookies": 0,
                "cookiesThisCycle": 0,
                "cycleCount": 0,
                "epochCount": 0,
                "cookieAveragePerCycle": 0,
                "cookieChargeMax": 0,
                "cookieChargeOptimal": 0,
                "totalActiveCycles": 0,
                "totalInactiveCycles": 0
            },
            'previous_analytics': {}
        }

    # {
    #   "cookies": {
    #       "default": "emoji",
    #       "custom": {
    #           "emoji": 10 //emoji and it's value in cookies
    #           }
    #       },
    #       "analytics": {
    #           "totalCookies": 123,
    #           "cookiesThisCycle": 123,
    #           "cycleCount": 123,
    #           "epochCount": 0,
    #           "cookieAveragePerCycle": 123,
    #           "cookieChargeMax": 100,
    #           "cookieChargeOptimal": 25,
    #           "totalActiveCycles": 9001,
    #           "totalInactiveCycles": 9999999
    #       }
    #   }
    # }
        
    @asyncio.coroutine
    def ticker(self, client, data):
        for server in data.servers:
            if 'cookies' in data.servers[server].customData:
                if 'analytics' in data.servers[server].customData['cookies']:
                    for t in self.configExample:
                        if t not in data.servers[server].customData['cookies']:
                            data.servers[server].customData['cookies'] = self.configExample[t]
                        else:
                            if t == 'analytics':
                                for y in self.configExample['analytics']:
                                    if y not in data.servers[server].customData['cookies']['analytics']:
                                        data.servers[server].customData['cookies']['analytics'][y] = \
                                            self.configExample['analytics'][y]
                    if os.path.exists(os.path.join(os.getcwd(), 'commander', 'cookies', server)):
                        user_files = os.listdir(os.path.join(os.getcwd(), 'commander', 'cookies', server))
                        
                        total_cookies = 0
                        active_cycles = 0
                        inactive_cycles = 0
                        get_cycle = []
                        get_average = []
                        give_cycle = []
                        give_average = []
                        
                        for userPath in user_files:
                            with open(userPath) as uFile:
                                u_data = json.load(uFile)
                                uFile.close()
                            for e in u_data:
                                if e == 'active_cycles':
                                    active_cycles = active_cycles + int(u_data[e])
                                if e == 'inactive_cycles':
                                    inactive_cycles = inactive_cycles + int(u_data[e])
                                if e == 'get':
                                    get_cycle.append(int(u_data[e]))
                                    avg = u_data[e]['total'] / (u_data['active_cycles'] + u_data['inactive_cycles'])
                                    get_average.append(avg)
                                    u_data[e]['average'] = avg
                                    total_cookies = total_cookies + u_data[e]['total']
                                if e == 'give':
                                    give_cycle.append(int(u_data[e]))
                                    avg = u_data[e]['total'] / (u_data['active_cycles'] + u_data['inactive_cycles'])
                                    give_average.append(avg)
                                    u_data[e]['average'] = avg
                else:
                    data.servers[server].customData['cookies']['analytics'] = self.configExample['analytics']

    @staticmethod
    def check_exists(paths):
        if type(paths).isinstance([]):
            paths = [paths]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)
                
    def check_vars(self, js):
        for t in self.userExample:
            if t not in js:
                js[t] = self.userExample[t]
        return js

    def h_user(self, user, backup, data):
        with open(user, 'r') as uFile:
            try:
                js = json.load(user)
            except Exception as e:
                print(repr(e))
                with open(backup, 'r') as bFile:
                    try:
                        js = json.load(backup)
                    except Exception as f:  # this is really bad...
                        print(repr(f))
                        js = self.userExample
                    bFile.close()
            uFile.close()
        js = self.check_vars(js)
        return js

    @asyncio.coroutine
    def reactor(self, client, reaction, user, data):
        msg = reaction.message
        emoji = reaction.emoji
        react = False
        if 'cookie' in data.servers[msg.server.id].customData:
            if 'default' in data.servers[msg.server.id].customData['cookie']:
                if emoji == data.servers[msg.server.id].customData['cookie']['default']:
                    react = True
        if react:
            u1 = user
            u2 = msg.author
            h = os.getcwd()
            cookies = os.path.join(h, 'commander', 'cookies')
            backup = os.path.join(cookies, 'backups')
            if not os.path.exists(cookies):
                os.makedirs(cookies)
            cookies = os.path.join(cookies, msg.server.id)
            if not os.path.exists(cookies):
                os.makedirs(cookies)
            u1_dir = os.path.join(cookies, u1.id + '.json')
            u2_dir = os.path.join(cookies, u2.id + '.json')
            cycle = str(data.servers[msg.server.id].customData['cookies']['analytics']['cycleCount'])
            u1_bak = os.path.join(backup, '[' + cycle + ']' + u1.id + '.json')
            u2_bak = os.path.join(backup, '[' + cycle + ']' + u2.id + '.json')
            
            js = self.h_user(u1_dir, u1_bak, data)
            json.dump(js, u1_bak)
            js['give']['cycle'] = js['give']['cycle'] + 1
            json.dump(js, u1_dir)
            
            js = self.h_user(u2_dir, u2_bak, data)
            json.dump(js, u2_bak)
            js['total_cookies'] = js['total_cookies'] + 1
            js['get']['cycle'] = js['get']['cycle'] + 1
            json.dump(js, u2_dir)

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
                    if arg.lower() not in self.commands:
                        results.append([
                            '',
                            data.embedder([
                                ['**Error:**', "Couldn't recognise ``" + arg + '``.']],
                                colour=data.embed_error
                            ),
                            msg.channel
                        ])
                        argpos += 1
                        continue
#############################################################################
                    if arg.lower() == 'help':
                        if len(args[argpos + 1:]) > 0:
                            _help = data.help(msg, self, args[argpos + 1:])
                            skip = len(args[argpos + 1:])
                        else:
                            _help = data.help(msg, self)
                        for h in _help:
                            results.append(h)
                    ########################################################
                    if arg.lower() == 'setcookie':
                        skip = 1
                        c = args[argpos + 1]
                        if not (msg.author.id == msg.server.owner.id or msg.author.id == data.id):
                            results.append([
                                '',
                                data.embedder(
                                    [[
                                        '**Error:**',
                                        'Insufficient permissions: You need to be the owner of ``' + msg.server.name +
                                        "`` or owner of this Bot to use this command."
                                    ]],
                                    colour=data.embed_error
                                ),
                                msg.channel
                            ])
                        else:
                            if '<' in c:
                                s = c.split(':')
                                c = s[1]
                            if 'cookie' in data.servers[msg.server.id].customData:
                                data.servers[msg.server.id].customData['cookie']['default'] = c
                            else:
                                data.servers[msg.server.id].customData['cookie'] = {'default': c}
                            data.servers[msg.server.id].update(client)
                            results.append(['', data.embedder([['Updated cookie:', c]]), msg.channel])
#############################################################################
                argpos += 1
            yield from data.messager(msg, results)
