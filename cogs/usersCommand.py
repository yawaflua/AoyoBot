from disnake.ext import commands
import disnake
from handlers import *
from log import *
import datetime
import json
import asyncio


class usersCommand(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        rootLogger.info("Модуль {} подключен!".format(self.__class__.__name__))

    @commands.user_command(name=disnake.Localized('Get avatar', key="GET_AVATAR"))
    async def getAvatar(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        embed = disnake.Embed(description=f"Аватарка пользователя {user.mention}")
        embed.set_image(user.avatar.url)
        await inter.response.send_message(inter.author.mention, embed=embed, ephemeral=True)

    @commands.message_command(name=disnake.Localized("Report", key="REPORT"))
    async def moderationReport(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
        await inter.response.send_modal(
            title="Репорты",
            custom_id="reportModal",
            components=[
                    disnake.ui.TextInput(
                        label="Комментарий к репорту",
                        placeholder='Меня оскорбили',
                        custom_id='comment',
                        style=disnake.TextInputStyle.short
                        
                    )
                ],)
        try:
            def check(m):
                return m.author == inter.author and m.channel == inter.channel
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                event="modal_submit",
                check=check,
                timeout=30.0,
            )
            valueFromFor = modal_inter.text_values['comment']
            embed = disnake.Embed(
                title=f"Подали репорт!", 
                description=f"Ссылка на сообщение: [Тык](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})\nАвтор сообщения: {message.author.name}\nАвтор репорта: {inter.author.name}\nСообщение, на которое подали жалобу: {message.content}\nПричина жалобы: {valueFromFor}", 
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            embed.set_image('https://media.discordapp.net/attachments/876280751488909332/979778066417070151/Frame_280.png?width=1440&height=4')
            embed.set_thumbnail(url=message.author.avatar)
            embed.set_footer(text=f"{inter.author.id}")
            path = Path("guilds/guilds.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            button = disnake.ui.View()
            button.add_item(disnake.ui.Button(style=disnake.ButtonStyle.success, custom_id="reportAccept", label="Принять"))
            button.add_item(disnake.ui.Button(style=disnake.ButtonStyle.success, custom_id="reportCreateTicket", label="Создать тикет"))
            button.add_item(disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id="deleteReport", label="Удалить репорт"))
            await self.bot.get_channel(int(data["guilds"][f"{message.guild.id}"]["report_channel"])).send(embed=embed, view=button)
            await modal_inter.response.send_message("Вы удачно отправили репорт! Я отправил сообщение модерации.", ephemeral=True)
            return
        except asyncio.TimeoutError:
            return

    @commands.message_command(name=disnake.Localized("Change Field", key="CHANGEFIELD"))
    @commands.has_permissions(administrator=True)
    async def change_field(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
        await inter.response.send_modal(
            title="Смена строки",
            custom_id="changeField",
            components=[
                    disnake.ui.TextInput(
                        label="Номер строки(Если их одна, то напишите 0)",
                        placeholder='1',
                        custom_id='numberField',
                        style=disnake.TextInputStyle.short,
                        max_length=1,
                        
                    ),
                    disnake.ui.TextInput(
                        label="Новое значение",
                        placeholder='Меня зовут Кира Йошикаге',
                        custom_id='newField',
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
            numberOfField = int(modal_inter.text_values['numberField']) if int(modal_inter.text_values['numberField']) == 0 else int(modal_inter.text_values['numberField']) - 1
            print(numberOfField)
            newField = modal_inter.text_values['newField']
            embed = message.embeds[0]
            name = embed.fields[numberOfField].name
            embed.remove_field(numberOfField)
            embed.add_field(name=name, value=newField)

            await message.edit(embed=embed)
            
        except asyncio.TimeoutError:
            return
        

    @commands.slash_command(name=disnake.Localized('issue-role', key='ISSUE_ROLE_NAME'), description=disnake.Localized('Roaling by pressing the button', key="ISSUE_ROLE_DESC"))
    @commands.has_permissions(administrator=True)
    async def issueRole(self, inter, role1: disnake.Role, role2: disnake.Role, role3: disnake.Role):
        
        path = Path("guilds/guilds.json")
        data = json.loads(path.read_text(encoding='utf-8'))
        embed = disnake.Embed(title='Выдача ролей', description=f'{role1.mention}\n{role2.mention}\n{role3.mention}', color=0x00ff00)
        embed.set_image('https://media.discordapp.net/attachments/876280751488909332/979778066417070151/Frame_280.png?width=1440&height=4')
        channel = bot.get_channel(inter.channel.id)
        message_id = await channel.send(embed=embed,
                                        components=[
                                            disnake.ui.Button(label=role1.name, style=disnake.ButtonStyle.secondary, custom_id="role1"),
                                            disnake.ui.Button(label=role2.name, style=disnake.ButtonStyle.secondary, custom_id="role2"),
                                            disnake.ui.Button(label=role3.name, style=disnake.ButtonStyle.secondary, custom_id="role3"),
                                        ],
                                        )
        data["guilds"][f"{inter.guild.id}"]["issues"] = {
            f"{message_id.id}":{
            "role1": role1.id,
            "role2": role2.id,
            "role3": role3.id,
        }}
        path.write_text(json.dumps(data, indent=7), encoding='utf-8', newline='\n')
        await inter.response.send_message('Готово!', ephemeral=True)
        
    @commands.slash_command(
        name='help',
        description='Показать список команд')
    async def help(inter):
        embed = disnake.Embed(title="**Aoyo help**", color=0x00ff00)
        embed.add_field(name="**!help**", value="Показать список команд", inline=False)
        embed.add_field(name="!clear [кол-во]", value="Удаляет сообщения", inline=False)
        embed.add_field(name="**/mute [пользователь] [время(1m, 1s)] [причина]**", value="Выдать мут", inline=False)
        embed.add_field(name="**/unmute [пользователь]**", value="Размут пользователя", inline=False)
        embed.add_field(name="**/changenick [пользователь] [ник]**", value="Изменить ник пользователя", inline=False)
        embed.add_field(name="**/embed [название] [текст]**", value="Создать embed сообщение", inline=False)
        embed.add_field(name="**/permmute [пользователь] [причина]**", value="Выдать мут навсегда", inline=False)
        embed.add_field(name="**/settings setup [роль мута] [канал для мута] [модератор роль] [роль для нынезашедших] [канал для транскрипций тикета]**", value="Настройки сервера", inline=False)
        embed.add_field(name="/ticket [название тикета] [описание тикета] [канал для тикета] [название первой кнопки] [пингующая роль первой кнопки] [и т.д.]", value="Создать тикет", inline=False)
        embed.add_field(name="/settings autoreaction [канал] [реакция] [реакция]", value="Создать автореакцию", inline=False)
        embed.add_field(name="/settings autobrench [канал]", value="Автосоздание веток в этом канале", inline=False)
        embed.add_field(name="/deletechannel", value="Созвать собрание администрации для удаления канала", inline=False)
        embed.add_field(name="/enableslowmode [время(1m, 1s)]", value="Включить медленный режим", inline=False)            
                        
        await inter.response.send_message(embed=embed, ephemeral=True)
def setup(bot):
    bot.add_cog(usersCommand(bot))
