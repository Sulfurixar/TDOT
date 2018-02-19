import discord
import asyncio
import logging
import sys
import time
from config import Config
from commandes import Commandes
from checkPermissions import CheckPermissions
# from concurrent.futures import ProcessPoolExecutor
import datetime
import json
import traceback

client = discord.Client()


class Data(object):
    def __init__(self):
        self.id = '149381939428589568'
        self.c = Config(client)
        self.perms = CheckPermissions(client)
        self.cmd = Commandes()
        self.cmds = self.cmd.commands
        self.tickEvents, self.reactEvents = self.cmd.get_events()
        self.answers = {}
        self.servers = {}
        self.messages = {}  # {authorID: [msg, msg, msg]}
        # //allows for multiple inquiries per single command, also allows to delete them at the same time.
        self.dmessages = {}  # {authorID: msg} //keeps track of the last command executed by user
        self.embed_normal = 0xFFE83C
        self.embed_error = 0xDC143C
        self.embed_announce = 0x00FFFF
        self.version = 'Truly Golden Update 0.3.2 - Anorexic'

    def check(self, cmd, msg):
        if msg.server.id in self.servers:
            p = self.servers[msg.server.id].perms
            for entry in p:
                if msg.author.id in entry['names']:
                    if cmd.name in entry['cmds']:
                        return True
                for role in entry['roles']:
                    r = discord.utils.find(lambda m: m.id == role, msg.author.roles)
                    if r is not None:
                        if cmd.name in entry['cmds']:
                            return True
        return False

    def can_use(self, cmd, msg):
        use = True
        for perm in cmd.permissions:
            a = self.perms._user(self, msg.author, [msg.channel, perm])
            if msg.author.id == self.id:
                b = True
            else:
                b = False
            c = self.check(cmd, msg)
            if True not in [a, b, c]:
                use = False
        if cmd.Owner:
            if msg.author.id != msg.server.owner.id:
                if msg.author.id != self.id:
                    use = False
        if cmd.bOwner and msg.author.id != self.id:
            use = False
        return use

    def error(self, cmd, msg):
        message = 'Insufficient permissions. '
        if len(cmd.permissions) > 0:
            message += 'You must have: '
            for perm in cmd.permissions:
                message += '``' + perm + '`` '
            message += '; permissions by default.'
        if cmd.Owner and not cmd.bOwner:
            message += ' This command can be run by the Owner of ``' + msg.server.name + '`` or ``Bot``.'
        elif cmd.bOwner:
            message += ' This command can be run only by the Owner of the ``Bot``.'
        return self.embedder([['**Error:**', message]], colour=self.embed_error)

    def embedder(self, fields, given_embed=None, colour=None):
        embed = discord.Embed()
        if given_embed is not None:
            embed = given_embed
        if colour is None:
            colour = self.embed_normal
        embed.colour = colour
        embed.set_author(
            name=client.user.display_name,
            url=discord.Embed.Empty,
            icon_url=client.user.avatar_url
        )
        if len(fields) > 0:
            for field in fields:
                embed.add_field(
                    name=field[0],
                    value=field[1]
                )
        return embed

    @staticmethod
    def base_help(cmd, desc):
        if not (cmd is None):
            return [
                "**Command: '" + cmd + "':**",
                desc + "\nUsage: ``{prefix}[command]`` ``(args)``\n" +
                "Legend: ``{}`` - required only on servers, ``[]``" +
                " - required every time, ``()`` - optional\n" +
                "Example: ``e!" +
                cmd +
                ' help help`` - displays how to use the help command.'
            ]
        else:
            return [
                "**Command: 'help':**",
                desc + "\nUsage: ``{prefix}[command]`` ``(args)``\n" +
                "Legend: ``{}`` - required only on servers, ``[]``" +
                " - required every time, ``()`` - optional\n" +
                "Example: ``e!help help`` - displays how to use the help command."
            ]

    def help(self, msg, _cmd, args=None):
        if args is None or len(args) == 0:
            cmds = ''
            for cmd in _cmd.commands:
                cmds += '``' + cmd + '`` '
            if cmds == '':
                cmds = 'Currently there are no arguments for this command.'
            if _cmd.name != 'help':
                base = self.base_help(_cmd.name, _cmd.description)
                return [['', self.embedder([[base[0], base[1]], ['**Available args:**', cmds]]), msg.channel]]
            else:
                base = self.base_help(None, _cmd.description)
                cmds = ''
                for cmd in self.cmds:
                    cmds += '``' + cmd + '`` '
                return [[
                    '',
                    self.embedder([
                        [base[0], base[1]],
                        ['**Available args:**', cmds]
                    ]), msg.channel
                ]]
        else:
            results = []
            for arg in args:
                if arg.lower() not in _cmd.commands:
                    results.append(
                        [
                            '',
                            self.embedder(
                                [['**Error:**', "Couldn't recognise: ``" + arg + '``.']],
                                colour=self.embed_error
                            ),
                            msg.channel
                        ]
                    )
                else:
                    results.append(
                        [
                            '',
                            self.embedder([["**Command '" + arg.lower() + "':**", _cmd.commands[arg.lower()]]]),
                            msg.channel
                        ]
                    )
            return results

    @asyncio.coroutine
    def messager(self, msg, messagess):
        archive = []
        if len(self.messages) > 0:
            if msg.author.id in self.messages and len(self.messages[msg.author.id]) > 0:
                for message in self.messages[msg.author.id]:
                    if self.perms._user(self, client.user, [message.channel, 'manage messages']):
                        try:
                            yield from client.delete_message(message)
                        except Exception as e:
                            print(repr(e))
            self.messages[msg.author.id] = []
        if len(messagess) > 0:
            for messag in messagess:
                if self.perms._user(self, client.user, [messag[2], 'send messages']):
                    try:
                        mesg = yield from client.send_message(messag[2], messag[0], embed=messag[1])
                        archive.append(mesg)
                    except Exception as e:
                        error = self.embedder([["**Error:**", str(e)]])
                        yield from client.send_message(msg.author, '...', embed=error)
                else:
                    error = self.embedder([[
                        "**Insufficient Permissions:**", "Unable to send message to ``" + message[2].server.name + ":" +
                        message[2].server.id + ">" + message[2].channel.name + ":" + message[2].channel.id +
                        "`` - 'send messages'."
                    ]])
                    yield from client.send_message(msg.author, '...', embed=error)
        else:
            if self.perms._user(self, client.user, [msg.channel, 'send messages']):
                try:
                    mesg = yield from client.send_message(
                        msg.channel,
                        '',
                        embed=self.embedder([['Error', 'No message was given to messager!']])
                    )
                    archive.append(mesg)
                except Exception as e:
                    error = self.embedder([["**Error:**", str(e)]])
                    yield from client.send_message(msg.author, '...', embed=error)
            else:
                error = self.embedder([[
                    "**Insufficient Permissions:**", "Unable to send message to ``" + msg.server.name + ":" +
                                                     msg.server.id + ">" + msg.channel.name + ":" +
                                                     msg.channel.id +
                                                     "`` - 'send messages'."
                ]])
                yield from client.send_message(msg.author, '...', embed=error)
        self.messages[msg.author.id] = archive

    def json(self, args, msg):
        js = ''
        results = []
        for nArg in args:
            js += nArg + ' '
            js = js.replace(u'“', '"').replace('\u201d', '"')
        try:
            emb = json.loads(js)
        except Exception as e:
            print(repr(e))
            tr = traceback.format_exc(limit=0)
            emb = None
            try:
                s = int(tr.split('\n')[1].split(':')[-1].split(' ')[-1].replace(')', ''))
                ns = ''
                if s < 35 and len(js) > s + 35:
                    ns = js[:s] + ' __**' + js[s] + '**__ ' + js[s+1:s+36]
                elif s < 35 and len(js) < s + 35:
                    ns = js[:s] + ' __**' + js[s] + '**__ ' + js[s+1:]
                elif s > 35 and len(js) > s + 35:
                    ns = js[s-35:s] + ' __**' + js[s] + '**__ ' + js[s+1:s+36]
                elif s > 15 and len(js) < s + 15:
                    ns = js[s-35:s] + ' __**' + js[s] + '**__ ' + js[s+36:]
                results.append([
                    '',
                    self.embedder(
                        [['**Error:**', traceback.format_exc(limit=0) + '\n' + ns]],
                        colour=self.embed_error
                    ),
                    msg.channel]
                )
            except Exception as f:
                print(f)
                results.append([
                    '',
                    self.embedder([['**Error:**', traceback.format_exc(limit=0) + '\n' + str(js)]]),
                    msg.channel
                ])
        return emb, results


