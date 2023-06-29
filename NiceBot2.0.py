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
LOG_CHANNEL_ID = data['LOG_CHANNEL_ID']
MUSIC_CHANNEL_ID = data['MUSIC_CHANNEL_ID']
PICTURE_ID = data['PICTURE_ID']
BLOCKED_IDS = data['BLOCKED_IDS']
ALLOWED_ROLE_ID = data['ALLOWED_ROLE_ID']

intents = discord.Intents(65419)
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    await tree.sync()
    print("Ready!")
@tree.command(description="Frag nach Hifle")
async def hilfe(ctx: discord.Interaction):
    await ctx.response.send_message('Hilfe ist untwegs')

@tree.command(description="Kategorie für Streamer erstellen")
async def streamer(interaction: discord.Interaction, streamer_name: str):
    category_name = f'📺 {streamer_name}'
    text_channel_names = ['🔊-streaming', '🎥-clips']
    voice_channel_names = [f'💻 {streamer_name}-Live', f'💻 {streamer_name}-Warteraum']
    role_names = [f'👨‍💻 {streamer_name}', f'👨‍💻 {streamer_name}-Mod', f'👨‍💻 {streamer_name}-Zuschauer']
    # Erstelle die Kategorie
    category = await interaction.guild.create_category(category_name)
    await interaction.response.defer()
    # Erstelle die Textchannels
    for name in text_channel_names:
        await category.create_text_channel(name)
    # Erstelle die Voicechannels
    for name in voice_channel_names:
        await category.create_voice_channel(name)
        #await interaction.edit_original_response(content = f"Die Channel für **{streamer_name}** wurden erstellt.")
    # Erstelle die Rollen
    roles = []
    for name in role_names:
        role = await interaction.guild.create_role(name=name)
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
    await category.set_permissions(interaction.guild.default_role, read_messages=False, connect=False)

    # Berechtigungen der Channel mit der Kategorie synchronisieren
    for channel in category.channels:
        await channel.edit(sync_permissions=True)
        await interaction.edit_original_response(content = f"Die Kategorie, Channel & Rollen für **{streamer_name}** wurden eingerichtet & können verwendet werden.")

@tree.command(description="Lösche Kategorie, Kanäle und Rollen für einen Streamer")
async def delstreamer(interaction: discord.Interaction, streamer_name: str):
    category_name = f'📺 {streamer_name}'
    # Überprüfe, ob die Kategorie existiert
    category = discord.utils.get(interaction.guild.categories, name=category_name)
    if not category:
        await interaction.response.defer(content=f"Die Kategorie für **{streamer_name}** existiert nicht.")
        return
    # Lösche die Kanäle in der Kategorie
    for channel in category.channels:
        await channel.delete()
    await interaction.response.defer()
    # Lösche die Rollen für den Streamer
    role_names = [f'👨‍💻 {streamer_name}', f'👨‍💻 {streamer_name}-Mod', f'👨‍💻 {streamer_name}-Zuschauer']
    for role_name in role_names:
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            await role.delete()
        #await interaction.edit_original_response(content=f"Die Rollen wurden gelöscht")        
    # Lösche die Kategorie
    await category.delete()
    await interaction.edit_original_response(content = f"Die Kategorie von **{streamer_name}** wurde gelöscht.")
    


@tree.command(description="Nutzerlimit für den aktuellen Talk ändern")
async def limit(interaction: discord.Interaction, limit: int):
    channel_id = interaction.channel.id
    if limit >= 99 or limit < 2:
        await interaction.response.send_message(content="**Das Limit muss zwischen 2 und 99 liegen!**")
        return 
    if channel_id in BLOCKED_IDS:
        await interaction.response.send_message(content="**Das ist für diesen Voicechannel nicht erwünscht!**")
        return
    if not interaction.user.voice:
        await interaction.response.send_message(content="**Du bist nicht in einem VoiceChannel!**")
        return
    if channel_id != interaction.user.voice.channel.id:
        await interaction.response.send_message(content="**Du bist nicht in dem dazugehörigen VoiceChannel!**")
    else:
        await interaction.user.voice.channel.edit(user_limit=limit)
        await interaction.response.send_message(content=f"Das Benutzerlimit für **{interaction.user.voice.channel.name}** wurde auf **{limit}** gesetzt")

@tree.command(description="Löscht eine angegebene Anzahl an Nachrichten im Channel")
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 20:
        await interaction.response.send_message(content="Die Anzahl der zu löschenden Nachrichten muss zwischen **1** und **20** liegen.")
        return
    channel = interaction.channel
    messages = []
    async for message in channel.history(limit=amount + 1):
        messages.append(message)
    if messages:
        await interaction.response.defer()
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        for message in messages:
            await log_channel.send(f'Die Nachricht "**{message.content}**" von **{message.author.name}** wurde aus dem **{message.channel.name}** gelöscht.')
            await channel.delete_messages(messages)
            await interaction.edit_original_response(content=f"Die Nachrichten wurden gelöscht")
    else:
        await interaction.response.send_message(content="**Du hast nicht die Berechtigung, Nachrichten zu löschen!**")

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
    
    if message.channel.id == PICTURE_ID:
        if not message.attachments and not message.reference:
            await message.delete()
        elif message.reference and not message.reference.resolved.attachments:
            await message.delete()

@bot.event
async def on_raw_message_delete(payload):
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return

    message = payload.cached_message
    if message is None or message.author.bot:
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
