import discord
from discord import app_commands
from youtube_search import YoutubeSearch
from flask import Flask
from threading import Thread
import os

# --- CẤU HÌNH WEB SERVER CHỐNG NGỦ ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render cấp Port ngẫu nhiên qua biến PORT, nếu không có thì dùng 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # Đảm bảo thread này tắt khi bot tắt
    t.start()

# --- CẤU HÌNH DISCORD BOT ---
class PhonkBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot Online: {self.user}")

client = PhonkBot()

# --- LỆNH /FIND ---
@client.tree.command(name="find", description="To search for songs and artist")
@app_commands.describe(query="Format: AUTHOR - SONG NAME")
@app_commands.checks.cooldown(1, 90.0)
async def find(interaction: discord.Interaction, query: str):
    if "-" not in query:
        embed_invalid = discord.Embed(
            title="Oops, something went wrong",
            description=f"Please select music by theme: Phonk/Funk.\nThe topic you got wrong: `{query}`",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed_invalid, ephemeral=True)
        return

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await interaction.response.send_message("❌ No results found!", ephemeral=True)
            return

        video = results[0]
        video_url = f"https://www.youtube.com/watch?v={video['id']}"

        embed_success = discord.Embed(
            title="🎵 Phonk/Funk Finder Result",
            description=f"**[{video['title']}]({video_url})**",
            color=discord.Color.dark_grey()
        )
        embed_success.set_image(url=video['thumbnails'][0])
        embed_success.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed_success)
    except:
        await interaction.response.send_message("An error occurred.", ephemeral=True)

# --- LỖI COOLDOWN (MÀU VÀNG) ---
@find.error
async def find_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed_cd = discord.Embed(
            title="Oops, something went wrong",
            description="Please wait 1 minute and 30 seconds before using this command.",
            color=discord.Color.from_rgb(255, 255, 0)
        )
        await interaction.response.send_message(embed=embed_cd, ephemeral=True)

# --- LỆNH /HELP ---
@client.tree.command(name="help", description="How to use the bot")
async def help(interaction: discord.Interaction):
    embed_help = discord.Embed(
        title="❓ How to use bot",
        description="😄 You can use the `/find` command, then click on the query and search for the song \"Phonk/Funk\".\n\n⚠️ **Note:** AUTHOR - SONG NAME\n❓ **Command:** `/find`",
        color=discord.Color.blue()
    )
    embed_help.add_field(name="Support", value="[Your Server Discord Support]")
    await interaction.response.send_message(embed=embed_help)

# --- CHẠY BOT ---
if __name__ == "__main__":
    keep_alive()
    # Khuyến khích dùng Environment Variable trên Render (Key: TOKEN)
    token = os.environ.get('TOKEN') or 'YOUR_BOT_TOKEN_HERE'
    client.run(token)
