import os
import json
import discord
import pymongo
from settings import *
from seed import seeder
from logger import logger
from datetime import datetime
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
client = pymongo.MongoClient("mongodb://{}:{}@{}:{}".format(
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT
))
db = client[DB_NAME]
s_col = db['school']

async def scistLog(message):
    logger.info(message)
    
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    message = '[{}] {}'.format(dt, message)
    channel = guild.get_channel(LOG_CH_ID)
    
    await channel.send(message)

@bot.event
async def on_ready():
    global guild
    global members

    seeder()

    guild = bot.get_guild(id=GUILD_ID)
    members = guild.fetch_members(limit=None)
    
    await scistLog('Logger in as {}'.format(bot.user.name))

@bot.event
async def on_member_join(member: discord.Member):
    message = '\n歡迎加入 SCIST !\n\n' \
            '請輸入 `!school 學校英文簡稱` ex. `!school tnfsh`\n\n' \
            '否則會每天收到提醒喔，超過五天沒有選擇身分組就會將你移出\n\n' \
            '如果沒有你所屬的學校的話請向管理員反應 !'
    
    await member.send(message)
    await scistLog('{} joined the server'.format(member.name))

@bot.command(description='choose your school role')
async def school(ctx, msg: str):
    school = msg.lower()
    author = ctx.message.author
    user_id, user_name = author.id, author.name
    member = guild.get_member(user_id)
    roles = member.roles
    have_school = False

    if not s_col.count_documents({'e_name': school}):
        await scistLog('{} try to add role with wrong school name'.format(member.name))
        await ctx.send('請重新確認你的學校簡寫是否正確!')
    else:
        for role in roles:
            if not have_school and s_col.count_documents({'idx': role.id}):
                have_school = True
            else: continue
        
        if have_school:
            await scistLog('{} add role fail, cause have role already'.format(member.name))
            await ctx.send('你已經有學校了喔!\n\n如果想要重新選擇學校請先使用 `!cschool` 取消現在的學校')
        else:
            _id = s_col.find_one({'e_name': school})['idx']
            role = guild.get_role(_id)
            
            await member.add_roles(role)
            await scistLog('{} added role {} success'.format(member.name, role.name))
            await ctx.send('{} 成功選擇 `{}` 身分\n\n歡迎加入 SCIST !'.format(member.name, role.name))

@bot.command(description='cancel school role')
async def cschool(ctx):
    user_id = ctx.message.author.id
    member = guild.get_member(user_id)
    roles = member.roles

    for role in roles:
        if s_col.count_documents({'idx': role.id}):
            role = guild.get_role(role.id)

            await member.remove_roles(role)
            await scistLog('{} remove self role {}'.format(member.name, role.name))
    
    await ctx.send('成功移除身分組!\n\n請記得在五天內重新選擇身分組否則會被移出 SCIST server 喔!')

if __name__ == '__main__':
    bot.run(BOT_TOKEN)
