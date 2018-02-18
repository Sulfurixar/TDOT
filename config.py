import json
import sys
from server import Server
import discord
from datetime import datetime


class Config(object):
    def __init__(self, client):
        self.path = 'config.json'
        self.config = json.load(open(self.path))
        self.login = None
        self.login_method = None
        self.prefix = None
        self.check(client)

    def check(self, client):
        abort = False
        if 'client' not in self.config:
            print("No 'client' was found in '" + self.path + "'. Aborting.")
            sys.exit(0)
        if 'login_method' in self.config['client']:
            self.login_method = self.config['client']['login_method']
        else:
            print("No 'login_method' was found in '" + self.path + "'. Aborting'")
            sys.exit(0)

        self.login = []
        if self.login_method == 'bot':
            if 'token' in self.config['client']:
                self.login.append(self.config['client']['token'])
            else:
                print("No 'token' was found in '" + self.path + "'. Aborting")
                abort = True
        elif self.login_method == 'user':
            if 'email' in self.config['client']:
                self.login.append(self.config['client']['email'])
            else:
                print("No 'email' was found in '" + self.path + "'. Aborting")
                abort = True
            if 'password' in self.config['client']:
                self.login.append(self.config['client']['password'])
            else:
                print("No 'password' was found in '" + self.path + "'. Aborting.")
                abort = True
        else:
            print("'login_method' was set to an invalid value '" + self.login_method + "'. Aborting.")
        if 'prefix' in self.config['client']:
            self.prefix = self.config['client']['prefix']
        else:
            print("No 'prefix' was found in '" + self.path + "'. Aborting.")
            abort = True

        if abort:
            sys.exit(0)

    def check_server(self, client, data):
        if 'servers' in self.config:
            servers = self.config['servers']
            for serve in servers:
                if 'id' in serve:
                    s = Server(client, serve['id'])
                    if 'active' in serve:
                        s.active = serve['active']
                    if 'auth' in serve:
                        if 'active' in serve['auth']:
                            if serve['auth']['active'] == 'True':
                                s.auth = True
                            if serve['auth']['active'] == 'False':
                                s.auth = False
                        if 'question' in serve['auth']:
                            s.question = serve['auth']['question']
                        if 'answer' in serve['auth']:
                            s.answer = serve['auth']['answer']
                            data.answers.update({s.answer: s.c_id})
                        if 'roles' in serve['auth']:
                            s.auth_roles = serve['auth']['roles']
                        if 'giveRoles' in serve['auth']:
                            s.give_roles = serve['auth']['roles']
                    if 'welcome' in serve:
                        ch = discord.utils.find(lambda m: m.id == serve['welcome'], s.serve.channels)
                        if ch is not None:
                            s.welcome_channel = [ch.name, serve['welcome'], ch]
                    if 'join' in serve:
                        ch = discord.utils.find(lambda m: m.id == serve['join'], s.serve.channels)
                        if ch is not None:
                            s.join_channel = [ch.name, serve['join'], ch]
                    if 'leave' in serve:
                        ch = discord.utils.find(lambda m: m.id == serve['leave'], s.serve.channels)
                        if ch is not None:
                            s.leave_channel = [ch.name, serve['leave'], ch]
                    if 'welcomeMessage' in serve:
                        s.welcome_message = serve['welcomeMessage']
                    if 'welcoming' in serve:
                        s.welcoming = serve['welcoming']
                    if 'debug' in serve:
                        ch = discord.utils.find(lambda m: m.id == serve['debug'], s.serve.channels)
                        if ch is not None:
                            s.debug_channel = [ch.name, serve['debug'], ch]
                    if 'command' in serve:
                        ch = discord.utils.find(lambda m: m.id == serve['command'], s.serve.channels)
                        if ch is not None:
                            s.command_channel = [ch.name, serve['command'], ch]
                    if 'delete' in serve:
                        ch = discord.utils.find(lambda m: m.id == serve['delete'], s.serve.channels)
                        if ch is not None:
                            s.delete_channel = [ch.name, serve['delete'], ch]
                    if 'edit' in serve:
                        ch = discord.utils.find(lambda m: m.id == serve['edit'], s.serve.channels)
                        if ch is not None:
                            s.edit_channel = [ch.name, serve['edit'], ch]
                    if 'perms' in serve:
                        s.perms = serve['perms']
                    if 'rules' in serve:
                        for mesg in serve['rules']:
                            text = ''
                            if 'text' in mesg:
                                text = mesg['text']
                            if 'embed' in mesg:
                                embed = discord.Embed()
                                if 'title' in mesg['embed']:
                                    embed.title = mesg['embed']['title']
                                if 'description' in mesg['embed']:
                                    embed.description = mesg['embed']['description']
                                if 'timestamp' in mesg['embed']:
                                    embed.timestamp = datetime.strptime(
                                        mesg['embed']['timestamp'].replace('-', ' ').replace(':', ' ').replace(
                                            'T', ' '
                                        ),
                                        '%Y %m %d %H %M %S'
                                    )
                                if 'color' in mesg['embed']:
                                    try:
                                        embed.color = int(mesg['embed']['color'])
                                    except Exception as e:
                                        print(str(e))
                                        embed.color = 000000
                                if 'footer' in mesg['embed']:
                                    ftext = discord.Embed.Empty
                                    icon = discord.Embed.Empty
                                    if 'text' in mesg['embed']['footer']:
                                        ftext = mesg['embed']['footer']['text']
                                    if 'icon_url' in mesg['embed']['footer']:
                                        icon = mesg['embed']['footer']['icon_url']
                                    embed.set_footer(text=ftext, icon_url=icon)
                                if 'image' in mesg['embed']:
                                    embed.set_image(url=mesg['embed']['image'])
                                if 'thumbnail' in mesg['embed']:
                                    embed.set_thumbnail(url=mesg['embed']['thumbnail'])
                                if 'author' in mesg['embed']:
                                    name = '   '
                                    url = discord.Embed.Empty
                                    icon = discord.Embed.Empty
                                    if 'name' in mesg['embed']['author']:
                                        name = mesg['embed']['author']['name']
                                    if 'url' in mesg['embed']['author']:
                                        url = mesg['embed']['author']['url']
                                    if 'icon_url' in mesg['embed']['author']:
                                        icon = mesg['embed']['author']['icon_url']
                                    embed.set_author(name=name, url=url, icon_url=icon)
                                if 'fields' in mesg['embed']:
                                    fields = mesg['embed']['fields']
                                    for field in fields:
                                        name = '   '
                                        value = '   '
                                        inline = True
                                        if 'name' in field:
                                            name = field['name']
                                        if 'value' in field:
                                            value = field['value']
                                        if 'inline' in field:
                                            if field['inline'] == 'False':
                                                inline = False
                                        embed.add_field(name=name, value=value, inline=inline)
                                s.rules.append([text, embed])
                    if 'customData' in serve:
                        s.custom_data = serve['customData']
                    if 'commandLogging' in serve:
                        s.command_logging = serve['commandLogging']
                    if 'messageDeleteLogging' in serve:
                        s.message_delete_logging = serve['messageDeleteLogging']
                    if 'messageEditLogging' in serve:
                        s.message_edit_logging = serve['messageEditLogging']
                    data.servers.update({s.c_id: s})
                else:
                    print("No 'id' was found in '" + serve + "' in '" + self.path + "'.")
        else:
            print("No 'servers' were  found in '" + self.path + "'.")
