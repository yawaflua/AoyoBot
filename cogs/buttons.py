from disnake.ext import commands
import disnake
import json
from pathlib import Path
import pyspw
from disnake import TextInputStyle
from handlers import api_id, api_token, takeSettings, bot
from asyncio import sleep
from random import randint
import datetime
import chat_exporter
import io

class buttons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @bot.listen("on_button_click")
    async def button(inter: disnake.MessageInteraction):
        if inter.component.custom_id in ['role1', 'role2', 'role3']:
            path = Path("guilds/guilds.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            role = bot.get_guild(inter.guild.id).get_role(data["guilds"][f"{inter.guild.id}"]['issues'][f"{inter.message.id}"][inter.component.custom_id])
            await inter.author.add_roles(role)
            await inter.response.send_message(f'{role.mention} вам выдалась!', ephemeral=True)
        elif inter.component.custom_id == "buttonOnModal":
            path = Path("guilds/guilds.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            modalData = data["guilds"][f"{inter.guild.id}"]["modals"][f"{inter.channel.id}"][f"{inter.message.id}"]
            if data["guilds"][f"{inter.guild.id}"]["server"] != {}:
                try:
                    api = pyspw.SpApi(card_id=api_id, card_token=api_token).get_user(inter.author.id).nickname
                    custom_id="customModal-api"
                except Exception:
                    api = None
                    custom_id = "customModal"
            
            component=[
                disnake.ui.TextInput(
                    label=modalData["0"],
                    custom_id=modalData["0"],
                    style=TextInputStyle.short,
                ),
            ]
            for i in range(len(modalData)-3):
                i = i + 1
                modalDatas = modalData[f"{i}"]
                component.append(
                    disnake.ui.TextInput(
                        label=f"{modalDatas}",
                        custom_id=f"{modalDatas}",
                        style=TextInputStyle.short,
                    ),
                )

            await inter.response.send_modal(
                    title="Aoyo Modal System",
                    custom_id=custom_id,
                    components=component,)
        elif inter.component.custom_id in ["closePrivateRoom", "hidePrivateRoom"]: 
            guild = bot.get_guild(inter.guild.id)
            role = guild.get_role(int(takeSettings(inter.guild.id, "on_join_role")))
            member = inter.author
            if inter.component.custom_id == "closePrivateRoom":
                overwrites = {
                    guild.default_role: disnake.PermissionOverwrite(connect=False),
                    role: disnake.PermissionOverwrite(connect=False),
                    member: disnake.PermissionOverwrite(connect=True)
                }
            else: 
                overwrites = {
                    guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                    role: disnake.PermissionOverwrite(view_channel=False),
                    member: disnake.PermissionOverwrite(view_channel=True)
            }
            await bot.get_channel(inter.channel.id).edit(overwrites=overwrites)
            await inter.response.send_message("Готово.", ephemeral=True)          
        
        elif inter.component.custom_id in ["giveOwner", "kickUser", "deleteChannel"]:
            path = Path("tempFiles/voiceTempFile.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            if int(data["voice_channels"][f"{inter.channel.id}"]["channel_owner"]) == inter.author.id:
                if inter.component.custom_id == "giveOwner": await inter.response.send_message("Отправьте пинг игрока, которому хотите передать права", ephemeral=True)
                elif inter.component.custom_id == "deleteChannel": await inter.channel.delete()
                else: await inter.response.send_message("Отправьте пинг игрока, которого хотите кикннуть", ephemeral=True)
                def check(m):
                    return m.author == inter.author and m.channel == inter.channel
                try:
                    message = await bot.wait_for('message', timeout=30.0, check=check)
                except TimeoutError:
                    return
                else:
                    content = message.mentions[0].id
                    await message.delete()
                    if inter.component.custom_id == "giveOwner":
                        data["voice_channels"][f"{inter.channel.id}"]["channel_owner"] = content
                        data["voice_channels"][f"{inter.channel.id}"]["old_channel_owner"] = inter.author.id
                        path.write_text(json.dumps(data, indent=6), encoding="utf-8", newline="\n")
                        await inter.response.send_message(f"Готово! Владелец канала теперь: <@{content}>", ephemeral=True)
                    else:
                        member = await bot.get_guild(inter.guild.id).fetch_member(int(content))
                        await member.edit(voice_channel=None)
                        await inter.response.send_message(f"Готово! <@{content}> был кикнут", ephemeral=True)
            else:
                await inter.response.send_message("Вы не создатель канала!", ephemeral=True)

        elif inter.component.custom_id == "takeOwner":
            path = Path("tempFiles/voiceTempFile.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            if data["voice_channels"][f"{inter.channel.id}"]["old_channel_owner"] == inter.author.id:
                data["voice_channels"][f"{inter.channel.id}"]["channel_owner"] = inter.author.id
                path.write_text(json.dumps(data, indent=6), encoding="utf-8", newline="\n")
                await inter.response.send_message(f"Готово! Владелец канала теперь: <@{inter.author.id}>", ephemeral=True)
        elif inter.component.custom_id == "renamePrivateRoom": 
                await inter.response.send_modal(
                    title="Aoyo Modal System",
                    custom_id="renamePrivateRoom",
                    components=[
                        disnake.ui.TextInput(
                            label='Новое название канала:',
                            placeholder="Я люблю нюхать бебру",
                            custom_id='newNamePrivateRoom',
                            style=disnake.TextInputStyle.short,
				            )
                        ],
                    )
        elif inter.component.custom_id == "setUsersLimit":
            await inter.response.send_modal(
                    title="Aoyo Modal System",
                    custom_id="setUsersLimit",
                    components=[
                        disnake.ui.TextInput(
                            label='Новое максимальное кол-во пользователей:',
                            placeholder="1",
                            custom_id='newUserLimit',
                            style=disnake.TextInputStyle.short,
                            )
                        ],
                    )
        # tickets
        elif inter.component.custom_id in ["firstTicket", "secondTicket", "thirdTicket", "createTicket", "reportCreateTicket"]:
            path = Path("guilds/guilds.json")
            ticketData = Path("tempFiles/ticket.json")
            aJsonData = json.loads(path.read_text(encoding="utf-8"))
            fromJsonData = json.loads(path.read_text(encoding="utf-8")).get('guilds')[f"{inter.guild_id}"]
            toJsonData = json.loads(ticketData.read_text(encoding="utf-8"))
            mention = inter.author.mention
            if inter.component.custom_id == "firstTicket":
                role = fromJsonData["ticket"][f"{inter.channel.id}"][f"{inter.message.id}"]["first_role"]
            if inter.component.custom_id == "secondTicket":
                role = fromJsonData["ticket"][f"{inter.channel.id}"][f"{inter.message.id}"]["second_role"]
            if inter.component.custom_id == "thirdTicket":
                role = fromJsonData["ticket"][f"{inter.channel.id}"][f"{inter.message.id}"]["third_role"]
            if inter.component.custom_id == "reportCreateTicket":
                role = fromJsonData["moderation_role"]
                embedMessage = inter.message.embeds[0]                
                mention = f"<@{embedMessage.footer.text}> \n{inter.author.mention}"
                
                await inter.message.edit(components=[
            disnake.ui.Button(style=disnake.ButtonStyle.success, custom_id="reportAccept", label="Принять"),
            disnake.ui.Button(label="Создать тикет", style=disnake.ButtonStyle.success, custom_id="reportCreateTicket", disabled=True),
            disnake.ui.Button(label="Удалить репорт", style=disnake.ButtonStyle.danger, custom_id="deleteReport"),
            ],)
            embed = disnake.Embed(title="Управление тикетом", description="Если вы готовы завершить тикет, нажмите ниже.", colour=disnake.Color.blue())
            buttons = disnake.ui.View()
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id="closeTicket", label="Закрыть тикет"))

            guild = bot.get_guild(inter.guild.id)
            roleOverwrite = guild.get_role(int(takeSettings(inter.guild.id, "on_join_role")))
            roleTicket = guild.get_role(int(role))
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                roleOverwrite: disnake.PermissionOverwrite(view_channel=False),
                inter.author: disnake.PermissionOverwrite(view_channel=True),
                roleTicket: disnake.PermissionOverwrite(view_channel=True)
            }
            if not fromJsonData['ticket'].get('counter'): 
                aJsonData['guilds'][f'{inter.guild.id}']['ticket']['counter'] = 1
            aJsonData['guilds'][f'{inter.guild.id}']['ticket']['counter'] = int(aJsonData['guilds'][f'{inter.guild.id}']['ticket']['counter']) + 1
            count = aJsonData['guilds'][f'{inter.guild.id}']['ticket']['counter']
            category = disnake.utils.get(guild.categories, id=inter.channel.category.id)
            channel = await guild.create_text_channel(name=f"ticket-{count}", category=category, overwrites=overwrites)
            await channel.send(content=f"{mention}\n<@&{role}>",embed=embed, view=buttons)
            newJsonData = {
                "channel_owner": f"{inter.author.mention}",
                "channel_name": f"{channel.name}",
                "panel": f"{inter.component.custom_id}"
            }
            if not toJsonData["ticket"].get(f"{inter.guild_id}"):
                toJsonData["ticket"][f"{inter.guild_id}"] = {}

            toJsonData["ticket"][f"{inter.guild_id}"][f"{channel.id}"] = newJsonData
            
            if inter.component.custom_id == "reportCreateTicket":
                toJsonData["ticket"][f"{inter.guild_id}"][f"{channel.id}"]["user_name"] = f"{embedMessage.footer.text}"
            path.write_text(json.dumps(aJsonData, indent=3), encoding="utf-8", newline="\n")
            ticketData.write_text(json.dumps(toJsonData, indent=3), encoding="utf-8", newline="\n")
            await inter.response.send_message(f'Ваш тикет: {channel.mention}', ephemeral=True)

        elif inter.component.custom_id == "closeTicket":
            embed = disnake.Embed(title="Подтверждение", description=f"Вы уверены, что хотите закрыть тикет, {inter.author.name}?")
            buttons = disnake.ui.View()
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id="closeTicketPerm", label="Да, закрыть тикет"))
            buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.success, custom_id="cancelCloseTicket", label="Нет"))
            await inter.response.send_message(embed=embed, view=buttons)
            await inter.message.edit(components=[
            disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id="closeTicket", label="Закрыть тикет", disabled=True),
            ],)
        elif inter.component.custom_id == "cancelCloseTicket":
            for message in (await inter.channel.history(limit=None, oldest_first=True).flatten()):
                msg = await bot.get_channel(inter.channel.id).fetch_message(message.id)
                break
            await msg.edit(components=[
                disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id="closeTicket", label="Закрыть тикет", disabled=False),
                ],)
            await inter.message.delete()
        elif inter.component.custom_id == "closeTicketPerm":
            embed = disnake.Embed(title='**Aoyo ticket system**', description=f'Канал закрыт {inter.author.mention}', color=0x00ff00)
            embed.set_image('https://media.discordapp.net/attachments/876280751488909332/979778066417070151/Frame_280.png?width=1440&height=4')
            buttons = disnake.ui.View().add_item(disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id='deleteChannelTicket', label='Удалить канал'))
            channel = bot.get_channel(inter.channel.id)
            overwrites = {
                inter.author: disnake.PermissionOverwrite(view_channel=False),
            }
            await inter.message.delete()
            await channel.edit(overwrites=overwrites, name=f"closed-{channel.name[7:]}")
            await channel.send(embed=embed, view=buttons)

        elif inter.component.custom_id == "deleteChannelTicket":
            path = Path("guilds/guilds.json")
            ticketData = Path("tempFiles/ticket.json")
            fromJsonData = json.loads(path.read_text(encoding="utf-8"))
            toJsonData = json.loads(ticketData.read_text(encoding="utf-8"))
            guild = bot.get_guild(inter.guild.id) 
            member = await guild.fetch_member(int(toJsonData["ticket"][f"{inter.guild.id}"][f"{inter.channel.id}"]["channel_owner"].replace('<@', '').replace('>', '')))
            channel = bot.get_channel(int(fromJsonData["guilds"][f"{inter.guild_id}"]["transcript_channel"]))
            transcript = await chat_exporter.export(
                inter.channel,
                bot=bot,
            )
            embed = disnake.Embed(title='**Aoyo ticket system**', colour=disnake.Color.green())
            embed.add_field(name="Создатель", value=member.mention)
            embed.add_field(name="Название канала", value=toJsonData["ticket"][f"{inter.guild.id}"][f"{inter.channel.id}"]["channel_name"], inline=False)
            embed.add_field(name="Причина открытия", value=toJsonData["ticket"][f"{inter.guild.id}"][f"{inter.channel.id}"]["panel"], inline=True)
            embed.set_image('https://media.discordapp.net/attachments/876280751488909332/979778066417070151/Frame_280.png?width=1440&height=4')
            
            transcript_file = disnake.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-{inter.channel.name}.html",
            )

            await bot.get_channel(int(fromJsonData["guilds"][f"{inter.guild.id}"]["transcript_channel"])).send(f"**Сохранен и отправлен {inter.channel.name}**",file=transcript_file)
            embed = disnake.Embed(title='**Aoyo ticket system**', description='Канал удалится в течении 10 секунд.', colour=disnake.Color.purple())
            await inter.message.edit(view=None)
            await inter.response.send_message(embed=embed)
            await sleep(9)
            await bot.get_channel(inter.channel.id).delete(reason=f'Deleted by {inter.author.id}')        
            del toJsonData["ticket"][f"{inter.guild.id}"][f"{inter.channel.id}"]
            ticketData.write_text(json.dumps(toJsonData, indent=3), encoding="utf-8", newline="\n")  
        # report
        elif inter.component.custom_id == "reportAccept":
            member = await bot.get_guild(inter.guild.id).fetch_member(int(inter.message.embeds[0].footer.text))
            await member.send(embed=disnake.Embed(title="Aoyo REPORT", description=f"Ваш репорт был принят и рассмотрен модератором {inter.author.mention}", color=0x00ff00,timestamp=datetime.datetime.now()))
            await inter.message.edit(components=[
                disnake.ui.Button(style=disnake.ButtonStyle.success, custom_id="reportAccept", label="Принять", disabled=True),
                disnake.ui.Button(label="Создать тикет", style=disnake.ButtonStyle.success, custom_id="reportCreateTicket", disabled=True),
                disnake.ui.Button(label="Удалить репорт", style=disnake.ButtonStyle.danger, custom_id="deleteReport", disabled=True),
            ],)
            await inter.message.edit(embed=inter.message.embeds[0].add_field(name="Репорт был принят!", value=f"Репорт принял {inter.author.mention}"))
            await inter.response.send_message("Готово!", ephemeral=True)
        elif inter.component.custom_id == "deleteReport":
            await inter.response.send_message("Готово!", ephemeral=True)
            await inter.message.edit(components=[
            disnake.ui.Button(style=disnake.ButtonStyle.success, custom_id="reportAccept", label="Принять", disabled=True),
            disnake.ui.Button(label="Создать тикет", style=disnake.ButtonStyle.success, custom_id="reportCreateTicket", disabled=True),
            disnake.ui.Button(label="Удалить репорт", style=disnake.ButtonStyle.danger, custom_id="deleteReport", disabled=True),
        ],)
        else:
            await inter.response.send_message('Ошибка!', ephemeral=True)
def setup(bot):
    bot.add_cog(buttons(bot))