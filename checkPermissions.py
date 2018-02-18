import inspect
import discord


class CheckPermissions(object):
    def __init__(self, client):
        base = discord.Permissions
        self.perms = {
            'create instant invite': base.create_instant_invite,    # 00 create instant invite
            'kick members': base.kick_members,				        # 01 kick members
            'ban members': base.ban_members,				        # 02 ban members
            'administrator': base.administrator,			        # 03 administrator
            'manage channels': base.manage_channels,			    # 04 manage channels
            'manage server': base.manage_server,			        # 05 manage server
            'add reactions': base.add_reactions,			        # 06 add reactions
            'view audit logs': base.view_audit_logs,			    # 07 view audit logs
            'read messages': base.read_messages,			        # 08 read messages
            'send messages': base.send_messages,			        # 09 send messages
            'send tts messages': base.send_tts_messages,		    # 10 send tts messages
            'manage messages': base.manage_messages,			    # 11 manage messages
            'embed links': base.embed_links,				        # 12 embed links
            'attach files': base.attach_files,				        # 13 attach files
            'read message history': base.read_message_history,		# 14 read message history
            'mention everyone': base.mention_everyone,			    # 15 mention everyone
            'external emojis': base.external_emojis,			    # 16 external emojis
            'connect': base.connect,					            # 17 connect
            'speak': base.speak,					                # 18 speak
            'mute members': base.mute_members,				        # 19 mute members
            'deafen members': base.deafen_members,			        # 20 deafen members
            'move members': base.move_members,				        # 21 move members
            'use voice activation': base.use_voice_activation,		# 22 use voice activation
            'change nickname': base.change_nickname,			    # 23 change nickname
            'manage nicknames': base.manage_nicknames,			    # 24 manage nicknames
            'manage roles': base.manage_roles,				        # 25 manage roles
            'manage webhooks': base.manage_webhooks,			    # 26 manage webhooks
            'manage emojis': base.manage_emojis,			        # 27 manage emojis
        }

    @staticmethod
    def get_props(obj):
        pr = {}
        for name in dir(obj):
            value = getattr(obj, name)
            if not name.startswith('__') and not inspect.ismethod(value):
                pr[name] = value
        return pr

    def _user(self, data, user, channel):
        perms = self.get_props(channel[0].permissions_for(channel[0].server.get_member(user.id)))
        if channel[1].replace('_', ' ') in self.perms:
            return perms[channel[1].replace(' ', '_')]
        else:
            print("Invalid Permission! %s:%s\n%s" % (str(user), str(channel), str(perms)))
            return False
