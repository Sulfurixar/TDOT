import asyncio
import discord
import json
import sys
import os
import traceback

class embed(object):

    def __init__(self):
        self.description = "Used to retrieve various kinds of information.\nThis command takes json formatted input.\nYou may use the following template as a guideline:\n\n``e!embed {\"text\":\"This is the normal text area.\",\"embed\":{\"title\":\"Title\",\"description\":\"This is where the description goes.\",\"footer\":{\"text\":\"Footer text\"},\"author\":{\"name\":\"My name\"},\"fields\":[{\"name\":\"Header1\",\"value\":\"Text under header.\"},{\"name\":\"Header2\",\"value\":\"Text under header... again.\"}]}}``\n\n";
        self.permissions = ['administrator'];
        self.Owner = False;
        self.bOwner = False;
        self.name = 'embed';
        self.tick = False;
        self.react = False;
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!embed help (args)\n' +
                'For Example: e!embed help help - shows this message.'
        };
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
        
    def makeEmbed(self, data, emb):
        text = '';
        embed = discord.Embed.Empty;
        if ('text' in emb):
            text = emb['text'];
        if ('embed' in emb):
            embed = discord.Embed();
            if ('title' in emb['embed']):
                embed.title = emb['embed']['title'];
            if ('description' in emb['embed']):
                embed.description = emb['embed']['description'];
            if ('timestamp' in emb['embed']):
                embed.timestamp = datetime.strptime(emb['embed']['timestamp'].replace('-', ' ').replace(':', ' ' ).replace('T', ' '), '%Y %m %d %H %M %S');
            if ('color' in emb['embed'] or 'colour' in emb['embed']):
                kw = 'color';
                if 'colour' in emb['embed']:
                    kw = 'colour';
                try:
                    embed.color = int(emb['embed'][kw]);
                except Exception as e:
                    try:
                        embed.color = int(emb['embed'][kw], 16);
                    except:
                        print(repr(e));
                        embed.color = data.embed_announce;
                        print(repr(e));
            else:
                embed.color = data.embed_announce;
            if ('footer' in emb['embed']):
                ftext = discord.Embed.Empty;
                icon = discord.Embed.Empty;
                if ('text' in emb['embed']['footer']):
                    ftext = emb['embed']['footer']['text'];
                if ('icon_url' in emb['embed']['footer']):
                    icon = emb['embed']['footer']['icon_url'];
                embed.set_footer(text=ftext,icon_url=icon);
            if ('image' in emb['embed']):
                embed.set_image(url=emb['embed']['image']);
            if ('thumbnail' in emb['embed']):
                embed.set_thumbnail(url=emb['embed']['thumbnail']);
            if ('author' in emb['embed']):
                name = '   ';
                url = discord.Embed.Empty;
                icon = discord.Embed.Empty;
                if ('name' in emb['embed']['author']):
                    name = emb['embed']['author']['name'];
                if ('url' in emb['embed']['author']):
                    url = emb['embed']['author']['url'];
                if ('icon_url' in emb['embed']['author']):
                    icon = emb['embed']['author']['icon_url'];
                embed.set_author(name=name,url=url,icon_url=icon);
            if ('fields' in emb['embed']):
                fields = emb['embed']['fields'];
                for field in fields:
                    name = '   '; value = '   ';
                    inline = True;
                    if ('name' in field):
                        name = field['name'];
                    if ('value' in field):
                        value = field['value'];
                    if ('inline' in field):
                        if (field['inline'] == 'False'):
                            inline = False;
                    embed.add_field(name=name,value=value,inline=inline);
        return [text, embed];

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
                        emb, res = data.json(nArgs);
                        if emb != None:
                            if type(emb) is list:
                                res = [];
                                for entry in emb:
                                    res.append(self.makeEmbed(data, entry));
                                for entry in res:
                                    if entry[1] is discord.Embed.Empty:
                                        yield from client.send_message(msg.channel, entry[0]);
                                    else:
                                        yield from client.send_message(msg.channel, entry[0], embed=entry[1]);
                            if type(emb) is dict:
                                res = self.makeEmbed(data, emb);
                                if res[1] is discord.Embed.Empty:
                                    yield from client.send_message(msg.channel, res[0]);
                                else:
                                    yield from client.send_message(msg.channel, res[0], embed=res[1]);    
                            
                        else:
                            for r in res:
                                results.append(r);
#############################################################################
                argpos += 1;
            yield from data.messager(msg, results);
            results = [];
