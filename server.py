import json
import discord

class server(object):
    def __init__(self, client, ID):
        self.client = client;
        self.serve = discord.utils.find(lambda m: m.id == ID, client.servers);
        self.id = ID;
        try:
            self.name = self.serve.name;
        except:
            self.name = ' ';
        self.active = True;
        self.auth = False;
        self.commandLogging = False;
        self.messageDeleteLogging = False;
        self.messageEditLogging = False;
        self.welcomeMessage = {'name':'Welcome!','value':'I hope you have a nice stay!'}
        self.welcoming = False
        self.question = '';
        self.answer = '';
        self.giveRoles = False;
        self.authRoles = {}; #name: id
        self.debugChannel = ['','']; #name, id, channel
        self.welcomeChannel = ['','']; #name, id, channel
        self.commandChannel = ['','']; #name, id, channel
        self.deleteChannel = ['','']; #name, id, channel
        self.editChannel = ['','']; #name, id, channel
        self.joinChannel = ['', '']; #name, id, channel
        self.leaveChannel = ['', '']; #name, id, channel
        self.perms = []; #[{name: [roles{name: id}, cmds[name]]}]
        self.rules = []; # {'text':'', 'embed':embed}
        self.customData = {};
        return super().__init__();

    def update(self, client):
        path = 'config.json';
        config = json.load(open(path));
        p1 = -1;
        for i in range(0, len(config['servers'])):
            if config['servers'][i]['id'] == self.id:
                p1 = i;
        serverData = {};
        serverData['id'] = self.id;
        serverData['name'] = discord.utils.find(lambda m: m.id == self.id, client.servers).name;
        serverData['active'] = self.active;
        serverData['auth'] = {
            "active": self.auth,
            "question": self.question,
            "answer": self.answer,
            "roles": self.authRoles,
            "giveRoles": self.giveRoles
        };
        serverData['customData'] = self.customData;
        serverData['commandLogging'] = self.commandLogging;
        serverData['messageDeleteLogging'] = self.messageDeleteLogging;
        serverData['messageEditLogging'] = self.messageEditLogging;
        serverData['welcome'] = self.welcomeChannel[1];
        serverData['join'] = self.joinChannel[1];
        serverData['leave'] = self.leaveChannel[1];
        serverData['welcomeMessage'] = self.welcomeMessage;
        serverData['welcoming'] = self.welcoming;
        serverData['debug'] = self.debugChannel[1];
        serverData['command'] = self.commandChannel[1];
        serverData['delete'] = self.deleteChannel[1];
        serverData['edit'] = self.editChannel[1];
        serverData['perms'] = self.perms;
        #print(self.rules);
        serverData['rules'] = [];
        for rule in self.rules:
            new_rule = {};
            new_rule['text'] = rule[0];
            embed = rule[1];
            #print(embed.__dict__);
            new_rule['embed'] = embed.to_dict();
            serverData['rules'].append(new_rule);
        print(serverData);
        if p1 != -1:
            config['servers'][p1] = serverData;
        else:
            config['servers'].append(serverData);
        with open('config.json', 'w') as f:
            json.dump(config, f);
            f.close();
