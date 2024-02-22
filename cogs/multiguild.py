from disnake import *
from disnake.ext import commands
from handlers import *
from log import rootLogger
import json
from dislash import Option
from pathlib import Path
import disnake
from validators import url



class multiGuildSettings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		rootLogger.info("Модуль {} подключен!".format(self.__class__.__name__))
	

	
 
 
	@commands.slash_command(name=Localized('settings', key="SETTINGS"))
	@commands.has_permissions(administrator=True)
	async def settings(self, inter):
		pass
  
  
	@settings.sub_command(
		name=Localized("setup", key="SETUP_NAME"),
		description=Localized("Setting a bot on the server.", key="SETUP_DESC"),)
	@commands.has_permissions(administrator=True)
	async def allsettings(inter, 
	mute_role: disnake.Role, 
	mute_channel: disnake.TextChannel,
	moderation_role: disnake.Role,
	on_join_role: disnake.Role,
	report_channel: disnake.TextChannel,
	transcript_channel: disnake.TextChannel,
		):
		writedData={
				"mute_role": f"{mute_role.id}",
				"mute_channel": f"{mute_channel.id}",
				"on_join_role": f"{on_join_role.id}",
				"moderation_role": f"{moderation_role.id}",
				"report_channel": f"{report_channel.id}",
		}
		path = Path("guilds/guilds.json")
		data = json.loads(path.read_text(encoding="utf-8"))
  
		if f"{inter.guild.id}" not in data["guilds"]: 
			data["guilds"][f"{inter.guild.id}"] = {}
			data["guilds"][f"{inter.guild.id}"]["mute_role"] = mute_role.id
			data["guilds"][f"{inter.guild.id}"]["mute_channel"]= mute_channel.id
			data["guilds"][f"{inter.guild.id}"]["on_join_role"] = on_join_role.id
			data["guilds"][f"{inter.guild.id}"]["report_channel"] = report_channel.id
			data["guilds"][f"{inter.guild.id}"]["moderation_role"] = moderation_role.id
			data["guilds"][f"{inter.guild.id}"]["transcript_channel"] = transcript_channel.id
			path.write_text(json.dumps(data, indent=7), encoding="utf-8", newline="\n")
		else: 
			data["guilds"][f"{inter.guild.id}"]["mute_role"] = mute_role.id
			data["guilds"][f"{inter.guild.id}"]["mute_channel"]= mute_channel.id
			data["guilds"][f"{inter.guild.id}"]["on_join_role"] = on_join_role.id
			data["guilds"][f"{inter.guild.id}"]["report_channel"] = report_channel.id
			data["guilds"][f"{inter.guild.id}"]["moderation_role"] = moderation_role.id
			data["guilds"][f"{inter.guild.id}"]["transcript_channel"] = transcript_channel.id
			path.write_text(json.dumps(data, indent=7), encoding="utf-8", newline="\n")
		await inter.response.send_message("Готово! Ваш сервер сохранен в настройках бота!", ephemeral=True)


	@settings.sub_command(name=Localized('guestroom', key="GUESTROOM_NAME"), description=Localized('Settings of the Entrance of the player', key="GUESTROOM_DESC"))
	@commands.has_permissions(administrator=True)
	async def guestroom(inter, 
                     guest_room: disnake.TextChannel=Option("guest_room",description="Укажите канал, в который будет отправляться сообщение о входе пользователя", required=True),
                     image: str=Option("image", description="Укажите ссылку на фото или гиф файл, который будет отправляться вместе с сообщением о прибытии!", required=True),
                     text: str=Option("text", description="Укажите текст, который должен присылаться вместе с сообщением о прибытии пользователя", required=True),
                     ):
		if not url(image):
			url = None
		path = Path("guilds/guilds.json")
		data = json.loads(path.read_text(encoding="utf-8"))
		data["guilds"][f"{inter.guild.id}"]["guest_room"] = guest_room.id
		data["guilds"][f"{inter.guild.id}"]["image_url"] = f"{image}"
		data["guilds"][f"{inter.guild.id}"]["guest_text"] = f"{text}"
		if "server" not in data:
			data["guilds"][f"{inter.guild.id}"]["server"] = "None" 
		path.write_text(json.dumps(data, indent=7), encoding="utf-8", newline="\n")
		await inter.response.send_message("Готово!", ephemeral=True) 
  
  
	@settings.sub_command(
        name=Localized('autobrench', key='AUTOBRENCH_NAME'),
        description=Localized("Automatic creation of branches in the channels", key="AUTOBRENCH_DESC")
    )
	@commands.has_permissions(administrator=True)
	async def autobrench(inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
		path = Path("guilds/guilds.json")
		jsonData = json.loads(path.read_text(encoding="utf-8"))
		if f"autobrench" not in jsonData["guilds"][f"{inter.guild.id}"]:
			jsonData["guilds"][f"{inter.guild.id}"]["autobrench"] = {}
			path.write_text(json.dumps(jsonData, indent=4), encoding="utf-8", newline="\n")
			jsonData = json.loads(path.read_text(encoding="utf-8"))
		
		jsonData["guilds"][f"{inter.guild.id}"]["autobrench"][f"{channel.id}"] = channel.id
		path.write_text(json.dumps(jsonData, indent=4), encoding="utf-8", newline="\n")
		await inter.response.send_message("Автоматическое создание веток настроено!", ephemeral=True)

	@settings.sub_command(
	name=Localized("autoreaction", key="AUTOREACTION_NAME"),
	description=Localized("Autoreaction setting up", key="AUTOREACTION_DESC")
	)
	@commands.has_permissions(administrator=True)
	async def autoreaction(inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, reaction1: disnake.Emoji, reaction2: disnake.Emoji=Option("reaction2")):
		path = Path("guilds/guilds.json")
		jsonData = json.loads(path.read_text(encoding="utf-8"))
		if f"autoreaction" not in jsonData["guilds"][f"{inter.guild.id}"]:
			jsonData["guilds"][f"{inter.guild.id}"]["autoreaction"] = {}
			path.write_text(json.dumps(jsonData, indent=4), encoding="utf-8", newline="\n")
			jsonData = json.loads(path.read_text(encoding="utf-8"))
		try:
			try:
				second_react = reaction2.id
			except:
				second_react = "None"
			jsonData["guilds"][f"{inter.guild.id}"]["autoreaction"][f"{channel.id}"] = {
			"reaction1": reaction1.id,
			"reaction2": second_react
			}
			path.write_text(json.dumps(jsonData, indent=4), encoding="utf-8", newline="\n")
			await inter.response.send_message("Автореакция установлена", ephemeral=True)
		except Exception as e:
			await inter.response.send_message(f"Эмодзи не найдено. Попробуйте использовать эмодзи с этого сервера", ephemeral=True)

	
 
	@settings.sub_command(
		name="auth",
		description=Localized("User authentication, if it is in the server database", key="AUTH_DESC")
	)
 
	@commands.has_permissions(administrator=True)
	async def authUser(inter, gived_role: disnake.Role, token_id: str, card_id: str):
		path = Path("guilds/guilds.json")
		data = json.loads(path.read_text(encoding="utf-8"))
		data["guilds"][f"{inter.guild.id}"]["server"] = {
			"role": f"{gived_role.id}",
			"token": token_id,
			"card": card_id
		}
		path.write_text(json.dumps(data, indent=7), encoding="utf-8", newline="\n")
		await inter.response.send_message('Готово!', ephemeral=True)
  
	@settings.sub_command(
		name=Localized("autovoice", key="AUTOVOICE_NAME"),
		description="Automatic creation of voice channels (if the user connects to [+] create)"
	)
	@commands.has_permissions(administrator=True)
	async def autovoice(inter, answer: str = commands.Param(choices=[
						disnake.OptionChoice(Localized("Turn ON", key="AUTOVOICE_ON"), "on"),
						disnake.OptionChoice(Localized("Turn OFF", key="AUTOVOICE_OFF"), "off"),
    				]
				)):
		path = Path("guilds/guilds.json")
		data = json.loads(path.read_text(encoding="utf-8"))
		if answer == "on": answer = True
		else: answer = False
		data["guilds"][f"{inter.guild.id}"]["autovoice"] = f"{answer}"
		path.write_text(json.dumps(data, indent=7), encoding="utf-8", newline="\n")
		await inter.response.send_message('Готово!', ephemeral=True)
  
  
def setup(bot):
	bot.add_cog(multiGuildSettings(bot))
