import discord
import asyncio
import logging
import json
import sys
import time
from config import config
from commandes import commandes
from checkPermissions import checkPermissions
from concurrent.futures import ProcessPoolExecutor
import datetime
import json

errorbuf = [];

client = discord.Client();

class data(object):
    def __init__(self):
        self.id = '149381939428589568'
        self.c = config(client);
        self.perms = checkPermissions(client);
        self.cmd = commandes();
        self.cmds = self.cmd.commands;
        self.tickEvents, self.reactEvents = self.cmd.getEvents();
        self.answers = {};
        self.servers = {};
        self.messages = {}; #{authorID: [msg, msg, msg]} //allows for multiple inquiries per single command, also allows to delete them at the same time.
        self.dmessages = {}; #{authorID: msg} //keeps track of the last command executed by user
        #print(self.cmds);
        self.embed_normal = 0xFFE83C;
        self.embed_error = 0xDC143C;
        self.embed_announce = 0x00FFFF;
        self.version = 'Truly Golden Update 0.3'
        return super().__init__();

    def embedder(self, fields, given_embed=None, colour=None):
        embed = discord.Embed();
        if given_embed is not None:
            embed = given_embed;
        if colour == None:
            colour = self.embed_normal;
        embed.colour = colour;
        embed.set_author(
            name = client.user.display_name,
            url = discord.Embed.Empty,
            icon_url = client.user.avatar_url
        );
        if len(fields) > 0:
            for field in fields:
                embed.add_field(
                    name = field[0],
                    value = field[1]
                );
        return embed;

    def baseHelp(self, cmd, desc):
        if not (cmd is None):
            return [
                "**Command: '" + cmd + "':**",
                desc + "\nUsage: ``{prefix}[command]`` ``(args)``\n" +
                    "Legend: ``{}`` - required only on servers, ``[]``" + 
                    " - required every time, ``()`` - optional\n" +
                    "Example: ``e!" + 
                    cmd + 
                    ' help help`` - displays how to use the help command.'
            ];
        else:
            return [
                "**Command: 'help':**",
                desc + "\nUsage: ``{prefix}[command]`` ``(args)``\n" +
                    "Legend: ``{}`` - required only on servers, ``[]``" + 
                    " - required every time, ``()`` - optional\n" +
                    "Example: ``e!help help`` - displays how to use the help command."
            ];

    def help(self, msg, _cmd, args=[]):
        if len(args) == 0:
            cmds = '';
            for cmd in _cmd.commands:
                cmds += '``' + cmd + '`` ';
            if cmds == '':
	                cmds = 'Currently there are no arguments for this command.';
            if _cmd.name != 'help':
                base = self.baseHelp(_cmd.name, _cmd.description);
                return [['', 
                    self.embedder([
                        [base[0], base[1]], 
                        ['**Available args:**', cmds]
                    ]), msg.channel
                ]];
            else:
                base = self.baseHelp(None, _cmd.description);
                cmds = '';
                for cmd in self.cmds:
                    cmds += '``' + cmd + '`` ';
                return [['', 
                    self.embedder([
                        [base[0], base[1]], 
                        ['**Available args:**', cmds]
                    ]), msg.channel
                ]];
        else:
            results = [];
            for arg in args:
                if arg.lower() not in _cmd.commands:
                    results.append(['', self.embedder([['**Error:**', "Couldn't recognise: ``" + arg + '``.']], colour=self.embed_error), msg.channel]);
                else:
                    results.append(['',self.embedder([["**Command '" + arg.lower() + "':**", _cmd.commands[arg.lower()]]]), msg.channel]);
            return results;

    @asyncio.coroutine
    def messager(self, msg, messages):
        if len(messages) > 0:
            if msg.author.id in self.messages:
                for message in self.messages[msg.author.id]:
                    if self.perms._user(self, client.user, [message.channel, 'manage messages']):
                        try:
                            yield from client.delete_message(message);
                        except:
                            pass
            self.messages[msg.author.id] = [];
            archive = [];
            for messag in messages:
                #print(messag[2])
                if self.perms._user(self, client.user, [messag[2], 'send messages']):
                    try:
                        mesg = yield from client.send_message(messag[2], messag[0], embed=messag[1]);
                        archive.append(mesg);
                    except Exception as e:
                        error = self.embedder([["**Error:**", str(e)]]);
                        yield from client.send_message(msg.author, '...', embed=error);
                else:
                    error = self.embedder([["**Insufficient Permissions:**", "Unable to send message to ``" + message[2].server.name + ":" +
                            message[2].server.id + ">" + message[2].channel.name + ":" + message[2].channel.id +
                            "`` - 'send messages'."]]);
                    yield from client.send_message(msg.author, '...', embed=error);
            self.messages[msg.author.id] = archive;
            
    def json(self, args):
        js = '';
        results = {};
        for nArg in args:
            js += nArg + ' ';
            js = js.replace(u'“', '"').replace('\u201d','"');
        emb = {};
        try:
            emb = json.loads(js);
        except Exception as e:
            #print(emb)
            tr = traceback.format_exc(limit=0);
            #print(tr.split('\n')[1].split(':')[-1].split(' ')[-1].replace(')', ''));
            emb = None;
            try:
                #print(traceback.format_exc(limit=10));
                s = int(tr.split('\n')[1].split(':')[-1].split(' ')[-1].replace(')', ''));
                #print(ord(js[s]));
                ns = '';
                if s < 35 and len(js) > s + 35:
                    ns = js[:s] + ' __**' + js[s] + '**__ ' + js[s+1:s+36];
                elif s < 35 and len(js) < s + 35:
                    ns = js[:s] + ' __**' + js[s] + '**__ ' + js[s+1:];
                elif s > 35 and len(js) > s + 35:
                    ns = js[s-35:s] + ' __**' + js[s] + '**__ ' + js[s+1:s+36];
                elif s > 15 and len(js) < s + 15:
                    ns = js[s-35:s] + ' __**' + js[s] + '**__ ' + js[s+36:];
                print(ns);
                results.append(['', data.embedder([['**Error:**', traceback.format_exc(limit=0) + '\n' + ns]], colour=data.embed_error), msg.channel]);
            except:
                results.append(['', data.embedder([['**Error:**', traceback.format_exc(limit=0) + '\n' + str(js)]]), msg.channel]);
        return emb, results;

