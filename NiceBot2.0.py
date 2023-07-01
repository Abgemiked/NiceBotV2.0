import discord
import json
import requests
import asyncio
from discord.ext import commands
from discord_interactions import verify_key_decorator, InteractionType
from discord import app_commands
from discord_interactions import InteractionResponseType
with open('config.json') as config_file:
    data = json.load(config_file)
with open('wettericon.json') as config_file:
    wettericon = json.load(config_file)
TOKEN = data['TOKEN']
ALLGEMEIN_ID = data['ALLGEMEIN_ID']
OOF_ID = data['OOF_ID']
GIF_ID = data['GIF_ID']
LOG_CHANNEL_ID = data['LOG_CHANNEL_ID']
MUSIC_CHANNEL_ID = data['MUSIC_CHANNEL_ID']
PICTURE_CHANNEL_ID = data['PICTURE_CHANNEL_ID']
BOT_CHANNEL_ID = data['BOT_CHANNEL_ID']
BLOCKED_CHANNEL_IDS = data['BLOCKED_CHANNEL_IDS']
TEMP_CHANNEL_ID = data['TEMP_CHANNEL_ID']
ALLOWED_ROLE_ID = data['ALLOWED_ROLE_IDS']
API_KEY = data['API_KEY']
BASE_URL = data['BASE_URL']
GEONAMES_API_USERNAME = data['GEONAMES_API_USERNAME']
weather_icons = wettericon["weather_icons"]
intents = discord.Intents(65419)
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
weather_command_count = {}
#bot get ready and sync the /-commands to discord
@bot.event
async def on_ready():
    await tree.sync()
    print("Ready!")
#like a test-comamnd
@tree.command(description="Frag nach Hilfe")
async def hilfe(ctx: discord.Interaction):
    await ctx.response.send_message('Hilfe ist untwegs')
#create a template of a categorie with drop-up-menu to searching for role
@tree.command(description="Kategorie für Streamer erstellen")
async def streamer(interaction: discord.Interaction, streamer_name: discord.Member):
    streamer_names = streamer_name.name.capitalize()
    category_name = f'📺 {streamer_names}'
    text_channel_names = ['🔊-streaming', '🎥-clips']
    voice_channel_names = [f'💻 {streamer_names}-Live', f'💻 {streamer_names}-Warteraum']
    role_names = [f'👨‍💻 {streamer_names}', f'👨‍💻 {streamer_names}-Mod', f'👨‍💻 {streamer_names}-Zuschauer']
    # creates category
    category = await interaction.guild.create_category(category_name)
    await interaction.response.defer()
    # creates textchannel
    for name in text_channel_names:
        await category.create_text_channel(name)
    # creates voicechannel
    for name in voice_channel_names:
        await category.create_voice_channel(name)
    # creates roles
    roles = []
    for name in role_names:
        role = await interaction.guild.create_role(name=name)
        roles.append(role)
    # set permissions for category
    for role in roles:
        if role.name == f'👨‍💻 {streamer_names}':
            await category.set_permissions(
                role,
                view_channel = True,
                manage_channels = True,
                manage_permissions = True,
                manage_webhooks = True,
                create_instant_invite = True,
                send_messages = True,
                send_messages_in_threads = True,
                create_public_threads = True,
                create_private_threads = True,
                embed_links = True,
                attach_files = True,
                add_reactions = True,
                use_external_emojis = True,
                use_external_stickers = True,
                mention_everyone = False,
                manage_messages = True, 
                manage_threads = True,
                read_message_history = True,
                send_tts_messages = True,
                use_application_commands = True,
                send_voice_messages = True,
                connect = True,
                speak= True,
                stream = True,
                use_embedded_activities = True,
                use_soundboard = True,
                use_external_sounds = True,
                use_voice_activation = True,
                mute_members = True,
                deafen_members = True,
                move_members = True,
                request_to_speak = True,
                manage_events = True
            )
        elif role.name == f'👨‍💻 {streamer_names}-Mod':
            await category.set_permissions(
                role, 
                view_channel = True,
                manage_channels = False,
                manage_permissions = False,
                manage_webhooks = False,
                create_instant_invite = True,
                send_messages = True,
                send_messages_in_threads = True,
                create_public_threads = True,
                create_private_threads = True,
                embed_links = True,
                attach_files = True,
                add_reactions = True,
                use_external_emojis = True,
                use_external_stickers = True,
                mention_everyone = False,
                manage_messages = True, 
                manage_threads = True,
                read_message_history = True,
                send_tts_messages = True,
                use_application_commands = True,
                send_voice_messages = True,
                connect = True,
                speak= True,
                stream = True,
                use_embedded_activities = True,
                use_soundboard = True,
                use_external_sounds = True,
                use_voice_activation = True,
                mute_members = True,
                deafen_members = True,
                move_members = True,
                request_to_speak = True,
                manage_events = False
            )
        elif role.name == f'👨‍💻 {streamer_names}-Zuschauer':
            await category.set_permissions(
                role, 
                view_channel = True,
                manage_channels = False,
                manage_permissions = False,
                manage_webhooks = False,
                create_instant_invite = True,
                send_messages = True,
                send_messages_in_threads = True,
                create_public_threads = True,
                create_private_threads = True,
                embed_links = True,
                attach_files = True,
                add_reactions = True,
                use_external_emojis = True,
                use_external_stickers = True,
                mention_everyone = False,
                manage_messages = False, 
                manage_threads = False,
                read_message_history = True,
                send_tts_messages = True,
                use_application_commands = True,
                send_voice_messages = True,
                connect = True,
                speak= True,
                stream = True,
                use_embedded_activities = True,
                use_soundboard = True,
                use_external_sounds = True,
                use_voice_activation = True,
                mute_members = False,
                deafen_members = False,
                move_members = False,
                request_to_speak = True,
                manage_events = False
            )
    await category.set_permissions(interaction.guild.default_role, read_messages=False, connect=False)

    for channel in category.channels:
        await channel.edit(sync_permissions=True)
        await interaction.edit_original_response(content = f"Die Kategorie, Channel & Rollen für **{streamer_names}** wurden eingerichtet & können verwendet werden.")
