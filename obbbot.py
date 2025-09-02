import logging
import time
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ───────── CONFIG ─────────

BOT_TOKEN = "8267761891:AAF56sqof0Kp0ljqaN7FNOFV_hXMc-Xt2gI"
OWNER_ID = 6236477871
OWNER_USERNAME = "@IG_shadow"
CHANNEL_LINK = "https://t.me/+it_aHo49otgwYmFl"

LOG_FILE = "logs.txt"
FILE_KEYWORDS_FILE = "file_keywords.txt"
USERS_FILE = "users.txt"
DUMP_FILE = "Dump_Skin_3.9.txt"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# ───────── HELPERS ─────────

def save_log(text: str):
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")

def load_file_keywords():
    try:
        with open(FILE_KEYWORDS_FILE, "r") as f:
            data = {}
            for line in f.read().splitlines():
                k, channel, msg_id = line.split("|")
                data[k] = (channel, int(msg_id))
            return data
    except:
        return {}

def save_file_keywords(data):
    with open(FILE_KEYWORDS_FILE, "w") as f:
        for k, v in data.items():
            f.write(f"{k}|{v[0]}|{v[1]}\n")

def log_user(user):
    try:
        with open(USERS_FILE, "r") as f:
            existing = f.read().splitlines()
    except FileNotFoundError:
        existing = []
    user_string = f"{user.id}|{user.username or 'N/A'}|{user.full_name}"
    if user_string not in existing:
        with open(USERS_FILE, "a") as f:
            f.write(user_string + "\n")

def is_owner(user_id: int):
    return user_id == OWNER_ID

def load_dump_mapping():
    mapping_id_to_name = {}
    mapping_name_to_ids = {}
    if not os.path.exists(DUMP_FILE):
        return mapping_id_to_name, mapping_name_to_ids
    with open(DUMP_FILE, "r", encoding="utf-8") as f:
        for line in f.read().splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[0].isdigit():
                id_val = parts[0]
                name = parts[2] if parts[2] else "(No Name)"
                mapping_id_to_name[id_val] = name
                mapping_name_to_ids.setdefault(name.lower(), []).append(id_val)
    return mapping_id_to_name, mapping_name_to_ids

FILE_KEYWORDS = load_file_keywords()

# ───────── MESSAGES ─────────

START_OWNER = (
    "⚡════════════════════════⚡\n\n"
    "🚀 𝐎𝐖𝐍𝐄𝐑: @{owner_username}\n\n"
    "🛠 𝐘𝐎𝐔 𝐇𝐀𝐕𝐄 𝐅𝐔𝐋𝐋 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 ⚙️ 𝐎𝐕𝐄𝐑 𝐓𝐇𝐈𝐒 𝐁𝐎𝐓.\n\n"
    "📲 𝐓𝐘𝐏𝐄 /help 𝐓𝐎 𝐒𝐄𝐄 𝐀𝐃𝐌𝐈𝐍 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒.\n\n"
    "🔗 𝐉𝐎𝐈𝐍 𝐓𝐇𝐄 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋:\n{channel_link}\n\n"
    "⚡════════════════════════⚡"
)

HELP_OWNER = (
    "🛠═══ 🏷 *OWNER COMMANDS* 🏷 ═══🛠\n\n"
    "╭──────────────────────╮\n"
    "│  📁 /set ➜ *Set file*              │\n"
    "│  📢 /broadcast ➜ *Send broadcast*   │\n"
    "│  📄 /logs ➜ *Show logs*             │\n"
    "│  🧹 /clearlogs ➜ *Clear logs*        │\n"
    "│  📊 /stats ➜ *Bot stats*            │\n"
    "│  👤 /userinfo ➜ *Get user info*     │\n"
    "│  🏓 /ping ➜ *Bot latency*            │\n"
    "│  👥 /users ➜ *List all users*       │\n"
    "│  🔢 /id2name ➜ *ID to Name (numbered)*    │\n"
    "│  🔤 /id2name_plain ➜ *ID to Name (plain)*  │\n"
    "│  🔢 /name2id ➜ *Name to ID (numbered)*     │\n"
    "│  🔤 /name2id_plain ➜ *Name to ID (plain)* │\n"
    "╰──────────────────────╯"
)