d = data();

@asyncio.coroutine
def messager(msg, text='', embed=discord.Embed.Empty):
    if len(d.messages) > 0:
            if msg.author.id in d.messages:
                for message in d.messages[msg.author.id]:
                    if d.perms._user(data, client.user, [message.channel, 'manage messages']):
                        try:
                            yield from client.delete_message(message);
                        except:
                            pass
            d.messages[msg.author.id] = [];
            archive = [];
            for messag in d.messages:
                if d.perms._user(data, client.user, [messag[2], 'send messages']):
                    try:
                        mesg = yield from client.send_message(messag[2], messag[0], embed=messag[1]);
                        archive.append(mesg);
                    except Exception as e:
                        error = d.embedder([["**Error:**", str(e)]]);
                        yield from client.send_message(msg.author, '...', embed=error);
                else:
                    error = d.embedder([["**Insufficient Permissions:**", "Unable to send message to ``" + message[2].server.name + ":" +
                            message[2].server.id + ">" + message[2].channel.name + ":" + message[2].channel.id +
                            "`` - 'send messages'."]]);
                    yield from client.send_message(msg.author, '...', embed=error);
            d.messages[msg.author.id] = archive;

@asyncio.coroutine
def ticker():
    c = 0;
    while True:
        if c != 0:
            t = 60.0 - datetime.datetime.now().minute;
            yield from asyncio.sleep(float(t*60.0));
        else:
            c = 1;
        print("Elapsed time: (" + str(c) + ")");
        try:
            c += 1;
        except:
            c = 1;
            print("Elapsed time counter max reached. Resetting to 1.");
        for cmd in d.tickEvents:
            yield from d.cmd.tick(client, d, cmd);
            
@asyncio.coroutine
def on_reaction_add(reaction, user):
    print("react");
    for cmd in d.reactEvents:
        yield from d.cmd.react(client, reaction, user, data, cmd);

log = logging.getLogger('discord');
log.setLevel(logging.ERROR);
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w');
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'));
log.addHandler(handler);

