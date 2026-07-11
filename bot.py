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
        await self.tree.sync()
        print("슬래시 명령어 동기화 완료!")

bot = MyBot()

# --- 공통 도배 함수 ---
async def perform_spam(channel, 문구, 횟수):
    for i in range(횟수):
        await channel.send(문구)
        await asyncio.sleep(0.5)

# --- 1. 도배 기능 (! / 둘 다 가능) ---
@bot.tree.command(name="도배", description="원하는 문구를 반복해서 출력합니다.")
@app_commands.describe(문구="도배할 내용", 횟수="반복 횟수 (최대 10회)")
async def slash_도배(interaction: discord.Interaction, 문구: str, 횟수: int):
    if 횟수 > 10:
        await interaction.response.send_message("⚠️ 최대 10번까지만 가능합니다!", ephemeral=True)
        return
    await interaction.response.send_message(f"🚀 '{문구}'를 {횟수}번 도배합니다!", ephemeral=True)
    await perform_spam(interaction.channel, 문구, 횟수)

@bot.command(name="도배")
async def prefix_도배(ctx, 문구: str, 횟수: int):
    try: await ctx.message.delete()
    except: pass
    if 횟수 > 10:
        msg = await ctx.send("⚠️ 최대 10번까지만 가능합니다!")
        await asyncio.sleep(3); await msg.delete(); return
    info_msg = await ctx.send(f"🚀 '{문구}'를 {횟수}번 도배합니다!")
    await asyncio.sleep(2); await info_msg.delete()
    await perform_spam(ctx.channel, 문구, 횟수)

# --- 2. 청소 기능 (! / 둘 다 가능) ---
@bot.tree.command(name="청소", description="메시지를 대량으로 삭제합니다.")
@app_commands.describe(수="삭제할 메시지 개수")
async def slash_청소(interaction: discord.Interaction, 수: int):
    if 수 > 100:
        await interaction.response.send_message("⚠️ 한 번에 최대 100개까지만 삭제 가능합니다!", ephemeral=True)
        return
    # 슬래시 명령어는 먼저 응답을 보내야 합니다.
    await interaction.response.send_message(f"🧹 {수}개의 메시지를 청소합니다.", ephemeral=True)
    await interaction.channel.purge(limit=수)

@bot.command(name="청소")
async def prefix_청소(ctx, 수: int):
    if 수 > 100:
        await ctx.send("⚠️ 한 번에 최대 100개까지만 삭제 가능합니다!"); return
    # 명령어 자체를 포함해서 삭제하기 위해 수 + 1
    await ctx.channel.purge(limit=수 + 1)
    msg = await ctx.send(f"✅ {수}개의 메시지를 삭제했습니다.")
    await asyncio.sleep(3); await msg.delete()

@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user.name}')

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))

