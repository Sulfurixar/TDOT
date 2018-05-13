import asyncio
import discord
import datetime
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
                'For Example: ``e!cookie setcookie :cookie:`` - sets the default cookie into a cookie.',
            'show':
                'Displays your cookies for 10 seconds.\n' +
                'How to use this command: ``e!cookie show``\n' +
                'For Example: ``e!cookie show`` - shows your cookies.',
            'give':
                'Give cookies to people who deserve them!\n' +
                'How to use this command: ``e!cookie give (user) (amount)``\n' +
                'For Example: ``e!cookie give @Elisiya 10`` - gifts 10 cookies to @Elisiya.',
            'setranks':
                'Sets ranks given out by the cookie system.\n' +
                'How to use this command: ``e!cookie setranks {"rank_id": ["role_name", "treshold_value"]}``\n' +
                'For Example: ``e!cookie setranks {"1234567788": ["I am a role", "0.3"]}``'
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
                },
                'cookieOverload': {
                    'date': '',
                    'active': False,
                    'penalty': 0
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
                "cookieBaseMultiplier": 0,
                "highestCookieCount": 0
            },
            "rankings": {}
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
    #       "previous_analytics":{},
    #       "rankings": {
    #           "role_id": ['role_name', 90] / 90%, meaning from average to highest cookie count at 90% ((highest - average)*0.9)
    #       }
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

    def update_user_data(self, server, u_data, member, curdate):
        # pprint.pprint(str(u_data).encode('utf-8'))
        # - UPDATE CURRENT STATE
        ###############################################################################################
        status = u_data['cookies']['status']
        if str(status['active']['active']) == 'True':
            if u_data['cookies']['give']['cycle'] == 0 or u_data['cookies']['get']['cycle'] == 0 or \
                    member.status is discord.Status.offline:
                #print('active/' + str(member.status))
                status['active']['active'] = False
                status['inactive']['active'] = True
                status['inactive']['date'] = curdate.strftime('%Y-%m-%d %H')
        if str(status['inactive']['active']) == 'True':
            if u_data['cookies']['give']['cycle'] > 0 or u_data['cookies']['get']['cycle'] > 0 or \
                    member.status is not discord.Status.offline:
                #print('inactive/' + str(member.status))
                status['inactive']['active'] = False
                status['frozen']['active'] = False
                status['active']['active'] = True
                status['active']['date'] = curdate.strftime('%Y-%m-%d %H')
            else:
                d1 = datetime.datetime.strptime(status['inactive']['date'], '%Y-%m-%d %H')
                d = curdate - d1
                if d.days >= 28 and not status['frozen']['active'] == 'True':
                    status['frozen']['active'] = True

        if str(status['cookieOverload']['active']) == 'True':
            if status['cookieOverload']['penalty'] == 0:
                status['cookieOverload']['active'] = False
            else:
                status['cookieOverload']['penalty'] = status['cookieOverload']['penalty'] - 0.1
        if u_data['cookies']['give']['cycle'] > server['analytics']['cookieChargeOptimal']:
            status['cookieOverload']['active'] = True
            status['cookieOverload']['date'] = curdate.strftime('%Y-%m-%d %H')
            status['cookieOverload']['penalty'] = server['analytics']['cookieChargeMax'] - \
                u_data['cookies']['give']['cycle']

        u_data['status'] = status
        ################################################################################################

        # - UPDATE CYCLES
        #########################################################################
        # print('active: ' + str(status['active']['active']))
        if status['active']['active']:
            u_data['cookies']['active_cycles'][0] += 1
            if u_data['cookies']['active_cycles'][0] > 672:
                u_data['cookies']['active_cycles'] = [0, u_data['cookies']['active_cycles'][1] + 1]
            # print('ac_c: ' + str(data['cookies']['active_cycles']))
        # print('inactive: ' + str(status['inactive']['active']))
        if status['inactive']['active']:
            u_data['cookies']['inactive_cycles'][0] += 1
            if u_data['cookies']['inactive_cycles'][0] > 672:
                u_data['cookies']['inactive_cycles'] = [0, u_data['cookies']['inactive_cycles'][1] + 1]
            # print('ic_c: ' + str(data['cookies']['inactive_cycles']))
        #########################################################################

        # - UPDATE GET/GIVE
        #############################################################################
        u_data['cookies']['get']['total'] = u_data['cookies']['get']['total'] + u_data['cookies']['get']['cycle']
        u_data['cookies']['get']['cycle'] = 0
        div = u_data['cookies']['active_cycles'][0] + u_data['cookies']['inactive_cycles'][0] +\
            672*(u_data['cookies']['active_cycles'][1] + u_data['cookies']['inactive_cycles'][1])
        if div == 0 or div is None:
            div = 1
        u_data['cookies']['get']['average'] = \
            u_data['cookies']['get']['total'] / div
        u_data['cookies']['give']['total'] = u_data['cookies']['give']['total'] + u_data['cookies']['give']['cycle']
        u_data['cookies']['give']['cycle'] = 0
        div = u_data['cookies']['active_cycles'][0] + u_data['cookies']['inactive_cycles'][0] + \
            672*(u_data['cookies']['active_cycles'][1] + u_data['cookies']['inactive_cycles'][1])
        if div == 0 or div is None:
            div = 1
        u_data['cookies']['give']['average'] = u_data['cookies']['give']['total'] / div
        #############################################################################

        return u_data

    def member_handle(self, members, data, server):
        cookies_this_cycle = 0
        total_cookies = 0
        average_average = 0
        total_active = 0
        total_inactive = 0
        curdate = datetime.datetime.now()
        highest_cookie_count = 0

        for member in members:
            # - GET DATA
            #######################################################################################################
            u_data = self.update_user(data.c.get_user_data(member), data)
            cookies_this_cycle += u_data['cookies']['get']['cycle']

            u2_data = self.update_user_data(server, u_data, member, curdate)
            # print('updates: ' + str(u_data))

            total_cookies += u2_data['cookies']['get']['total']
            if u2_data['cookies']['get']['total'] > highest_cookie_count:
                highest_cookie_count = u2_data['cookies']['get']['total']
            average_average += u2_data['cookies']['give']['average']
            total_active += u2_data['cookies']['active_cycles'][0] + 672 * u2_data['cookies']['active_cycles'][1]
            total_inactive += u2_data['cookies']['inactive_cycles'][0] + 672 * u2_data['cookies']['inactive_cycles'][1]
            #######################################################################################################

            # - UPDATE USER DATA
            #######################################################
            data.c.set_user_data(member, data=u2_data)
            #######################################################

        return total_cookies, average_average, total_active, total_inactive, cookies_this_cycle, highest_cookie_count

    @asyncio.coroutine
    def rank_members(self, client, data, server, members):
        conf = server.custom_data['cookies']
        average = int(conf['analytics']['totalCookies']/len(members))
        tresholder = conf['analytics']['highestCookieCount'] - average
        ranks = conf['rankings']

        for member in members:
            u_data = self.update_user(data.c.get_user_data(member), data)
            best_rank_value = None
            best_rank = None
            current_rank = None
            for rank in ranks:
                treshold = int(tresholder * float(ranks[rank][1]))
                if u_data['cookies']['get']['total'] >= treshold:
                    if best_rank_value is None or best_rank_value < float(ranks[rank][1]):
                        best_rank_value = float(ranks[rank][1])
                        best_rank = discord.utils.find(lambda m: m.id == rank, server.serve.roles)
                role = discord.utils.find(lambda m: m.id == rank, server.serve.roles)
                if role in member.roles:
                    current_rank = role
                    if best_rank_value is not None and float(ranks[rank][1]) > best_rank_value:
                        best_rank_value = float(ranks[rank][1])
                        best_rank = role
            if best_rank is not None:
                give = True
                if current_rank is not None:
                    if current_rank == best_rank:
                        give = False
                    else:
                        yield from client.remove_roles(member, current_rank)
                if give:
                    yield from client.add_roles(member, best_rank)
            try:
                print('({}:{}):{}: tresholder({}), average({})'.format(
                    member.name, str(u_data['cookies']['get']['total']), best_rank.name, str(tresholder), str(average))
                )
            except:
                try:
                    print(member.name)
                except:
                    print(member.id)
                print(str(u_data['cookies']['get']['total']))
                try:
                    print(best_rank.name)
                except:
                    print(best_rank)
                print(str(tresholder))
                print(str(average))

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

            total_cookies, average_average, total_active, total_inactive, cookies_this_cycle, \
                highest_cookie_count = self.member_handle(members, data, conf)

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

            conf['analytics']['highestCookieCount'] = highest_cookie_count

            a = data.servers[server].serve.member_count
            c = np.log(a)/np.log((total_cookies**0.25) + 2)
            b = (a*2)**c
            d = 2*(total_cookies**0.75) + 1
            e = b/d

            conf['analytics']['cookieBaseMultiplier'] = e
            f = (a/10)
            g = int(f) / 20
            if g < 1:
                h = 20 + np.ceil(e/100)
            else:
                h = (f / g) + np.ceil(e/100)
            conf['analytics']['cookieChargeMax'] = h
            conf['analytics']['cookieChargeOptimal'] = np.ceil(h*0.75)
            data.servers[server].custom_data['cookies'] = conf

            yield from self.rank_members(client, data, data.servers[server], members)

            data.servers[server].update(client)

    def give_cookie(self, data, msg, u1, u2, amount):
        if u1 != u2:
            u_data1 = self.update_user(data.c.get_user_data(u1), data)
            c = u_data1['cookies']['give']['cycle']
            p = u_data1['cookies']['status']['cookieOverload']['penalty']
            m = data.servers[msg.server.id].custom_data['cookies']['analytics']['cookieChargeMax']
            if str(u_data1['cookies']['status']['cookieOverload']['active']) == 'True':
                n = c + np.ceil(p)
            else:
                n = c
            if n < m:
                if amount > m:
                    amount = m
                u_data1['cookies']['give']['cycle'] += amount
                data.c.set_user_data(u1, data=u_data1)
                u_data2 = self.update_user(data.c.get_user_data(u2), data)
                u_data2['cookies']['get']['cycle'] += amount
                data.c.set_user_data(u2, data=u_data2)
                return u_data1, u_data2, True
            return u_data1, None, False

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
            self.give_cookie(data, msg, u1, u2, 1)


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
                ########################################################
                if arg.lower() == 'show':
                    u_data = self.update_user(data.c.get_user_data(msg.author), data)
                    print(u_data['cookies'])
                    nmsg = yield from client.send_message(
                        msg.channel,
                        '',
                        embed=data.embedder([[
                            "You have received:",
                            str(u_data['cookies']['get']['total']) + ' ' +
                            data.servers[msg.server.id].custom_data['cookie']['default']
                            ],
                            [
                            '\nPending cookies:',
                            str(u_data['cookies']['get']['cycle']) +
                            data.servers[msg.server.id].custom_data['cookie']['default']
                        ]])
                    )
                    yield from asyncio.sleep(10)
                    yield from client.delete_message(nmsg)
                ##########################################################################
                if arg.lower() == 'give':
                    skip = len(args) - 1
                    user = None
                    if len(args) >= argpos + 1:
                        name = args[argpos + 1]
                        # print(name)
                        if '@' in name:
                            name = name[2:len(name) - 1]
                            if name[0] == '!':
                                name = name[1:]
                            f_user = msg.server.get_member(name)
                        else:
                            f_user = discord.utils.find(lambda m: m.display_name == name[1:], msg.server.members)
                        if user is None:
                            f_user = discord.utils.find(lambda m: m.id == name, msg.server.members)
                        if f_user is None:
                            results.append([
                                '',
                                data.embedder(
                                    [['**Error:**', 'Specified user: ``' + name + '`` could not be found.']]
                                ),
                                msg.channel
                            ])
                        else:
                            user = f_user
                    if user is not None:
                        amount = 1
                        if len(args) > argpos + 2:
                            try:
                                amount = int(args[argpos + 2])
                                # print(amount)
                            except:
                                results.append([
                                    '',
                                    data.embedder(
                                        [[
                                            'Error:',
                                            'Specified amount of cookies (' +
                                            args[argpos + 2] + ') is not in a valid format.'
                                        ]]
                                    ),
                                    msg.channel
                                ])
                        u2 = user
                        u1 = msg.author
                        u_data1, u_data2, success = self.give_cookie(data, msg, u1, u2, amount)
                        print(u_data2)
                        if success:
                            nmsg = yield from client.send_message(
                                msg.channel,
                                '',
                                embed=data.embedder([[
                                    "You have given:",
                                    str(amount) + ' ' +
                                    data.servers[msg.server.id].custom_data['cookie']['default']
                                ]])
                            )
                            yield from asyncio.sleep(10)
                            yield from client.delete_message(nmsg)
                #############################################################################
                if arg.lower() == 'setranks':
                    skip = len(args)
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
                        n_args = args[argpos + 1:]
                        emb, res = data.json(n_args, msg)
                        if emb is not None:
                            if cookie in data.servers[msg.server.id].custom_data:
                                conf = data.servers[msg.server.id].custom_data['cookies']
                            else:
                                data.servers[msg.server.id].custom_data['cookies'] = {}
                                conf = data.servers[msg.server.id].custom_data['cookies']
                            conf['rankings'] = emb
                            data.servers[msg.server.id].update(client)
                            m = ''
                            for rank in conf['rankings']:
                                m += conf['rankings'][rank][0] + ':' + \
                                     conf['rankings'][rank][1] + ':' + str(rank) + '\n'
                            results.append([
                                '',
                                data.embedder([['**Set rankings to:**', m]]),
                                msg.channel
                            ])
                        else:
                            for r in res:
                                results.append(r)
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
