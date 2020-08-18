import os
import json
import asyncio
import discord
import pymongo
from settings import *
from seed import seeder
from logger import logger
from discord.ext import commands, tasks
from datetime import datetime, timedelta

bot = commands.Bot(command_prefix='!')
client = pymongo.MongoClient("mongodb://{}:{}@{}:{}".format(
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT
))
db = client[DB_NAME]
s_col = db['school']
u_col = db['no_role_user']

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
    members = await guild.fetch_members(limit=None).flatten()
 
    CheckRole.start()
    
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

@tasks.loop(hours=4)
async def CheckRole():
    global members

    no_role_user = list()
    
    for member in members:
        have_school = False
        
        for role in member.roles:
            if s_col.count_documents({'idx': role.id}):
                have_school = True

                continue

        if not have_school and not member.bot:
            no_role_user.append(member) 
    
    for member in no_role_user:
        if member.name == '你想喵喵喵嗎?':
            user = u_col.find_one({'idx': member.id})
            times = 0 if not user else user['times']

            if not times:
                u_col.insert_one({'idx': member.id, 'times': 1})
            elif times < 5:
                u_col.update_one({'idx': member.id}, {'$inc': {'times': 1}})
            else:
                u_col.delete_one({'idx': member.id})
                
                await scistLog('{} has been kicked cause not choose role in 5 days'.format(member.name))
                await member.send('你因為超過五天沒登記身分組\n\n' 
                                    '所以被移出 server 且無法再使用 scist bot 所提供的功能了\n\n' \
                                    '如想要重新進入伺服器請聯繫 SCIST 粉專謝謝!') 
                await guild.kick(member)

                continue

            await scistLog('{} has already not choose for {} days'.format(member.name, times+1))
            await member.send('你已經 {} 天沒有登記身分組了\n\n在 {} 天就會被移出 server\n\n請盡快登記!'.format(times, 5-times))
    
    members = await guild.fetch_members(limit=None).flatten()

@CheckRole.before_loop
async def BeforeCheckRole():
    await bot.wait_until_ready()

    now = datetime.now()
    fut = now.replace(year=now.year, month=now.month, day=now.day, hour=CHECK_HOUR, minute=CHECK_MIN, second=0)
    
    if now.hour >= fut.hour and now.minute > fut.minute:
        fut = fut + timedelta(days=1)

    await asyncio.sleep((fut-now).total_seconds())

if __name__ == '__main__':
    bot.run(BOT_TOKEN)
