from disnake.ext import commands
import disnake
import chat_exporter
from typing import Optional
import io
class saveChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(name=disnake.Localized('save-channel', key='SAVECHANNEL_NAME'),
                            description=disnake.Localized('Saves channel data, and later sends them to a separate channel', key="SAVECHANNEL_DESC"))
    @commands.has_permissions(administrator=True)
    async def save_channel(self, inter, chat: Optional[disnake.TextChannel]):
        if type(chat) == disnake.TextChannel:
            channel = chat
        else:
            channel = inter.channel
            
        transcript = await chat_exporter.export(
            channel,
            bot=self.bot,
        )
        if transcript is None:
            return

        transcript_file = disnake.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{inter.channel.name}.html",
        )

        await inter.send(file=transcript_file)
        await inter.response.send_message("Готово!", ephemeral=True)     
        
def setup(bot):
    bot.add_cog(saveChannel(bot))
        