HELP_GENERAL = (
    "📖═══ 📌 *AVAILABLE COMMANDS* 📌 ═══📖\n\n"
    "💡 Type a keyword to get a file.\n"
    "✏️ Example: `contact owner for that😁`\n\n"
    "❗ Contact owner for issues.\n\n"
    "╭──────────────────────╮\n"
    "│  👤 /userinfo ➜ *Get user info*      │\n"
    "│  🔢 /id2name ➜ *ID to Name (numbered)*    │\n"
    "│  🔤 /id2name_plain ➜ *ID to Name (plain)*  │\n"
    "│  🔢 /name2id ➜ *Name to ID (numbered)*     │\n"
    "│  🔤 /name2id_plain ➜ *Name to ID (plain)* │\n"
    "╰──────────────────────╯"
)

# ───────── COMMANDS ─────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user

    if is_owner(uid):
        msg = START_OWNER.format(owner_username=OWNER_USERNAME[1:], channel_link=CHANNEL_LINK)
    else:
        msg = (
            f"👋 𝐇𝐞𝐥𝐥𝐨 {user.first_name}!\n"
            "𝐓𝐲𝐩𝐞 /help 𝐭𝐨 𝐬𝐞𝐞 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬.\n\n"
            f"🔗 𝐉𝐨𝐢𝐧 𝐎𝐮𝐫 𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐂𝐡𝐚𝐧𝐧𝐞𝐥:\n{CHANNEL_LINK}"
        )
    await update.message.reply_text(msg)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_owner(uid):
        text = HELP_OWNER
    else:
        text = HELP_GENERAL

    buttons_help = [
        [InlineKeyboardButton("📩 Contact Owner", url=f"https://t.me/{OWNER_USERNAME[1:]}")],
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]
    ]

    reply_markup = InlineKeyboardMarkup(buttons_help)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def set_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage: /set <keyword> <t.me_link>")
        return
    keyword = context.args[0].lower()
    link = context.args[1].replace("https://", "").replace("http://", "")
    parts = link.split("/")
    if len(parts) < 2:
        await update.message.reply_text("❌ Invalid link format. Use t.me/channel/message_id")
        return
    channel = parts[-2]
    if not channel.startswith("@"):
        channel = "@" + channel
    try:
        message_id = int(parts[-1])
        FILE_KEYWORDS[keyword] = (channel, message_id)
        save_file_keywords(FILE_KEYWORDS)
        await update.message.reply_text(f"✅ File set for keyword: {keyword}")
        save_log(f"SET FILE: {keyword} -> {link}")
    except ValueError:
        await update.message.reply_text("❌ Invalid message ID")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    message = update.message.text.partition(' ')[2]
    if not message.strip():
        await update.message.reply_text("❌ Usage: /broadcast <message>")
        return
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().strip().split('\n')
    except FileNotFoundError:
        await update.message.reply_text("❌ No users to broadcast.")
        return
    sent, failed = 0, 0
    for line in users:
        if line.strip() == "":
            continue
        uid = int(line.split("|")[0])
        try:
            await context.bot.send_message(chat_id=uid, text=message)
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"📢 Broadcast sent to {sent} users, failed {failed}.")

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    try:
        with open(LOG_FILE, "r") as f:
            content = f.read()
        if not content.strip():
            await update.message.reply_text("📄 Logs file is empty.")
        elif len(content) > 4000:
            await update.message.reply_document(open(LOG_FILE, "rb"))
        else:
            await update.message.reply_text(f"📄 Logs:\n{content}")
    except FileNotFoundError:
        await update.message.reply_text("📄 Logs file not found.")

