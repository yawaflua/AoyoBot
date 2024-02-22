import disnake
import yt_dlp   # type: ignore
from disnake.ext import commands, tasks
import asyncio
from typing import Any, Dict, Optional
# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ""
from yandex_music import ClientAsync, Client
import ytmusicapi
from handlers import logger
from pathlib import Path
import json
import os

type_to_name = {
    'track': 'трек',
    'artist': 'исполнитель',
    'album': 'альбом',
    'playlist': 'плейлист',
    'video': 'видео',
    'user': 'пользователь',
    'podcast': 'подкаст',
    'podcast_episode': 'эпизод подкаста',
}
yt = ytmusicapi.YTMusic()
ffmpeg_options = {'options': '-vn', 'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}

ytdl = yt_dlp.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(self, source: disnake.AudioSource, *, data: Dict[str, Any], volume: float = 0.125):
        super().__init__(source, volume)

        self.title = data.get("title")
        self.author = data.get("author")
        self.source = data.get("source")
        self.id = data.get("unicalID")
        self.thumbnails: str = data.get("icon")
        self.data = data

    @classmethod
    async def from_url(
        cls, url, *, loop: Optional[asyncio.AbstractEventLoop] = None, stream: bool = True
    ):
        player = None
        if not "http" in url:
            try:
                url = f"https://youtube.com/watch?v={yt.search(url)[0]['videoId']}"
                
            except Exception:
                env = os.environ
                client = await ClientAsync(env.get("YANDEX_TOKEN")).init()
                func = (await client.search(url, nocorrect=False)).best
                artists = str(func.result.artists_name()).replace("'", '').replace("[", '').replace("]", '')
                logger.info(f"[yandex] Downloading {func.result.title}")
                # func.result.download(f"music.mp3")
                logger.info(f"[yandex] Downloaded...")
                logger.info(f"[yandex] Openning ....")
                
                try:
                    player = cls(disnake.FFmpegPCMAudio(await (await func.result.get_download_info_async())[0].get_direct_link_async(), **ffmpeg_options), data={'title': func.result.title, 'author': artists, 'source': "YandexMusic", 'fileName': f"{func.result.title}", 'type': "mp3", 'unicalID': f"https://music.yandex.ru/track/{func.result.id}", "icon": func.result.get_og_image_url()})
                except Exception:
                    player = cls(disnake.FFmpegPCMAudio(f"music.mp3", **ffmpeg_options), data={'title': func.result.title, 'author': artists, 'source': "YandexMusic", 'fileName': f"{func.result.title}", 'type': "mp3", 'unicalID': f"https://music.yandex.ru/track/{func.result.id}", "icon": func.result.get_og_image_url()})
                logger.info(f"[yandex] Playing {func.result.title}")
        if not player:
            loop = loop or asyncio.get_event_loop()
            data: Any = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(url, download=False)
            )
            filename = data["formats"][5]["url"] if stream else ytdl.prepare_filename(data)
            data["author"] = data["channel"]
            data["source"] = "YouTube"
            data["type"] = data["formats"][5]["audio_ext"]
            data["unicalID"] = url
            data["icon"] = data["thumbnails"][38]["url"]
            data["fileName"] = filename
            title = data.get("title")
            audio_type = data["type"]
            logger.info(f"[YouTube] Playing {title}")
            logger.info(f"[Youtube] Audio type {audio_type}")
            player = cls(disnake.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        return player
        

        

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = {"a": "a"}
        
    def __channel(self, inter) -> disnake.VoiceProtocol | None:
        for voiceProtocol in self.bot.voice_clients:
            if voiceProtocol.guild == inter.guild:
                return voiceProtocol
    # @tasks.loop()
    # async def on_Voice_state_loop(self):
    #     voice_state = self.bot.voice_clients
        
        
    @commands.slash_command()
    async def join(self, inter: disnake.ApplicationCommandInteraction, channel: Optional[disnake.VoiceChannel] = None):
        """Joins a voice channel"""
        channel = inter.author.voice.channel if not channel else channel 
        if self.__channel(inter): await self.__channel(inter).disconnect()
        await channel.connect()
        await inter.response.send_message(f"Подключился к каналу {channel.mention}", ephemeral=True)

    # @commands.slash_command()
    # async def queue(self, inter, *args): pass
    
    # @commands.slash_command(name="queue")
    # async def add_to_queue(self, inter: disnake.ApplicationCommandInteraction, prompt_to_queue: str):
    #     try:
    #             await inter.response.defer()
    #             player = await YTDLSource.from_url(prompt_to_queue, loop=self.bot.loop, stream=True)
    #             try:
    #                 if len(self.queue[inter.guild.id]) == 0:
    #                     if self.__channel(inter): await self.__channel(inter).disconnect()
    #                     self.start_playing(await self.ensure_voice(inter), player, inter.guild)
    #                     await inter.send(f':mag_right: **Searching for** ``' + prompt_to_queue + '``\n<:youtube:763374159567781890> **Now Playing:** ``{}'.format(player.title) + "``")
    #                 else:
    #                     self.queue[len(self.queue[inter.guild.id])] = player
    #                     await inter.send(f':mag_right: **Searching for** ``' + prompt_to_queue + '``\n<:youtube:763374159567781890> **Added to queue:** ``{}'.format(player.title) + "``")
    #             except KeyError:
    #                 self.queue[inter.guild.id] = []
    #                 if self.__channel(inter): await self.__channel(inter).disconnect()
    #                 self.start_playing(await self.ensure_voice(inter), player, inter.guild)
    #                 await inter.send(f':mag_right: **Searching for** ``' + prompt_to_queue + '``\n<:youtube:763374159567781890> **Now Playing:** ``{}'.format(player.title) + "``")


    #     except Exception as e:

    #         await inter.send(f"Somenthing went wrong - please try again later! ||{e}||")
    
    # def start_playing(self, voice_client, player, guild:disnake.Guild):
    #     self.queue[guild.id].append(player)

        
    #     for i in self.queue[guild.id]:
    #         try:
    #             voice_client.play(i, after=lambda e: print('Player error: %s' % e) if e else None)

    #         except:
    #             pass
            
        

    @commands.slash_command()
    async def play(self, inter: disnake.ApplicationCommandInteraction, prompt: str):
        """Plays from a url (almost anything youtube_dl supports)"""
        if self.__channel(inter): await self.__channel(inter).disconnect()
            
        voiceState: disnake.VoiceClient = await self.ensure_voice(inter)
        
        await inter.response.defer(with_message=True)
        player = await YTDLSource.from_url(prompt, loop=self.bot.loop, stream=True)
        embed = disnake.Embed(title="Вопроизведение музыки.", description=f"**Трек**: {player.title}\n **Автор**: {player.author}\n **Ссылка**: [Тык]({player.id})").set_footer(text=f"Источник: {player.source}").set_thumbnail(url=player.thumbnails)
        await inter.send(embed=embed)
        voiceState.play(
            player, after=lambda e: logger.error(f"Error: {e}") if e else None
        )

    @commands.slash_command()
    async def leave(self, inter: disnake.ApplicationCommandInteraction):
        """Stops and disconnects the bot from voice"""
        await self.__channel(inter).disconnect()
        await inter.response.send_message("Бот вышел из канала", ephemeral=True)
        
    @commands.slash_command()
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        """Paused music"""
        await self.ensure_voice(inter)
        await inter.response.send_message("Бот остановил воспроизведение", ephemeral=True)
        
    @commands.slash_command()
    async def pause(self, inter: disnake.ApplicationCommandInteraction):
        """Paused music"""
        await self.ensure_voice(inter, 'pause')
        await inter.response.send_message("Бот остановил воспроизведение", ephemeral=True)  
          
    @commands.slash_command()
    async def resume(self, inter: disnake.ApplicationCommandInteraction):
        """Paused music"""
        await self.ensure_voice(inter, 'resume')
        await inter.response.send_message("Бот продолжил воспроизведение воспроизведение", ephemeral=True)   
        
    
    async def ensure_voice(self, inter, types:str = None):
        if self.__channel(inter) == None:
            if inter.author.voice:
                return await inter.author.voice.channel.connect()
            else:
                await inter.send("You are not connected to a voice channel.", ephemeral=True)
                raise commands.CommandError("Author not connected to a voice channel.")
        elif types == "pause" and self.__channel(inter).is_playing():
            self.__channel(inter).pause()
        elif types == "resume" and not self.__channel(inter).is_playing():
            self.__channel(inter).resume()
        elif self.__channel(inter).is_playing():
            self.__channel(inter).stop()
        
        
            
            
def setup(bot):
    bot.add_cog(Music(bot))
