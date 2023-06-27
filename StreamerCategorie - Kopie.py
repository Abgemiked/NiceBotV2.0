import discord
import json
import asyncio
from discord.ext import commands
from discord_interactions import verify_key_decorator, InteractionType
from discord import app_commands
from discord_interactions import InteractionResponseType

with open('config.json') as config_file:
    data = json.load(config_file)

TOKEN = data['TOKEN']
ALLGEMEIN_ID = data['ALLGEMEIN_ID']
OOF_ID = data['OOF_ID']
GIF_ID = data['GIF_ID']
BLOCKED_IDS = data['BLOCKED_IDS']
ALLOWED_ROLE_ID = data['ALLOWED_ROLE_ID']
LOG_CHANNEL_ID = data['LOG_CHANNEL_ID']
MUSIC_CHANNEL_ID = data['MUSIC_CHANNEL_ID']

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    await tree.sync()
    print("Ready!")

@tree.command(description="Kategorie für Streamer erstellen")
async def streamer(ctx, streamer_name: str):
    category_name = f'📺 {streamer_name}'
    text_channel_names = ['🔊-streaming', '🎥-clips']
    voice_channel_names = [f'💻 {streamer_name}-Live', f'💻 {streamer_name}-Warteraum']
    role_names = [f'👨‍💻 {streamer_name}', f'👨‍💻 {streamer_name}-Mod', f'👨‍💻 {streamer_name}-Zuschauer']

    # Erstelle die Kategorie
    category = await ctx.guild.create_category(category_name)

    # Erstelle die Textchannels
    for name in text_channel_names:
        await category.create_text_channel(name)

    # Erstelle die Voicechannels
    for name in voice_channel_names:
        await category.create_voice_channel(name)

    # Erstelle die Rollen
    roles = []
    for name in role_names:
        role = await ctx.guild.create_role(name=name)
        roles.append(role)

    # Berechtigungen für die Kategorie festlegen
    for role in roles:
        if role.name == f'👨‍💻 {streamer_name}':
            await category.set_permissions(role, read_messages=True, manage_channels=True, manage_permissions=True, manage_webhooks=True, manage_roles=True,
                                          mention_everyone=False, manage_messages=True, manage_threads=True)
        elif role.name == f'👨‍💻 {streamer_name}-Mod':
            await category.set_permissions(role, read_messages=True, manage_channels=False, manage_permissions=False, manage_webhooks=False, manage_roles=True,
                                          mention_everyone=False, manage_messages=True, manage_threads=True)
        elif role.name == f'👨‍💻 {streamer_name}-Zuschauer':
            await category.set_permissions(role, read_messages=True, manage_channels=False, manage_permissions=False, manage_webhooks=False, manage_roles=False,
                                          mention_everyone=False, manage_messages=False, manage_threads=False)
    # Berechtigungen für @everyone in der Kategorie festlegen
    await category.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)

    # Berechtigungen der Channel mit der Kategorie synchronisieren
    for channel in category.channels:
        await channel.edit(sync_permissions=True)

    await ctx.channel.send(f"Kategorie und Channel für **{streamer_name}** wurden erstellt.")
    await ctx.edit_original_response(content=f"Kategorie und Channel für **{streamer_name}** wurden erstellt.")

@tree.command(description="Lösche Kategorie, Kanäle und Rollen für einen Streamer")

async def delstreamer(ctx, streamer_name: str):
    category_name = f'📺 {streamer_name}'

    # Überprüfe, ob die Kategorie existiert
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    if not category:
        await ctx.channel.send(f"Die Kategorie für **{streamer_name}** existiert nicht.")
        return

    # Lösche die Kanäle in der Kategorie
    for channel in category.channels:
        await channel.delete()

    # Lösche die Rollen für den Streamer
    role_names = [f'👨‍💻 {streamer_name}', f'👨‍💻 {streamer_name}-Mod', f'👨‍💻 {streamer_name}-Zuschauer']
    for role_name in role_names:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await role.delete()

    # Lösche die Kategorie
    await category.delete()

    await ctx.channel.send(f"Kategorie, Kanäle und Rollen für **{streamer_name}** wurden gelöscht.")


@tree.command(description="Nutzerlimit für den aktuellen Talk ändern")

async def limit(ctx, limit: int):
    channel_id = ctx.channel.id
    if (limit >= 99 or limit < 2):
        await ctx.channel.send(f"**Das Limit muss zwischen 2 und 99 liegen!**")
        return 
    if channel_id in BLOCKED_IDS:
        await ctx.channel.send(f"**Das ist für diesen Voicechannel nicht erwünscht!**")
        return
    if not ctx.user.voice:
        await ctx.channel.send(f"**Du bist nicht in einem VoiceChannel!**")
        return
    if channel_id != ctx.user.voice.channel.id:
        await ctx.channel.send(f"**Du bist nicht in dem dazugehörigen VoiceChannel!**")
    else:
        await ctx.user.voice.channel.edit(user_limit=limit)
        await ctx.channel.send(f"Das Benutzerlimit für **{ctx.user.voice.channel.name}** wurde auf **{limit}** gesetzt")

@tree.command(description="Löscht eine angegebene Anzahl an Nachrichten im Channel")
async def clear(ctx, amount: int):
    channel = ctx.channel
    messages = []
    allowed_role_found = False

    for role in ctx.user.roles:
        if role.id in ALLOWED_ROLE_ID:
            async for message in channel.history(limit=amount + 1):
                messages.append(message)

            # Protokolliere die gelöschten Nachrichten
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            for message in messages:
                await log_channel.send(f'Die Nachricht "**{message.content}**" von **{message.author.name}** wurde aus dem **{message.channel.name}** gelöscht.')

            # Lösche die Nachrichten
            await channel.delete_messages(messages)

            return

    await ctx.channel.send(f"**Du hast nicht die Berechtigung, Nachrichten zu löschen!**")
      
@bot.event
async def on_message(message):
    if message.channel.id == OOF_ID and message.content != "oof":
        await message.delete()
        return

    if message.channel.id == GIF_ID:
        if message.content and not message.content.startswith("https://tenor.com/"):
            await message.delete()
            return

        if message.attachments:
            for attachment in message.attachments:
                if not attachment.url.startswith("https://tenor.com/"):
                    await message.delete()
                    return

@bot.event
async def on_raw_message_delete(payload):
    channel = bot.get_channel(payload.channel_id)
    message = payload.cached_message

    if message.author.bot:
        return

    allowed_role_found = False
    for role in message.author.roles:
        if role.id in ALLOWED_ROLE_ID:
            if channel.id == MUSIC_CHANNEL_ID:
                return
            else:
                allowed_role_found = True
                log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
                await log_channel.send(f'Eine **Teamnachricht** wurde aus dem **{message.channel.name}** gelöscht.')
                break

    if not allowed_role_found:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await log_channel.send(f'Die Nachricht "**{message.content}**" von **{message.author.name}** wurde aus dem **{message.channel.name}** gelöscht.')


bot.run(TOKEN)
