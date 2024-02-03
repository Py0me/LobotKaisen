import asyncio
import discord
from discord.ext import commands

@commands.command(name='help', description='bruh')
async def cmd_help(cntxt:discord.Context):
	cntxt.channel.send('lobotomy')
	