async def clearlogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    open(LOG_FILE, "w").close()
    await update.message.reply_text("🧹 Logs cleared successfully.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    total_users = 0
    try:
        with open(USERS_FILE, "r") as f:
            total_users = len([line for line in f.read().splitlines() if line.strip()])
    except FileNotFoundError:
        total_users = 0
    msg = (f"📊 Bot Statistics:\n"
           f"🔑 Total Keywords: {len(FILE_KEYWORDS)}\n"
           f"👥 Total Users: {total_users}")
    await update.message.reply_text(msg)

async def userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = None
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            user = await context.bot.get_chat(user_id)
        except Exception:
            await update.message.reply_text("❌ Invalid User ID.")
            return
    else:
        user = update.effective_user
    text = (f"👤 User Info:\n"
            f"ID: {user.id}\n"
            f"Name: {user.full_name}\n"
            f"Username: @{user.username if user.username else 'N/A'}")
    await update.message.reply_text(text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    elapsed = (time.time() - start_time) * 1000
    await msg.edit_text(f"🏓 Pong! {int(elapsed)}ms")

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().strip().split('\n')
        if not users or users == ['']:
            await update.message.reply_text("📃 No users found.")
            return
        message_lines = ["📃 Users using the bot:\n"]
        for line in users:
            uid, username, full_name = line.split("|")
            message_lines.append(f"ID: {uid}\nUsername: @{username}\nName: {full_name}\n---")
        message = "\n".join(message_lines)
        for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
            await update.message.reply_text(chunk)
    except FileNotFoundError:
        await update.message.reply_text("📃 No users found.")

async def id2name_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mapping_id_to_name, _ = load_dump_mapping()
    text = update.message.text.partition(' ')[2].strip()
    if not text:
        await update.message.reply_text("❌ Provide IDs after the command, comma-separated or grouped by line.")
        return
    lines = text.split("\n")
    results = []
    for idx, line in enumerate(lines, start=1):
        ids = [x.strip() for x in line.split(',') if x.strip()]
        names = [mapping_id_to_name.get(id_val, "ID not found") for id_val in ids]
        results.append(f"{idx}. {', '.join(names)}")
    message = "\n".join(results)
    chunk_size = 4000
    for i in range(0, len(message), chunk_size):
        await update.message.reply_text(message[i:i+chunk_size])

async def id2name_plain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mapping_id_to_name, _ = load_dump_mapping()
    text = update.message.text.partition(' ')[2].strip()
    lines = text.split("\n")
    results = []
    for line in lines:
        ids = [x.strip() for x in line.split(',') if x.strip()]
        names = [mapping_id_to_name.get(id_val, "ID not found") for id_val in ids]
        results.append(", ".join(names))
    message = "\n".join(results)
    chunk_size = 4000
    for i in range(0, len(message), chunk_size):
        await update.message.reply_text(message[i:i+chunk_size])

async def name2id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, mapping_name_to_ids = load_dump_mapping()
    text = update.message.text.partition(' ')[2].strip()
    if not text:
        await update.message.reply_text("❌ Provide names after the command, comma-separated.")
        return
    names = [n.strip() for n in text.split(',') if n.strip()]
    results = []
    for idx, name in enumerate(names, start=1):
        id_matches = mapping_name_to_ids.get(name.lower(), [])
        if id_matches:
            results.append(f"{idx}. {', '.join(id_matches)}")
        else:
            results.append(f"{idx}. Name not found")
    message = "\n".join(results)
    chunk_size = 4000
    for i in range(0, len(message), chunk_size):
        await update.message.reply_text(message[i:i+chunk_size])

async def name2id_plain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, mapping_name_to_ids = load_dump_mapping()
    text = update.message.text.partition(' ')[2].strip()
    if not text:
        await update.message.reply_text("❌ Provide names after the command, comma-separated.")
        return
    names = [n.strip() for n in text.split(',') if n.strip()]
    results = []
    for name in names:
        id_matches = mapping_name_to_ids.get(name.lower(), [])
        if id_matches:
            results.append(", ".join(id_matches))
        else:
            results.append("Name not found")
    message = "\n".join(results)
    chunk_size = 4000
    for i in range(0, len(message), chunk_size):
        await update.message.reply_text(message[i:i+chunk_size])

async def keyword_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    if uid != OWNER_ID:
        log_user(user)
    text = update.message.text.lower().strip()
    if text in FILE_KEYWORDS:
        channel, msg_id = FILE_KEYWORDS[text]
        try:
            await context.bot.copy_message(chat_id=uid, from_chat_id=channel, message_id=msg_id)
            save_log(f"FILE: {uid} requested {text}")
        except Exception:
            await update.message.reply_text("❌ Cannot send this file. Bot must be admin in channel.")
    else:
        await update.message.reply_text("❌ No file found for this keyword.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("set", set_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("clearlogs", clearlogs))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("userinfo", userinfo))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("users", users_cmd))
    app.add_handler(CommandHandler("id2name", id2name_cmd))
    app.add_handler(CommandHandler("id2name_plain", id2name_plain_cmd))
    app.add_handler(CommandHandler("name2id", name2id_cmd))
    app.add_handler(CommandHandler("name2id_plain", name2id_plain_cmd))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), keyword_forward))
    print("🤖 Stylish Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
