import discord
from discord.ext import commands
import logging
import requests
from data.Users import User
import data.sql as db_session

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
global_langs = ['en']
client = discord.Client(intents=intents)

prefix = '!'
active = True


@client.event
async def on_message(message):
    global prefix
    global active
    global global_langs
    command = message.content.lower().split()[0]
    if command == prefix + 'help':  # Команда помощи пользователю
        await message.channel.send(f'''Hello! I am a translator bot. Here is an available list of my commands:
        ```{prefix}user_add (user_id) (user's native language) (to_translate[on/off]) - Connects the user to the 
        translation function. \n
{prefix}user_edit_language (user_id) (user's native language) - Changes the user's 
        primary language.\n 
{prefix}user_edit_translating (on/off) - Enables/disables the translation of the user's text.\n
{prefix}prefix (new prefix) - Changes my prefix.\n
{prefix}active (on/off) - Enables or disables the translation function for all.\n
{prefix}global_language (add/delete/show) [language] - Shows/deletes/adds the language into which the text of each 
text will be translated.```''')
    elif command == prefix + 'prefix':
        cmd, new_prefix = message.content.split()
        prefix = new_prefix
        await message.channel.send(f'Prefix successfully changed to {prefix}')
    elif command == prefix + 'active':
        if len(message.content.split()) != 2:
            await message.channel.send(f'Invalid number of arguments')
            return
        cmd, status = message.content.split()
        if status == 'on':
            active = True
            await message.channel.send(f'The translation function is successfully enabled for all')
        elif status == 'off':
            active = False
            await message.channel.send(f'The translation function is successfully disabled for all')
        else:
            await message.channel.send(f'The status is incorrectly specified')
    elif command == prefix + 'user_add':
        cmd, user_id, language, status = message.content.split()
        session = db_session.create_session()
        for user in session.query(User).filter(User.User_id == user_id):
            await message.channel.send(f'User with this id already exists')
            return
        db_sess = db_session.create_session()

        new_user = User()
        new_user.User_id = user_id
        new_user.Translating = status
        new_user.Language = language

        db_sess.add(new_user)
        db_sess.commit()
        await message.channel.send(f'<@{user_id}> is successfully connected to the translation function')
    elif command == prefix + 'user_edit_language':
        cmd, user_id, new_language = message.content.split()
        session = db_session.create_session()
        for user in session.query(User).filter(User.User_id == user_id):
            this_user_id = user.User_id
            this_translating = user.Translating

            db_sess = db_session.create_session()

            db_sess.delete(user)
            db_sess.commit()

            new_user = User()
            new_user.User_id = this_user_id
            new_user.Translating = this_translating
            new_user.Language = new_language

            db_sess.add(new_user)
            db_sess.commit()
            await message.channel.send(f"<@{user_id}>'s native language has been successfully changed")
            return
        await message.channel.send(f'The user with this id is not connected to the translator')
    elif command == prefix + 'user_edit_translating':
        cmd, user_id, new_status = message.content.split()
        session = db_session.create_session()
        for user in session.query(User).filter(User.User_id == user_id):
            this_user_id = user.User_id
            this_language = user.Language

            db_sess = db_session.create_session()

            db_sess.delete(user)
            db_sess.commit()

            new_user = User()
            new_user.User_id = this_user_id
            new_user.Translating = new_status
            new_user.Language = this_language

            db_sess.add(new_user)
            db_sess.commit()
            await message.channel.send(f"The translation of <@{user_id}> text has been changed successfully")
            return
        await message.channel.send(f'The user with this id is not connected to the translator')
    elif command == prefix + 'global_language':
        cmd, ex = message.content.split()
        if ex == 'show':
            await message.channel.send(f'The global laguages are: {" ".join(global_langs)}')
            return
        cmd2, ex = ex.split()
        if cmd2 == 'add':
            global_langs.append(ex.lower())
            await message.channel.send(f'"{ex}" has been successfully added to the list of global languages')
        elif cmd2 == 'delete':
            if ex not in global_langs:
                await message.channel.send(f'{ex} is not a global language')
            else:
                global_langs.pop(global_langs.index(ex.lower()))
                await message.channel.send(f'"{ex}" has been successfully removed to the list of global languages')
        else:
            await message.channel.send(f'ERROR')
    elif message.content[0:len(prefix) - 1] == prefix:
        await message.channel.send(f'Invalid command "{message}"')
    else:
        session = db_session.create_session()
        if active:
            user = session.query(User).get(message.author.id)
            if not user or user.Translating is False:
                return
            result = ''
            from_lang = user.Language
            for gl_language in global_langs:
                response = requests.get(
                    'https://api.mymemory.translated.net/get',
                    params={'q': message, 'langpair': '|'.join((from_lang, gl_language))}
                ).json()
                result += gl_language + ':\n' + response['responseData']['translatedText']
            await message.channel.send(result)


TOKEN = ""
db_session.global_init("db/users.db")
client.run(TOKEN)
