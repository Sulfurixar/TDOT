import json
import discord


class Server(object):
    def __init__(self, client, c_id):
        self.client = client
        self.serve = discord.utils.find(lambda m: m.id == c_id, client.servers)
        self.c_id = c_id
        try:
            self.name = self.serve.name
        except Exception as e:
            print(e)
            self.name = ' '
        self.active = True
        self.auth = False
        self.command_logging = False
        self.message_delete_logging = False
        self.message_edit_logging = False
        self.welcome_message = {'name': 'Welcome!', 'value': 'I hope you have a nice stay!'}
        self.welcoming = False
        self.question = ''
        self.answer = ''
        self.give_roles = False
        self.auth_roles = {}             # name: c_id
        self.debug_channel = ['', '']     # name, c_id, channel
        self.welcome_channel = ['', '']   # name, c_id, channel
        self.command_channel = ['', '']   # name, c_id, channel
        self.delete_channel = ['', '']    # name, c_id, channel
        self.edit_channel = ['', '']      # name, c_id, channel
        self.join_channel = ['', '']     # name, c_id, channel
        self.leave_channel = ['', '']    # name, c_id, channel
        self.perms = []                 # [{name: [roles{name: c_id}, cmds[name]]}]
        self.rules = []                 # {'text':'', 'embed':embed}
        self.custom_data = {}

    def update(self, client):
        path = 'config.json'
        config = json.load(open(path))
        p1 = -1
        for i in range(0, len(config['servers'])):
            if config['servers'][i]['id'] == self.c_id:
                p1 = i
        server_data = {
            'id': self.c_id,
            'name': discord.utils.find(lambda m: m.id == self.c_id, client.servers).name,
            'active': self.active, 'auth': {
                "active": self.auth,
                "question": self.question,
                "answer": self.answer,
                "roles": self.auth_roles,
                "giveRoles": self.give_roles
            },
            'customData': self.custom_data, 'commandLogging': self.command_logging,
            'messageDeleteLogging': self.message_delete_logging, 'messageEditLogging': self.message_edit_logging,
            'welcome': self.welcome_channel[1], 'join': self.join_channel[1], 'leave': self.leave_channel[1],
            'welcomeMessage': self.welcome_message, 'welcoming': self.welcoming,
            'debug': self.debug_channel[1], 'command': self.command_channel[1],
            'delete': self.delete_channel[1], 'edit': self.edit_channel[1], 'perms': self.perms, 'rules': []
        }
        for rule in self.rules:
            new_rule = {'text': rule[0]}
            embed = rule[1]
            new_rule['embed'] = embed.to_dict()
            server_data['rules'].append(new_rule)
        if p1 != -1:
            config['servers'][p1] = server_data
        else:
            config['servers'].append(server_data)
        with open('config.json', 'w') as f:
            json.dump(config, f)
            f.close()
