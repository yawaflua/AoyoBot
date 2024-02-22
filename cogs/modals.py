# modals.py
from handlers import logger, bot, api_id, api_token

import disnake
from pathlib import Path
import json
from disnake.ext import commands
import pyspw
import sqlite3
import psycopg2
from handlers import execute 
class modals(commands.Cog):
    def __init__(self, bot: disnake.Client):
        self.bot = bot
        logger.info(f"Модуль {self.__class__.__name__} включен!")

    @commands.Cog.listener("on_modal_submit")
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        await inter.response.send_message(f"{inter.custom_id}", ephemeral=True)
        if inter.custom_id in ["changeNamePrivateRoom", "newUsersLimit"]:
            path = Path("tempFiles/voiceTempFile.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            if (
                int(data["voice_channels"][f"{inter.channel.id}"]["channel_owner"])
                == inter.author.id
            ):
                path = Path("tempFiles/voiceName.json")
                data = json.loads(path.read_text(encoding="utf-8"))
                for key, value in inter.text_values.items():
                    if inter.custom_id == "changeNamePrivateRoom":
                        data[f"{inter.author.id}"] = {
                            "chat_name": f"{value[:1024]}",
                            "channel_id": f"{inter.channel.id}",
                        }
                        path.write_text(
                            json.dumps(data, indent=7), encoding="utf-8", newline="\n"
                        )
                        await self.bot.get_channel(inter.channel_id).edit(name=value[:1024])
                    else:
                        await self.bot.get_channel(inter.channel_id).edit(
                            user_limit=int(value[:1024])
                        )
                await inter.response.send_message("Готово!", ephemeral=True)
            else:
                await inter.response.send_message(
                    "Вы не создатель канала!", ephemeral=True
                )
        elif inter.custom_id in ["customModal", "customModal-api", "interpol", "interpol-api"]:
            path = Path("guilds/guilds.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            embed = disnake.Embed(
                description=f"{inter.author.mention}", colour=inter.author.colour
            )
            for key, value in inter.text_values.items():
                embed.add_field(
                    name=key.capitalize(),
                    value=value[:1024],
                    inline=False,
                )

            embed.set_image(url=inter.author.avatar.url if inter.author.avatar else None)
            if inter.custom_id in ["customModal-api", "interpol-api"]:
                api = (
                    pyspw.SpApi(card_id=api_id, card_token=api_token)
                    .get_user(inter.author.id)
                    .nickname
                )
                embed.set_footer(text=f"Игрок подтвержден! Никнейм: {api}")
            if inter.custom_id in ["interpol-api", "interpol"]:
                embed.set_footer(text=f"{inter.channel.id}")
                await self.bot.get_channel(
                        data["guilds"][f"{inter.guild.id}"]["modals"][f"{inter.channel.id}"]["channel"]).send(
                            f"{inter.author.mention}",
                            embed=embed,
                            components=[
                                disnake.ui.Button(
                                    label="Принять",
                                    style=disnake.ButtonStyle.success,
                                    custom_id="acceptInterpol",
                                ),
                                disnake.ui.Button(
                                    label="Отклонить",
                                    style=disnake.ButtonStyle.danger,
                                    custom_id="declineInterpol",
                                ),
                                disnake.ui.Button(
                                    label="Создать тикет",
                                    style=disnake.ButtonStyle.blurple,
                                    custom_id="createInterpolTicket",
                                ),
                            ],
                        )
            else:
                await self.bot.get_channel(
                    data["guilds"][f"{inter.guild.id}"]["modals"][f"{inter.channel.id}"][
                        f"{inter.message.id}"
                    ]["channel"]
                ).send(f"{inter.author.mention}", embed=embed)
            await inter.response.send_message("Готово!", ephemeral=True)
        elif inter.custom_id in ["addCourtModal", "addSityModal"]:
            modal_inter = inter
            if inter.custom_id == "addCourtModal":
                print("no")
                sityName = "Unbound"
                for key, values in modal_inter.text_values.items():
                        sityName = values
                i = -1
                embed = inter.message.embeds[0]
                fieldFromEmbed = None
                for field in embed.fields:
                    i = i + 1
                    if field.name == sityName:
                        fieldFromEmbed = field
                        break
                if not fieldFromEmbed: 
                    await modal_inter.response.send_message("Вы указали неправильный город", ephemeral=True)
                    return False
                symbol = (list(fieldFromEmbed.value)[-2])
                embed = inter.message.embeds[0]
                embed.set_field_at(i, name=sityName, value=fieldFromEmbed.value.replace(f"({symbol})", f"({str(int(symbol)+1)})"), inline=False)
                await modal_inter.response.send_message("Готово!", ephemeral=True)
                await inter.message.edit(embed=embed)
            else:
                await modal_inter.response.send_message("Готово!", ephemeral=True)
                sityName = "Unbound"
                sityCoordinates = "Unbound"
                for key, values in modal_inter.text_values.items():
                    if key == "sityName":
                        sityName = values
                    elif key == "sityCoordinates":
                        sityCoordinates = values
                embed = inter.message.embeds[0]
                embed.add_field(name=sityName, value=f"> **Расположение**: {sityCoordinates} \n > **Количество проведенных судов**: (0)", inline=False)
                await inter.message.edit(embed=embed)
        elif inter.custom_id == "addFarmModal":
            
            
            farmName = "Unbound"
            farmCoordinates = "Unbound"
            farmType = "Unbound"
            sityName = "Unbound"
            for key, values in inter.text_values.items():
                if key == "farmName":
                    farmName = values
                elif key == "farmCoordinates":
                    farmCoordinates = values
                elif key == "farmType":
                    farmType = values
                elif key == "sityName":
                    sityName = values
            if ";" in farmName or ";" in farmCoordinates or ";" in farmType or ";" in sityName:
                await inter.response.send_message("SQL инъекции не работает, сын шалавы", ephemeral=True)
                await (await inter.guild.fetch_member(945317832290336798)).send(f"Сын шлюхи {inter.author.mention} попытался использовать sql-инъекцию в {inter.channel.mention}")
                return 
            if inter.message.embeds[0].title == "**Фермы**":
                execute("INSERT INTO farms VALUES ({}, {}, {}, {}, {})".format(f'"{farmName}"', f'"{farmCoordinates}"', f'"{farmType}"', f'"{sityName}"', inter.author.id))
            else:
                execute("INSERT INTO private_farms VALUES ({}, {}, {}, {}, {})".format(f'"{farmName}"', f'"{farmCoordinates}"', f'"{farmType}"', f'"{sityName}"', inter.author.id))

            embed = inter.message.embeds[0]
            embed.add_field(name=sityName, value=f"> **Название фермы**: {farmName} \n > **Расположение**: {farmCoordinates} \n > **Тип фермы**: {farmType}", inline=False)
            await inter.message.edit(embed=embed)
            await inter.response.send_message("Готово!", ephemeral=True)

def setup(bot):
   bot.add_cog(modals(bot))
