import discord
from discord.ext import commands
from discord.ui import Button, View
from flask import Flask
from threading import Thread
import os

# --- Render에서 24시간 유지를 위한 웹 서버 ---
app = Flask('')

@app.route('/')
def home():
    return "봇이 작동 중입니다!"

def run():
    # Render가 정해주는 포트를 사용합니다
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="티켓 열기", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        channel_name = f"티켓-{user.name}"
        
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"이미 열려있는 티켓이 있습니다: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        embed = discord.Embed(title="티켓이 생성되었습니다", description=f"{user.mention}님, 무엇을 도와드릴까요?\n관리자가 곧 확인하겠습니다.", color=discord.Color.blue())
        
        close_view = View()
        close_button = Button(label="티켓 닫기", style=discord.ButtonStyle.red)
        async def close_callback(interaction):
            await interaction.channel.delete()
        close_button.callback = close_callback
        close_view.add_item(close_button)
        
        await channel.send(embed=embed, view=close_view)
        await interaction.response.send_message(f"티켓이 생성되었습니다: {channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f'봇 로그인 성공: {bot.user.name}')
    bot.add_view(TicketView())

@bot.command()
async def 티켓생성(ctx):
    embed = discord.Embed(title="문의하기", description="아래 버튼을 눌러 티켓을 생성하세요.", color=discord.Color.green())
    await ctx.send(embed=embed, view=TicketView())

# 24시간 유지를 위한 서버 시작
keep_alive()

# 중요: Render의 Environment 메뉴에 설정한 DISCORD_TOKEN을 가져옵니다.
bot.run(os.environ.get('DISCORD_TOKEN'))

