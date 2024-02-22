import asyncio
import datetime as dt
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Union

import disnake
from disnake import Localized, OptionChoice
from disnake.ext import commands, tasks
from handlers import bot, now, takeSettings
from log import rootLogger


class common:
    def __init__(self, 
                 bot,
                 user_id: Optional[int] = None,
                 guild_id: Optional[int] = None):
        """Common functions 

        Args:
            user_id (Optional[int], optional): _description_. Defaults to None.
            guild_id (Optional[int], optional): _description_. Defaults to None.
        """
        self.bot = bot
        self.path = Path("mute.json")
        self.guild_id = guild_id if guild_id is not None else None
        self.user_id = user_id if user_id is not None else None
        self.role = None

    async def embed_message(self, end_time: str, time: int, reason: str, muted: int, file: Optional[str] = None):
        guild = bot.get_guild(self.guild_id)
        member = await guild.fetch_member(muted)
        channel = self.bot.get_channel(int(takeSettings(self.guild_id, "mute_channel")))
        emb = disnake.Embed(title=f"**System - Mute**", color=disnake.Color.purple(), timestamp=datetime.now())
        emb.add_field(name="**Выдал:**", value=f"<@{self.user_id}>", inline=True)
        emb.add_field(name="**Нарушитель:**", value=f"<@{muted}>", inline=True)
        emb.add_field(name="**Причина:**", value=reason, inline=False)
        if file != None: 
            emb.set_image(file)
        if end_time in ["м", "m"]:
            emb.add_field(name="**Длительность:**", value="{} минут()".format(time))
            timesdelta = timedelta(minutes=float(time))
        elif end_time in ["ч", "h"]:
            emb.add_field(name="**Длительность:**", value="{} час(ов)".format(time))
            timesdelta = timedelta(hours=float(time))
        elif end_time in ["д", "d"]:
            emb.add_field(name="**Длительность:**", value="{} день(ей)".format(time))
            timesdelta = timedelta(days=float(time))
            
        local_time = ((datetime.now() + timesdelta)
            .astimezone()
            .strftime("%d/%m/%Y %H:%M")
        )
        path = Path("mute.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        data["mutes"][f"{local_time}"] = {f"{member.id}": {"user": f"{member.id}", "guild": f"{self.guild_id}"}}
        path.write_text(json.dumps(data, indent=7), encoding="utf-8", newline="\n")
        
        await channel.send(embed=emb)
        emb.remove_field(index=0)
        emb.add_field(name="**Сервер:**", value=guild.name, inline=True)
        await member.send(embed=emb)
        
    def checkIsInMuted(self):
        """Проверка на наличие в базе мутов игрока

        Args:
            user (int): айдишечка пользователя

        Returns:
            bool: возвращается результат
        """
        userData = json.loads(self.path.read_text(encoding="utf-8"))
        for key in userData["mutes"]:
            for data in userData["mutes"][key]:

                return int(self.user_id) == int(userData["mutes"][key][data]['user'])

    def new_DB(self):
        """Create db

        Args:
            guild_id (int): guild`s id for db
            member (disnake.Member): member for data into db
        """
        if not os.path.isfile(f"users/users_{self.guild_id}.json"):
            with open(f"users/users_{self.guild_id}.json", "a") as file:
                writeinfiledata = {
                    f"{self.guild_id}": {
                        f"{self.user_id}": {
                            "userID": f"{self.user_id}",
                            "warnCounter": "0",
                            "muteCounter": "1",
                            "userMention": f"<@{self.user_id}>",
                            "guild": f"{self.guild_id}",
                        }
                    }
                }
                json.dump(writeinfiledata, file)
                file.close()

        path = Path(f"users/users_{self.guild_id}.json")
        userData = json.loads(path.read_text(encoding="utf-8"))
        if f"{self.user_id}" not in userData[f"{self.guild_id}"]:
            newUserData = {
                "userID": f"{self.user_id}",
                "warnCounter": "0",
                "muteCounter": "1",
                "userMention": f"<@{self.user_id}>",
                "guild": f"{self.guild_id}",
            }
            userData[f"{self.guild_id}"]["muteCounter"] = newUserData
        else:
            userData[f"{self.guild_id}"]["muteCounter"] = +1
        path.write_text(json.dumps(userData, indent=7), encoding="utf-8", newline="\n")

    def deleteMute(self):
        """Удаление мута из базы данных

        Args:
            user (int): Айди пользователя
        """
        userData = json.loads(self.path.read_text(encoding="utf-8"))
        for key in userData["mutes"]:
            for data in userData["mutes"][key]:
                if data == self.user_id:
                    del userData["mutes"][key]
                    self.path.write_text(
                        json.dumps(userData, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                        newline="\n",
                    )
                    return

    def mute(self): return int(takeSettings(self.guild_id, "mute_role"))
    def moderator(self): return int(takeSettings(self.guild_id, "moderation_role"))
    
    async def issuedRole(self, types):
        """Выдача роли в отдельной функции для выдачи роли

        Args:
            guild_id (int): _description_
            user_id (int): _description_

        """
        guild: disnake.Guild = self.bot.get_guild(int(self.guild_id))
        member: disnake.Member = await guild.fetch_member(int(self.user_id)) 
        
        return bool(await member.add_roles(guild.get_role(types(self))))
        

    async def removeRole(self, type: str):
        """Забирать роли для оптимизации кода

        Args:
            guild_id (int): Передавать guild id для забирания роли
            user_id (int): Передавать user id для забирания роли
            type (str): Передавать вид роли для выполнения функции

        """
        guild: disnake.Guild = self.bot.get_guild(int(self.guild_id))
        if type == "mute":
            role: disnake.Role = guild.get_role((takeSettings(self.guild.id, "mute_role")))
        member: disnake.Member = await guild.fetch_member(int(self.user_id))
        await member.remove_roles(role)


class moderationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = Path("mute.json")
        rootLogger.info("Модуль {} Включен".format(self.__class__.__name__))


    async def preMuteFunc(self, user: int, guild: int):
        """Передача данных для полной работы с всеми требуемыми функциями

        Args:
            user (int): _description_
            guild (int): _description_

        Returns:
            _type_: _description_
        """
        
        common(self.bot, user_id=user, guild_id=guild).new_DB()
        if common(self.bot, user_id=user).checkIsInMuted():
            common(self.bot, user_id=user).deleteMute()
        await common(self.bot, user_id=user, guild_id=guild).issuedRole(common.mute)


    @commands.slash_command(name=Localized("clear", key="CLEAR_NAME"), description=Localized("Clear message in current channel", key="CLEAR_DESC"))
    @commands.has_permissions(manage_messages=True)
    async def clear(inter, amount: int):
        await inter.response.send_message("Выполняется!", ephemeral=True)
        channel = bot.get_channel(inter.channel.id)
        await channel.purge(limit=amount + 1)

    
    @commands.user_command(name=Localized("Mute", key="APP_MUTE_NAME") )
    @commands.has_permissions(manage_messages=True)
    async def muteUserByApplication(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        await inter.response.send_modal(
            title='Mute',
            custom_id='muteByApp',
            components=[
                disnake.ui.TextInput(
                        label="Время мута",
                        placeholder='2h',
                        custom_id='muteTime',
                        style=disnake.TextInputStyle.short,
                        max_length=3,
                    ),
                disnake.ui.TextInput(
                        label="Причина",
                        placeholder='Флуд',
                        custom_id='muteReason',
                        style=disnake.TextInputStyle.short,
                    ),
                ],
        )
        try:
            def check(m):
                return m.author == inter.author and m.channel == inter.channel
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                event="modal_submit",
                check=check,
                timeout=30.0,
            )
            await modal_inter.response.send_message('Готово!', ephemeral=True)
            amount = modal_inter.text_values['muteTime']
            reason = modal_inter.text_values['muteReason']
            await self.preMuteFunc(member.id, inter.guild.id)
            
            await common(bot, inter.author.id, inter.guild.id).embed_message(end_time = amount[-1:], time = amount[:-1], reason = reason, muted=member.id)
        except asyncio.TimeoutError:
            return

    

    @commands.slash_command(name="embed", description=Localized("Create Embedded Message", key="CREATE_EMBED_DESC"))
    @commands.has_permissions(administrator=True)
    async def embed_message(self, inter, title: str, description: str, file: Optional[disnake.Attachment] = None):
        emb = disnake.Embed(title=title, description=f"{description}", color=disnake.Color.purple())
        # emb.add_field(name=field_name, value=field_value, inline=False)
        if file != None: emb.set_image(file.url)
        await inter.response.send_message("Готово!", ephemeral=True)
        await self.bot.get_channel(inter.channel.id).send(embed=emb)

    @commands.slash_command(name=Localized("mute", key="MUTE_NAME"), description=Localized("Mute user", key="MUTE_DESC"))
    @commands.has_permissions(manage_messages=True)
    async def add(self, inter, member: disnake.Member, amount: str, reason: str, file: disnake.Attachment):
        await self.preMuteFunc(member.id, inter.guild.id)
        await common(bot, inter.author.id, inter.guild.id).embed_message(end_time = amount[-1:], time = amount[:-1], reason = reason, muted=member.id, file= file.url)
        await inter.response.send_message("Готово!", ephemeral=True)

    @commands.slash_command(
        name=Localized("enableslowmode", key="ENABLEWLOWMODE_NAME"), description=Localized("Enable or disable slowmode in this channel", key="ENABLEWLOWMODE_DESC")
    )
    @commands.has_permissions(kick_members=True)
    async def enableslowmode(inter, amount: int, time: str = commands.Param(
            choices=[
                    OptionChoice("minute", "m"),
                    OptionChoice("second", "s"),
                    ]
                )
            ):

        await inter.response.send_message("Готово!", ephemeral=True)
        if time == "s":
            await inter.channel.edit(slowmode_delay=amount)
        elif time == "m":
            await inter.channel.edit(slowmode_delay=(amount * 60))

        else:
            await inter.response.send_message(
                "Неправильно указано время, или иное", ephemeral=True
            )


    @commands.slash_command(name=Localized("unmute", key="UNMUTE_NAME"), description=Localized("Unmute user", key="UNMUTE_DESC"))
    @commands.has_permissions(kick_members=True)
    async def unmute(self, inter, user: disnake.Member):
        role = self.bot.get_guild(inter.guild.id).get_role(
            takeSettings(inter.guild.id, "mute_role")
        )
        if role in user.roles:
            await inter.response.send_message("Готово!", ephemeral=True)
            await common(bot, user.id, inter.guild.id).removeRole("mute_role")
        else:
            await inter.response.send("Неправильный аргумент, или пользователь не замучен", ephemeral=True)

    @commands.slash_command(name=Localized("changenick", key='CHANGENICK_NAME'), description=Localized("Changes nickname ", key="CHANGENICK_DESC"))
    async def changenick(self, inter, member: disnake.Member, changednick):
        path= Path(f"users/users_{inter.guild.id}.json")
        common(bot, member.id, inter.guild.id).new_DB()
        await inter.response.send_message("Готово!", ephemeral=True)
        readedData = json.loads(path.read_text(encoding="utf-8"))
        warnCounter = int(
            readedData[f"{inter.guild.id}"][f"{member.id}"]["warnCounter"]
        )
        e = disnake.Embed(
            description="Aoyo.Moderation SYSTEM", color=disnake.Color.purple()
        )
        e.add_field(name="**Сменил:**", value=inter.author.mention)
        e.add_field(name="**Старый ник:**", value=member.name)
        e.add_field(name="**Новый ник:**", value=changednick)
        e.add_field(name="**Количество смененных ников:**", value=f"{warnCounter+1}")

        readedData[f"{inter.guild_id}"][f"{member.id}"]["warnCounter"] = +1
        path.write_text(
            json.dumps(readedData, indent=6), encoding="utf-8", newline="\n"
        )

        await member.edit(nick=changednick)
        await self.bot.get_channel(
            int(takeSettings(inter.guild_id, "mute_channel"))
        ).send(embed=e)
        e.remove_field(index=0)
        e.add_field(name="**Сервер:**", value=inter.guild.name, inline=True)
        await member.send(embed=e)


def setup(bot):
    bot.add_cog(moderationCommands(bot))
