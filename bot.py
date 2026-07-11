import discord
from discord.ext import commands
from discord.ui import Button, View

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 티켓 생성 버튼 클래스
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None) # 버튼이 사라지지 않게 설정

    @discord.ui.button(label="티켓 열기", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # 티켓 채널 이름 설정
        channel_name = f"티켓-{user.name}"
        
        # 이미 티켓이 있는지 확인 (선택 사항)
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"이미 열려있는 티켓이 있습니다: {existing_channel.mention}", ephemeral=True)
            return

        # 티켓 채널 생성 (관리자와 생성자만 볼 수 있게 설정)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        
        # 티켓 채널에 메시지 보내기
        embed = discord.Embed(title="티켓이 생성되었습니다", description=f"{user.mention}님, 무엇을 도와드릴까요?\n관리자가 곧 확인하겠습니다.", color=discord.Color.blue())
        
        # 티켓 닫기 버튼 추가
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
    # 봇이 켜지면 버튼을 계속 감시하도록 설정
    bot.add_view(TicketView())

@bot.command()
async def 티켓생성(ctx):
    embed = discord.Embed(title="문의하기", description="아래 버튼을 눌러 티켓을 생성하세요.", color=discord.Color.green())
    await ctx.send(embed=embed, view=TicketView())

# 여기에 아까 복사한 토큰을 넣으세요
bot.run('MTUyNTQwNDM5MDEwMDMwODA5OA.Ge1Y7C.YgbsbALxvW9nUAtA9H7j6Sj82zU6QOm7SX86-0')
