import asyncio
import os
import discord
import datetime


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
            'active_cycles': [0, 0],  # [cycle, epoch]
            'inactive_cycles': [0, 0],  # [cycle, epoch]
            'get': {'total': 0, 'cycle': 0, 'average': 0},
            'give': {'total': 0, 'cycle': 0, 'average': 0},
            'status': {
                'active': {
                    'date': datetime.datetime.now().strftime('%Y-%m-%d %H'),
                    'active': True
                },
                'inactive': {
                    'date': '',
                    'active': False
                },
                'frozen': {
                    'date': '',
                    'active': False
                }
            }

        }
        self.configExample = {
            'default': '',
            "analytics": {
                "totalCookies": 0,
                "cookiesThisCycle": 0,
                "cycleStartDate": datetime.datetime.now().strftime('%Y-%m-%d %H'),
                "cycleCount": [0, 0],
                "cookieAveragePerCycle": 0,
                "cookieChargeMax": 0,
                "cookieChargeOptimal": 0,
                "totalActiveCycles": 0,
                "totalInactiveCycles": 0
            }
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
    #           "cycleStartDate": 1998-12-13 6,
    #           "cycleCount": 123, /hours 0 ->
    #           "epochCount": 0, /28 days
    #           "cookieAveragePerCycle": 123,
    #           "cookieChargeMax": 100,
    #           "cookieChargeOptimal": 25,
    #           "totalActiveCycles": 9001,
    #           "totalInactiveCycles": 9999999
    #       },
    #       "previous_analytics":{}
    #   }
    # }

    def update_config(self, conf):
        default = self.configExample
        for key in default:
            if key not in conf:
                conf[key] = default[key]
            if key == 'analytics':
                for key2 in default[key]:
                    if key2 not in conf[key]:
                        conf[key][key2] = default[key][key2]
        return conf

    def update_user(self, u_data):
        default = self.userExample
        for key in default:
            if key not in u_data:
                u_data[key] = default[key]
            if key == 'get' or key == 'give':
                for key2 in default[key]:
                    if key2 not in u_data[key]:
                        u_data[key][key2] = default[key][key2]
                        if key == 'status':
                            for key3 in default[key][key2]:
                                if key3 not in u_data[key][key2]:
                                    u_data[key][key2][key3] = default[key][key2][key3]
        return u_data

    @staticmethod
    def update_user_data(u_data, member, curdate):
        # - UPDATE CURRENT STATE
        ###############################################################################################
        if u_data['status']['active']['active'] == 'True':
            if u_data['give']['cycle'] == 0 or u_data['get']['cycle'] == 0:
                if member.status is discord.Status.offline:
                    u_data['status']['active']['active'] = False
                    u_data['status']['inactive']['active'] = True
                    u_data['status']['inactive']['date'] = curdate.strftime('%Y-%m-%d %H')
        if u_data['status']['inactive']['active'] == 'True':
            if u_data['give']['cycle'] > 0 or u_data['get']['cycle'] > 0 or \
                    member.status is not discord.Status.offline:
                u_data['status']['inactive']['active'] = False
                u_data['status']['frozen']['active'] = False
                u_data['status']['active']['active'] = True
                u_data['status']['active']['date'] = curdate.strftime('%Y-%m-%d %H')
            else:
                d1 = u_data['status']['inactive']['date'].strptime('%Y-%m-%d %H')
                d = curdate - d1
                if d.days >= 28 and not u_data['status']['frozen']['active'] == 'True':
                    u_data['status']['frozen']['active'] = True
        ################################################################################################

        # - UPDATE CYCLES
        #########################################################################
        if u_data['status']['active']['active'] == 'True':
            u_data['active_cycles'][0] += 1
            if u_data['active_cycles'][0] % 672 == 0:
                u_data['active_cycles'] = [0, u_data['active_cycles'][1] + 1]
        if u_data['status']['inactive']['active'] == 'True':
            u_data['inactive_cycles'][0] += 1
            if u_data['inactive_cycles'][0] % 672 == 0:
                u_data['inactive_cycles'] = [0, u_data['inactive_cycles'][1] + 1]
        #########################################################################

        # - UPDATE GET/GIVE
        #############################################################################
        u_data['get']['total'] = u_data['get']['total'] + u_data['get']['cycle']
        u_data['get']['cycle'] = 0
        u_data['get']['average'] = \
            u_data['get']['total'] / \
            (
                    u_data['active_cycles'][0] + u_data['inactive_cycles'][0] +
                    672*(u_data['active_cycles'][1] + u_data['inactive_cycles'][1])
            )
        u_data['give']['total'] = u_data['give']['total'] + u_data['give']['cycle']
        u_data['give']['cycle'] = 0
        u_data['give']['average'] = \
            u_data['give']['total'] / \
            (
                    u_data['active_cycles'][0] + u_data['inactive_cycles'][0] +
                    672 * (u_data['active_cycles'][1] + u_data['inactive_cycles'][1])
            )
        #############################################################################

        return u_data

    @asyncio.coroutine
    def ticker(self, client, data):
        curdate = datetime.datetime.now()
        for server in data.servers:

            cookies_this_cycle = 0
            total_cookies = 0
            average_average = 0
            total_active = 0
            total_inactive = 0

            # - COOKIE ANALYTICS IN CONFIG.JSON
            ####################################################################
            if 'cookies' not in data.servers[server].custom_data:
                data.servers[server].custom_data['cookies'] = self.configExample
                conf = data.servers[server].custom_data['cookies']
            else:
                conf = self.update_config(data.servers[server].custom_data['cookies'])
            ####################################################################
            s = client.get_server(server)
            if s.large:
                yield from client.request_offline_members(s)
            members = s.members
            c = len(members)
            for member in members:
                u_data = self.update_user(data.c.get_user_data(member))
                cookies_this_cycle += u_data['get']['cycle']

                u_data = self.update_user_data(u_data, member, curdate)

                total_cookies += u_data['get']['total']
                average_average += u_data['give']['average']
                total_active += u_data['active_cycles']
                total_inactive += u_data['inactive_cycles']

                data.c.set_user_data(member, u_data=u_data)

            conf['analytics']['totalCookies'] = total_cookies
            conf['analytics']['cookiesThisCycle'] = cookies_this_cycle
            conf['analytics']['cycleCount'][0] += 1
            if conf['analytics']['cycleCount'][0] % 672 == 0:
                conf['analytics']['cycleCount'][0] = 0
                conf['analytics']['cycleCount'][1] += 1
            conf['analytics']['cookieAveragePerCycle'] = total_cookies / \
                                                         (
                                                                 conf['analytics']['cycleCount'][0] +
                                                                 672*conf['analytics']['cycleCount'][1]
                                                         )
            conf['analytics']['totalActiveCycles'] = total_active
            conf['analytics']['totalInactiveCycles'] = total_inactive

            #TODO: cookie charge max, cookie charge optimal

    @asyncio.coroutine
    def reactor(self, client, reaction, user, data):
        msg = reaction.message
        emoji = reaction.emoji
        react = False
        if 'cookie' in data.servers[msg.server.id].custom_data:
            if 'default' in data.servers[msg.server.id].custom_data['cookie']:
                if emoji == data.servers[msg.server.id].custom_data['cookie']['default']:
                    react = True
        if react:
            u1 = user
            u2 = msg.author

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
                            if 'cookie' in data.servers[msg.server.id].custom_data:
                                data.servers[msg.server.id].custom_data['cookie']['default'] = c
                            else:
                                data.servers[msg.server.id].custom_data['cookie'] = {'default': c}
                            data.servers[msg.server.id].update(client)
                            results.append(['', data.embedder([['Updated cookie:', c]]), msg.channel])
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
