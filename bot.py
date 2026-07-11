import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio

# --- 24시간 유지용 웹 서버 (Render용) ---
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
        # 유저 설치형 명령어는 글로벌 동기화가 필요합니다.
        await self.tree.sync()
        print("✅ 모든 슬래시 명령어 동기화 완료!")

bot = MyBot()

# --- 어디서든(디엠 포함) 쓸 수 있는 도배 명령어 ---
@bot.tree.command(
    name="도배", 
    description="원하는 문구를 반복해서 출력합니다.",
    # 유저 설치와 서버 설치 모두 허용
    integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install},
    # 서버, 봇디엠, 개인디엠 어디서든 사용 가능하게 설정
    contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
)
@app_commands.describe(문구="도배할 내용", 횟수="반복 횟수 (최대 10회)")
async def slash_도배(interaction: discord.Interaction, 문구: str, 횟수: int):
    if 횟수 > 10:
        await interaction.response.send_message("⚠️ 최대 10번까지만 가능합니다!", ephemeral=True)
        return

    # 첫 번째 메시지 전송
    await interaction.response.send_message(f"🚀 '{문구}' 도배를 시작합니다!")
    
    # 개인 디엠에서도 안정적으로 메시지를 보내기 위해 followup 사용
    for i in range(횟수 - 1):
        try:
            await interaction.followup.send(문구)
            await asyncio.sleep(0.5) # 너무 빠르면 차단될 수 있어 0.5초 간격 유지
        except Exception as e:
            print(f"메시지 전송 실패: {e}")
            break

# --- 어디서든 쓸 수 있는 청소 명령어 (서버 전용) ---
@bot.tree.command(
    name="청소", 
    description="메시지를 삭제합니다. (서버에서만 작동)",
    integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install},
    contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
)
@app_commands.describe(수="삭제할 메시지 개수")
async def slash_청소(interaction: discord.Interaction, 수: int):
    # 디스코드 정책상 개인 디엠 메시지는 봇이 지울 수 없습니다.
    if not interaction.guild:
        await interaction.response.send_message("⚠️ '청소' 기능은 서버(채널)에서만 사용할 수 있습니다.", ephemeral=True)
        return
        
    await interaction.response.send_message(f"🧹 {수}개의 메시지를 청소합니다.", ephemeral=True)
    try:
        await interaction.channel.purge(limit=수)
    except:
        await interaction.followup.send("⚠️ 권한이 부족하여 메시지를 삭제할 수 없습니다.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'🤖 로그인 성공: {bot.user.name}')
    # 상태 메시지 설정
    await bot.change_presence(activity=discord.Game(name="/도배 명령어를 입력하세요!"))

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))
