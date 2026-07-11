import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio # 도배 간격을 위해 필요합니다

# --- 24시간 유지를 위한 웹 서버 ---
app = Flask('')
@app.route('/')
def home(): return "봇이 작동 중입니다!"
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    t = Thread(target=run)
    t.start()
# --------------------------------

intents = discord.Intents.default()
intents.message_content = True # 메시지 내용을 읽기 위해 꼭 필요!
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user.name}')

# !도배 [문구] [횟수] 명령어
# 예: !도배 안녕 5
@bot.command()
async def 도배(ctx, 문구: str, 횟수: int):
    # 너무 많이 하면 봇이 잘릴 수 있으니 10번으로 제한!
    if 횟수 > 10:
        await ctx.send("⚠️ 도배는 최대 10번까지만 가능합니다! (봇 정지 방지)")
        return

    await ctx.send(f"🚀 '{문구}' 문구를 {횟수}번 도배합니다!")
    
    for i in range(횟수):
        await ctx.send(문구)
        await asyncio.sleep(0.5) # 0.5초씩 쉬면서 안전하게 보냅니다

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))
