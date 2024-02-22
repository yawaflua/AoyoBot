from handlers import bot
from disnake.ext import commands
import disnake
class courtCogs(commands.Cog):
    def __init__(self, bot: disnake.Client):
        self.bot = bot
    
    
    @commands.slash_command(name="court")
    @commands.has_permissions(administrator=True)
    async def court(self, inter):
        embed = disnake.Embed(title="**Города, где проходил суд**")
        embed.add_field(name=" Селестия", value="> **Расположение**: -1050 -500 \n > **Количество проведенных судов**: (3)", inline=False)
        embed.add_field(name=" South Point", value="> **Расположение**: -444 727 \n > **Количество проведенных судов**: (3)", inline=False)
        embed.set_footer(text="Города добавляются через кнопки ниже. За пренебрежение командами следует наказание!")
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Добавить город", custom_id="addSity"))
        view.add_item(disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Провести суд", custom_id="addCourt"))
        
        await inter.response.send_message(embed=embed, view=view)
        
    @commands.Cog.listener("on_button_click")
    async def on_button_click_court(self, inter: disnake.MessageInteraction):

        if inter.component.custom_id == "addSity":
            await inter.response.send_modal(title="Добавить город", custom_id="addSityModal", components=[
                disnake.ui.TextInput(
                    label="Название города",
                    custom_id="sityName",
                    style=disnake.TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Координаты города",
                    custom_id="sityCoordinates",
                    style=disnake.TextInputStyle.short,
                )])
        if inter.component.custom_id == "addCourt":
            await inter.response.send_modal(title="Провести суд", custom_id="addCourtModal", components=[
                disnake.ui.TextInput(
                    label="Название города",
                    custom_id="sityName",
                    style=disnake.TextInputStyle.short,
                )])
                
                
def setup(bot):
    bot.add_cog(courtCogs(bot))