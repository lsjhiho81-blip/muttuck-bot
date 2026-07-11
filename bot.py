import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio

# --- 24시간 유지용 웹 서버 ---
app = Flask('')
@app.route('/')
def home(): return "봇이 작동 중입니다!"
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 이 부분이 핵심입니다! 모든 서버와 유저 설치형 명령어를 동기화합니다.
        await self.tree.sync()
        print("모든 명령어 동기화 완료!")

bot = MyBot()

# --- 어디서든 쓸 수 있는 도배 명령어 ---
@bot.tree.command(
    name="도배", 
    description="원하는 문구를 반복해서 출력합니다.",
    # 유저 설치(User Install)와 서버 설치(Guild Install) 둘 다 가능하게 설정
    integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install},
    # 서버, 디엠, 그룹디엠 어디서든 쓸 수 있게 설정
    contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
)
@app_commands.describe(문구="도배할 내용", 횟수="반복 횟수 (최대 100회)")
async def slash_도배(interaction: discord.Interaction, 문구: str, 횟수: int):
    if 횟수 > 100:
        await interaction.response.send_message("⚠️ 최대 100번까지만 가능합니다!", ephemeral=True)
        return

    # 첫 번째 메시지는 응답으로 보냅니다.
    await interaction.response.send_message(f"🚀 '{문구}' 도배를 시작합니다!")
    
    # 봇이 해당 서버에 초대되어 있지 않으면 추가 메시지를 보내지 못할 수 있습니다.
    # 하지만 디엠(DM)에서는 아주 잘 작동합니다!
    for i in range(횟수 - 1):
        try:
            await interaction.channel.send(문구)
            await asyncio.sleep(0.1)
        except:
            break

# --- 어디서든 쓸 수 있는 청소 명령어 ---
@bot.tree.command(
    name="청소", 
    description="메시지를 삭제합니다.",
    integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install},
    contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
)
@app_commands.describe(수="삭제할 메시지 개수")
async def slash_청소(interaction: discord.Interaction, 수: int):
    # 봇이 서버에 초대되어 있어야만 메시지를 지울 수 있습니다. (디스코드 보안 규칙)
    if not interaction.guild:
        await interaction.response.send_message("⚠️ 디엠에서는 청소 기능을 쓸 수 없습니다.", ephemeral=True)
        return
        
    await interaction.response.send_message(f"🧹 {수}개의 메시지를 청소합니다.", ephemeral=True)
    try:
        await interaction.channel.purge(limit=수)
    except:
        await interaction.followup.send("⚠️ 메시지 관리 권한이 없어서 삭제하지 못했습니다.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user.name}')

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))
