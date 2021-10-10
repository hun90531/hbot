# from ssl import AlertDescription
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio

from youtube_dl import YoutubeDL

from collections import deque

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import bs4

import random

import settingBot
from py import discordMusic, mongodb


TOKEN = settingBot.TOKEN

bot = commands.Bot(command_prefix='~')
vc = None


YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


musicList = deque() # [[title1, url1], [title2, url2] ... ]


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
            await ctx.send('채널에 유저가 접속해있지 않습니다.')
            await ctx.send('먼저 봇을 불러낼 채널에 접속해주세요.')
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
    else:
        await ctx.send('이미 음악이 재생 중입니다.')
        await ctx.send('~ps 검색어를 통해 음악을 예약하거나 모든 음악을 종료시킨 후 다시 시도해주세요.')


# 검색을 통한 유튜브 재생
# ~ps 산들 취기를 빌려 => msg = "산들 취기를 빌려"
@bot.command(name='ps')
async def youtubePlaySearch(ctx, *, msg):
    title, url = discordMusic.getMusicInfo(msg)
    musicList.append([title, url])

    def play_next(ctx):
        if len(musicList) > 0:
            play = musicList.popleft()

            # 음악 재생
            URL = discordMusic.playMusic(play[1])
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e:play_next(ctx))
            
    if not vc.is_playing():
        play = musicList.popleft()

        # 음악 재생
        URL = discordMusic.playMusic(play[1])
        
        await ctx.send(embed = discord.Embed(title='음악재생', description = play[0] + '을(를) 재생하고 있습니다.', color = 0x00ff00))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e:play_next(ctx))
    else:
        await ctx.send(embed = discord.Embed(title='음악예약', description = title + '이 예약되었습니다.', color = 0x00ff00))


# 예약 리스트 출력
@bot.command(name='li')
async def youtubePlaySearch(ctx):
    await ctx.send("음악 대기열입니다.\n")
    titleList = [music[0] for music in musicList]
    titleList = '\n'.join(titleList)
    await ctx.send(titleList)


# 예약 리스트 셔플
@bot.command(name='sh')
async def shuffle(ctx):
    random.shuffle(musicList)
    await ctx.send('예약 순서가 랜덤으로 바뀝니다.')


# 검색 결과에 대해 리스트 출력하기
@bot.command(name='sl')
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


# 아이디를 통해 플레이 리스트 저장, 삭제 목록보기
@bot.command(name='conn')
async def savePlayList(ctx, *, msg):
    user_id = ctx.author.id
    uset_nick = str(ctx.author).split('#')[0]

    if len(msg) > 0 and msg[0] == 's':
        msg = msg[1:]
        title, url = discordMusic.getMusicInfo(msg)
        
        res = mongodb.savePlayList(user_id, title, url, 'playlist') # res : 결과 메세지
        await ctx.send(embed = discord.Embed(title='Success', description = res, color = 0x00ff00))

    elif len(msg) > 0 and msg[0] == 'l':
        res = mongodb.showPlayList(user_id, 'playlist')

        if res:
            await ctx.send('%s님의 플리이리스트' % uset_nick)
            for i in range(len(res)):
                await ctx.send('%d. %s\n' %(i + 1, res[i][0]))
        else:
            await ctx.send(embed=discord.Embed(title='Fail', description = '아무 노래도 저장되어 있지 않습니다.'))    
        

    elif len(msg) > 0 and msg[0] == 'd':
        num = 0
        if len(msg) > 1:
            num = int(msg[2])
        
        res = mongodb.deletePlayList(user_id, num, 'playlist')
        await ctx.send(embed = discord.Embed(title='Success', description = res, color = 0x00ff00))

    else:
        res = '"conn s 노래 제목"\n"conn d (삭제 번호 or 전체 삭제 : -1)"\n"conn l"\n위와 같은 형식으로 입력해주세요.'
        await ctx.send(embed=discord.Embed(title='Fail', description = res))


bot.run(TOKEN)