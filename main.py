print("Loading....")
import asyncio
import logging
import configparser
import os
import discord
from discord.ext import commands
import datetime
from threading import Thread
import launchparser
import requests
import aqualink
import cleverbot_io
from bs4 import BeautifulSoup
import random
from pyowm import OWM
from subprocess import check_output
config = configparser.ConfigParser()
config.read('config-Tricker.ini')
bot=cleverbot_io.set(user=config['API']['CLEVERBOT_IO_USER'],key=config['API']['CLEVERBOT_IO_KEY'],nick='Tricker')
client = commands.Bot(command_prefix = '!')
players = {}
schoolcode = {}
cleverlist={}
region={}
dt=datetime.datetime.now()
API_key=config['API']['OPENWEATHERMAP_KEY']
owm=OWM(API_key)
if not(os.path.isdir("log")):
        os.makedirs(os.path.join("log"))
logfile=os.path.join('log',(str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second) + ".txt"))
log = logging.getLogger('snowdeer_log')
log.setLevel(logging.DEBUG)
chatfile=os.path.join('chats/chat-',(str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second) + ".txt"))
chatlog = logging.getLogger('snowdeer_log')
chatlog.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler(logfile, 'w', 'utf-8')
queues = {}
volumes = {}
videoid = {}
title = {}
voiceclis = {}
requester = {}
streamHandler = logging.StreamHandler()
log.addHandler(fileHandler)
log.addHandler(streamHandler)
token = config['API']['DISCORD_TOKEN']
print("Value Set Complete")
print("Definding Functions...")
@client.event
async def on_ready():
        print('로그인 완료됨:')
        print('이름:'+str(client.user.name))
        print('아이디:'+str(client.user.id))
        print("===========")
        aqualink.Connection(client)
        await client.aqualink.connect(password="youshallnotpass", ws_url="ws://localhost:2333", rest_url="http://localhost:2333")
        await client.change_presence(activity=discord.Game(name='서버' + str(len(client.guilds)) + '개 서비스중'))
async def check_queue(player):
    id=player.guild.id
    if id in queues:
        pass
    else:
        return
    if queues[id] == []:
        return
    videotitle=queues[id].pop(0)
    tracks = await voiceclis[id].query(videotitle)
    await voiceclis[id].play(tracks[0])
    title[id]=tracks[0].title
    if id in volumes:
        voiceclis[id].set_volume(volumes[id])
    voiceclis[id].track_callback = check_queue
