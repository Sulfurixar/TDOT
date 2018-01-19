import inspect
import discord

class checkPermissions(object):
    def __init__(self, client):
        base = discord.Permissions;
        self.perms = {
            'create instant invite': base.create_instant_invite,	#00 create instant invite
            'kick members': base.kick_members,				#01 kick members
            'ban members': base.ban_members,				#02 ban members
            'administrator': base.administrator,			#03 administrator
            'manage channels': base.manage_channels,			#04 manage channels
            'manage server': base.manage_server,			#05 manage server
            'add reactions': base.add_reactions,			#06 add reactions
            'view audit logs': base.view_audit_logs,			#07 view audit logs
            'read messages': base.read_messages,			#08 read messages
            'send messages': base.send_messages,			#09 send messages
            'send tts messages': base.send_tts_messages,		#10 send tts messages
            'manage messages': base.manage_messages,			#11 manage messages
            'embed links': base.embed_links,				#12 embed links
            'attach files': base.attach_files,				#13 attach files
            'read message history': base.read_message_history,		#14 read message history
            'mention everyone': base.mention_everyone,			#15 mention everyone
            'external emojis': base.external_emojis,			#16 external emojis
            'connect': base.connect,					#17 connect
            'speak': base.speak,					#18 speak
            'mute members': base.mute_members,				#19 mute members
            'deafen members': base.deafen_members,			#20 deafen members
            'move members': base.move_members,				#21 move members
            'use voice activation': base.use_voice_activation,		#22 use voice activation
            'change nickname': base.change_nickname,			#23 change nickname
            'manage nicknames': base.manage_nicknames,			#24 manage nicknames
            'manage roles': base.manage_roles,				#25 manage roles
            'manage webhooks': base.manage_webhooks,			#26 manage webhooks
            'manage emojis': base.manage_emojis,			#27 manage emojis
        };
        return super().__init__();

    def getProps(self, obj):
        pr = {};
        for name in dir(obj):
            value = getattr(obj, name);
            if not name.startswith('__') and not inspect.ismethod(value):
                pr[name] = value;
        return pr;

    """def checkPerms(self, data, client, channel): #channel: [channel(channel object), permission(string)]
        perms = self.getProps(channel[0].permissions_for(channel[0].server.get_member(client.user.id)));
        #perms = self.getProps(channel[0].server.get_member(client.user.id).permissions_in(channel[0]));
        if channel[1].replace('_',' ') in self.perms:
            #print(client.user.display_name + ':' + str(perms));
            return perms[channel[1].replace(' ','_')];
        else:
            #raise Exception("Invalid permission: " + channel[1]);
            pass"""

    def _user(self, data, user, channel):
        #print(channel)
        perms = self.getProps(channel[0].permissions_for(channel[0].server.get_member(user.id)));
        #print('UMMMMMMMMM');
        #print('PERMS: ' + str(perms) + '\n')
        #print(channel[0].server.owner);
        #perms = self.getProps(user.permissions_in(channel[0]));
        #print(user.display_name + ':' + str(perms))
        if channel[1].replace('_',' ') in self.perms:
            return perms[channel[1].replace(' ','_')];
        else:
            #raise Exception("Invalid permission: " + channel[1]);
            return False;