d = Data()


@asyncio.coroutine
def ticker():
    c = 0
    while True:
        if c != 0:
            t = 60.0 - datetime.datetime.now().minute
            yield from asyncio.sleep(float(t*60.0))
        else:
            c = 1
        print("Elapsed time: (" + str(c) + ")")
        try:
            c += 1
        except Exception as e:
            print(e)
            c = 1
            print("Elapsed time counter max reached. Resetting to 1.")
        for cmd in d.tickEvents:
            yield from d.cmd.tick(client, d, cmd)


@client.event
@asyncio.coroutine
def on_reaction_add(reaction, user):
    for cmd in d.reactEvents:
        yield from d.cmd.react(client, reaction, user, d, cmd)


@asyncio.coroutine
def prep_cmd(cmd, msg):
    args = []
    if ' ' in cmd:
        args = cmd.split(' ')
        cmd = args[0]
        args = args[1:]
    if cmd in d.cmds:
        d.dmessages[msg.author.id] = msg
        yield from client.delete_message(msg)
        yield from d.cmd.execute(client, msg, d, args, cmd)
        s = msg.server.id
        if s in d.servers:
            s = d.servers[s]
            if s.command_channel != ['', ''] and s.command_logging:
                embed = d.embedder([
                    ["**Command Execution:**", '``' + msg.content + '``'],
                    ["**User:**", "Name: " + msg.author.display_name + "\n<@" + msg.author.id + ">"]
                ])
                yield from client.send_message(s.command_channel[2], embed=embed)
    elif msg.content in d.answers and msg.server == d.servers[d.answers[msg.content]]:
        s = d.servers[d.answers[msg.content]]
        ms = ''
        u = discord.utils.find(lambda m: m.id == msg.author.id, s.serve.members)
        if u.id != client.user.id:
            for role in s.auth_roles:
                r = discord.utils.find(lambda m: m.id == s.auth_roles[role], s.serve.roles)
                c = 0
                while r not in u.roles or c < 10:
                    yield from client.add_roles(u, r)
                    c += 1
                ms += "Added ``" + r.name + "`` to ``" + u.name + "``.\n"
        if s.debug_channel != ['', '']:
            embed = discord.Embed()
            icon = client.user.avatar_url
            embed.colour = 0xFFE83C
            embed.set_author(
                name=client.user.display_name,
                url=discord.Embed.Empty, icon_url=icon
            )
            embed.add_field(name='**Giving roles:**', value=ms)
            yield from client.send_message(s.debug_channel[2], embed=embed)
        yield from client.send_message(msg.author, "Permissions granted for " + msg.server.name + "!")
    else:
        if msg.channel.type == discord.ChannelType.text:
            yield from client.delete_message(msg)
        embed = discord.Embed()
        icon = client.user.avatar_url
        embed.colour = 0xFFE83C
        embed.set_author(
            name=client.user.display_name,
            url=discord.Embed.Empty, icon_url=icon)
        embed.add_field(name='**Invalid command...**', value='``No such command was found.``')
        yield from d.messager(msg, [['', embed, msg.channel]])


