import os
import shutil
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ======================
# LOAD ENV
# ======================

load_dotenv()

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MUSIC_FILE = os.getenv("MUSIC_FILE", "music.mp3")

# ======================
# BOT
# ======================

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ======================
# OWNER CHECK
# ======================

def is_owner(user_id):
    return user_id == OWNER_ID

# ======================
# MUSIC
# ======================

def play_music(vc: discord.VoiceClient):
    try:

        if vc is None:
            return

        if not os.path.isfile(MUSIC_FILE):
            print(f"❌ Music file not found: {MUSIC_FILE}")
            return

        ffmpeg_path = shutil.which("ffmpeg")

        if ffmpeg_path is None:
            print("❌ FFmpeg not found.")
            return

        source = discord.FFmpegPCMAudio(
            source=MUSIC_FILE,
            executable=ffmpeg_path
        )

        vc.play(
            source,
            after=lambda e: print(
                f"Player Error: {e}"
            ) if e else None
        )

        print(f"🎵 Playing {MUSIC_FILE}")

    except Exception as e:
        print("Music Error:", e)

# ======================
# READY
# ======================

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print("Sync Error:", e)

    print(f"Logged in as {bot.user}")
    print(f"Music file exists: {os.path.exists(MUSIC_FILE)}")
    print(f"FFmpeg: {shutil.which('ffmpeg')}")

# ======================
# JOIN COMMAND
# ======================

@bot.tree.command(
    name="join",
    description="Join VC and start music"
)
async def join(interaction: discord.Interaction):

    await interaction.response.defer()

    try:

        if not is_owner(interaction.user.id):
            await interaction.followup.send(
                "❌ Owner only."
            )
            return

        if not interaction.user.voice:
            await interaction.followup.send(
                "❌ Join a VC first."
            )
            return

        channel = interaction.user.voice.channel

        vc = interaction.guild.voice_client

        if vc:

            if vc.channel != channel:
                await vc.move_to(channel)

        else:

            vc = await channel.connect()

        if vc.is_playing():
            vc.stop()

        play_music(vc)

        await interaction.followup.send(
            f"✅ Joined **{channel.name}**"
        )

    except Exception as e:

        print("Join Error:", e)

        await interaction.followup.send(
            f"❌ {e}"
        )

# ======================
# LEAVE COMMAND
# ======================

@bot.tree.command(
    name="leave",
    description="Leave VC"
)
async def leave(interaction: discord.Interaction):

    await interaction.response.defer()

    try:

        if not is_owner(interaction.user.id):
            await interaction.followup.send(
                "❌ Owner only."
            )
            return

        vc = interaction.guild.voice_client

        if vc is None:
            await interaction.followup.send(
                "❌ Not connected."
            )
            return

        if vc.is_playing():
            vc.stop()

        await vc.disconnect(force=True)

        await interaction.followup.send(
            "✅ Disconnected."
        )

    except Exception as e:

        print("Leave Error:", e)

        await interaction.followup.send(
            f"❌ {e}"
        )

# ======================
# RESTART MUSIC WHEN USER JOINS BOT VC
# ======================

@bot.event
async def on_voice_state_update(member, before, after):

    if member.bot:
        return

    vc = member.guild.voice_client

    if vc is None:
        return

    if vc.channel is None:
        return

    # User joined bot VC
    if (
        before.channel != vc.channel
        and after.channel == vc.channel
    ):

        print(f"{member} joined {vc.channel.name}")

        if vc.is_playing():
            vc.stop()

        play_music(vc)

# ======================
# RUN
# ======================

bot.run(TOKEN)
