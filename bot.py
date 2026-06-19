import asyncio
import os

# 🔴 ফিক্স: Pyrogram ইমপোর্ট করার আগেই Event Loop সেট করে দেওয়া হলো!
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web

# ==========================================
# ১. ক্রেডেনশিয়ালস এবং কনফিগারেশন
# ==========================================
API_ID = 38733071
API_HASH = "9e4cb9c28ffe9c07d77c05ebe02b2ca5"
BOT_TOKEN = "8802637285:AAGPayeuyhxBFEH8CzwqRVI1G768SBUqE60"
ADMIN_IDS = [8869219008, 8291108314, 8272050428]
MONGO_URI = "mongodb+srv://projapoti_admin:Projapoti1@cluster0.xdcd4ck.mongodb.net/?appName=Cluster0"

db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["queen_projapoti_db"]
members_col = db["group_members"]
buttons_col = db["buttons"]
config_col = db["config"]

app = Client("queen_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ==========================================
# ২. গ্রুপ লিস্ট 
# ==========================================
ACTIVE_GROUP_IDS = [-1003628308355, -1003830226952, -1003771108723, -1003752042042, -1003632495992, -1002950867312]

DEFAULT_GROUPS = [
    {"name": "Bangladeshi GAY", "url": "https://t.me/+8tjqRErPds5mOTZl"},
    {"name": "Gay Voice Off Bangladesh", "url": "https://t.me/+sFKJ7gtbcIo0MDA9"},
    {"name": "Dhaka Gay Comm unity", "url": "https://t.me/dhaka_community"},
    {"name": "Gay Video Call Adda", "url": "https://t.me/+SLVwEktnWR5hMGM1"},
    {"name": "Queen Projapoti_Federation", "url": "https://t.me/BangladeshiGayFriends"},
    {"name": "Rajshahi City Group", "url": "https://t.me/+lw8ah99Er5MxZTg1"},
    {"name": "Hot Couple & Bull", "url": "https://t.me/+Bp6LPINNOjM3ZDBl"},
    {"name": "Orgy / গ্যাংব্যাং House", "url": "https://t.me/+MLQLo5pViGI2NjBl"}
]

GIF_URL = "https://graph.org/file/9167b02374ced565c8375-a3ee659aa8e21277c1.mp4"

async def get_dynamic_buttons():
    groups = await buttons_col.find().to_list(length=100)
    buttons = []
    for i in range(0, len(groups), 2):
        row = [InlineKeyboardButton(groups[i]["name"], url=groups[i]["url"])]
        if i + 1 < len(groups):
            row.append(InlineKeyboardButton(groups[i+1]["name"], url=groups[i+1]["url"]))
        buttons.append(row)
    return buttons

# ==========================================
# ৩. ইনবক্স (PM) কমান্ড
# ==========================================
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("সব গ্রুপে এড হতে ক্লিক করুন", callback_data="show_all_groups")]])
    await message.reply_animation(
        animation=GIF_URL,
        caption="✨ **Welcome To Queen Projapoti World!** ✨\n\nভরপুর বিনোদন, জমজমাট আড্ডা এবং এক্সক্লুসিভ ভিডিও চ্যানেলগুলোর এক্সেস এখন একটি মাত্র বটেই!\n\nনিচের বাটনে ক্লিক করে আমাদের সকল গ্রুপের এক্সেস নিন।",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("show_all_groups"))
async def show_all_groups_callback(client, callback_query: CallbackQuery):
    group_buttons = await get_dynamic_buttons()
    bot_info = await app.get_me()
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_info.username}?start=unlock&text=এক্সক্লুসিভ%20ভিডিও%20দেখতে%20বটটি%20ট্রাই%20করো!"
    group_buttons.append([InlineKeyboardButton("🔓 মিডিয়া আনলক করতে শেয়ার করুন", url=share_url)])
    reply_markup = InlineKeyboardMarkup(group_buttons)
    await callback_query.message.edit_text(
        "👇 **আমাদের সকল গ্রুপ এবং চ্যানেলের লিস্ট নিচে দেওয়া হলো:**\nসবগুলোতে জয়েন করুন এবং মিডিয়া আনলক করতে শেয়ার করুন!",
        reply_markup=reply_markup
    )

