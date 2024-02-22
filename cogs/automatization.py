
from handlers import *
from disnake.ext import commands, tasks
import disnake 
from datetime import datetime
from log import rootLogger
import pyspw
import json
import aiogram
from aiogram import types
class automatization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mutes.start()
        rootLogger.info("Starting automatization...")
        
    @tasks.loop(seconds=60.0)
    async def mutes(self):
        thisTime = datetime.now().strftime("%d/%m/%Y %H:%M")
        path = Path("mute.json")
        userData = json.loads(path.read_text(encoding="utf-8"))
        if f"{thisTime}" in userData["mutes"]:
            for items in userData["mutes"][f"{thisTime}"]:
                guild = self.bot.get_guild(int(userData["mutes"][f"{thisTime}"][items]["guild"]))
                member = await guild.fetch_member(int(userData["mutes"][f"{thisTime}"][items]["user"]))
                await member.remove_roles(disnake.utils.get(guild.roles, id = int(takeSettings(guild.id, "mute_role"))))
                del userData["mutes"][f"{thisTime}"]
                path.write_text(json.dumps(userData, indent=4, ensure_ascii=False), encoding="utf-8", newline="\n")
        
    @bot.listen()
    async def on_message(message: disnake.Message):
        
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if "autoreaction" in data["guilds"][f"{message.guild.id}"] and not message.author.bot: 
            if f"{message.channel.id}" in data["guilds"][f"{message.guild.id}"]["autoreaction"]:
                reaction1 = bot.get_emoji(int(data["guilds"][f"{message.guild.id}"]["autoreaction"][f"{message.channel.id}"]["reaction1"]))
                await message.add_reaction(reaction1)
                try:
                    reaction2 = bot.get_emoji(int(data["guilds"][f"{message.guild.id}"]["autoreaction"][f"{message.channel.id}"]["reaction2"]))
                    await message.add_reaction(reaction2)
                except: pass
        if "autobrench" in data["guilds"][f"{message.guild.id}"] and not message.author.bot:
            if f"{message.channel.id}" in data["guilds"][f"{message.guild.id}"]["autobrench"]:
                await message.create_thread(name='Autobranch')

    @bot.event
    async def on_member_join(member):
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        guildData = data["guilds"][f"{member.guild.id}"]
        onJoinRole = disnake.utils.get(member.guild.roles, id = int(takeSettings(member.guild.id, "on_join_role")))
        if "guest_room" in guildData or guildData["server"] != ["None", {}]:
            if "guest_room" in guildData:
                channelGuestRoom = bot.get_channel(int(guildData["guest_room"]))
                try:
                    description = guildData["guest_text"].format(user=member.mention)
                except:
                    description = guildData["guest_text"]
                emb = disnake.Embed(title=f"**Привет, {member.name}!**", description=description, colour=disnake.Colour.from_rgb(47, 49, 54))
                try:
                    emb.set_image(url=guildData["image_url"])
                except:
                    print()
                    
            if guildData["server"] != ["None", {}]:
                if guildData["server"]["server"] == "POOP":
                    try:
                        api = pyspw.SpApi(card_id=api_id, card_token=api_token).get_user(member.id).nickname
                    except:
                        print('Api error.... Again')
                    if api:
                        await member.edit(nick=api)
                        await member.add_roles(bot.get_guild(member.guild.id).get_role(int(guildData["server"]["role"])))
                        if "guest_room" in guildData:
                            emb.set_footer(text=f"Игрок подтвержден! Ник: {api}")
                    else:
                        if "guest_room" in guildData:
                            emb.set_footer(text=f"Игрок не подтвержден!")
            else:    
                await member.add_roles(onJoinRole)
            if "guest_room" in guildData:
                await channelGuestRoom.send(member.mention,embed=emb)


            

    @bot.event
    async def on_member_remove(member):
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        guildData = data["guilds"][f"{member.guild.id}"]
        if "image" in guildData:
            channelGuestRoom = bot.get_channel(int(takeSettings(member.guild.id, "guest_room")))
            emb = disnake.Embed(title=f"**Пока-пока, {member.name}!**", colour=disnake.Colour.from_rgb(47, 49, 54))
            emb.set_image(url=guildData["image"])
            emb.set_footer(text="Ждем тебя снова!")
            await channelGuestRoom.send(embed=emb)


def setup(bot):
    bot.add_cog(automatization(bot))