@client.event
@asyncio.coroutine
def on_message(msg):
    if msg.author.id != client.user.id:
        if (msg.channel.type == discord.ChannelType.text) and (msg.content.startswith(d.c.prefix)):
            yield from prep_cmd(msg.content[len(d.c.prefix):], msg)
        if msg.channel.type == discord.ChannelType.private:
            yield from prep_cmd(msg.content, msg)


@client.event
@asyncio.coroutine
def on_message_delete(msg):
    s = msg.server.id
    if s in d.servers and msg.author.id != client.user.id:
        s = d.servers[s]
        if s.message_delete_logging and s.delete_channel != ['', ''] and s.active and s.delete_channel[2] != msg.channel:
            if msg.author.id in d.dmessages:
                if msg.type == type(d.dmessages[msg.author.id]):
                    if msg.content == d.dmessages[msg.author.id].content:
                        return
            embed = d.embedder([[
                '**Detected message deletion:**', 'Deleted message owned by: <@' + msg.author.id + '> ' +
                msg.author.display_name + ':' + msg.author.id + '\nContents: \'' + msg.content + '\'\nTime: ' +
                str(datetime.datetime.now()) + '\nChannel: ``' + msg.channel.name + ":" + msg.channel.id + "``"
            ]])
            yield from client.send_message(s.delete_channel[2], '_   _', embed=embed)
            if len(msg.embeds) > 0:
                yield from client.send_message(s.delete_channel[2], "It had embed(s) with it:")
                for embedd in msg.embeds:
                    yield from client.send_message(s.delete_channel[2], '```' + str(embedd) + '```')
            if len(msg.attachments) > 0:
                yield from client.send_message(s.delete_channel[2], "It had attachment(s) with it:")
                for attachment in msg.attachments:
                    yield from client.send_message(s.delete_channel[2], attachment)


