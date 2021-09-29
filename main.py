from ssl import AlertDescription
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio

from youtube_dl import YoutubeDL

from collections import deque

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import bs4

import settingBot
from py import discordMusic


TOKEN = settingBot.TOKEN

bot = commands.Bot(command_prefix='~')
vc = None


YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


musicList = deque()


@bot.event
async def on_ready():
    print(f'{bot.user.name} ... connection was sucessful')
    await bot.change_presence(status=discord.Status.online, activity=None)


# 채널에 봇 불러내기
# pip install pynacl
@bot.command(name='on')
async def on(ctx):
    await ctx.send('Hello Wolrd~~!')

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()

    except Exception as e1:
        print(f'error 1\n{e1}')
        
        try:
            # 봇이 호출한 사람과 다른 채널에 있다면
            # 내가 있는 채널로 불러낸다.
            await vc.move_to(ctx.message.author.voice.channel)

        except Exception as e2:
            # 유저가 채널에 접속하지 않은 상태로
            # 봇을 부르면 메세지 호출
            await ctx.send('채널에 유저가 접속해있지 않습니다.\n먼저 봇을 불러낼 채널에 접속해주세요.')
            print(f'error 2\n{e2}')


# 봇 퇴장
@bot.command(name='off')
async def off(ctx):
    await vc.disconnect()

    
# URL 재생
@bot.command(name='pu')
async def youtubePlayURL(ctx, *, url):
    if not vc.is_playing():
        URL = discordMusic.playMusic(url)

        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)) # 오디오 소스 재생
        await ctx.send(embed = discord.Embed(title = '음악재생', description = f'play {url}', color=0x00ff00))


# 검색을 통한 유튜브 재생
# ~ps 산들 취기를 빌려 => msg = "산들 취기를 빌려"
@bot.command(name='ps')
async def youtubePlaySearch(ctx, *, msg):
    if not vc.is_playing():
        title, url = discordMusic.getMusicInfo(msg)

        music_now.appendleft(title)

        # 음악 재생
        URL = discordMusic.playMusic(url)
        
        await ctx.send(embed = discord.Embed(title='음악재생', description = music_now[0] + '을(를) 재생하고 있습니다.', color = 0x00ff00))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), alter=lambda e:play_next(ctx))
    
    else:
        await ctx.send('이미 음악이 재생 중입니다.')


# 검색 결과에 대해 리스트 출력하기
@bot.command(name='li')
async def youtubePlaySearch(ctx, *, msg):
    chromedriver_file = 'chromedriver.exe'
    driver = webdriver.Chrome(chromedriver_file)
        
    driver.get('https://www.youtube.com/results?search_query=' + msg)
    print(f'msg : {msg}')
    bs = bs4.BeautifulSoup(driver.page_source, 'lxml')

    titles = bs.find_all('a', {'id' : 'video-title'})

    for i in range(5):
        title = titles[i].text.strip()
        await ctx.send('%d. %s\n' %(i + 1, title))
    
    driver.quit()


# 일시정지
@bot.command(name='p')
async def youtubePause(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed = discord.Embed(title='일시정지', description = '음악을 중단합니다.\n다시 시작하려면 \"~rs\"를 입력해주세요.'))
    else:
        await ctx.send('음악 재생 중이 아닙니다.')


# 다시 시작
@bot.command(name='rs')
async def replay(ctx):
    try:
        vc.resume()
    except:
        await ctx.send('재생할 노래가 없어요.')
    else:
        await ctx.send(embed=discord.Embed(title='다시재생', description = '정지된 음악을 다시 재생합니다.'))


bot.run(TOKEN)