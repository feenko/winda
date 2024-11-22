from typing import List
import asyncio
import discord
from discord.ext import commands
import traceback
import os
import dotenv

dotenv.load_dotenv()

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("#"),
    intents=discord.Intents.all(),
    help_command=None,
    strip_after_prefix=True,
    # IDs of persons that are allowed to use the bot
    owner_ids=[
        1155452926970577008,
        555855189517664272,
        796382549273215087,
    ],
)


async def move_user_through_channels(
    user: discord.Member,
    channels: List[discord.VoiceChannel],
    max_iterations: int,
    delay: float = 0.25,
) -> int:
    iterations = 0
    for channel in channels:
        if iterations >= max_iterations:
            break
        try:
            await user.move_to(channel)
            iterations += 1
            await asyncio.sleep(delay)
        except discord.HTTPException:
            continue
    return iterations


def shorten_text(text: str, max_length: int) -> str:
    if len(text) > max_length:
        return text[: max_length - 3] + "..."
    return text


@bot.command(aliases=["start"])
@commands.guild_only()
@commands.is_owner()
@commands.cooldown(1, 120, commands.BucketType.default)
async def winda(
    ctx: commands.Context,
    member: discord.Member,
    mode: str = "normal",
) -> None:
    silent = mode == "silent"
    if silent:
        await ctx.message.delete()

    if not member.voice:
        if not silent:
            await ctx.reply("Osoba nie jest na kanale głosowym")
        return

    original_channel = member.voice.channel
    if not original_channel:
        if not silent:
            await ctx.reply("Osoba nie jest na kanale głosowym")
        return

    if not silent:
        status_msg = await ctx.reply("Rozpoczynam przesuwanie...")

    try:
        voice_channels = sorted(
            ctx.guild.voice_channels,
            key=lambda x: x.position,
        )

        iterations = await move_user_through_channels(
            user=member, channels=voice_channels, max_iterations=9
        )

        try:
            await member.move_to(original_channel)
        except discord.HTTPException:
            return

        if not silent:
            await status_msg.edit(content=f"Gotowe! ({iterations} przesunięć)")

    except Exception as e:
        print(e)
        if not silent:
            await status_msg.edit(
                content=f"```py\n{shorten_text(traceback.format_exc(), 2000)}```",
            )


@winda.error
async def winda_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(
            f"Kolejna akcja jest dostępna za {error.retry_after:.2f} sekund"
        )


bot.run(os.getenv("TOKEN"))
