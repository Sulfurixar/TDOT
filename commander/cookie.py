import asyncio
import discord
import datetime
import pprint
import copy
import numpy as np


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
                "totalInactiveCycles": 0,
                "cookieBaseMultiplier": 0
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

    def update_user(self, u_data, data):
        default = copy.deepcopy(self.userExample)
        if 'cookies' not in u_data:
            u_data['cookies'] = {}
        for key in default:
            if key not in u_data['cookies']:
                u_data['cookies'][key] = default[key]
            if key == 'get' or key == 'give' or key == 'status':
                for key2 in default[key]:
                    if key2 not in u_data['cookies'][key]:
                        u_data['cookies'][key][key2] = default[key][key2]
                        if key == 'status':
                            for key3 in default[key][key2]:
                                if key3 not in u_data['cookies'][key][key2]:
                                    u_data['cookies'][key][key2][key3] = default[key][key2][key3]

        return u_data

    def update_user_data(self, data, member, curdate):
        # pprint.pprint(str(u_data).encode('utf-8'))
        # - UPDATE CURRENT STATE
        ###############################################################################################
        status = data['cookies']['status']
        if str(status['active']['active']) == 'True':
            if data['cookies']['give']['cycle'] == 0 or data['get']['cycle'] == 0:
                if member.status is discord.Status.offline:
                    status['active']['active'] = False
                    status['inactive']['active'] = True
                    status['inactive']['date'] = curdate.strftime('%Y-%m-%d %H')
        if str(status['inactive']['active']) == 'True':
            if data['cookies']['give']['cycle'] > 0 or data['get']['cycle'] > 0 or \
                    member.status is not discord.Status.offline:
                status['inactive']['active'] = False
                status['frozen']['active'] = False
                status['active']['active'] = True
                status['active']['date'] = curdate.strftime('%Y-%m-%d %H')
            else:
                d1 = status['inactive']['date'].strptime('%Y-%m-%d %H')
                d = curdate - d1
                if d.days >= 28 and not status['frozen']['active'] == 'True':
                    status['frozen']['active'] = True

        data['status'] = status
        ################################################################################################

        # - UPDATE CYCLES
        #########################################################################
        # print('active: ' + str(status['active']['active']))
        if status['active']['active']:
            data['cookies']['active_cycles'][0] += 1
            if data['cookies']['active_cycles'][0] > 672:
                data['cookies']['active_cycles'] = [0, data['cookies']['active_cycles'][1] + 1]
            # print('ac_c: ' + str(data['cookies']['active_cycles']))
        # print('inactive: ' + str(status['inactive']['active']))
        if status['inactive']['active']:
            data['cookies']['inactive_cycles'][0] += 1
            if data['cookies']['inactive_cycles'][0] > 672:
                data['cookies']['inactive_cycles'] = [0, data['cookies']['inactive_cycles'][1] + 1]
            # print('ic_c: ' + str(data['cookies']['inactive_cycles']))
        #########################################################################

        # - UPDATE GET/GIVE
        #############################################################################
        data['cookies']['get']['total'] = data['cookies']['get']['total'] + data['cookies']['get']['cycle']
        data['cookies']['get']['cycle'] = 0
        div = data['cookies']['active_cycles'][0] + data['cookies']['inactive_cycles'][0] +\
            672*(data['cookies']['active_cycles'][1] + data['cookies']['inactive_cycles'][1])
        if div == 0 or div is None:
            div = 1
        data['cookies']['get']['average'] = \
            data['cookies']['get']['total'] / div
        data['cookies']['give']['total'] = data['cookies']['give']['total'] + data['cookies']['give']['cycle']
        data['cookies']['give']['cycle'] = 0
        div = data['cookies']['active_cycles'][0] + data['cookies']['inactive_cycles'][0] + \
            672*(data['cookies']['active_cycles'][1] + data['cookies']['inactive_cycles'][1])
        if div == 0 or div is None:
            div = 1
        data['cookies']['give']['average'] = data['cookies']['give']['total'] / div
        #############################################################################

        return data

    def member_handle(self, members, data):
        cookies_this_cycle = 0
        total_cookies = 0
        average_average = 0
        total_active = 0
        total_inactive = 0
        curdate = datetime.datetime.now()

        for member in members:
            # - GET DATA
            #######################################################################################################
            u_data = self.update_user(data.c.get_user_data(member), data)
            cookies_this_cycle += u_data['cookies']['get']['cycle']

            u2_data = self.update_user_data(u_data, member, curdate)
            # print('updates: ' + str(u_data))

            total_cookies += u2_data['cookies']['get']['total']
            average_average += u2_data['cookies']['give']['average']
            total_active += u2_data['cookies']['active_cycles'][0] + 672 * u2_data['cookies']['active_cycles'][1]
            total_inactive += u2_data['cookies']['inactive_cycles'][0] + 672 * u2_data['cookies']['inactive_cycles'][1]
            #######################################################################################################

            # - UPDATE USER DATA
            #######################################################
            data.c.set_user_data(member, data=u2_data)
            #######################################################

        return total_cookies, average_average, total_active, total_inactive, cookies_this_cycle

    @asyncio.coroutine
    def ticker(self, client, data):
        for server in data.servers:

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

            total_cookies, average_average, \
                total_active, total_inactive, cookies_this_cycle = self.member_handle(members, data)

            conf['analytics']['totalCookies'] = total_cookies
            conf['analytics']['cookiesThisCycle'] = cookies_this_cycle
            conf['analytics']['cycleCount'][0] += 1
            if conf['analytics']['cycleCount'][0] > 672:
                conf['analytics']['cycleCount'][0] = 0
                conf['analytics']['cycleCount'][1] += 1
            div = (conf['analytics']['cycleCount'][0] + 672*conf['analytics']['cycleCount'][1])
            if div == 0:
                div += 1
            conf['analytics']['cookieAveragePerCycle'] = total_cookies / div
            conf['analytics']['totalActiveCycles'] = total_active
            conf['analytics']['totalInactiveCycles'] = total_inactive

            a = data.servers[server].serve.member_count
            c = np.log(a)/np.log((total_cookies**0.25) + 2)
            b = (a*2)**c
            d = 2*(total_cookies**0.75) + 1
            e = b/d

            conf['analytics']['cookieBaseMultiplier'] = e

            #TODO: cookie charge max, cookie charge optimal

    @asyncio.coroutine
    def reactor(self, client, reaction, user, data):
        msg = reaction.message
        emoji = reaction.emoji
        if type(emoji) is str:
            e_name = emoji
        else:
            try:
                e_name = '<:' + emoji.name + ':' + emoji.id + '>'
            except:
                e_name = None
        react = False
        if 'cookie' in data.servers[msg.server.id].custom_data:
            if 'default' in data.servers[msg.server.id].custom_data['cookie']:
                if e_name == data.servers[msg.server.id].custom_data['cookie']['default']:
                    react = True
        if react:
            u1 = user
            u2 = msg.author
            if u1 != u2:
                u_data = self.update_user(data.c.get_user_data(u1), data)
                u_data['cookies']['give']['cycle'] += 1
                data.c.set_user_data(u1, data=u_data)
                u_data = self.update_user(data.c.get_user_data(u2), data)
                u_data['cookies']['get']['cycle'] += 1
                data.c.set_user_data(u2, data=u_data)


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
                            if ':' in c:
                                a = c.split(':')
                                if len(a) != 3:
                                    results.append([
                                        '',
                                        data.embedder([[
                                            'Invalid input for cookie emoji!', 'Invalid input: ' + str(c)
                                        ]]),
                                        msg.channel
                                    ])
                                else:
                                    cooki = c
                                    if 'cookie' in data.servers[msg.server.id].custom_data:
                                        data.servers[msg.server.id].custom_data['cookie']['default'] = cooki
                                    else:
                                        data.servers[msg.server.id].custom_data['cookie'] = {'default': cooki}
                                    data.servers[msg.server.id].update(client)
                                    results.append([
                                        '',
                                        data.embedder([['Updated cookie:', cooki]]),
                                        msg.channel
                                    ])
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
