import asyncio
import discord
import datetime


class embed(object):

    def __init__(self):
        self.description = "Used to retrieve various kinds of information.\n" + \
                           "This command takes json formatted input." + \
                           "\nYou may use the following template as a guideline:\n\n" + \
                           "``e!embed {\"text\":\"This is the normal text area.\",\"embed\":" + \
                           "{" \
                           "\"title\":\"Title\"," \
                           "\"description\":" \
                           "\"This is where the description goes.\"," \
                           "\"footer\":{" \
                           "\"text\":\"Footer text\"" \
                           "}," \
                           "\"author\":{" \
                           "\"name\":\"My name\"" \
                           "}," \
                           "\"fields\":[" \
                           "{" \
                           "\"name\":\"Header1\"," \
                           "\"value\":\"Text under header.\"" \
                           "}," \
                           "{" \
                           "\"name\":\"Header2\"," \
                           "\"value\":\"Text under header... again.\"" \
                           "}" \
                           "]" \
                           "}" \
                           "}``\n\n"
        self.permissions = ['administrator']
        self.Owner = False
        self.bOwner = False
        self.name = 'embed'
        self.tick = False
        self.react = False
        self.commands = {
            'help':
                'Displays how to use a specific command.\n' +
                'How to use this command: e!embed help (args)\n' +
                'For Example: e!embed help help - shows this message.'
        }

    @staticmethod
    def make_embed(data, emb):
        _embed = discord.Embed.Empty
        text = ''
        if 'text' in emb:
            text = emb['text']
        if 'embed' in emb:
            _embed = discord.Embed()
            if 'title' in emb['embed']:
                _embed.title = emb['embed']['title']
            if 'description' in emb['embed']:
                _embed.description = emb['embed']['description']
            if 'timestamp' in emb['embed']:
                _embed.timestamp = datetime.strptime(
                    emb['embed']['timestamp'].replace('-', ' ').replace(':', ' ').replace('T', ' '),
                    '%Y %m %d %H %M %S'
                )
            if 'color' in emb['embed'] or 'colour' in emb['embed']:
                kw = 'color'
                if 'colour' in emb['embed']:
                    kw = 'colour'
                try:
                    _embed.color = int(emb['embed'][kw])
                except Exception as e:
                    try:
                        _embed.color = int(emb['embed'][kw], 16)
                    except Exception as f:
                        print(repr(e))
                        _embed.color = data.embed_announce
                        print(repr(f))
            else:
                _embed.color = data.embed_announce
            if 'footer' in emb['embed']:
                ftext = discord.Embed.Empty
                icon = discord.Embed.Empty
                if 'text' in emb['embed']['footer']:
                    ftext = emb['embed']['footer']['text']
                if 'icon_url' in emb['embed']['footer']:
                    icon = emb['embed']['footer']['icon_url']
                _embed.set_footer(text=ftext, icon_url=icon)
            if 'image' in emb['embed']:
                _embed.set_image(url=emb['embed']['image'])
            if 'thumbnail' in emb['embed']:
                _embed.set_thumbnail(url=emb['embed']['thumbnail'])
            if 'author' in emb['embed']:
                name = '   '
                url = discord.Embed.Empty
                icon = discord.Embed.Empty
                if 'name' in emb['embed']['author']:
                    name = emb['embed']['author']['name']
                if 'url' in emb['embed']['author']:
                    url = emb['embed']['author']['url']
                if 'icon_url' in emb['embed']['author']:
                    icon = emb['embed']['author']['icon_url']
                _embed.set_author(name=name, url=url, icon_url=icon)
            if 'fields' in emb['embed']:
                fields = emb['embed']['fields']
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
                    _embed.add_field(name=name, value=value, inline=inline)
        return [text, _embed]

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
                    #############################################################################
                    if arg.lower() == 'help':
                        if len(args[argpos + 1:]) > 0:
                            _help = data.help(msg, self, args[argpos + 1:])
                            skip = len(args[argpos + 1:])
                        else:
                            _help = data.help(msg, self)
                        for h in _help:
                            results.append(h)
                    ##########################
                    else:
                        skip = len(args[argpos:])
                        n_args = args[argpos:]
                        emb, res = data.json(n_args, msg)
                        if emb is not None:
                            if type(emb) is list:
                                res = []
                                for entry in emb:
                                    res.append(self.make_embed(data, entry))
                                for entry in res:
                                    if entry[1] is discord.Embed.Empty:
                                        yield from client.send_message(msg.channel, entry[0])
                                    else:
                                        yield from client.send_message(msg.channel, entry[0], embed=entry[1])
                            if type(emb) is dict:
                                res = self.make_embed(data, emb)
                                if res[1] is discord.Embed.Empty:
                                    try:
                                        yield from client.send_message(msg.channel, res[0])
                                    except discord.errors.HTTPException as e:
                                        results.append([
                                                '',
                                                data.embedder([['Error:', repr(e)]], colour=data.embed_error),
                                                msg.channel
                                        ])
                                else:
                                    try:
                                        yield from client.send_message(msg.channel, res[0], embed=res[1])
                                    except discord.errors.HTTPException as e:
                                        results.append([
                                                '',
                                                data.embedder([['Error:', repr(e)]], colour=data.embed_error),
                                                msg.channel
                                        ])
                        else:
                            for r in res:
                                results.append(r)
                #############################################################################
                argpos += 1
            yield from data.messager(msg, results)
