print("Loading....")
import asyncio
import logging
import configparser
import os
import discord
from discord.ext import commands
import aqualink
import datetime
from threading import Thread
import launchparser
import requests
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
        print("Login Complete: ")
        print("Name:"+str(client.user.name))
        print("ID:"+str(client.user.id))
        print("===========")
        aqualink.Connection(client)
        await client.aqualink.connect(password="youshallnotpass", ws_url="ws://localhost:2333", rest_url="http://localhost:2333")
        await client.change_presence(activity=discord.Game(name="Servicing "+str(len(client.guilds))+" Servers"))
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
                    log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "]: " + str(message.content) + " File Saved Filename:"+ str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second) + "-" + message.attachments[0].filename)
            else:
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "]: " + str(message.content))#메세지 로깅
        except:
            pass
        if message.author.bot: #봇에게는 명령전달 하지 않음
                return
        try:
            if server.id in cleverlist and message.content.startswith("!"):
                if message.author.id in cleverlist[server.id]:
                    if message.content.startswith("!quit"):
                        await channel.send("Shutting Down Cleverbot mode")
                        del cleverlist[server.id][cleverlist[server.id].index(message.author.id)]
                    else:
                        async with channel.typing():
                            answer=bot.ask(str(message.content)[1:])
                            await channel.send(answer)
                    return
            if message.content.startswith('!dice'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Dice Command.")
                await channel.send('Dice Rolls....')
                await channel.send('Dice Says ' + str(random.randrange(1,6)) + '!')
            if message.content.startswith('!weather'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Wather Command")
                if server.id not in region:
                    region[server.id]={}
                if message.author.id not in region[server.id]:
                    await channel.send("Require User Info.")
                    await channel.send("Please Enter Current Living City in English.")
                    try:
                        regiondata = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("You need to enter in 15 seconds. Retry:!weather")
                        return
                    regiondata = str(regiondata.content).title()
                    region[server.id][message.author.id]=regiondata
                    await channel.send("Inatilization Complete.")
                    del regiondata
                    return
                obs = owm.weather_at_place(region[server.id][message.author.id])
                w = obs.get_weather()
                temp=w.get_temperature(unit='celsius')
                await channel.send(region[server.id][message.author.id]+"'s Weather it's " + w.get_status() + "and current temperture it's " + str(temp['temp']) + '.') #Show Status
            if message.content.startswith('!time'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used time command.")
                await channel.send("Current date it's " + str(dt.year) + "Year " + str(dt.month) + "Month " + str(dt.day) + "Day. and Current time it's " + str(dt.hour) + "Hour " + str(dt.minute) + "Miniute " + str(dt.second) + "Seconds.")
            if message.content.startswith('!info'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Info Command.")
                if message.author.guild_permissions.administrator:
                    meg="Administrator"
                else:
                    meg="Normal"
                userdata=client.get_user(message.author.id)
                embed=discord.Embed(description="User:"+message.author.name+"\nID:"+str(message.author.id)+"\nPermission:"+meg+"\nRegisteration Date:"+str(message.author.joined_at)+"\nDiscord Registration date:"+str(userdata.created_at)+"\nAvatar Url:"+str(userdata.avatar_url))
                embed.set_thumbnail(url=userdata.avatar_url)
                await channel.send(embed=embed)
            if message.content.startswith("!coin"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Coin Command.")
                bitdata = requests.get('https://api.bithumb.com/public/ticker/all').json()
                await channel.send("Please Enter Coin name!")
                try:
                    coin = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("You need to enter in 15 seconds. Retry:!coin")
                    return
                coin = str(coin.content).upper()
                await channel.send(embed=discord.Embed(description=coin +"\nPrice: "+bitdata['data'][coin]['closing_price']+" Won\n"+" Change: "+bitdata['data'][coin]['24H_fluctate']+" Won " + bitdata['data'][coin]['24H_fluctate_rate'] + " %"))
            if message.content.startswith("!join"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Join Command.")

                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("Only Administrator Can Join bots on servers")
                    return
                if message.author.voice is None:
                    await channel.send("ERROR: Use on Audio Channels")
                    return
                voicechannel = message.author.voice.channel
                if server.id in voiceclis:
                    return
                else:
                    voiceclis[server.id] = client.aqualink.get_player(server.id) # get the player object
                    await voiceclis[server.id].connect(voicechannel.id) # connect to the author's VC
                    del voicechannel
            if message.content.startswith("!exit"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Exit Command.")
                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("Only Administrator can make Bot quit from audio channels")
                    return
                if server.id in voiceclis:
                    await voiceclis[server.id].disconnect()
                    del voiceclis[server.id]
            if message.content.startswith("!play"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Play Command.")

                if server.id in voiceclis:
                    pass
                else:
                    await channel.send("ERROR: Bot Didn't Join Audio Channels")
                    return
                if server.id not in requester:
                    requester[server.id] = {}
                await channel.send("Enter Youtube Play ID or title")
                try:
                    videoid[server.id] = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("You need to enter in 15 seconds. Retry:!play")
                    return
                videoid[server.id] = str(videoid[server.id].content)
                tempid = check_output(["youtube-dl",'--get-id',"--default-search","ytsearch","--",videoid[server.id]])
                tempid = tempid.decode('cp949').replace('\n','')
                if voiceclis[server.id]._playing == True:
                    if voiceclis[server.id] is not None:
                        if server.id in queues:
                            queues[server.id].append(tempid)
                            requester[server.id][videoid[server.id]] = message.author.id
                        else:
                            queues[server.id] = []
                            queues[server.id].append(tempid)
                            requester[server.id][videoid[server.id]] = message.author.id
                        await channel.send("We have added Your Song to Line Number:"+str(queues[server.id].index(tempid) + 1))
                else:
                    tracks = await voiceclis[server.id].query(tempid)
                    title[server.id] = tracks[0].title
                    await voiceclis[server.id].play(tracks[0])
                    requester[server.id][videoid[server.id]] = message.author.id
                    if server.id in volumes:
                        voiceclis[server.id].volume=volumes[server.id]
                    await channel.send("Playing "+'[' + title[server.id] + ']')
                    voiceclis[server.id].track_callback = check_queue
            if message.content.startswith("!song"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] used Song Command.")
                if server.id in title:
                    player = client.aqualink.get_player(server.id)
                    track = player.track
                    em = discord.Embed(title="Song Information")
                    em.add_field(name="Title", value=track.title)
                    em.add_field(name="Author", value=track.author)
                    em.add_field(name="Length", value=str(datetime.timedelta(milliseconds=track.length)))
                    em.add_field(name="Posistion", value=str(datetime.timedelta(milliseconds=track.position)))
                    em.add_field(name="Volume", value=f"{player.volume}%")
                    em.set_thumbnail(url=track.thumbnail)
                    await channel.send(embed=em)
                else:
                    await channel.send("Currently Playing Nothing.")
            if message.content.startswith("!pause"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Pause Command.")
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("Only Administrator Or Requester Can pause Music.")
                    return
                await voiceclis[server.id].set_pause(True)
            if message.content.startswith("!stop"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Stop command.")
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("Only Administrator Or Requester Can stop Music.")
                    return
                await voiceclis[server.id].stop()
                del title[server.id]
            if message.content.startswith("!resume"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Resume command.")
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("Only Administrator Or Requester Can resume Music.")
                    return
                voiceclis[server.id].set_pause(False)
            if message.content.startswith("!log"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Log command.")
                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("Only Administrator can See the log.")
                    return
                await channel.send("Current Log:", file=discord.File(str(logfile)))
            if message.content.startswith("!volume"):
                if message.author.guild_permissions.administrator or message.author.id == requester[server.id][videoid[server.id]]:
                    pass
                else:
                    await channel.send("Only Administrator Or Requester Can change the volume.")
                    return
                await channel.send("Please Enter Volume(1~100)")
                try:
                    volume = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("You need to enter in 15 seconds. Retry:!volume")
                    return
                if int(str(volume.content)) < 0 or int(str(volume.content)) > 100:
                    await channel.send("Incorrect Value! Retry:!volume")
                    return
                volume = int(str(volume.content))
                if message.author.guild_permissions.administrator:
                    volumes[server.id]=volume
                try:
                    await voiceclis[server.id].set_volume(volume)
                except:
                    pass
                del volume
            if message.content.startswith("!inatilize"):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used Inatilize command.")
                await channel.send("Inatilize User Data? (Y/N)")
                try:
                    answer = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("You need to enter in 15 seconds. Retry:!inatilize")
                    return
                answer = str(answer.content).upper()
                if answer == "Y" or answer == "N":
                    pass
                else:
                    await channel.send("Incorrect Value! Retry: !inatilize")
                    return
                if answer == "Y":
                    if server.id in region:
                        if message.author.id in region[server.id]:
                            del region[server.id][message.author.id]
                    await channel.send("User Data Has Been Inatilized.")
                if message.author.guild_permissions.administrator:
                    await channel.send("Inatilize Server Data? (Y/N)")
                    try:
                        answer = await client.wait_for('message', timeout=15.0, check=pred)
                    except:
                        await channel.send("You need to enter in 15 seconds. Retry:!inatilize")
                        return
                    answer=str(answer.content).upper()
                    if answer == "Y" or answer == "N":
                        pass
                    else:
                        await channel.send("Incorrect Value! Retry: !inatilize")
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
                        await channel.send("Server Data Has been Inatilized.")
            if message.content.startswith('!chatclean'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used chatclean command.")
                if message.author.guild_permissions.administrator:
                    pass
                else:
                    await channel.send("It's Administrator only Command.")
                    return
                await channel.send("Clean Chat history? (Y/N)")
                try:
                    answer = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("You need to enter in 15 seconds. Retry:!chatclean")
                    return
                answer=str(answer.content).upper()
                if answer == "Y" or answer == "N":
                    pass
                else:
                    await channel.send("Incorrect Value! Retry: !chatclean")
                    return
                if answer == "Y":
                    counter = 0
                    async for x in channel.history(limit=100):
                        if counter < 100:
                            await x.delete()
                            counter += 1
                    await channel.send("Chat Clean Complete.")
            if message.content.startswith('!privmessage'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used privmessage command.")
                await channel.send("Please Input target User ID")
                try:
                    answer = await client.wait_for('message', timeout=15.0, check=pred)
                except:
                    await channel.send("You need to enter in 15 seconds. Retry:!privmessage")
                    return
                userdata=client.get_user(int(str(answer.content)))
                await channel.send("Enter Content")
                answer = await client.wait_for('message', timeout=15.0, check=pred)
                if answer is None:
                    await channel.send("You need to enter in 15 seconds. Retry:!privmessage")
                    return
                await userdata.send("Message from Anonymous....\n"+str(answer.content))
                await channel.send("Sending Succseeded")
            if message.content.startswith('!cleverbot'):
                log.info(realtime + " " + message.author.name + " [ID:" + str(message.author.id) +  "] Used cleverbot command.")
                await channel.send("Changed to Cleverbot mode.")
                await channel.send("To Talk to me you must start with '!' Like this !Hello To exit cleverbot type !quit")
                if server.id not in cleverlist:
                    cleverlist[server.id]=[]
                cleverlist[server.id].append(message.author.id)
        except Exception as ex:
            await channel.send("Error Has been Ocurr. Error code: " + str(ex))
            log.error(realtime +  " Error Has been Ocurr. Error code: " + str(ex)) #오류코드 출력 및 기록
print("Function Definding Complete")
print("Starting Bot...")
client.run(token)
