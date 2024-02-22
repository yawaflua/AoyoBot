from disnake.ext import *
import disnake
from pathlib import Path 
from handlers import *
import json
from log import rootLogger

voiceChannelData = Path("tempFiles/voiceTempFile.json")
voiceChannelName = Path("tempFiles/voiceName.json")
class audioChannelAutomatization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        rootLogger.info(f'Модуль {self.__class__.__name__} включен!')
    

    
    
    @bot.event
    async def on_voice_state_update(member, before, after):       
        if after.channel and after.channel != before.channel and after.channel.name in ['[+] СОЗДАТЬ', '[+]СОЗДАТЬ']:
            guild = bot.get_guild(member.guild.id)
            
            category = disnake.utils.get(guild.categories, id=after.channel.category.id)

            data = json.loads(voiceChannelName.read_text(encoding="utf-8"))
            
            if f"{member.id}" in data:
                channel = await guild.create_voice_channel(name=f'{data[f"{member.id}"]["chat_name"]}', category=category)
            else:
                channel = await guild.create_voice_channel(name=f'{member.name}`s voice channel', category=category)
            await member.edit(voice_channel=channel)
            data[f"{member.id}"]["channel_id"] = f"{channel.id}"
            voiceChannelName.write_text(json.dumps(data, indent=7), "utf-8", newline='\n')
            embeded = disnake.Embed(title="Пользователь присоединился к каналу", description=f"Пользователь: {member.mention}\n Канал: {after.channel.name}",timestamp=datetime.datetime.now(), color=0x00ff00)
            embed = disnake.Embed(title = '**Управление приватными комнатами**', 
                                description="""Вы можете изменить конфигурацию своей комнаты с помощью кнопок ниже.
**Переименовать приватную комнату:** ✏️
**Задать лимит участников приватной комнаты:**👥
**Закрыть/Открыть приватную комнату:**🔒
**Скрыть/Открыть приватную комнату:**👀
**Удалить канал(только для создателей канала):** \"Удалить канал\"""", colour=disnake.Colour.from_rgb(47, 49, 54))
            buttons = disnake.ui.View()
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id='renamePrivateRoom', emoji='✏'))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id='setUsersLimit', emoji='👥'))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id='closePrivateRoom', emoji=f'🔒'))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id='hidePrivateRoom', emoji=f'👀'))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id='kickUser', label='Кикнуть пользователя'))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id='deleteChannel', label='Удалить канал'))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id='giveOwner', label='Передать права на канал'))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.success, custom_id='takeOwner', label='Забрать права на канал'))
            await bot.get_guild(member.guild.id).get_channel(channel.id).send(embed=embed, view=buttons)
            writeData = {
                    'chat_name': f'{after.channel.name}',
                    'channel_owner': f'{member.id}',
                    'chat_id': f'{after.channel.id}', 
                    }
            data = json.loads(voiceChannelData.read_text(encoding="utf-8"))
            data["voice_channels"][f'{after.channel.id}'] = writeData
            voiceChannelData.write_text(json.dumps(data, indent=7), encoding="utf-8", newline="\n")


        elif before.channel and after.channel != before.channel:
            embeded = disnake.Embed(title="Пользователь покинул канал.", description=f"Пользователь: {member.mention}\n Канал: {before.channel.name}",timestamp=datetime.datetime.now(), color=disnake.Colour.from_rgb(186, 0, 6))
            guild = bot.get_guild(member.guild.id)
            data = json.loads(voiceChannelName.read_text(encoding="utf-8"))
            for item in data:
                if data[item]['channel_id'] == str(before.channel.id):
                    if before.channel.name == f'{member.name}`s voice channel' or before.channel.name == data[item]["chat_name"] and not len(before.channel.members):
                        try:
                            await before.channel.delete()
                        except Exception as e:
                            print(e)
        else: pass
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["guilds"][f"{member.guild.id}"]["logs"]:
            embeded.set_thumbnail(url=member.avatar)
            await bot.get_channel(data["guilds"][f"{member.guild.id}"]["logs"]).send(embed=embeded)
             
def setup(bot):
    bot.add_cog(audioChannelAutomatization(bot))