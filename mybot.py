Python 3.14.5 (tags/v3.14.5:5607950, May 10 2026, 10:43:50) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import discord
... from discord.ext import commands
... import sqlite3
... import random
... import os
... 
... # ========== 数据库初始化 ==========
... def init_db():
...     conn = sqlite3.connect('levels.db')
...     c = conn.cursor()
...     c.execute('''
...         CREATE TABLE IF NOT EXISTS user_levels (
...             user_id INTEGER,
...             guild_id INTEGER,
...             xp INTEGER DEFAULT 0,
...             level INTEGER DEFAULT 1,
...             PRIMARY KEY (user_id, guild_id)
...         )
...     ''')
...     conn.commit()
...     conn.close()
... 
... init_db()
... 
... # ========== 升级所需经验 ==========
... def get_xp_required(level):
...     return level * 100
... 
... # ========== 更新等级 ==========
... async def update_user_level(user, guild, xp_to_add):
...     conn = sqlite3.connect('levels.db')
...     c = conn.cursor()
...     
...     c.execute("SELECT xp, level FROM user_levels WHERE user_id = ? AND guild_id = ?", 
...               (user.id, guild.id))
...     result = c.fetchone()
...     
...     if result is None:
...         current_xp, current_level = 0, 1
...         c.execute("INSERT INTO user_levels (user_id, guild_id, xp, level) VALUES (?, ?, ?, ?)",
...                   (user.id, guild.id, current_xp, current_level))
...     else:
...         current_xp, current_level = result
...     
...     new_xp = current_xp + xp_to_add
    new_level = current_level
    
    while new_xp >= get_xp_required(new_level):
        new_xp -= get_xp_required(new_level)
        new_level += 1
        channel = guild.system_channel
        if channel:
            await channel.send(f"🎉 {user.mention} 升级到 {new_level} 级！")
    
    c.execute("UPDATE user_levels SET xp = ?, level = ? WHERE user_id = ? AND guild_id = ?",
              (new_xp, new_level, user.id, guild.id))
    conn.commit()
    conn.close()

# ========== 机器人配置 ==========
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ========== 上线事件 ==========
@bot.event
async def on_ready():
    print(f'✅ 机器人 {bot.user} 已上线！')

# ========== 监听消息 ==========
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    await update_user_level(message.author, message.guild, random.randint(1, 5))
    await bot.process_commands(message)

# ========== 查看等级 ==========
@bot.command()
async def rank(ctx):
    conn = sqlite3.connect('levels.db')
    c = conn.cursor()
    c.execute("SELECT xp, level FROM user_levels WHERE user_id = ? AND guild_id = ?",
              (ctx.author.id, ctx.guild.id))
    result = c.fetchone()
    conn.close()
    
    if result:
        xp, level = result
        await ctx.send(f"📊 {ctx.author.mention} 等级 {level} | 经验 {xp}/{get_xp_required(level)}")
    else:
        await ctx.send(f"📊 {ctx.author.mention} 还没开始聊天呢！")

# ========== 运行 ==========
