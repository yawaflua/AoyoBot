from disnake.ext import commands
from disnake import *
from handlers import *
from log import *
import json
from dislash import Option
import disnake
from pathlib import Path


class ticket(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		rootLogger.info(f"Модуль {self.__class__.__name__} подключен!")

 

	@commands.slash_command(
		name=Localized("ticket", key="TICKET_NAME"),
		description=Localized("Creating a tick for your server! (With buttons)", key="TICKET_DESC"))
	@commands.has_permissions(administrator=True)
	async def createTicket(inter, 
	ticket_name: str, 
	ticket_description: str, 
	channel: disnake.TextChannel,
	first_button_name: str,
	first_button_role: disnake.Role,
	channel_for_transcript: disnake.TextChannel,
	second_button_name: str=Option("second_button_name", description="Укажите название второй кнопки"),
	second_button_role: disnake.Role=Option("second_button_name", description="Укажите роль для второй кнопки"),
	third_button_name: str=Option("third_button_name", description="Укажите название третьей кнопки"),
	third_button_role: disnake.Role = Option("third_button_name", type=disnake.Role, description="Укажите роль для третьей кнопки") ):
		"""
		Give several cookies to a user

		Parameters
		----------
		ticket_description: Description in create_ticket message
		channel: Specify the channel through which the message will be sent to create tickets
		first_button_name: First name of the button
		first_button_role: The first role that will be pinged when the ticket is opened, 
		channel_for_transacript: The channel, where the message with transcript will be sent
		"""
		embed = disnake.Embed(title="**Ticket**", description=ticket_description, colour=disnake.Color.blue())
		embed.set_image('https://media.discordapp.net/attachments/876280751488909332/979778066417070151/Frame_280.png?width=1440&height=4')
		embed.set_footer(text='Aoyo ticket system by YaFlay',)
		buttons = disnake.ui.View()
		buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="firstTicket", label=first_button_name))
		msg = await channel.send(embed=embed, view=buttons)
		try: category = channel_for_transcript.category.id
		except Exception: category = channel.category.id

		try: 
			sec_role = second_button_role.id
			buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id="secondTicket", label=second_button_name))
		except Exception: sec_role = "None"

		try: 
			third_role = third_button_role.id
			buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.green, custom_id="thirdTicket", label=third_button_name))
		except Exception: third_role = "None"

		writedData={
			"channel": f"{channel_for_transcript.id}",
			"category": f"{category}",
			"message_id": f"{msg.id}",
			"guild": f"{inter.guild_id}",
			"first_role": f"{first_button_role.id}",
			"second_role": f"{sec_role}",
			"third_role": f"{third_role}"
			
		}
		path = Path("guilds/guilds.json")
		data = json.loads(path.read_text(encoding="utf-8"))
		if f"{inter.guild.id}" not in data["guilds"]:
			await inter.response.send_message("Вы не настроили сервер! сделайте это прямо сейчас при помощи команды /settings setup!")
			return
		elif "ticket" not in data["guilds"][f"{inter.guild_id}"]:
			data["guilds"][f"{inter.guild_id}"]["ticket"] = {}
			data["guilds"][f"{inter.guild_id}"]["ticket"][f"{channel.id}"] = {}
			
		data["guilds"][f"{inter.guild_id}"]["ticket"][f"{channel.id}"][f"{msg.id}"] = (writedData)
		path.write_text(json.dumps(data, indent=3), encoding="utf-8", newline="\n")
		await inter.response.send_message('Готово!', ephemeral=True)

def setup(bot):
	bot.add_cog(ticket(bot))