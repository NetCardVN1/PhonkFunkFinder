import discord
from discord import app_commands
from youtube_search import YoutubeSearch
from flask import Flask
from threading import Thread
import os

# --- CẤU HÌNH WEB SERVER (ĐỂ CHẠY 24/7 TRÊN RENDER) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CẤU HÌNH DISCORD BOT ---
class PhonkBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Đồng bộ lệnh Slash khi Bot khởi động
        await self.tree.sync()
        print(f"Logged in as {self.user} | Commands Synced")

client = PhonkBot()

# --- LỆNH /FIND ---
@client.tree.command(name="find", description="To search for songs and artist")
@app_commands.describe(query="Format: AUTHOR - SONG NAME (Ex: PERTO - SXYGX)")
@app_commands.checks.cooldown(1, 90.0) # Cooldown 1 lần mỗi 90 giây
async def find(interaction: discord.Interaction, query: str):
    
    # 1. Kiểm tra tính hợp lệ (Yêu cầu định dạng Author - Song)
    if "-" not in query:
        embed_invalid = discord.Embed(
            title="Oops, something went wrong",
            description=f"Please select music by theme: Phonk/Funk. The topic you got wrong: `{query}`",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed_invalid, ephemeral=True)
        return

    # 2. Tìm kiếm trên YouTube
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await interaction.response.send_message("❌ No results found for this song.", ephemeral=True)
            return

        video = results[0]
        video_url = f"https://www.youtube.com/watch?v={video['id']}"

        # 3. Trả về kết quả (Embed)
        embed_success = discord.Embed(
            title="🎵 Phonk/Funk Finder Result",
            description=f"**[{video['title']}]({video_url})**",
            color=discord.Color.dark_theme()
        )
        embed_success.set_image(url=video['thumbnails'][0])
        embed_success.add_field(name="👤 Artist/Channel", value=video['channel'], inline=True)
        embed_success.add_field(name="⏱️ Duration", value=video['duration'], inline=True)
        embed_success.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed_success)

    except Exception as e:
        await interaction.response.send_message("An error occurred during search.", ephemeral=True)

# --- XỬ LÝ LỖI COOLDOWN (MÀU VÀNG) ---
@find.error
async def find_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed_cd = discord.Embed(
            title="Oops, something went wrong",
            description=f"Please wait 1 minute and 30 seconds before using this command.",
            color=discord.Color.from_rgb(255, 255, 0) # Màu vàng
        )
        await interaction.response.send_message(embed=embed_cd, ephemeral=True)

# --- LỆNH /HELP ---
@client.tree.command(name="help", description="How to use the bot")
async def help(interaction: discord.Interaction):
    embed_help = discord.Embed(
        title="❓ How to use bot",
        description="😄 You can use the `/find` command, then click on the query and search for the song \"Phonk/Funk\".",
        color=discord.Color.blue()
    )
    embed_help.add_field(
        name="⚠️ Note",
        value="When writing down a song, you must also include the author (Example: PERTO - SXYGX)",
        inline=False
    )
    embed_help.add_field(
        name="❓ Explanation of the command",
        value="• `/find` : to search for songs and artist",
        inline=False
    )
    embed_help.add_field(
        name="Need help?",
        value="Join the [Support Server](https://discord.gg/your_link_here)",
        inline=False
    )
    await interaction.response.send_message(embed=embed_help)

# --- KHỞI CHẠY ---
if __name__ == "__main__":
    keep_alive() # Chạy Flask song song
    # Thay 'YOUR_BOT_TOKEN' bằng Token thực tế hoặc dùng biến môi trường
    client.run('YOUR_BOT_TOKEN')

