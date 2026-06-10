```python
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

music_started = False

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

    global music_started

    try:

        if not vc:
            return

        if vc.is_playing():
            return

        if music_started:
            return

        source = discord.FFmpegPCMAudio(
            source=MUSIC_FILE,
            executable="ffmpeg",
            options="-stream_loop -1"
        )

        vc.play(
            source,
            after=lambda e:
            print("Audio ended:", e)
        )

        music_started = True

        print("Music started")

    except Exception as e:

        print("Music error:", e)


# ======================
# READY
# ======================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"Logged in as {bot.user}")


# ======================
# JOIN
# ======================

@bot.tree.command(
    name="join",
    description="Join voice channel"
)
async def join(
    interaction: discord.Interaction
):

    await interaction.response.defer()

    try:

        if not is_owner(
            interaction.user.id
        ):

            await interaction.followup.send(
                "❌ Owner only."
            )
            return

        if not interaction.user.voice:

            await interaction.followup.send(
                "❌ Join a VC first."
            )
            return

        channel = (
            interaction.user.voice.channel
        )

        vc = (
            interaction.guild.voice_client
        )

        if vc:

            await vc.move_to(
                channel
            )

        else:

            await channel.connect()

        await interaction.followup.send(
            f"✅ Joined {channel.name}"
        )

    except Exception as e:

        print(e)

        await interaction.followup.send(
            f"❌ {e}"
        )


# ======================
# LEAVE
# ======================

@bot.tree.command(
    name="leave",
    description="Leave VC"
)
async def leave(
    interaction: discord.Interaction
):

    global music_started

    await interaction.response.defer()

    try:

        if not is_owner(
            interaction.user.id
        ):

            await interaction.followup.send(
                "❌ Owner only."
            )
            return

        vc = (
            interaction.guild.voice_client
        )

        if not vc:

            await interaction.followup.send(
                "❌ Not connected."
            )
            return

        music_started = False

        if vc.is_playing():
            vc.stop()

        await vc.disconnect(
            force=True
        )

        await interaction.followup.send(
            "✅ Left voice channel"
        )

    except Exception as e:

        print(e)

        await interaction.followup.send(
            "❌ Failed."
        )


# ======================
# AUTO MUSIC
# ======================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if member.bot:
        return

    vc = (
        member.guild.voice_client
    )

    if not vc:
        return

    if (
        after.channel
        and
        vc.channel
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

        if len(humans) > 0:

            play_music(vc)


# ======================
# START
# ======================

bot.run(TOKEN)
```