@client.event
async def on_message(message):
        id = message.author.id
        server=message.guild
        channel = message.channel
        dt=datetime.datetime.now()
        realtime="%04d-%02d-%02d %02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) #실제로 사용할 포멧으로 정의
        def pred(m):
            return m.author == message.author and m.channel == message.channel
        try:
            if len(message.attachments) is not 0:
                if message.attachments[0].url is not "404":
                    await message.attachments[0].save(str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second) + "-" +message.attachments[0].filename)
                    log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "]: " + str(message.content) + " 파일 저장됨 파일명:"+ str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second) + "-" + message.attachments[0].filename)
            else:
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "]: " + str(message.content))#메세지 로깅
                chatlog.info(str(message.content))
        except:
            pass
        if message.author.bot: #봇에게는 명령전달 하지 않음
                return
        try:
            if server.id in cleverlist and message.content.startswith("!"):
                if message.author.id in cleverlist[server.id]:
                    if message.content.startswith("!종료"):
                        await channel.send("Cleverbot 모드를 종료합니다.")
                        del cleverlist[server.id][cleverlist[server.id].index(message.author.id)]
                    else:
                        async with channel.typing():
                            answer=bot.ask(str(message.content)[1:])
                            await channel.send(answer)
                    return
            realtime="%04d-%02d-%02d %02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            if message.content.startswith('!주사위'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 주사위 커맨드를 사용했습니다.")
                await channel.send('주사위의 값은....')
                await channel.send('바로 ' + str(random.randrange(1,6)) + ' 입니다!')
            if message.content.startswith('!날씨'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 날씨 커맨드를 사용했습니다.")
                if server.id not in region:
                    region[server.id]={}
                if message.author.id not in region[server.id]:
                    await channel.send("초기 설정이 필요합니다.")
                    await channel.send("거주하고 계신 도시의 이름을 영문으로 입력해주세요.")
                    try:
                        regiondata = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("15초내로 입력해주세요. 다시시도 : !날씨")
                        return
                    regiondata = str(regiondata.content).title()
                    region[server.id][message.author.id]=regiondata
                    await channel.send("초기 설정 완료.")
                    del regiondata
                    return
                obs = owm.weather_at_place(region[server.id][message.author.id])
                w = obs.get_weather()
                temp=w.get_temperature(unit='celsius')
                await channel.send(region[server.id][message.author.id]+"의 날씨는 " + w.get_status() + '이며 현재 기온은 ' + str(temp['temp']) + '입니다.') #Show Status
            if message.content.startswith('!현재시간') or message.content.startswith('!시간'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 현재시간 커맨드를 사용했습니다.")
                await channel.send("현재 날짜는 " + str(dt.year) + "년 " + str(dt.month) + "월 " + str(dt.day) + "일 입니다. 현재 시간은 " + str(dt.hour) + "시 " + str(dt.minute) + "분 " + str(dt.second) + "초 입니다.")
            if message.content.startswith('!정보'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 정보 커맨드를 사용했습니다.")
                if message.author.guild_permissions.administrator:
                    meg="관리자"
                else:
                    meg="일반"
                userdata=client.get_user(message.author.id)
                embed=discord.Embed(description="유저:"+message.author.name+"\nID:"+str(message.author.id)+"\n권한:"+meg+"\n가입일자:"+str(message.author.joined_at)+"\n디스코드 가입날짜:"+str(userdata.created_at)+"\n아바타 url:"+str(userdata.avatar_url)+"")
                embed.set_thumbnail(url=userdata.avatar_url)
                await channel.send(embed=embed)
            if message.content.startswith("!급식"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 급식 커맨드를 사용했습니다.")
                if server.id not in schoolcode:
                    schoolcode[server.id]={}
                if message.author.id not in schoolcode[server.id]:
                    await channel.send("초기설정이 필요합니다.")
                    await channel.send("고유코드를 입력하십시오.")
                    try:
                        tempid = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("15초내로 입력해주세요. 다시시도 : !급식")
                        return
                    tempid=str(tempid.content)
                    await channel.send("안내받으실 급식은? (1:아침,2:점심,3:저녁)")
                    try:
                        chooseneat = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("15초내로 입력해주세요. 다시시도 : !급식")
                        return
                    chooseneat = int(str(chooseneat.content))
                    if chooseneat >= 4 or chooseneat < 1:
                        await channel.send("알맞지 않은 값입니다. 다시시도 : !급식")
                        return
                    await channel.send("무슨 학교인지 입력해주세요 1:유치원 2:초등학교 3:중학교 4:고등학교")
                    try:
                        schoollevel = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("15초내로 입력해주세요. 다시시도 : !급식")
                        return
                    schoollevel = int(str(schoollevel.content))
                    if schoollevel >= 5 or schoollevel < 1:
                        await channel.send("알맞지 않은 값입니다. 다시시도 : !급식")
                        return
                    await channel.send("교육청 사이트의 주소를 입력하십시오. (지역마다 다릅니다. 예시(서울):http://stu.sen.go.kr/)")
                    try:
                        schoolwebsite = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("15초내로 입력해주세요. 다시시도 : !급식")
                        return
                    schoolwebsite=str(schoolwebsite.content)
                    schoollevel=str(schoollevel)
                    chooseneat=str(chooseneat)
                    schoolcode[server.id][message.author.id]=(tempid+chooseneat+schoollevel+schoolwebsite)
                    del tempid
                    del chooseneat
                    del schoollevel
                    await channel.send("초기설정이 완료되었습니다.")
                    return
                await channel.send("이번주의 급식입니다.")
                await channel.send(embed=discord.Embed(description="월요일\n"+launchparser.get_diet(int(schoolcode[server.id][message.author.id][10:11]), str(dt.year)+str(dt.month)+str(dt.day), 0, schoolcode[server.id][message.author.id][12:], schoolcode[server.id][message.author.id][0:10], int(schoolcode[server.id][message.author.id][11:12]))))
                await channel.send(embed=discord.Embed(description="화요일\n"+launchparser.get_diet(int(schoolcode[server.id][message.author.id][10:11]), str(dt.year)+str(dt.month)+str(dt.day), 1, schoolcode[server.id][message.author.id][12:], schoolcode[server.id][message.author.id][0:10], int(schoolcode[server.id][message.author.id][11:12]))))
                await channel.send(embed=discord.Embed(description="수요일\n"+launchparser.get_diet(int(schoolcode[server.id][message.author.id][10:11]), str(dt.year)+str(dt.month)+str(dt.day), 2, schoolcode[server.id][message.author.id][12:], schoolcode[server.id][message.author.id][0:10], int(schoolcode[server.id][message.author.id][11:12]))))
                await channel.send(embed=discord.Embed(description="목요일\n"+launchparser.get_diet(int(schoolcode[server.id][message.author.id][10:11]), str(dt.year)+str(dt.month)+str(dt.day), 3, schoolcode[server.id][message.author.id][12:], schoolcode[server.id][message.author.id][0:10], int(schoolcode[server.id][message.author.id][11:12]))))
                await channel.send(embed=discord.Embed(description="금요일\n"+launchparser.get_diet(int(schoolcode[server.id][message.author.id][10:11]), str(dt.year)+str(dt.month)+str(dt.day), 4, schoolcode[server.id][message.author.id][12:], schoolcode[server.id][message.author.id][0:10], int(schoolcode[server.id][message.author.id][11:12]))))
            if message.content.startswith("!코인"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 코인 커맨드를 사용했습니다.")
                bitdata = requests.get('https://api.bithumb.com/public/ticker/all').json()
                await channel.send("코인의 단위를 입력해주세요!")
                try:
                    coin = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("15초내로 입력해주세요. 다시시도 : !코인")
                    return
                coin = str(coin.content).upper()
                await channel.send(embed=discord.Embed(description=coin +"\n시세: "+bitdata['data'][coin]['closing_price']+" 원\n"+" 변동: "+bitdata['data'][coin]['24H_fluctate']+" 원 " + bitdata['data'][coin]['24H_fluctate_rate'] + " %"))
            if message.content.startswith("!참여"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 참여 커맨드를 사용했습니다.")

                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("관리자만이 봇을 음성방에 참여 시킬 수 있습니다.")
                    return
                if message.author.voice is None:
                    await channel.send("오류: 오디오 채널에서 사용하십시오.")
                    return
                voicechannel = message.author.voice.channel
                if server.id in voiceclis:
                    return
                else:
                    voiceclis[server.id] = client.aqualink.get_player(server.id) # get the player object
                    await voiceclis[server.id].connect(voicechannel.id) # connect to the author's VC
                    del voicechannel
            if message.content.startswith("!나가기"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 나가기 커맨드를 사용했습니다.")
                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("관리자만이 봇을 음성방에서 나가게 할 수 있습니다.")
                    return
                if server.id in voiceclis:
                    await voiceclis[server.id].disconnect()
                    del voiceclis[server.id]
            if message.content.startswith("!재생"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 재생 커맨드를 사용했습니다.")

                if server.id in voiceclis:
                    pass
                else:
                    await channel.send("오류:오디오 채널에 참여하지 않았습니다.")
                    return
                if server.id not in requester:
                    requester[server.id] = {}
                await channel.send("유튜브 재생 ID또는 제목을 입력해주세요!")
                try:
                    videoid[server.id] = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("15초내로 입력해주세요. 다시시도 : !재생")
                    return
                videoid[server.id] = str(videoid[server.id].content)
                tempid = check_output(["youtube-dl",'--get-id',"--default-search","ytsearch","--",videoid[server.id]])
                tempid = tempid.decode('cp949').strip()
                if voiceclis[server.id]._playing == True:
                    if voiceclis[server.id] is not None:
                        if server.id in queues:
                            queues[server.id].append(tempid)
                            requester[server.id][videoid[server.id]] = message.author.id
                        else:
                            queues[server.id] = []
                            queues[server.id].append(tempid)
                            requester[server.id][videoid[server.id]] = message.author.id
                        await channel.send("다른 곡이 재생중이기에 " +str(queues[server.id].index(tempid) + 1)+"번 대기열에 지정되었습니다.")
                else:
                    tracks = await voiceclis[server.id].query(tempid)
                    title[server.id]=tracks[0].title
                    await voiceclis[server.id].play(tracks[0])
                    requester[server.id][videoid[server.id]] = message.author.id
                    if server.id in volumes:
                        voiceclis[server.id].volume=volumes[server.id]
                    await channel.send('[' + title[server.id] + ']' + "음악을 재생합니다.")
                    voiceclis[server.id].track_callback = check_queue
            if message.content.startswith("!현재곡"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 현재곡 커맨드를 사용했습니다.")
                if server.id in title:
                    player = client.aqualink.get_player(server.id)
                    track = player.track
                    em = discord.Embed(title="곡 정보")
                    em.add_field(name="곡", value=track.title)
                    em.add_field(name="작사", value=track.author)
                    em.add_field(name="길이", value=str(datetime.timedelta(milliseconds=track.length)))
                    em.add_field(name="위치", value=str(datetime.timedelta(milliseconds=track.position)))
                    em.add_field(name="볼륨", value=f"{player.volume}%")
                    em.set_thumbnail(url=track.thumbnail)
                    await channel.send(embed=em)
                else:
                    await channel.send("현재 아무 곡도 재생하지 않고 있습니다.")
            if message.content.startswith("!일시정지"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 일시정지 커맨드를 사용했습니다.")
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("관리자 또는 영상 요청자 만이 영상을 일시정지 할 수 있습니다.")
                    return
                await voiceclis[server.id].set_pause(True)
            if message.content.startswith("!정지"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 정지 커맨드를 사용했습니다.")
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("관리자 또는 영상 요청자 만이 영상을 정지 할 수 있습니다.")
                    return
                await voiceclis[server.id].stop()
                del title[server.id]
            if message.content.startswith("!재계"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 재계 커맨드를 사용했습니다.")
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("관리자만 또는 영상 요청자 만이 영상을 재계 할 수 있습니다.")
                    return
                voiceclis[server.id].set_pause(False)
            if message.content.startswith("!로그"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 로그 커맨드를 사용했습니다.")
                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("관리자자 만이 로그를 열람 할 수 있습니다.")
                    return
                await channel.send("현재까지 기록된 로그입니다.", file=discord.File(str(logfile)))
            if message.content.startswith("!볼륨"):
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("관리자 또는 영상 요청자 만이 볼륨을 변경할 수 있습니다.")
                    return
                await channel.send("볼륨을 입력해주세요(1~100)")
                try:
                    volume = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("15초내로 입력해주세요. 다시\시도 : !볼륨")
                    return
                if int(str(volume.content)) < 0 or int(str(volume.content)) > 100:
                    await channel.send("알맞지 않은 값입니다 다시시도: !볼륨")
                    return
                volume = int(str(volume.content))
                if message.author.guild_permissions.administrator:
                    volumes[server.id]=volume
                try:
                    await voiceclis[server.id].set_volume(volume)
                    #볼륨설정 시도
                except:
                    pass
                del volume
            if message.content.startswith("!초기화"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 초기화 커맨드를 사용했습니다.")
                await channel.send("유저 데이터를 초기화 하시겠습니까? (Y/N)")
                try:
                    answer = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("15초내로 입력해주세요. 다시시도 : !초기화")
                    return
                answer = str(answer.content).upper()
                if answer == "Y" or answer == "N":
                    pass
                else:
                    await channel.send("알맞지 않은 값입니다 다시시도: !초기화")
                    return
                if answer == "Y":
                    if server.id in schoolcode:
                        if message.author.id in schoolcode[server.id]:
                            del schoolcode[server.id][message.author.id]
                    if server.id in region:
                        if message.author.id in region[server.id]:
                            del region[server.id][message.author.id]
                    await channel.send("유저 데이터 초기화가 완료되었습니다.")
                if message.author.guild_permissions.administrator:
                    await channel.send("서버 데이터를 초기화 하시겠습니까? (Y/N)")
                    try:
                        answer = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("15초내로 입력해주세요. 다시시도 : !초기화")
                        return
                    answer=str(answer.content).upper()
                    if answer == "Y" or answer == "N":
                        pass
                    else:
                        await channel.send("알맞지 않은 값입니다 다시시도: !초기화")
                        return
                    if answer == "Y":
                        if server.id in queues:
                            del queues[server.id]
                        if server.id in volumes:
                            del volumes[server.id]
                        if server.id in players:
                            voiceclis[server.id].stop()
                            del voiceclis[server.id]
                        try:
                            if server.id in voiceclis:
                                await voiceclis[server.id].disconnect()
                                del voiceclis[server.id]
                        except:
                            pass
                        if server.id in requester:
                            del requester[server.id]
                        if server.id in title:
                            del title[server.id]
                        await channel.send("서버 데이터 초기화가 완료되었습니다.")
            if message.content.startswith('!채팅청소'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 채팅청소 커맨드를 사용했습니다.")
                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("관리자 전용 명령어 입니다.")
                    return
                await channel.send("채팅창을 청소하시겠습니까? (Y/N)")
                try:
                    answer = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("15초내로 입력해주세요. 다시시도 : !채팅청소")
                    return
                answer=str(answer.content).upper()
                if answer == "Y" or answer == "N":
                    pass
                else:
                    await channel.send("알맞지 않은 값입니다 다시시도: !채팅청소")
                    return
                if answer == "Y":
                    counter = 0
                    async for x in channel.history(limit=100):
                        if counter < 100:
                            await x.delete()
                            counter += 1
                    await channel.send("채팅청소가 완료되었습니다.")
            if message.content.startswith("!비밀메세지"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 비밀메세지 커맨드를 사용했습니다.")
                await channel.send("유저 ID를 입력해주세요")
                try:
                    answer = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("15초내로 입력해주세요. 다시시도 : !비밀메세지")
                    return
                userdata=client.get_user(int(str(answer.content)))
                await channel.send("내용을 입력해주세요")
                answer = await client.wait_for('message', timeout=15.0, check=pred)
                if answer is None:
                    await channel.send("15초내로 입력해주세요. 다시시도 : !비밀메세지")
                    return
                await userdata.send("익명으로부터의 메세지입니다....\n"+str(answer.content))
                await channel.send("전송에 성공하였습니다.")
            if message.content.startswith('!cleverbot'):
                #클레버봇 모드 전환(버그없음 수정금지.)
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] 님이 Cleverbot 커맨드를 사용했습니다.")
                await channel.send("Cleverbot 모드로 전환되었습니다.")
                await channel.send("말을 거실려면 !를 앞에 붙여주세요 예시:!안녕 또는 나가실려면 !종료 를 입력해주세요.")
                if server.id not in cleverlist:
                    cleverlist[server.id]=[]
                cleverlist[server.id].append(message.author.id)
        except Exception as ex:
            await channel.send("오류가 발생하였습니다. 오류코드: " + str(ex))
            log.error(realtime +  " 오류가 발생하였습니다. 오류코드: " + str(ex)) #오류코드 출력 및 기록
print("Function Definding Complete")
print("Starting Bot...")
client.run(token)
