import os
import sys
import json
import re
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import asyncio
import asyncpg

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found!")
else:
    with open("config.json", encoding="utf-8") as file:
        config = json.load(file)

API_KEY = os.environ["API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

bot = AsyncTeleBot(API_KEY, parse_mode="Markdown")


async def cid_check(cid):
    conn = await asyncpg.connect(DATABASE_URL)
    check = await conn.execute(
        '''SELECT 1
            FROM data
            WHERE chat = $1''', cid
    )
    if check == 'SELECT 0':
        await conn.execute(
        '''INSERT INTO data (chat)
            VALUES ($1)
        ''', cid
    )
    await conn.close()    
    

async def insert(cid, field, value):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        f"UPDATE data SET {field} = $1 WHERE chat = $2", value, cid
    )
    await conn.close()
    

async def insertarray(cid, field, value):
    conn = await asyncpg.connect(DATABASE_URL)
    res = await conn.fetch(
        f"SELECT {field} FROM data WHERE chat = $1", cid
    )
    print(res[0].get(field))
    if field == 'names':
        if res and res[0].get(field):
            res = res[0].get(field)
            res.append(value)
            
        else:
            res = [value]
    
    else:
        if res and res[0].get(field):
            res = res[0].get(field)
            res.append(int(value))
            
        else:
            res = [int(value)]
        
    print(res)
    await conn.execute(
        f"UPDATE data SET {field} = $1 WHERE chat = $2", res, cid
    )
    await conn.close()
    
    
    
    
    
    
# async def fuck(cid):
#     conn = await asyncpg.connect(DATABASE_URL)
#     await conn.execute(
#         '''UPDATE data array_append(lanjiao2, $2)
#             WHERE chat = $1
#         ''', cid, 50000
#     )
#     await conn.close()

    


    
############# MARKUPS LMAO ########################
markupSTART = types.ReplyKeyboardMarkup(row_width=2)
btn1 = types.KeyboardButton('New Request')
btn2 = types.KeyboardButton('Kekg')
markupSTART.add(btn1, btn2)

markupADDING = types.ReplyKeyboardMarkup(row_width=3)
butt1 = types.KeyboardButton('Calculate!')
butt2 = types.KeyboardButton('Delete Prev. Entry')
butt3 = types.KeyboardButton('New Request')
markupADDING.add(butt1, butt2, butt3)

############ START MSG HANDLER ###################
@bot.message_handler(commands=['help', 'start'])
async def command_start(m):
    cid = m.chat.id
    print(cid)
    await cid_check(cid)
    await bot.send_message(cid, config["start_msg"], reply_markup = markupSTART)

########### NEW REQUEST MSG HANDLER ##############
@bot.message_handler(func=lambda message: message.text.lower() == 'new request')
async def command_new(m):
    cid = m.chat.id
    await cid_check(cid)
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        '''UPDATE data SET quantity = NULL, price = NULL, names = NULL, buyins = NULL, chiptotal = NULL WHERE
            chat = $1
        ''', cid
    )
    await conn.close()
    await bot.send_message(cid, "Input chips per buy-in in format 'buyin (int)' please")
    
########### CHIPS PER BUY-IN MSG HANDLER ############## 


@bot.message_handler(func=lambda message: len(message.text) > 6 and message.text[:6].lower() == 'buyin ')
async def command_buyin(m):
    cid = m.chat.id
    await cid_check(cid)
    try:
        int(m.text[6:].strip())
        await insert(cid, "quantity", int(m.text[6:].strip()))
        await bot.send_message(cid, "Input price of buy-in in format 'price (int)' please")
    
    except:
        await bot.send_message(cid, "Please use an integer for number of chips! Try again with 'buyin (int)'")
 
    

########### PRICE OF BUY-IN MSG HANDLER ##############
@bot.message_handler(func=lambda message: len(message.text) > 6 and message.text[:6].lower() == 'price ')
async def command_price(m):
    cid = m.chat.id
    await cid_check(cid)
    try:
        float(m.text[6:])
        await insert(cid, "price", float(m.text[6:]))
        await bot.send_message(cid, "Please enter player data in the format ''player' break (name) break (number of buyins) break (end chip total)' and press calculate when done\n\nExample:", reply_markup = markupADDING)
        await bot.send_message(cid, "player\nBobby\n2\n42069", reply_markup = markupADDING)
        
    
    except:
        await bot.send_message(cid, "Please insert a valid price! Try again with 'price (float)'")
        


############# PLAYER DATA ENTRY MSG HANDLER ###############
@bot.message_handler(func=lambda message: len(message.text) > 6 and 'player' in message.text.lower())
async def command_player(m):
    cid = m.chat.id
    await cid_check(cid)
    if m.text.count('\n') == 3:
        try:
            content = m.text.split('\n')      ##eg.['player', 'bobby', '2', '435']
            content = [e.strip() for e in content]
            print(content)
            if not bool(re.match('[a-zA-Z\s]+$', content[1])):
                raise Exception("kek")
            if await checkduplicate(cid, content[1]):
                raise Exception("duplicate name")
            content[2] = int(content[2])
            content[3] = int(content[3])
            await insertarray(cid, 'names', content[1]), await insertarray(cid, 'buyins', content[2]), await insertarray(cid, 'chiptotal', content[3])
            
        except:
            print('[command_player] rip')
        
            
        
async def checkduplicate(cid, name):
    conn = await asyncpg.connect(DATABASE_URL)
    res = await conn.fetch(
        f"SELECT names FROM data WHERE chat = $1", cid
    )
    print(res[0].get("names"))
    if res[0].get("names") and name in res[0].get("names"):
        await bot.send_message(cid, "Player name already exists!")
        return 1
    await conn.close()
    return 0
        
    
############# CALCULATION HANDLER ###############    
@bot.message_handler(func=lambda message: message.text.lower().strip() == 'calculate')
async def command_price(m):
    cid = m.chat.id
    
    
        
        
        
            
            

    
    
    
    

    

########### BOT POLLING #######################
asyncio.run(bot.infinity_polling())