from handlers import *
from disnake.ext import *
from disnake import *
import disnake
from pathlib import Path
import pyspw
import json

class customModals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        rootLogger.info(f"{__class__.__name__} подключен!")
    
    
    @commands.slash_command(
        name=Localised("createmodal", key="CREATE_MODAL_NAME"),
        description=Localised("Create your`s own modal`s window.", key="CREATE_MODAL_DESC")
    )
    @commands.has_permissions(administrator=True)
    async def createCustomModals(inter, channel: disnake.TextChannel, text_in_message: str,  first_label: str, second_label: str, third_label: str, fourth_label: str=Option("fourth_label"), fifth_label: str=Option("fifth_label")):
        """Creation of your own windows (profiles)

        Args:
            channel (disnake.TextChannel): This is required to transfer the channel where the message will go about the application
            text_in_message (str): This requires to transmit the text that will be above the application button (questionnaire/modal)
            first_label (str): Enter here what you want to see in the first line of the questionnaire (tests are welcome)
            second_label (str): Enter here what you want to see in the second line of the questionnaire (tests are welcome)
            third_label (str): Enter here what you want to see in the third line of the questionnaire (tests are welcome)
            fourth_label (str, optional): Enter here what you want to see in the fourth line of the questionnaire (tests are welcome)
            fifth_label (str, optional): Enter here what you want to see in the fifth line of the questionnaire (tests are welcome)
        """
        embed = disnake.Embed(title="**Aoyo Modal SYSTEM**")
        embed.add_field(name="Нажмите на кнопку нижу для подачи заявки!", value=f"{text_in_message}")
        buttons = disnake.ui.View().add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id='buttonOnModal', label='Нажми на меня!'))
        await inter.response.send_message("Готово!", ephemeral=True)
        msg = await bot.get_channel(inter.channel.id).send(embed=embed, view=buttons)
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        arrayToSql = ["guild_id", "message_id", "channel_id", "first", "second", "third"]
        dataToSql = [inter.guild.id, msg.id, channel.id, first_label, second_label, third_label]
        newData = {
            "channel": channel.id,
            0: first_label,
            1: second_label,
            2: third_label,
            "message_id": msg.id
        }
        if type(fourth_label) == str:
            newData["3"] = fourth_label
            arrayToSql.append("fourth")
            dataToSql.append(fourth_label)
        if type(fifth_label) == str:
            newData["4"] = fifth_label
            arrayToSql.append("fifths")
            dataToSql.append(fifth_label)
        print(SQL().createTable("modals"))
        print(SQL().insertData(arrayToSql, dataToSql, "modals"))
        if f"modals" not in data["guilds"][f"{inter.guild.id}"]:
            data["guilds"][f"{inter.guild.id}"]["modals"] = {}
        if f"{inter.channel.id}" not in data["guilds"][f"{inter.guild.id}"]["modals"]:
            data["guilds"][f"{inter.guild.id}"]["modals"][f"{inter.channel.id}"] = {}

        data["guilds"][f"{inter.guild.id}"]["modals"][f"{inter.channel.id}"][f"{msg.id}"] = newData
        path.write_text(json.dumps(data, indent=6), encoding="utf-8", newline="\n") 

        
        

def setup(bot):
    bot.add_cog(customModals(bot))