#command deletes a category with drop-up-menu to searching for it, also deletes roles which was created for the categorie(streamer)
@tree.command(description="Lösche Kategorie, Kanäle und Rollen für einen Streamer")
async def delstreamer(interaction: discord.Interaction, streamer: discord.Member):
    streamer_category = streamer.name.capitalize()
    category_name = f'📺 {streamer_category}'
    category = discord.utils.get(interaction.guild.categories, name=category_name)
    if not category:
        await interaction.response.send_message(content=f"Die Kategorie für **{streamer_category}** existiert nicht.")
        return
    await interaction.response.defer()
    for channel in category.channels:
        
        await channel.delete()
    role_names = [f'👨‍💻 {streamer_category}', f'👨‍💻 {streamer_category}-Mod', f'👨‍💻 {streamer_category}-Zuschauer']
    for role_name in role_names:
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            await role.delete()
    await category.delete()
    await interaction.edit_original_response(content = f"Die Kategorie von **{streamer_category}** wurde gelöscht.")
#command for set the voicechannel-user-limit
@tree.command(description="Nutzerlimit für den aktuellen Talk ändern")
async def limit(interaction: discord.Interaction, limit: int):
    channel_id = interaction.channel.id
    if limit >= 99 or limit < 2:
        await interaction.response.send_message(content="**Das Limit muss zwischen 2 und 99 liegen!**")
        return 
    if channel_id in BLOCKED_CHANNEL_IDS:
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
#command to clear a given number of the latest messages in the channel
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
#command give you the local weatherdetails for the city you were written
@tree.command(description="Hier kannst du das Wetter für deine Ortschaft abfragen")
async def wetter(interaction: discord.Interaction, ort: str):
    city_name = ort.capitalize()
    complete_url = BASE_URL + "lang=de" + "&key=" + API_KEY + "&city=" + city_name + "&days=1"
    response = requests.get(complete_url)
    data = response.json()
    await interaction.response.defer()
    if not city_name.isalpha():
        await interaction.response.send_message("Ungültige Eingabe für den Ortsnamen. Bitte verwende nur Buchstaben.")
        return
    if data.get("data"):
        weather_data = data["data"][0]
        current_temperature = weather_data["temp"]
        current_temperature_celsius = str(round(current_temperature))
        current_humidity = weather_data["rh"]
        weather_description = weather_data["weather"]["description"]
        precipitation_probability = weather_data["precip"]
        if precipitation_probability is not None:
            precipitation_probability = f"{precipitation_probability}"
        else:
            precipitation_probability = "N/A"
        city_name = weather_data["city_name"].capitalize()
        embed = discord.Embed(
            title=f"Wetter in {city_name}",
            color=interaction.guild.me.top_role.color,
            timestamp=interaction.created_at,)
        embed.add_field(name="Wetter", value=f"**{weather_description}**", inline=False)
        embed.add_field(name="Temperatur(°C)", value=f"**{current_temperature_celsius}°C**", inline=False)
        embed.add_field(name="Luftfeuchtigkeit(%)", value=f"**{current_humidity}%**", inline=False)
        hourly_data = weather_data.get("hourly")
        if hourly_data:
            for hour in hourly_data:
                time = hour.get("time")
                temperature = hour.get("temp")
                temperature_celsius = str(round(temperature))
                humidity = hour.get("rh")
                embed.add_field(name=f"Zeit: {time}", value=f"Temperatur: {temperature_celsius}°C, Luftfeuchtigkeit: {humidity}%", inline=False)
        await interaction.edit_original_response(embed=embed)
    else:
        await interaction.edit_original_response(content= "Ortschaft nicht gefunden.")
