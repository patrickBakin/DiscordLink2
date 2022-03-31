import discord

import requests

import asyncio
client=discord.Client()

ip="127.0.0.1"
port=2424
WebhookName="TestHook"
channel_id=719316097907556393
steam_api="013E39D266CAFAFF6347FD2C7AAC1D80"
bStatusConnected=False
webhook=None
GlobalReader=None
GlobalWriter=None
DefaultAvatar="https://s.isanook.com/mv/0/rp/rc/w850h510/yatxacm1w0/aHR0cHM6Ly9zLmlzYW5vb2suY29tL212LzAvdWQvMjEvMTA5MjI1LzEwOTIyNS10aHVtYm5haWwuanBn.jpg"


class ReceiveChat:
    def __init__(self,webhook,ip,port,steam_api):
        self.webhook=webhook
        self.ip=ip
        self.port=port
        self.steam_api=steam_api
        self.reader=None
        self.writer=None
    async def Connect(self):
        global bStatusConnected,GlobalReader,GlobalWriter
        while True:
            try:
                self.reader, self.writer = await asyncio.open_connection(f'{self.ip}', self.port)
                GlobalReader=self.reader
                GlobalWriter=self.writer

                break
            except Exception as e:
                print("retrying: ", e)
                await asyncio.sleep(1)
        bStatusConnected=True
        print("connected")
        await self.HandleMessage()
        #loop = asyncio.get_event_loop()
       # loop.run_until_complete(self.HandleMessage())


    async def HandleMessage(self):
        global bStatusConnected

        data = None
        while True:
            print(0)

            data = await self.reader.read(1024)
            if data==bytes():
                break
           # data = self.client.recv(1024)
            print(1)
            SteamID, username, content, AvatarURL = self.GetPlayerMessageInfo(data)
            print(2)
            print(SteamID, username, content, AvatarURL)
            if len(AvatarURL) == 0 or SteamID == 0:
                AvatarURL = DefaultAvatar
            # client.loop.create_task(self.webhook.send(content=content, username=username, avatar_url=AvatarURL, wait=False))
            await   self.webhook.send(content=content, username=username, avatar_url=AvatarURL, wait=True)

        print("Reconnecting...")
        bStatusConnected = False
        self.writer.close()
        await self.writer.wait_closed()
        while True:
            try:
                    await self.Connect()
                    break
            except Exception as E:
                    print(f"Error: {E}  retrying...")
                    await asyncio.sleep(1)
        return

    @staticmethod
    async def SendMessages(GW,webhook,Msg):
        if(bStatusConnected==False):
            await  webhook.send(content="Can not send a message while connection is not successfully being established", username="System", avatar_url=DefaultAvatar, wait=True)
            print("Can not send a message while connection is not successfully being established")
            return
        GW.write(Msg.encode('utf-8'))
        await GW.drain()

    def GetPlayerMessageInfo(self,data):
        Raw=self.decodedata(data.decode('utf-8'))
        print(Raw)
        Rawarr= Raw.split(':')
        SteamID=int(Rawarr[0],16)
        username=Rawarr[1]
        content=Rawarr[2]
        try:
            r = requests.get(url=f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.steam_api}&steamids={SteamID}")
        except Exception as E:
            print("Error: ", str(E))
        try:
            AvatarURL=r.json()['response']['players'][0]['avatar']
        except:
            AvatarURL=""
        return SteamID,username,content,AvatarURL


    @staticmethod
    def decodedata(string):
        numarray = string.split('/')
        Text = ""
        for numi in range(len(numarray)):
            Text = Text + chr(int(numarray[numi]))
        return Text


@client.event
async def on_ready():
        global webhook
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
        channel = client.get_channel(channel_id)
        webhooks = await channel.webhooks()
        foundwebhook=0
        webhooki=None
        for webhooki in webhooks:
            if (webhooki.name == WebhookName):
                foundwebhook=1
        if(foundwebhook>0):
            webhook=webhooki
        else:
                webhook = await channel.create_webhook(name=WebhookName)
        if(webhook!=None):
            await ReceiveChat(webhook, "127.0.0.1", 2424, steam_api).Connect()
          # ReceiveChatClass=ReceiveChat(webhook,"127.0.0.1",2424,steam_api)
          # thread= threading.Thread(target=ReceiveChatClass.Connect)
         #  thread.start()
           #ReceiveChat(webhook,"127.0.0.1",2424,steam_api).Connect()
        else:
            print("Error Webhook None")


        await webhook.send(content="Succesfully!", username="System", avatar_url=DefaultAvatar, wait=True)

@client.event
async def on_message(message):
        # we do not want the bot to reply to itself
        if message.author == client.user:
            return

        if message.content.startswith('$'):
           await ReceiveChat.SendMessages(GlobalWriter,webhook,message.content[1:])
        if message.content.startswith('@'):
            await message.channel.send('Pong!')


if __name__ == '__main__':

    client.run('NzE5MTY1OTIyNDcxODM3NzY3.XtzddQ.LuJMq6lNx6EQHXpO7IjBacGzAlw')

