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
def home(): return "봇이 온라인입니다!"
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
        await self.tree.sync()
        print("✅ 모든 슬래시 명령어 동기화 완료!")

bot = MyBot()

# --- 어디서든(디엠 포함) 쓸 수 있는 도배 명령어 ---
@bot.tree.command(
    name="도배", 
    description="원하는 문구를 반복해서 출력합니다."
)
# 유저 설치와 서버 설치 모두 허용
@app_commands.installs(guild=True, user=True)
# 서버, 봇디엠, 개인디엠 어디서든 사용 가능하게 설정
@app_commands.allowed_contexts(guild=True, dms=True, private_channels=True)
@app_commands.describe(문구="도배할 내용", 횟수="반복 횟수 (최대 1000회)")
async def slash_도배(interaction: discord.Interaction, 문구: str, 횟수: int):
    if 횟수 > 1000:
        await interaction.response.send_message("⚠️ 최대 1000번까지만 가능합니다!", ephemeral=True)
        return

    await interaction.response.send_message(f"🚀 '{문구}' 도배를 시작합니다!")
    
    for i in range(횟수 - 1):
        try:
            await interaction.followup.send(문구)
            await asyncio.sleep(0.3)
        except:
            break

# --- 어디서든 쓸 수 있는 청소 명령어 ---
@bot.tree.command(
    name="청소", 
    description="메시지를 삭제합니다. (서버 전용)"
)
@app_commands.installs(guild=True, user=True)
@app_commands.allowed_contexts(guild=True, dms=True, private_channels=True)
@app_commands.describe(수="삭제할 메시지 개수")
async def slash_청소(interaction: discord.Interaction, 수: int):
    if not interaction.guild:
        await interaction.response.send_message("⚠️ 서버에서만 사용할 수 있습니다.", ephemeral=True)
        return
        
    await interaction.response.send_message(f"🧹 {수}개의 메시지를 청소합니다.", ephemeral=True)
    try:
        await interaction.channel.purge(limit=수)
    except:
        await interaction.followup.send("⚠️ 권한이 없습니다.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'🤖 로그인 성공: {bot.user.name}')

keep_alive()
bot.run(os.environ.get('MTUyNTQwNDM5MDEwMDMwODA5OA.GE1KYA.2iAJS4xG8oDpuirI4wtZsUxk7W2rM52Qq2k3ss'))
