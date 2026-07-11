import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio

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
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user.name}')

@bot.command()
async def 도배(ctx, 문구: str, 횟수: int):
    # 1. 사용자가 입력한 명령어(!도배 문구 횟수) 삭제
    try:
        await ctx.message.delete()
    except:
        pass # 봇에게 메시지 관리 권한이 없을 경우 대비

    if 횟수 > 10:
        msg = await ctx.send("⚠️ 도배는 최대 10번까지만 가능합니다! (봇 정지 방지)")
        await asyncio.sleep(3)
        await msg.delete()
        return

    # 2. 안내 메시지 보내고 잠시 후 삭제
    info_msg = await ctx.send(f"🚀 '{문구}' 문구를 {횟수}번 도배합니다!")
    await asyncio.sleep(2) # 2초 동안 보여줌
    await info_msg.delete() # 안내 메시지 삭제
    
    # 3. 진짜 도배 시작
    for i in range(횟수):
        await ctx.send(문구)
        await asyncio.sleep(0.5)

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))