#command which allows you to change the config-data in discord without access to bot-host-server
@tree.command(description="Servereinrichtung anpassen")
async def settings(interaction: discord.Interaction, allgemein_channel: discord.TextChannel=None, oof_channel: discord.TextChannel=None, gif_channel: discord.TextChannel=None, log_channel: discord.TextChannel=None, musiccommand_channel: discord.TextChannel=None, temp_template_channel: discord.VoiceChannel=None, botcommand_channel: discord.TextChannel=None, adminrole: discord.Role=None, picture_channel: discord.TextChannel=None, api_key_weather: str=None,base_url: str=None, geonames_username: str=None):
    await interaction.response.defer()
    with open('config.json') as config_file:
        data = json.load(config_file)
    variables = [allgemein_channel, oof_channel, gif_channel, log_channel, musiccommand_channel, temp_template_channel, botcommand_channel, adminrole, picture_channel, api_key_weather, base_url, geonames_username]
    for variable in variables:
        if allgemein_channel is not None:
            data['ALLGEMEIN_ID'] = allgemein_channel.id
        if oof_channel is not None:
            data['OOF_ID'] = oof_channel.id
        if gif_channel is not None:
            data['GIF_ID'] = gif_channel.id
        if log_channel is not None:
            data['LOG_CHANNEL_ID'] = log_channel.id
        if musiccommand_channel is not None:
            data['MUSIC_CHANNEL_ID'] = musiccommand_channel.id
        if picture_channel is not None:
            data['PICTURE_CHANNEL_ID'] = picture_channel.id
        if botcommand_channel is not None:
            data['BOT_CHANNEL_ID'] = botcommand_channel.id
        if temp_template_channel is not None:
            data['TEMP_CHANNEL_ID'] = temp_template_channel.id
        if adminrole is not None:
            data['ALLOWED_ROLE_IDS'] = adminrole.id
        if api_key_weather is not None:
            data['API_KEY'] = api_key_weather
        if base_url is not None:
            data['BASE_URL'] = base_url
        if geonames_username is not None:
            data['GEONAMES_API_USERNAME']  = geonames_username
    with open('config.json', 'w') as config_file:
        json.dump(data, config_file)
    with open('config.json') as config_file:
        data = json.load(config_file)    
    if all(variable is None for variable in variables):
        embed = discord.Embed(
            title="Aktuelle Einstellungen",
            color=interaction.guild.me.top_role.color,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Allgemeiner Channel", value=f"{data['ALLGEMEIN_ID']}", inline=False)
        embed.add_field(name="OOF Channel", value=f"{data['OOF_ID']}", inline=False)
        embed.add_field(name="Gif Channel", value=f"{data['GIF_ID']}", inline=False)
        embed.add_field(name="Bilderchannel", value=f"{data['PICTURE_CHANNEL_ID']}", inline=False)
        embed.add_field(name="Logchannel", value=f"{data['LOG_CHANNEL_ID']}", inline=False)
        embed.add_field(name="Musikbefehlchannel", value=f"{data['MUSIC_CHANNEL_ID']}", inline=False)
        embed.add_field(name="Temp-Vorlage-Channel", value=f"{data['TEMP_CHANNEL_ID']}", inline=False)
        embed.add_field(name="Botbefehlechannel", value=f"{data['BOT_CHANNEL_ID']}", inline=False)
        embed.add_field(name="eingeschränkte Rollen", value=f"{data['BLOCKED_CHANNEL_IDS']}", inline=False)
        embed.add_field(name="Admninrolle", value=f"{data['ALLOWED_ROLE_IDS']}", inline=False)
        embed.add_field(name="API-Key für Wetter", value=f"{data['API_KEY']}", inline=False)
        embed.add_field(name="BASE-URL für Wetter", value=f"{data['BASE_URL']}", inline=False)
        embed.add_field(name="GEONAMES Username für Wetter", value=f"{data['GEONAMES_API_USERNAME']}", inline=False)
        await interaction.edit_original_response(embed=embed)
        return
    else:
        await interaction.edit_original_response(content="Die Servereinstellungen wurden aktualisiert.")
#event which makes the bot to spectate special channel for the usage
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
    if message.channel.id == PICTURE_CHANNEL_ID:
        if not message.attachments and not message.reference:
            await message.delete()
        elif message.reference and not message.reference.resolved.attachments:
            await message.delete()
    if message.channel.id == BOT_CHANNEL_ID:
        await message.delete()
        return
#event which creates a temp voicechannel and deletes it if the channel will be empty
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None and after.channel.id == TEMP_CHANNEL_ID:
        guild = member.guild
        channel_name = member.name.capitalize()
        category = after.channel.category
        temp_channel = await category.create_voice_channel(name=channel_name)
        await member.move_to(temp_channel)
        await temp_channel.set_permissions(
            member,  
            view_channel = True,
            manage_channels = False,
            manage_permissions = False,
            manage_webhooks = False,
            create_instant_invite = True,
            connect = True,
            speak= True,
            stream = True,
            use_embedded_activities = True,
            use_soundboard = True,
            use_external_sounds = True,
            use_voice_activation = True,
            mute_members = True,
            deafen_members = True,
            move_members = True,
            send_messages = True,
            embed_links = True,
            attach_files = True,
            add_reactions = True,
            use_external_emojis = True,
            use_external_stickers = True,
            mention_everyone = False,
            manage_messages = True, 
            read_message_history = True,
            send_tts_messages = True,
            use_application_commands = True,
            manage_events = False
        )
        await temp_channel.set_permissions(
            guild.default_role,
            view_channel = True,
            manage_channels = False,
            manage_permissions = False,
            manage_webhooks = False,
            create_instant_invite = True,
            connect = True,
            speak= True,
            stream = True,
            use_embedded_activities = True,
            use_soundboard = True,
            use_external_sounds = True,
            use_voice_activation = True,
            mute_members = False,
            deafen_members = False,
            move_members = False,
            send_messages = True,
            embed_links = True,
            attach_files = True,
            add_reactions = True,
            use_external_emojis = True,
            use_external_stickers = True,
            mention_everyone = False,
            manage_messages = False, 
            read_message_history = True,
            send_tts_messages = True,
            use_application_commands = False,
            manage_events = False
        )
    if before.channel is not None and before.channel.id != TEMP_CHANNEL_ID and len(before.channel.members) == 0:
        temp_channel = discord.utils.get(member.guild.voice_channels, name=member.name.capitalize())
        if temp_channel is not None and before.channel == temp_channel:
            await before.channel.delete()
#all deleted messages will logged in the log-channel
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