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
# 에러 방지를 위해 숫자로 직접 설정 (0: 서버 설치, 1: 유저 설치)
@bot.tree.command(
    name="도배", 
    description="원하는 문구를 반복해서 출력합니다.",
    integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install},
    contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
)
@app_commands.describe(문구="도배할 내용", 횟수="반복 횟수 (최대 10회)")
async def slash_도배(interaction: discord.Interaction, 문구: str, 횟수: int):
    if 횟수 > 10:
        await interaction.response.send_message("⚠️ 최대 10번까지만 가능합니다!", ephemeral=True)
        return

    await interaction.response.send_message(f"🚀 '{문구}' 도배를 시작합니다!")
    
    for i in range(횟수 - 1):
        try:
            await interaction.followup.send(문구)
            await asyncio.sleep(0.5)
        except:
            break

# --- 어디서든 쓸 수 있는 청소 명령어 ---
@bot.tree.command(
    name="청소", 
    description="메시지를 삭제합니다. (서버 전용)",
    integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install},
    contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
)
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
bot.run(os.environ.get('DISCORD_TOKEN'))