@client.event
@asyncio.coroutine
def on_message_edit(before, after):
    try:
        s = before.server.id
        if before.content != after.content and s in d.servers and before.author.id != client.user.id:
            s = d.servers[s]
            if s.message_edit_logging and s.edit_channel != ['', ''] and s.active:
                embed = d.embedder([[
                    '**Detected message edit:**', 'Edited message owned by: <@' + before.author.id + '> ' +
                    before.author.display_name + ':' + before.author.id + '\nContent before: \'' + before.content +
                    '\'\nContent after: \'' + after.content + '\'\nTime: ' + str(datetime.datetime.now()) +
                    '\nChannel: ``' + before.channel.name + ":" + before.channel.id + "``"
                ]])
                yield from client.send_message(s.edit_channel[2], '_   _', embed=embed)
    except Exception as e:
        print(e)


@client.event
@asyncio.coroutine
def on_member_join(member):
    if member.server.id in d.servers:
        s = d.servers[member.server.id]
        ms = ''
        if s.active:
            if s.welcoming and s.welcome_channel != ['', '']:
                embed = d.embedder([[s.welcome_message['name'], s.welcome_message['value']]])
                yield from client.send_message(s.welcome_channel[2], '', embed=embed)
                yield from client.send_message(member, '', embed=embed)
            if s.auth:
                if s.question != '':
                    yield from client.send_message(member, s.question)
            else:
                u = member
                if u.id != client.user.id and len(s.auth_roles) > 0:
                    for role in s.auth_roles:
                        r = discord.utils.find(lambda m: m.id == s.auth_roles[role], s.serve.roles)
                        c = 0
                        while r not in u.roles or c < 10:
                            yield from client.add_roles(u, r)
                            c += 1
                        ms += "Added ``" + r.name + "`` to ``" + u.name + "`` [" + str(u.id) + "].\n"
                if s.joinChannel != ['', '']:
                    embed = discord.Embed()
                    icon = client.user.avatar_url
                    embed.colour = 0xFFE83C
                    embed.set_author(
                        name=client.user.display_name,
                        url=discord.Embed.Empty, icon_url=icon
                    )
                    if len(s.auth_roles) > 0:
                        embed.add_field(name='**User Joined:**', value=ms)
                        yield from client.send_message(s.join_channel[2], embed=embed)
                    else:
                        embed.add_field(
                            name='**User Joined:**',
                            value='``'+u.name+':'+str(u.id)+'`` -> <@' + str(u.id) + '>'
                        )
                        yield from client.send_message(s.join_channel[2], embed=embed)
                    yield from client.send_message(member, "Permissions granted!")


@client.event
@asyncio.coroutine
def on_member_remove(member):
    if member.server.id in d.servers:
        s = d.servers[member.server.id]
        if s.active:
            r = ''
            for role in member.roles:
                r += '``' + role.name + '``\n'
            if s.leave_channel != ['', '']:
                embed = discord.Embed()
                icon = client.user.avatar_url
                embed.colour = 0xFFE83C
                embed.set_author(
                    name=client.user.display_name,
                    url=discord.Embed.Empty, icon_url=icon
                )
                embed.add_field(
                    name='**Leaving note**',
                    value='``' + member.name + '``[' + str(member.id) + ']\nRoles:\n' + r
                )
                yield from client.send_message(s.leave_channel[2], embed=embed)
                
                
@client.event
@asyncio.coroutine
def on_ready():
    d.c.check_server(client, d)
    print(d.answers)


@asyncio.coroutine
def login():
    if len(d.c.login) == 1:
        yield from client.login(d.c.login[0])
    elif len(d.c.login) == 2:
        yield from client.login(d.c.login[0], d.c.login[1])
    else:
        print('Invalid amount of login parameters were set... This should not be possible. Aborting.')
        sys.exit(0)
    yield from client.connect()


log = logging.getLogger('discord')
log.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)
errorbuf = []


def errors(e):
    if e not in errorbuf:
        errorbuf.append(e)
        print(repr(e))
        if len(errorbuf) > 10:
            errorbuf.remove(errorbuf[0])


def execute():
    # executor = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()
    try:
        tasks = [asyncio.Task(login()),  asyncio.Task(ticker())]
        # tasks = [asyncio.Task(login()),  asyncio.Task(ticker())]
        loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        errors(e)
        loop.run_until_complete(client.logout())
        for task in asyncio.Task.all_tasks():
            try:
                task.cancel()
            except Exception as f:
                errors(f)
    finally:
        loop.close()


run = True
while run:
    try:
        execute()
    except KeyboardInterrupt:
        run = False
    except Exception as ex:
        errors(ex)
        time.sleep(10)
