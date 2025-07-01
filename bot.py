import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True  # Required to track joins
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# Store invites in memory
guild_invites = {}
referral_counts = {}  # Optional: Track total invites per user

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    for guild in bot.guilds:
        invites = await guild.invites()
        guild_invites[guild.id] = {invite.code: invite.uses for invite in invites}

@bot.event
async def on_member_join(member):
    invites_before = guild_invites.get(member.guild.id, {})
    invites_after = await member.guild.invites()

    for invite in invites_after:
        before_uses = invites_before.get(invite.code, 0)
        after_uses = invite.uses or 0
        if after_uses > before_uses:
            inviter = invite.inviter
            # Track referral count (optional)
            if inviter.id in referral_counts:
                referral_counts[inviter.id] += 1
            else:
                referral_counts[inviter.id] = 1

            # Log who invited whom
            channel = discord.utils.get(member.guild.text_channels, name="test")
            if channel:
                await channel.send(
                    f"{member.name} joined using {inviter.name}'s invite link! 🎉 "
                    f"(Total invites: {referral_counts[inviter.id]})"
                )
            break

    # Update invites
    guild_invites[member.guild.id] = {invite.code: invite.uses for invite in invites_after}

@bot.command()
async def referral(ctx):
    invite = await ctx.channel.create_invite(unique=True, max_uses=0, max_age=0)
    await ctx.send(f"Here’s your personal invite link: {invite.url}")

bot.run(TOKEN)