# ==========================================
# ৪. ওয়েলকাম মেসেজ এবং অন্যান্য ফিচার্স
# ==========================================
async def auto_delete_message(chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception:
        pass

@app.on_message(filters.new_chat_members)
async def welcome_new_members(client, message):
    if message.chat.id not in ACTIVE_GROUP_IDS: return
    for member in message.new_chat_members:
        await members_col.update_one({"chat_id": message.chat.id, "user_id": member.id}, {"$set": {"mention": member.mention}}, upsert=True)
        welcome_text = (f"✨ Hello {member.mention},\n🦋 **Royal Welcome To Projapoti Federation!** 👑\n\n"
                        f"আমাদের পরিবারে যুক্ত হওয়ার জন্য অসংখ্য ধন্যবাদ।\n\n📌 **বিশেষ সতর্কতা:**\n"
                        f"🔸 গ্রুপে কোনো প্রকার লিংক শেয়ার বা স্প্যাম করা সম্পূর্ণ নিষেধ。\n"
                        f"🔸 গ্রুপের সকল রুলস কঠোরভাবে মেনে চলতে হবে。\n\n👇 নিচের বাটনগুলোতে ক্লিক করে চ্যানেল ঘুরে দেখুন।")
        group_buttons = await get_dynamic_buttons()
        reply_markup = InlineKeyboardMarkup(group_buttons)
        try:
            sent_msg = await message.reply_animation(animation=GIF_URL, caption=welcome_text, reply_markup=reply_markup)
            asyncio.create_task(auto_delete_message(message.chat.id, sent_msg.id, 180))
        except Exception: pass

@app.on_message(filters.group & ~filters.bot, group=1)
async def passive_member_scraper(client, message):
    if message.chat.id in ACTIVE_GROUP_IDS and message.from_user:
        await members_col.update_one({"chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"mention": message.from_user.mention}}, upsert=True)

@app.on_message(filters.command("all") & filters.group & filters.user(ADMIN_IDS))
async def tag_all_members(client, message):
    if message.chat.id not in ACTIVE_GROUP_IDS:
        return await message.reply_text("❌ পারমিশন নেই।")
    custom_msg = message.text.replace("/all", "").strip() or "গুরুত্বপূর্ণ নোটিশ!"
    status_msg = await message.reply_text("⏳ মেনশন শুরু হচ্ছে...")
    members = await members_col.find({"chat_id": message.chat.id}).to_list(length=None)
    if not members: return await status_msg.edit_text("❌ ডেটাবেসে কোনো মেম্বার নেই!")
    mentions = [m["mention"] for m in members]
    count = 0
    for i in range(0, len(mentions), 5):
        batch = mentions[i:i + 5]
        try:
            await app.send_message(message.chat.id, f"{custom_msg}\n\n" + ", ".join(batch))
            count += len(batch)
        except Exception: pass
        if count % 100 == 0:
            await asyncio.sleep(300)
        else:
            await asyncio.sleep(2)
    await app.send_message(message.chat.id, f"✅ মেনশন সম্পন্ন! মোট {count} জন।")

@app.on_message(filters.command("addbtn") & filters.private & filters.user(ADMIN_IDS))
async def add_button(client, message):
    try:
        btn_name, btn_url = [x.strip() for x in message.text.replace("/addbtn ", "").split("|")]
        await buttons_col.update_one({"name": btn_name}, {"$set": {"name": btn_name, "url": btn_url}}, upsert=True)
        await message.reply_text(f"✅ বাটন অ্যাড হয়েছে: {btn_name}")
    except: await message.reply_text("❌ ফরম্যাট: `/addbtn নাম | লিংক`")

@app.on_message(filters.command("delbtn") & filters.private & filters.user(ADMIN_IDS))
async def del_button(client, message):
    btn_name = message.text.replace("/delbtn ", "").strip()
    result = await buttons_col.delete_one({"name": btn_name})
    await message.reply_text(f"🗑️ বাটন ডিলিট হয়েছে!" if result.deleted_count > 0 else "❌ বাটন পাওয়া যায়নি।")

async def looping_message_task():
    while True:
        await asyncio.sleep(3600) 
        group_buttons = await get_dynamic_buttons()
        bot_info = await app.get_me()
        share_url = f"https://t.me/share/url?url=https://t.me/{bot_info.username}?start=unlock&text=এক্সক্লুসিভ%20ভিডিও%20দেখতে%20বট%20স্টার্ট%20করুন!"
        group_buttons.append([InlineKeyboardButton("🔓 মিডিয়া আনলক করুন (Share)", url=share_url)])
        loop_keyboard = InlineKeyboardMarkup(group_buttons)
        for chat_id in ACTIVE_GROUP_IDS:
            try:
                config_data = await config_col.find_one({"chat_id": chat_id})
                if config_data and config_data.get("last_loop_msg_id"):
                    try: await app.delete_messages(chat_id, config_data["last_loop_msg_id"])
                    except: pass
                sent_msg = await app.send_animation(chat_id, animation=GIF_URL, caption="🦋 **Queen Projapoti World** 🦋\n\nএক্সক্লুসিভ ভিডিও দেখতে নিচের বাটনে ক্লিক করুন!", reply_markup=loop_keyboard)
                await config_col.update_one({"chat_id": chat_id}, {"$set": {"last_loop_msg_id": sent_msg.id}}, upsert=True)
                await asyncio.sleep(3)
            except: pass

# ==========================================
# ৫. ডামি ওয়েব সার্ভার (বটকে ২৪ ঘণ্টা লাইভ রাখতে)
# ==========================================
async def web_server():
    async def handle(request):
        return web.Response(text="Bot is Live & Running on Render!")
    
    app_web = web.Application()
    app_web.router.add_get('/', handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ Web server successfully started on port {port}")

# ==========================================
# ৬. মেইন স্টার্টআপ ফাংশন
# ==========================================
async def main():
    await web_server()
    if await buttons_col.count_documents({}) == 0:
        await buttons_col.insert_many(DEFAULT_GROUPS)
        
    await app.start()
    print("🤖 Queen Projapoti Bot is Running Smoothly...")
    
    asyncio.create_task(looping_message_task())
    
    from pyrogram import idle
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
