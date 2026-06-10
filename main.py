import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

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
intents.voice_states = True
intents.guilds = True

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

def play_music(vc):

    if not vc:
        return

    if vc.is_playing():
        return

    source = discord.FFmpegPCMAudio(
        MUSIC_FILE,
        options="-stream_loop -1"
    )

    vc.play(source)


# ======================
# READY
# ======================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"Logged in as {bot.user}")


# ======================
# /JOIN
# ======================

@bot.tree.command(
    name="join",
    description="Join configured voice channel"
)
async def join(
    interaction: discord.Interaction
):

    if not is_owner(
        interaction.user.id
    ):

        await interaction.response.send_message(
            "❌ Owner only.",
            ephemeral=True
        )
        return

    if not interaction.user.voice:

        await interaction.response.send_message(
            "❌ Join a VC first.",
            ephemeral=True
        )
        return

    channel = (
        interaction.user.voice.channel
    )

    vc = (
        interaction.guild.voice_client
    )

    try:

        if vc:

            await vc.move_to(
                channel
            )

        else:

            vc = await channel.connect()

        await interaction.response.send_message(
            f"✅ Joined {channel.name}"
        )

    except Exception as e:

        await interaction.response.send_message(
            str(e),
            ephemeral=True
        )


# ======================
# /LEAVE
# ======================

@bot.tree.command(
    name="leave",
    description="Disconnect bot"
)
async def leave(
    interaction: discord.Interaction
):

    if not is_owner(
        interaction.user.id
    ):

        await interaction.response.send_message(
            "❌ Owner only.",
            ephemeral=True
        )
        return

    vc = (
        interaction.guild.voice_client
    )

    if not vc:

        await interaction.response.send_message(
            "❌ Not connected.",
            ephemeral=True
        )
        return

    vc.stop()

    await vc.disconnect()

    await interaction.response.send_message(
        "✅ Left voice channel"
    )


# ======================
# AUTO PLAY
# ======================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if member.bot:
        return

    vc = member.guild.voice_client

    if not vc:
        return

    if (
        after.channel
        and
        after.channel.id
        ==
        vc.channel.id
    ):

        humans = [
            m
            for m
            in vc.channel.members
            if not m.bot
        ]

        if humans:

            play_music(vc)


# ======================
# START
# ======================

bot.run(TOKEN)