@asyncio.coroutine
def prepCmd(cmd, msg):
    args = [];
    if ' ' in cmd:
        args = cmd.split(' ');
        cmd = args[0];
        args = args[1:];
    if cmd in d.cmds:
        #todo if there's an actual command
        d.dmessages[msg.author.id] = msg;
        yield from client.delete_message(msg);
        yield from d.cmd.execute(client, msg, d, args, cmd);
        s = msg.server.id;
        if s in d.servers:
            s = d.servers[s];
            if s.commandChannel != ['',''] and s.commandLogging:
                embed = d.embedder([["**Command Execution:**", '``' + msg.content + '``'],["**User:**", "Name: " + msg.author.display_name + "\n<@" + msg.author.id + ">"]]);
                yield from client.send_message(s.commandChannel[2], embed=embed);
    elif (msg.content in d.answers and msg.server == d.servers[d.answers[msg.content]]):
        s = d.servers[d.answers[msg.content]];
        ms = '';
        u = discord.utils.find(lambda m: m.id == msg.author.id, s.serve.members);
        if u.id != client.user.id:
            for role in s.authRoles:
                r = discord.utils.find(lambda m: m.id == s.authRoles[role], s.serve.roles);
                yield from client.add_roles(u, r);
                yield from client.add_roles(u, r);
                ms += "Added ``" + r.name + "`` to ``" + u.name + "``.\n"
            print(u.name + "|" + str(r.name));
        if (s.debugChannel != ['','']):
            embed = discord.Embed();
            icon = client.user.avatar_url;
            embed.colour = 0xFFE83C;
            embed.set_author(
                name=client.user.display_name, 
                url=discord.Embed.Empty, icon_url=icon);
            embed.add_field(name='**Giving roles:**', value=ms);
            yield from client.send_message(s.debugChannel[2], embed=embed);
            yield from client.send_message(msg.author, "Permissions granted!");
    else:
        #todo if it was neither
        if msg.channel.type == discord.ChannelType.text:
            yield from client.delete_message(msg);
        embed = discord.Embed();
        icon = client.user.avatar_url;
        embed.colour = 0xFFE83C;
        embed.set_author(
            name=client.user.display_name, 
            url=discord.Embed.Empty, icon_url=icon);
        embed.add_field(name='**Invalid command...**', value='``No such command was found.``');
        yield from messager(msg, embed=embed);

@client.event
@asyncio.coroutine
def on_message(msg):
    if msg.author.id != client.user.id:
        if (msg.channel.type == discord.ChannelType.text):
            if (msg.content.startswith(d.c.prefix)):
                yield from prepCmd(msg.content[len(d.c.prefix):], msg);
        if (msg.channel.type == discord.ChannelType.private):
            yield from prepCmd(msg.content, msg);

@client.event
@asyncio.coroutine
def on_message_delete(msg):
    s = msg.server.id;
    if s in d.servers and msg.author.id != client.user.id:
        s = d.servers[s];
        if s.messageDeleteLogging:
            if s.deleteChannel != ['','']:
                if s.active:
                    if s.deleteChannel[2] != msg.channel:
                        if msg.author.id in d.dmessages:
                            #print(type(msg))
                            #print(type(d.dmessages[msg.author.id]))
                            if type(msg) == type(d.dmessages[msg.author.id]):
                                if msg.content == d.dmessages[msg.author.id].content:
                                    return;
                        embed = d.embedder([['**Detected message deletion:**', 'Deleted message owned by: <@' + msg.author.id + '> '+ msg.author.display_name + ':' + msg.author.id + '\nContents: \'' + msg.content + '\'\nTime: ' + str(datetime.datetime.now()) + '\nChannel: ``' + msg.channel.name + ":" + msg.channel.id + "``"]]);
                        yield from client.send_message(s.deleteChannel[2], '_   _', embed=embed);

@client.event
@asyncio.coroutine
def on_message_edit(before, after):
    try:
        s = before.server.id;
        if before.content != after.content:
            if s in d.servers and before.author.id != client.user.id:
                s = d.servers[s];
                if s.messageEditLogging:
                    if s.editChannel != ['','']:
                        if s.active:
                            embed = d.embedder([['**Detected message edit:**', 'Edited message owned by: <@' + before.author.id + '> '+ before.author.display_name + ':' + before.author.id + '\nContent before: \'' + before.content + '\'\nContent after: \'' + after.content + '\'\nTime: ' + str(datetime.datetime.now()) + '\nChannel: ``' + before.channel.name + ":" + before.channel.id + "``"]]);
                            yield from client.send_message(s.editChannel[2], '_   _', embed=embed);
    except:
        pass
                        
