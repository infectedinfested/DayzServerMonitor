from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from CustomErrors import error

inviteUrl = "https://discord.com/oauth2/authorize?client_id=1164920132972335214&permissions=1634504013888&scope=bot"

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
GUILD_ID: Final[str] = os.getenv('GUILD_ID')

intents: Intents = Intents.default()
intents.message_content = True 
client: Client = Client(intents=intents)

async def send_message(channel: Message, user_message: str) -> None:
    try: 
        print(channel)
        await channel.send(user_message)
        # message.channel.send(user_message)
        
    except Exception as e:
        print("1"+str(error(e)))


class postAlert(Client):
    message = ""
    channelName = ""
    def __init__(self, *args, **kwargs):
        self.guild_id = kwargs.pop('guild_id')
        self.message = kwargs.pop('message')
        self.channelToPost = kwargs.pop('channelToPost')

        super().__init__(intents=Intents.default())

    async def on_ready(self):
        try:
            await self.wait_until_ready()
            guild = self.get_guild(int(self.guild_id))
            
            if self.channelToPost.isdigit():
                channel = guild.get_channel(int(self.channelToPost))
            else:
                channel_array = guild.text_channels
                channel_id = []  
                for channel_info in channel_array:
                    if channel_info.name == self.channelToPost:
                        channel_id.append(channel_info.id)
                if not len(channel_id) == 1:
                    print("To many or no channels were found to post the message to")
                    raise CustomError("To many or no channels were found to post the message to")
                    #return error("ToManyChannels","To many or no channels were found to post the message to")
                channel = guild.get_channel(channel_id[0]) 
            
            
            await channel.send(self.message)
            await self.close()
        except Exception as e:
            await self.close()
            print(e)
            return error(e)

async def post_alert(channelToPost, message):
    client = postAlert(channelToPost = channelToPost,message = message,guild_id=GUILD_ID)
    await client.start(TOKEN)


