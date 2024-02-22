from disnake.ext import commands
from log import rootLogger
from handlers import *
import datetime
class audit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        rootLogger.info(f"{self.__class__.__name__} подключен")
    
    @bot.event
    async def on_guild_channel_create(channel):
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if "logs" in data["guilds"][f"{channel.guild.id}"]:
            embed = disnake.Embed(title="Создание канала", description=f"Создан канал: {channel.name}! \n Категория канала: {channel.category.name}", timestamp=datetime.datetime.now())
            await bot.get_channel(data["guilds"][f"{channel.guild.id}"]["logs"]).send(embed=embed)

    @bot.event
    async def on_guild_channel_update(before, after):
        channel = before
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        after_changed = []
        before_changed = []
        if before.position != after.position: 
            after_changed.append(f"Position: {after.position}")
            before_changed.append(f"Position: {before.position}")
        if before.changed_roles != after.changed_roles:
            after_changed.append(f'Roles: {after.changed_roles}')
            before_changed.append(f'Roles: {before.changed_roles}')
        if before.overwrites != after.overwrites: 
            for item in after.overwrites:
                after_changed_perms = list(iter(after.overwrites[item].pair()[0]))
                a_item_mention = item.mention
                
            for item in before.overwrites:
                before_changed_perms = list(iter(before.overwrites[item].pair()[0]))
            for item in range(len(before_changed_perms)):
                
                if after_changed_perms[item][1] != before_changed_perms[item][1]:
                    before_changed.append({a_item_mention: before_changed_perms[item]})
                    after_changed.append({a_item_mention: after_changed_perms[item]})
                    
        if before.name != after.name:
            after_changed.append(f'Name: {after.name}')
            before_changed.append(f'Name: {before.name}')
        after_changed = str(after_changed).replace("'", '').replace('{', '').replace('}', '').replace('[', '').replace(']', '')
        before_changed = str(before_changed).replace("'", '').replace("{", '').replace("}", '').replace('[', '').replace(']', '')
        print(after_changed)
        if "logs" in data["guilds"][f"{channel.guild.id}"]:
            embed = disnake.Embed(title="Создание канала",
                description=f"Изменен канал: {channel.name}! \nКатегория канала: {channel.category.name};\nИзмененные настройки до: {before_changed};\nИзмененные настройки после: {after_changed};",
                timestamp=datetime.datetime.now())
            await bot.get_channel(data["guilds"][f"{channel.guild.id}"]["logs"]).send(embed=embed)


    @bot.event
    async def on_guild_channel_delete(channel):
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if "logs" in data["guilds"][f"{channel.guild.id}"]:
            embed = disnake.Embed(title="Удаление канала", description=f"Удален канал: {channel.name}! \n Категория канала: {channel.category.name}", timestamp=datetime.datetime.now())
            await bot.get_channel(data["guilds"][f"{channel.guild.id}"]["logs"]).send(embed=embed)
    
    @bot.event
    async def on_message_edit(before, after):
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if "logs" in data["guilds"][f"{before.guild.id}"] and before.content != after.content:
            embed = disnake.Embed(title="Изменение сообщения.", description=f"Автор: {before.author.mention}\n Канал: {before.channel.name}",timestamp=datetime.datetime.now(), color=0x00ff00)
            embed.add_field(name="Сообщение до: ", value=before.content, inline=True)
            embed.add_field(name="Сообщение после: ", value=after.content, inline=True)
            embed.set_thumbnail(url=before.author.avatar)
            await bot.get_channel(data["guilds"][f"{before.guild.id}"]["logs"]).send(embed=embed)
    
    @bot.event
    async def on_message_delete(message): 
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if "logs" in data["guilds"][f"{message.guild.id}"]:
            embed = disnake.Embed(title="Удаление сообщения.", description=f"Автор: {message.author.mention}\n Канал: {message.channel.name}\n Сообщение: {message.content}",timestamp=datetime.datetime.now(), color=disnake.Colour.from_rgb(186, 0, 6))
            embed.set_thumbnail(url=message.author.avatar)
            await bot.get_channel(data["guilds"][f"{message.guild.id}"]["logs"]).send(embed=embed)
    
    @bot.event
    async def on_member_update(before, after):
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if "logs" in data["guilds"][f"{before.guild.id}"]:
            if len(before.roles) > len(after.roles) or len(before.roles) < len(after.roles):
                embed = disnake.Embed(title="Изменение ролей.", description=f"Пользователь: {before.mention}",timestamp=datetime.datetime.now(), color=0x00ff00)
                rolesBefore = []
                rolesAfter = []
                for role in before.roles:
                    rolesBefore.append(role.mention)
                for role in after.roles:
                    rolesAfter.append(role.mention)
                embed.add_field(name="Роли до: ", value=str(rolesBefore).replace('[', '').replace(']', '').replace("'", ''), inline=True)
                embed.add_field(name="Роли после: ", value=str(rolesAfter).replace('[', '').replace(']', '').replace("'", ''), inline=True)
                embed.set_thumbnail(url=before.avatar)
                if len(rolesAfter) > len(rolesBefore):
                
                    for role in before.roles:
                        try:
                            rolesAfter.remove(role.mention)
                        except:
                            pass
                
                    embed.add_field(name="Измененная роль:", value=str(rolesAfter).replace('[', '').replace(']', '').replace("'", ''))
                else:
                    for role in after.roles:
                        try:
                            rolesBefore.remove(role.mention)
                        except:
                            pass
                
                    embed.add_field(name="Измененная роль:", value=str(rolesBefore).replace('[', '').replace(']', '').replace("'", ''))
                await bot.get_channel(data["guilds"][f"{before.guild.id}"]["logs"]).send(embed=embed)

    
def setup(bot):
    bot.add_cog(audit(bot))
        