@client.event
@asyncio.coroutine
def on_member_join(member):
    if (member.server.id in d.servers):
        s = d.servers[member.server.id];
        ms = '';
        if (s.active):
            if s.welcoming:
                if s.welcomeChannel != ['','']:
                    embed = d.embedder([[s.welcomeMessage['name'],s.welcomeMessage['value']]]);
                    yield from client.send_message(s.welcomeChannel[2], '', embed=embed);
                yield from client.send_message(member, '', embed=embed);
            if s.auth:
                if s.question != '':
                    yield from client.send_message(member, s.question);
            else:
                u = member;
                if u.id != client.user.id:
                    if len(s.authRoles) > 0:
                        for role in s.authRoles:
                            r = discord.utils.find(lambda m: m.id == s.authRoles[role], s.serve.roles);
                            yield from client.add_roles(u, r);
                            yield from client.add_roles(u, r);
                            ms += "Added ``" + r.name + "`` to ``" + u.name + "`` [" + str(u.id) + "].\n"
                    #print(u.name + "|" + str(r.name));
                if (s.joinChannel != ['','']):
                    embed = discord.Embed();
                    icon = client.user.avatar_url;
                    embed.colour = 0xFFE83C;
                    embed.set_author(
                        name=client.user.display_name, 
                        url=discord.Embed.Empty, icon_url=icon);
                    if len(s.authRoles) > 0:
                        embed.add_field(name='**User Joined:**', value=ms);
                        yield from client.send_message(s.joinChannel[2], embed=embed);
                    else:
                        embed.add_field(name='**User Joined:**', value='``'+u.name+':'+str(u.id)+'`` -> <@' + str(u.id) + '>');
                        yield from client.send_message(s.joinChannel[2], embed=embed);
                    yield from client.send_message(member, "Permissions granted!");

@client.event
@asyncio.coroutine
def on_member_remove(member):
    if (member.server.id in d.servers):
        s = d.servers[member.server.id];
        if (s.active):
            r = '';
            for role in member.roles:
                r += '``' + role.name + '``\n';
            if s.leaveChannel != ['','']:
                embed = discord.Embed();
                icon = client.user.avatar_url;
                embed.colour = 0xFFE83C;
                embed.set_author(
                    name=client.user.display_name,
                    url=discord.Embed.Empty, icon_url=icon);
                embed.add_field(name='**Leaving note**', value='``' + member.name + '``[' + str(member.id) + ']\nRoles:\n' + r);
                yield from client.send_message(s.leaveChannel[2], embed=embed);
@client.event
@asyncio.coroutine
def on_ready():
    d.c.checkServer(client, d);
    print(d.answers);

@asyncio.coroutine
def login():
    if len(d.c.login) == 1:
        yield from client.login(d.c.login[0]);
    elif len(d.c.login) == 2:
        yield from client.login(d.c.login[0], d.c.login[1]);
    else:
        print('Invalid amount of login parameters were set... This should not be possible. Aborting.');
        sys.exit(0);
    yield from client.connect();

def execute():
    executor = ProcessPoolExecutor(2);
    try:
        loop = asyncio.get_event_loop();
        tasks = [asyncio.Task(login()),  asyncio.Task(ticker())]; #tasks = [asyncio.Task(login()),  asyncio.Task(ticker())]
        loop.run_until_complete(asyncio.gather(*tasks));
    except Exception as e:
        print(e);
        if not ('errorbuf' in locals()):
            errorbuf = [];
        if not (e in errorbuf):
            log.exception(e);
            errorbuf.append(e);
            if (len(errorbuf) > 10):
                errorbuf = errorbuf[1:];
        loop.run_until_complete(client.logout());
        for task in asyncio.Task.all_tasks():
            task.cancel();
    finally:
        loop.close();

run = True;
while (run):
    try:
        execute();
    except KeyboardInterrupt:
        run = False;
    except Exception as ex:
        print(str(ex));
        time.sleep(10);
