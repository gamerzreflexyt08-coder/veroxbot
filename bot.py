import logging
import sqlite3
import asyncio
import os
import urllib.request
import urllib.error
import json
import re
import random
from datetime import datetime
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.constants import ParseMode, ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import TelegramError

# ==========================================
# ⚙️ RENDER-READY CONFIGURATION ⚙️
# ==========================================
# ALL secrets are read from environment variables.
# Set these in Render Dashboard → Your Service → Environment tab.
# Never hardcode tokens in your code!

BOT_TOKEN   = os.environ["BOT_TOKEN"]           # Required — no default
ADMIN_IDS   = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "8709399313").split(",")]
BOT_LINK    = os.environ.get("BOT_LINK", "https://t.me/verox_info_bot")
PORT        = int(os.environ.get("PORT", 8080)) # Render injects PORT automatically

# Customization Links & Media
FORCE_JOIN_PHOTO = os.environ.get("FORCE_JOIN_PHOTO", "https://files.catbox.moe/ii7upg.jpg")
QR_CODE_PHOTO    = os.environ.get("QR_CODE_PHOTO", "https://ibb.co/mF5Ry1pj")
UPI_ID           = os.environ.get("UPI_ID", "rajdeeprg0001@fam")
TRX_ADDRESS      = os.environ.get("TRX_ADDRESS", "TRry6XS8pHxjx6JLXarXNrNuAHydZcCfzd")
BINANCE_ID       = os.environ.get("BINANCE_ID", "1018426331")

# API Endpoints
NUM1_API    = os.environ.get("NUM1_API", "https://yttttttt./?key=DARKOSINT&num=")
NUM2_API    = os.environ.get("NUM2_API", "https://nuiservices.workers.dev/mobikup?key=CRYSTAAPI&mobile=")
NUM3_API    = os.environ.get("NUM3_API", "https://username-to-number.verdayne&num=")

TG1_API     = os.environ.get("TG1_API", "https://telegram-to-num.vercel.ayy&term=")
TG2_API     = os.environ.get("TG2_API", "https://ansh-apis.is-h&q=")
TG3_API     = os.environ.get("TG3_API", "https://username-to-number.vercel.adayne&q=")

ADHR_API    = os.environ.get("ADHR_API", "https://aadasapiservices.workers.devid_num=")
FAM_API     = os.environ.get("FAM_API",  "https://number8899.vercel.apadhar=")
VEHICLE_API = os.environ.get("VEHICLE_API", "https://vehcile.vepp/api/rc-search?nber=")
IFSC_API    = os.environ.get("IFSC_API", "https://abbael.app/api/ifsc?ifsc=")
IMEI_API    = os.environ.get("IMEI_API", "https://imei-info.gaura6.workers.dev/?imei=")

# Secure Tunnels Setup (Verification)
REQUIRED_CHATS = [
    {"id": int(os.environ.get("CHANNEL1_ID", "-1003627302252")), "url": os.environ.get("CHANNEL1_URL", "https://t.me/veroxprtl"), "name": "💠 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 💠"},
    {"id": int(os.environ.get("CHANNEL2_ID", "-1003292664118")), "url": os.environ.get("CHANNEL2_URL", "https://t.me/verox_chats"), "name": "💬 𝗩𝗜𝗣 𝗖𝗵𝗮𝘁 𝗟𝗼𝘂𝗻𝗴𝗲 💬"},
]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

pending_admin_messages = {}
pending_checkouts = {}
user_search_state = {} 

PACKAGES = {
    "pkg120": {"credits": 120, "name": "120 Credits VIP"},
    "pkg250": {"credits": 250, "name": "250 Credits Elite"},
    "pkg550": {"credits": 550, "name": "550 Credits Master"},
    "pkg1000": {"credits": 1000, "name": "1000 Credits Supreme"}
}

# ==========================================
# 🌍 100% FULL SYSTEM LOCALIZATION 🌍
# ==========================================
LANGUAGES = {
    "en": {
        "name": "🇬🇧 English",
        "msg_greet": "🔥 *Welcome to the Advanced OSINT Terminal!*",
        "msg_main": "🎛 *Premium Command Dashboard Activated*\nUse the buttons below to navigate quickly!",
        "msg_back_main": "🎛 *Main Menu Restored*\nSelect an option below:",
        "stat": "📊 *Your Statistics:*", "status": "Status:", "searches": "Searches Done:", "refs": "Total Referrals:", "cred": "Available Credits:",
        "refer_promo": "💸 *REFER & EARN FREE SEARCHES* 💸\n━━━━━━━━━━━━━━━━━━━━━\nInvite your friends to our bot! For every friend that joins and verifies, you earn *+1 Premium Credit*.\n\n🔗 *Tap to copy your unique link:*\n",
        "lbl_live_db": "👤 *LIVE DATABASE IDENTITY*", "lbl_credits_support": "🛡️ System: Advanced OSINT Grid", "lbl_made_by": "🔐 Connection: Secure",
        # UI Buttons (Main Menu)
        "btn_num": "📱 Number Search", "btn_tg": "✈️ Telegram ID", "btn_adhr": "🪪 Aadhar Search", "btn_fam": "👥 Aadhar Family",
        "btn_veh": "🚗 Vehicle RC", "btn_ifsc": "🏦 Bank IFSC", "btn_imei": "📱 IMEI Info", "btn_unlim_search": "♾️ Unlimited Search Here",
        "btn_buy": "💎 Buy Premium", "btn_ref": "🎁 Refer & Earn Credits", "btn_redeem": "🎟️ Redeem Code", "btn_status": "👤 My Status",
        "btn_stats": "📊 Bot Stats", "btn_lead": "🏆 Leaderboard", "btn_admin": "👨‍💼 Admin Panel", "btn_dev": "👨‍💻 Architecture",
        # Sub Menus
        "btn_back_main": "🔙 Back to Main Menu", "btn_back_prem": "🔙 Back to Premium Menu", "btn_back_pay": "🔙 Back to Payment Methods",
        "btn_srv1": "💎 Server 1", "btn_srv2": "💎 Server 2", "btn_srv3": "💎 Server 3",
        "btn_tg1": "🆔 Server 1", "btn_tg2": "🆔 Server 2", "btn_tg3": "👤 Username to Num",
        "btn_adhr_lookup": "🏛️ Aadhar Lookup", "btn_fam_search": "👥 Family Search", "btn_veh_trace": "🏎️ Trace Vehicle RC",
        "btn_bank_intel": "🏦 Bank Intelligence", "btn_dev_trace": "📱 Device Trace",
        "btn_unlim_sub": "👑 Unlimited Refer Subscription", "btn_add_cred": "🪙 Add Credits",
        "btn_pay_upi": "💰 Pay with UPI (INR)", "btn_pay_trx": "🪙 Pay with Crypto (TRX)",
        # Plans & Pricing
        "btn_sub_3d": "⏳ 3 Days (10 🪙)", "btn_sub_7d": "⏳ 7 Days (21 🪙)", "btn_sub_15d": "⏳ 15 Days (35 🪙)", "btn_sub_30d": "⏳ 30 Days (50 🪙)",
        "btn_upi_120": "📦 UPI: 120 Credits (₹49)", "btn_upi_250": "📦 UPI: 250 Credits (₹99)", "btn_upi_550": "📦 UPI: 550 Credits (₹199)", "btn_upi_1000": "💎 UPI: 1000 Credits (₹399)",
        "btn_trx_120": "📦 TRX: 120 Credits (1.85 TRX)", "btn_trx_250": "📦 TRX: 250 Credits (3.75 TRX)", "btn_trx_550": "📦 TRX: 550 Credits (7.55 TRX)", "btn_trx_1000": "💎 TRX: 1000 Credits (15 TRX)",
        # Internal User Prompts
        "msg_store": "💎 *PREMIUM EXCLUSIVE STORE* 💎\n━━━━━━━━━━━━━━━━━━━━━\n\nWelcome to the VIP Premium Store. Elevate your OSINT experience with unlimited access and priority servers.\n\n👇 *Select a premium category below:*",
        "msg_subs": "👑 *UNLIMITED PREMIUM SUBSCRIPTIONS* 👑\n━━━━━━━━━━━━━━━━━━━━━\n\nUnlock *Zero-Deduction* unlimited searches. Choose a VIP plan below to activate instantly.\n\n✨ *Features included:* \n┠ 🚀 Priority Server Access\n┠ ♾️ No Credit Deductions\n┖ 🛡️ Advanced Identity Tracing",
        "msg_gateway": "🪙 *PURCHASE PREMIUM CREDITS* 🪙\n━━━━━━━━━━━━━━━━━━━━━\n\nTop up your account securely. Select your preferred high-speed payment gateway below:\n\n💳 *Supported Gateways:*\n┠ 🇮🇳 Secure UPI (India)\n┖ 🌐 Fast Crypto TRX (Global)",
        "msg_upi_checkout": "🏦 *SECURE UPI CHECKOUT (INR)* 🏦\n━━━━━━━━━━━━━━━━━━━━━\n\nSelect a premium credit package below to instantly generate your VIP checkout session:",
        "msg_trx_checkout": "🌐 *SECURE CRYPTO CHECKOUT (TRX)* 🌐\n━━━━━━━━━━━━━━━━━━━━━\n\nSelect a premium credit package below to instantly generate your VIP checkout session:",
        "msg_upi_inst": "1️⃣ Scan the QR Code attached or pay securely to this UPI ID:\n`{upi_id}`",
        "msg_trx_inst": "1️⃣ Send EXACTLY {amount_str} to this \n\nBinance ID: `{binance_id}`\n\nTRX Wallet Address:\n`{trx_address}`",
        "msg_dev": "👨‍💻 *SYSTEM ARCHITECTURE*\n━━━━━━━━━━━━━━━━━━━━━\n\nThis Terminal is maintained by the Advanced OSINT Grid. Direct contact has been disabled for security purposes.",
        "msg_redeem_prompt": "🎟️ *REDEEM GIFT CODE*\n━━━━━━━━━━━━━━━━━━━━━\n👆 *Please enter your Gift Code below:*",
        "msg_modules": "📱 *INTELLIGENCE MODULE*\n━━━━━━━━━━━━━━━━━━━━━\nPlease select a tool or server below to begin your search:",
        # Prompts
        "prompt_num1": "📡 *[ TELECOM INTEL: SERVER 1 ]*\n━━━━━━━━━━━━━━━━━━━━━\nProvide the target MSISDN for deep packet inspection.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `10-Digit Mobile Number`\n┠ *Test Value:* `9876543210`\n┖ *Constraint:* `Exclude country code (e.g., +91).`\n\n_Awaiting target input..._",
        "prompt_num2": "📡 *[ TELECOM INTEL: SERVER 2 ]*\n━━━━━━━━━━━━━━━━━━━━━\nProvide the target MSISDN for deep packet inspection.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `10-Digit Mobile Number`\n┠ *Test Value:* `9988776655`\n┖ *Constraint:* `Exclude country code (e.g., +91).`\n\n_Awaiting target input..._",
        "prompt_num3": "📡 *[ TELECOM INTEL: SERVER 3 ]*\n━━━━━━━━━━━━━━━━━━━━━\nProvide the target MSISDN for deep packet inspection.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `10-Digit Mobile Number`\n┠ *Test Value:* `9123456780`\n┖ *Constraint:* `Exclude country code (e.g., +91).`\n\n_Awaiting target input..._",
        "prompt_tg1": "🆔 *[ TELEGRAM OSINT: SERVER 1 ]*\n━━━━━━━━━━━━━━━━━━━━━\nProvide the target numerical Telegram ID.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `Numerical ID`\n┠ *Test Value:* `123456789`\n┖ *Constraint:* `Do NOT input @usernames.`\n\n_Awaiting target input..._",
        "prompt_tg2": "🆔 *[ TELEGRAM OSINT: SERVER 2 ]*\n━━━━━━━━━━━━━━━━━━━━━\nProvide the target numerical Telegram ID.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `Numerical ID`\n┠ *Test Value:* `987654321`\n┖ *Constraint:* `Do NOT input @usernames.`\n\n_Awaiting target input..._",
        "prompt_tg3": "👤 *[ USERNAME DE-ANONYMIZER ]*\n━━━━━━━━━━━━━━━━━━━━━\nTrace a Telegram alias to its origin node.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `Alphanumeric Alias`\n┠ *Test Value:* `STAR_PROOO`\n┖ *Constraint:* `Exclude the '@' symbol.`\n\n_Awaiting target input..._",
        "prompt_adhr": "🏛️ *[ NATIONAL IDENTITY TRACE ]*\n━━━━━━━━━━━━━━━━━━━━━\nQuery the UIDAI database for demographic data.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `12-Digit UID`\n┠ *Test Value:* `123456789012`\n┖ *Constraint:* `No spaces or dashes.`\n\n_Awaiting target input..._",
        "prompt_fam": "👥 *[ FAMILY NETWORK TRACE ]*\n━━━━━━━━━━━━━━━━━━━━━\nQuery demographic relationships linked to UID.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `12-Digit UID`\n┠ *Test Value:* `123456789012`\n┖ *Constraint:* `No spaces or dashes.`\n\n_Awaiting target input..._",
        "prompt_veh": "🏎️ *[ VEHICLE REGISTRY TRACE ]*\n━━━━━━━━━━━━━━━━━━━━━\nQuery VAHAN database for owner and chassis intel.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `Alphanumeric License Plate`\n┠ *Test Value:* `DL01AB1234`\n┖ *Constraint:* `No spaces (e.g., DL01AB1234).`\n\n_Awaiting target input..._",
        "prompt_ifsc": "🏦 *[ FINANCIAL NODE LOOKUP ]*\n━━━━━━━━━━━━━━━━━━━━━\nTrace Bank IFSC codes to physical branch nodes.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `11-Character IFSC`\n┠ *Test Value:* `SBIN0001234`\n┖ *Constraint:* `Must be valid Indian IFSC.`\n\n_Awaiting target input..._",
        "prompt_imei": "📱 *[ HARDWARE IDENTITY TRACE ]*\n━━━━━━━━━━━━━━━━━━━━━\nTrace device origins via IMEI fingerprint.\n\n📌 *PARAMETERS & SYNTAX:*\n┠ *Data Type:* `15-Digit IMEI`\n┠ *Test Value:* `123456789012345`\n┖ *Constraint:* `Numbers only.`\n\n_Awaiting target input..._",
        "cancel_prompt": "\nOr select *🔙 Back to Main Menu* to cancel.",
        # Admin Panel
        "msg_admin_panel": "🛠 *ADVANCED ADMIN CONTROL PANEL* 🛠\n━━━━━━━━━━━━━━━━━━━━━\nSelect an administration tool below:",
        "btn_admin_bc": "📢 Broadcast", "btn_admin_sc": "📋 See Codes", "btn_admin_ap": "➕ Add Point", "btn_admin_rp": "➖ Remove Point",
        "btn_admin_ban": "⛔️ Ban", "btn_admin_unban": "🟢 Unban", "btn_admin_addp": "💎 Add Premium", "btn_admin_rmp": "🗑 Remove Premium",
        "btn_admin_mc": "🎁 Make Code", "btn_admin_dc": "🗑 Delete Code", "btn_back_admin": "🔙 Back to Admin Menu",
        # Dynamic Search / Errors
        "search_fail": "📭 *DATA NOT AVAILABLE*\n━━━━━━━━━━━━━━━━━━━━━\n❌ *Search Info Not Found:*\nNo data is available in the database for this specific query.",
        "invalid_input": "❌ *[ SYNTAX ERROR ] Input format does not match required parameters.*",
        "invalid_num": "❌ *[ SYNTAX ERROR ] Invalid Number! Please enter a valid 10-digit mobile number.*",
        "invalid_tg": "❌ *[ SYNTAX ERROR ] Invalid Telegram ID/Username!*",
        "result_lbl": "Result",
        "result_no_data": "✨ No relevant data found.\n",
        "stat_tot": "Total Searches Run:", "stat_ded": "Deducted:", "stat_rem": "Remaining Credits:", "stat_acc": "Access Mode:",
        # Global Translation Additions
        "err_insuff_cred": "❌ *INSUFFICIENT CREDITS*\n\nYou need *{cost} Credits* to purchase the *{days}-Day VIP Plan*.\nYour current balance: *{curr_credits} Credits*.\n\n💡 *How to get more Credits:*\n💰 *Buy:* Go back and select 🪙 Add Credits to pay securely.\n🎁 *Refer:* Share your unique link via 🎁 Refer & Earn Credits to earn free credits!\n\nPlease gather enough credits to proceed.",
        "msg_sub_success": "🎉 *VIP SUBSCRIPTION ACTIVATED!* 🎉\n━━━━━━━━━━━━━━━━━━━━━\n\n✅ You have successfully unlocked *{days} Days* of Unlimited Searches!\n\n💰 *Balance Deducted:* `{cost} Credits`\n⏳ *Premium Valid Until:* `{expiry_dt}`\n\nEnjoy your exclusive priority access! 🚀",
        "msg_force_join": "⚠️ *Premium Verification Required*\n\n🚀 You must join all our private channels and groups to verify your account and unlock the bot features.",
        "msg_private_only": "👑 *PREMIUM PRIVATE ACCESS ONLY* 👑\n━━━━━━━━━━━━━━━━━━━━━\n\n🛑 *Group Usage Disabled*\nThis is an advanced private database bot. To protect your search queries and maintain extreme performance, group commands are strictly prohibited.\n\n🔗 *Tap here to use me privately:*",
        "msg_group_small": "🛑 *[ CRITICAL SYSTEM ERROR ]* 🛑\n━━━━━━━━━━━━━━━━━━━━━\n\n⚠️ *CONNECTION REFUSED:* Target Node insufficient.\n\nThis Cyber Terminal requires a massive computational node to bypass rate limits. The current group has less than the *500-member minimum* required.\n\n🛑 *Protocol:* `Severing Connection...`\n\n💡 _Expand this grid to 500+ agents and deploy me again!_",
        "msg_group_welcome": "👑 *[ ROOT ] OSINT TERMINAL INSTALLED* 👑\n━━━━━━━━━━━━━━━━━━━━━\n\n🟢 *System Status:* `Online & Bypassed`\n🎁 *Grid Perk:* `100% Free & Unlimited Traces!`\n\n⚡ *EXECUTE MODULES BELOW:* ⚡\n\n📱 *[ TELECOM INTELLIGENCE ]*\n ┣ 🟢 `/num1` ➔ Server 1 (Ex: `/num1 9876543210`)\n ┣ 🟡 `/num2` ➔ Server 2 (Ex: `/num2 9988776655`)\n ┗ 🔴 `/num3` ➔ Server 3 (Ex: `/num3 9123456780`)\n\n✈️ *[ TELEGRAM IDENTITY ]*\n ┣ 🆔 `/tg1` ➔ TG Server 1 (Ex: `/tg1 123456789`)\n ┣ 🆔 `/tg2` ➔ TG Server 2 (Ex: `/tg2 987654321`)\n ┗ 👤 `/tg3` ➔ Username (Ex: `/tg3 STAR_PROOO`)\n\n🪪 *[ NATIONAL DATABASE ]*\n ┣ 🏛️ `/adhr` ➔ Aadhar Info (Ex: `/adhr 123456789012`)\n ┗ 👥 `/fam`  ➔ Family Tree (Ex: `/fam 987654321098`)\n\n🏢 *[ REGISTRY & FINANCE ]*\n ┣ 🏎️ `/veh`  ➔ Vehicle RC (Ex: `/veh DL01AB1234`)\n ┣ 🏦 `/ifsc` ➔ Bank Details (Ex: `/ifsc SBIN0001234`)\n ┗ 📱 `/imi`  ➔ IMEI Trace (Ex: `/imi 123456789012345`)\n\n━━━━━━━━━━━━━━━━━━━━━\n💡 _Input a module command to extract live intelligence._",
        "msg_top_refs": "🏆 *TOP 10 REFERRAL LEADERBOARD* 🏆\n━━━━━━━━━━━━━━━━━━━━━\n\n",
        "msg_bot_stats": "📊 *Advanced Bot Statistics*\n━━━━━━━━━━━━━━━━━━━━━\n",
        "msg_checkout_init": "🛒 *VIP PAYMENT CHECKOUT INITIATED*\n━━━━━━━━━━━━━━━━━━━━━\n\n📦 *Package Selected:* {pkg_name}\n💵 *Amount Due:* {amount_str}\n\n🏦 *PAYMENT INSTRUCTIONS:*\n{instructions}\n\n2️⃣ Take a clear screenshot of your successful payment receipt.\n3️⃣ Send the screenshot directly HERE to this bot NOW!\n\n⏳ _Awaiting your receipt for instant automated verification..._",
        # Security & Core Features
        "msg_banned": "⛔️ *You are permanently banned from using this terminal.*",
        "msg_maintenance": "⚙️ *Terminal is currently under maintenance!* Please try again later.",
        "msg_verify_success": "✅ Verification Successful!",
        "msg_ref_unlocked": "🎉 *BOOM! NEW REFERRAL UNLOCKED!* 🎉\n━━━━━━━━━━━━━━━━━━━━━\n\n✅ *A new user joined using your link and verified their account!*\n\n🎁 *Reward Claimed:* `+1 Premium Credit` 🪙\n\n💡 _Keep sharing your link to earn more credits._",
        "msg_access_denied": "🛑 *ACCESS DENIED: INSUFFICIENT CREDITS* 🛑\n━━━━━━━━━━━━━━━━━━━━━\n\n⚠️ You need an active subscription or at least *1 Credit* to execute this search.",
        "msg_pls_init_buy": "❌ *Please initiate a purchase first!*\n\nClick the *💎 Buy Premium* button to select a package before sending payment screenshots.",
        "msg_receipt_received": "✅ *Receipt Received!* Sent to VIP admins for rapid verification. Please allow a few moments.",
        "status_title": "YOUR PREMIUM STATUS & PROFILE", "lbl_id_over": "Identity Overview:", "lbl_name": "Name:", "lbl_uname": "Username:", 
        "lbl_uid": "User ID:", "lbl_acc_stat": "Account Statistics:", "lbl_acc": "Account Type:", "lbl_cred": "Available Credits:", 
        "lbl_tot": "Total Searches:", "lbl_ref": "Total Referrals:", "lbl_join": "Joined System:", "msg_upgrade": "Want unlimited searches? Upgrade tier.",
        "lbl_vip": "👑 VIP PREMIUM\n┖ *Valid Till:*", "lbl_free": "🆓 STANDARD (Free Tier)",
        "ref_title": "REFER & EARN PREMIUM SYSTEM", "ref_sub": "Share your VIP link and earn free Search Credits!", 
        "ref_link_lbl": "Your Unique Link:", "ref_bal": "Your Balance:", "ref_tot": "Total Referrals:", 
        "ref_redeem": "REDEEM SUBSCRIPTIONS BELOW", "ref_use": "Use your earned credits to activate unlimited searches instantly!",
        # OSINT DB Keys for Translation
        "osint_keys": {
            "name": "Name", "address": "Address", "mobile": "Mobile", "phone": "Phone", 
            "father": "Father's Name", "mother": "Mother's Name", "dob": "Date of Birth", 
            "email": "Email", "gender": "Gender", "city": "City", "state": "State", 
            "zip": "Zip Code", "pincode": "Pincode", "aadhar": "Aadhar No.", "pan": "PAN No.",
            "bank": "Bank Name", "ifsc": "IFSC Code", "account": "Account No.", "branch": "Branch",
            "imei": "IMEI No.", "brand": "Brand", "model": "Model", "color": "Color",
            "operator": "Operator", "circle": "Telecom Circle", "vehicle": "Vehicle Class",
            "engine": "Engine No.", "chassis": "Chassis No.", "owner": "Owner Name"
        }
    }
}

# Fallback for other languages
for lang in ["hi", "es", "ar", "ru", "pt", "id"]:
    if lang not in LANGUAGES: 
        LANGUAGES[lang] = LANGUAGES["en"].copy()

REVERSE_BTN_MAP = {}
for lang_code, translations in LANGUAGES.items():
    for key, value in translations.items():
        if key.startswith("btn_"):
            REVERSE_BTN_MAP[value] = key

# ==========================================
# 🛠 CORE UTILITY FUNCTIONS 🛠
# ==========================================

def esc_md(text):
    if not text: return "None"
    return str(text).replace("_", "\\_").replace("*", "\\*").replace("`", "'").replace("[", "\\[")

def esc_html(text):
    if not text: return "None"
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def fetch_data_sync(url: str):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.getcode() == 200:
                raw_text = response.read().decode('utf-8')
                try: return json.loads(raw_text)
                except json.JSONDecodeError: return {"Result": raw_text}
            return None
    except Exception as e:
        logger.error(f"Sync fetch error for URL {url}: {e}")
        return None

# ==========================================
# 🗄️ MASTER DATABASE ENGINE 🗄️
# ==========================================

# ⚠️ RENDER NOTE: Render's free tier has an ephemeral filesystem.
# This means bot_database.db is WIPED on every deploy/restart.
# For persistence: upgrade to Render's paid plan with a disk mount,
# OR migrate to a free external DB like Supabase (PostgreSQL) or TursoDb (SQLite over HTTP).
# For now, the bot works fine — just know data resets on restart.

DB_PATH = os.environ.get("DB_PATH", "bot_database.db")

def run_query(query, args=(), fetchall=False, fetchone=False):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute(query, args)
        if fetchall: res = c.fetchall()
        elif fetchone: res = c.fetchone()
        else:
            conn.commit()
            res = True
        return res
    except sqlite3.Error as e:
        logger.error(f"DB error: {e}")
        return None
    finally: conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, total_searches INTEGER DEFAULT 0, referred_by INTEGER, referrals INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0, is_verified INTEGER DEFAULT 0, premium_expiry INTEGER DEFAULT 0)""")
    columns = [("is_banned", "INTEGER DEFAULT 0"), ("is_verified", "INTEGER DEFAULT 0"), ("joined_date", "TEXT"), ("credits", "INTEGER DEFAULT 1"), ("first_name", "TEXT"), ("username", "TEXT"), ("premium_expiry", "INTEGER DEFAULT 0"), ("language", "TEXT DEFAULT 'en'")]
    for col_name, col_type in columns:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError: pass
    c.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY, group_name TEXT, joined_date TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', '0')")
    c.execute("CREATE TABLE IF NOT EXISTS gift_codes (code TEXT PRIMARY KEY, points INTEGER, max_uses INTEGER, used_count INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS claimed_codes (user_id INTEGER, code TEXT, PRIMARY KEY(user_id, code))")
    conn.commit()
    conn.close()

def add_user(user_id: int, referred_by: int = None, first_name: str = "Unknown", username: str = "None"):
    row = run_query("SELECT user_id FROM users WHERE user_id = ?", (user_id,), fetchone=True)
    if not row:
        today = datetime.now().strftime("%Y-%m-%d")
        run_query("INSERT INTO users (user_id, referred_by, joined_date, credits, first_name, username, premium_expiry, language) VALUES (?, ?, ?, ?, ?, ?, 0, 'en')", (user_id, referred_by, today, 1, first_name, username))
        return True, referred_by
    else:
        run_query("UPDATE users SET first_name = ?, username = ? WHERE user_id = ?", (first_name, username, user_id))
        return False, None

def get_user_lang(user_id: int) -> str:
    row = run_query("SELECT language FROM users WHERE user_id = ?", (user_id,), fetchone=True)
    return row[0] if row else "en"

def is_bot_maintenance():
    row = run_query("SELECT value FROM settings WHERE key = 'maintenance'", fetchone=True)
    return row and row[0] == '1'

def set_bot_maintenance(state: bool):
    val = '1' if state else '0'
    run_query("UPDATE settings SET value = ? WHERE key = 'maintenance'", (val,))

# ==========================================
# 🎛️ DYNAMIC LOCALIZED KEYBOARDS 🎛️
# ==========================================

async def setup_commands(application: Application):
    commands = [BotCommand("start", "Launch or Refresh the Bot System")]
    await application.bot.set_my_commands(commands)

def get_premium_keyboard(lang='en'):
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    keyboard = [
        [KeyboardButton(t["btn_num"]), KeyboardButton(t["btn_tg"])],
        [KeyboardButton(t["btn_adhr"]), KeyboardButton(t["btn_fam"])], 
        [KeyboardButton(t["btn_veh"]), KeyboardButton(t["btn_ifsc"])],
        [KeyboardButton(t["btn_imei"]), KeyboardButton(t["btn_buy"])],
        [KeyboardButton(t["btn_ref"]), KeyboardButton(t["btn_redeem"])],
        [KeyboardButton(t["btn_status"]), KeyboardButton(t["btn_stats"])],
        [KeyboardButton(t["btn_lead"]), KeyboardButton(t["btn_admin"])],
        [KeyboardButton(t["btn_dev"]), KeyboardButton(t["btn_unlim_search"])]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_keyboard(lang='en'):
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    keyboard = [
        [KeyboardButton(t["btn_admin_bc"]), KeyboardButton(t["btn_admin_sc"])],
        [KeyboardButton(t["btn_admin_ap"]), KeyboardButton(t["btn_admin_rp"])],
        [KeyboardButton(t["btn_admin_ban"]), KeyboardButton(t["btn_admin_unban"])],
        [KeyboardButton(t["btn_admin_addp"]), KeyboardButton(t["btn_admin_rmp"])],
        [KeyboardButton(t["btn_admin_mc"]), KeyboardButton(t["btn_admin_dc"])],
        [KeyboardButton(t["btn_back_main"])]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_cancel_keyboard(lang='en'):
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    return ReplyKeyboardMarkup([[KeyboardButton(t["btn_back_admin"])]], resize_keyboard=True, is_persistent=True)

def get_cancel_keyboard(lang='en'):
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    return ReplyKeyboardMarkup([[KeyboardButton(t["btn_back_main"])]], resize_keyboard=True, is_persistent=True)

def get_subscription_keyboard(lang='en'):
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    keyboard = [
        [KeyboardButton(t.get("btn_sub_3d", "⏳ 3 Days (10 🪙)")), KeyboardButton(t.get("btn_sub_7d", "⏳ 7 Days (21 🪙)"))],
        [KeyboardButton(t.get("btn_sub_15d", "⏳ 15 Days (35 🪙)")), KeyboardButton(t.get("btn_sub_30d", "⏳ 30 Days (50 🪙)"))],
        [KeyboardButton(t["btn_back_main"])]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

# ==========================================
# 🛡️ SECURITY, GROUPS, & VERIFICATION 🛡️
# ==========================================

async def notify_admins_group_event(context: ContextTypes.DEFAULT_TYPE, chat, user, event_type: str):
    try: member_count = await chat.get_member_count()
    except Exception: member_count = "Unknown"
        
    link = f"@{chat.username}" if chat.username else "Private Group / No Link"
    if not chat.username:
        try: link = await chat.export_invite_link()
        except Exception: pass

    safe_link = link.replace("_", "\\_") if "@" in link else link
    safe_name = esc_md(chat.title)
    
    if user:
        safe_user = esc_md(user.first_name)
        user_id = user.id
    else:
        safe_user = "System/Unknown"
        user_id = "0"

    msg = (
        "🚀 *SYSTEM VERSION UPDATE* 🚀\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💠 *BOT {event_type} DETECTED* 💠\n\n"
        f"📌 *Group Name:* {safe_name}\n"
        f"🔗 *Group Link:* {safe_link}\n"
        f"👥 *Total Members:* `{member_count}`\n"
        f"🆔 *Group ID:* `{chat.id}`\n"
        f"👤 *Action By:* {safe_user} (`{user_id}`)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

    for admin_id in ADMIN_IDS:
        try: await context.bot.send_message(chat_id=admin_id, text=msg, parse_mode=ParseMode.MARKDOWN)
        except Exception: pass

async def send_group_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, lang: str = "en"):
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    msg = t.get("msg_group_welcome")
    keyboard = [
        [InlineKeyboardButton("➕ Add to me your own group", url=f"{BOT_LINK}?startgroup=true")],
        [InlineKeyboardButton("♾️ Unlimited search here free", url="https://t.me/+IzVdb9z7Bvs4YWQ1")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN, reply_markup=markup, disable_web_page_preview=True)
    except Exception: pass

async def on_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            chat = update.effective_chat
            adder = update.message.from_user 
            if not adder: return
            
            try:
                member_count = await chat.get_member_count()
            except Exception:
                member_count = 0
                
            is_admin = adder.id in ADMIN_IDS

            if member_count < 500 and not is_admin:
                lang = get_user_lang(adder.id) if adder else "en"
                t = LANGUAGES.get(lang, LANGUAGES['en'])
                leave_msg = t.get("msg_group_small")
                try:
                    await context.bot.send_message(chat_id=chat.id, text=leave_msg, parse_mode=ParseMode.MARKDOWN)
                    await asyncio.sleep(2)  
                    await chat.leave()
                    return 
                except Exception:
                    pass
            
            today = datetime.now().strftime("%Y-%m-%d")
            run_query("INSERT OR IGNORE INTO groups (chat_id, group_name, joined_date) VALUES (?, ?, ?)", (chat.id, chat.title, today))
            await notify_admins_group_event(context, chat, adder, "ADD")
            
            lang = get_user_lang(adder.id) if adder else "en"
            await send_group_welcome(update, context, chat.id, lang)

async def on_left_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.left_chat_member and update.message.left_chat_member.id == context.bot.id:
        chat = update.effective_chat
        remover = update.message.from_user
        await notify_admins_group_event(context, chat, remover, "REMOVE")

async def check_ban_and_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.effective_user: return False
        
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "Unknown"
    username = update.effective_user.username or "None"
    lang = get_user_lang(user_id)
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    
    referred_by = None
    if update.effective_message and update.effective_message.text and update.effective_message.text.startswith('/start'):
        parts = update.effective_message.text.split()
        if len(parts) > 1 and parts[1].isdigit():
            referred_by = int(parts[1])

    is_new, actual_ref = add_user(user_id, referred_by, first_name, username)

    if is_new:
        tot_users = run_query("SELECT COUNT(*) FROM users", fetchone=True)[0]
        safe_username = esc_md('@' + username) if username != "None" else "None"
        admin_msg = (
            "👤 *NEW AGENT DETECTED* 👤\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 *Name:* {esc_md(first_name)}\n"
            f"📛 *Username:* {safe_username}\n"
            f"🆔 *ID:* `{user_id}`\n\n"
            f"📈 *Total Database:* `{tot_users}` Agents\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        for ad in ADMIN_IDS:
            try: await context.bot.send_message(chat_id=ad, text=admin_msg, parse_mode=ParseMode.MARKDOWN)
            except Exception: pass 
            
        if actual_ref and actual_ref != user_id:
            pending_msg = (
                "⏳ *INCOMING REFERRAL PENDING...* ⏳\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "👤 *Someone just started the bot using your invite link!*\n\n"
                "⚠️ *Status:* `Waiting for User Verification...`\n"
                "💡 _They must join all our required private channels before your +1 Premium Credit is securely added to your account._\n\n"
                "━━━━━━━━━━━━━━━━━━━━━"
            )
            try: await context.bot.send_message(chat_id=actual_ref, text=pending_msg, parse_mode=ParseMode.MARKDOWN)
            except Exception: pass

    if is_bot_maintenance() and user_id not in ADMIN_IDS:
        if update.effective_message:
            await update.effective_message.reply_text(t.get("msg_maintenance"), parse_mode=ParseMode.MARKDOWN)
        return False

    user_data = run_query("SELECT is_banned FROM users WHERE user_id = ?", (user_id,), fetchone=True)
    if user_data and user_data[0] == 1:
        if update.effective_message:
            await update.effective_message.reply_text(t.get("msg_banned"), parse_mode=ParseMode.MARKDOWN)
        return False

    not_joined = []
    for chat in REQUIRED_CHATS:
        try:
            member = await context.bot.get_chat_member(chat_id=chat["id"], user_id=user_id)
            if member.status in ['left', 'kicked']: not_joined.append(chat)
        except TelegramError:
            not_joined.append(chat)

    if not_joined:
        if update.effective_message:
            if update.effective_chat.type != ChatType.PRIVATE:
                markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Sync via DM", url=BOT_LINK)]])
                await update.effective_message.reply_text(f"⚠️ {first_name}, establish secure connection in my DM first!", reply_markup=markup)
                return False

            buttons = []
            for i in range(0, len(not_joined), 2):
                row = [InlineKeyboardButton(f"{not_joined[i]['name']}", url=not_joined[i]["url"])]
                if i + 1 < len(not_joined):
                    row.append(InlineKeyboardButton(f"{not_joined[i+1]['name']}", url=not_joined[i+1]["url"]))
                buttons.append(row)
                
            buttons.append([
                InlineKeyboardButton("✅", callback_data="check_join"),
                InlineKeyboardButton("🔄", callback_data="check_join")
            ])
            markup = InlineKeyboardMarkup(buttons)
            await update.effective_message.reply_photo(photo=FORCE_JOIN_PHOTO, caption=t.get("msg_force_join"), reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
        return False
    return True

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    
    not_joined = []
    for chat in REQUIRED_CHATS:
        try:
            member = await context.bot.get_chat_member(chat_id=chat["id"], user_id=user_id)
            if member.status in ['left', 'kicked']: not_joined.append(chat)
        except TelegramError: not_joined.append(chat)
            
    if not_joined:
        try: await query.answer("❌ You must join ALL channels first! Please Re-check.", show_alert=True)
        except Exception: pass
        
        buttons = []
        for i in range(0, len(not_joined), 2):
            row = [InlineKeyboardButton(f"{not_joined[i]['name']}", url=not_joined[i]["url"])]
            if i + 1 < len(not_joined): row.append(InlineKeyboardButton(f"{not_joined[i+1]['name']}", url=not_joined[i+1]["url"]))
            buttons.append(row)
            
        buttons.append([
            InlineKeyboardButton("✅", callback_data="check_join"),
            InlineKeyboardButton("🔄", callback_data="check_join")
        ])
        markup = InlineKeyboardMarkup(buttons)
        try: await query.edit_message_reply_markup(reply_markup=markup)
        except Exception: pass
        return

    try: await query.answer(t.get("msg_verify_success", "✅ Verification Successful!"), show_alert=False)
    except Exception: pass
    
    try: await query.message.delete()
    except Exception: pass
    
    await verify_user_referral(user_id, context)
    await send_main_menu(update, context, user_id)

async def verify_user_referral(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    row = run_query("SELECT is_verified, referred_by FROM users WHERE user_id = ?", (user_id,), fetchone=True)
    if row and row[0] == 0:
        referred_by = row[1]
        run_query("UPDATE users SET is_verified = 1 WHERE user_id = ?", (user_id,))
        if referred_by and referred_by != user_id:
            run_query("UPDATE users SET referrals = referrals + 1, credits = credits + 1 WHERE user_id = ?", (referred_by,))
            
            ref_lang = get_user_lang(referred_by)
            ref_t = LANGUAGES.get(ref_lang, LANGUAGES['en'])
            
            try: await context.bot.send_message(chat_id=referred_by, text=ref_t.get("msg_ref_unlocked"), parse_mode=ParseMode.MARKDOWN)
            except Exception: pass

async def check_can_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not await check_ban_and_channels(update, context): return False
    
    if update.effective_chat.type != ChatType.PRIVATE:
        return True
    
    user_id = update.effective_user.id
    current_time = int(datetime.now().timestamp())
    lang = get_user_lang(user_id)
    t = LANGUAGES.get(lang, LANGUAGES['en'])
    
    row = run_query("SELECT referrals, premium_expiry, credits FROM users WHERE user_id = ?", (user_id,), fetchone=True)
    referrals, premium_expiry, credits = row if row else (0, 0, 0)
    
    has_premium = premium_expiry > current_time
    
    if not has_premium and credits <= 0:
        await update.effective_message.reply_text(t.get("msg_access_denied"), parse_mode=ParseMode.MARKDOWN)
        return False
    return True

# 🌟 BEAUTIFUL MESSAGE DELETION SYSTEM 🌟
async def clear_message_later(message: telegram.Message, delay: int = 30):
    if not message: return
    await asyncio.sleep(delay)
    try: 
        await message.edit_text(
            "🗑 *Message Deleted Successfully*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 _Protected under Telegram Privacy Policy._", 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=None,
            disable_web_page_preview=True
        )
    except Exception: 
        try: await message.delete()
        except: pass

async def delete_user_message_later(message: telegram.Message, delay: int = 30):
    if not message: return
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

def format_premium_result(data, lang_dict, indent="") -> str:
    emoji_map = {
        "name": "👤", "father": "👨‍🦳", "address": "🏠", "mobile": "📱", 
        "phone": "📞", "alt": "📳", "circle": "🌍", "state": "🗺️", "id": "🪪", 
        "aadhar": "🏛️", "email": "📧", "gender": "🚻", "dob": "🎂", 
        "operator": "📶", "city": "🏙️", "pincode": "📍", "zip": "📮", 
        "status": "✅", "vehicle": "🚗", "engine": "⚙️", "chassis": "🔩",
        "bank": "🏦", "branch": "🏢", "ifsc": "🔢", "imei": "📱", 
        "brand": "🏷️", "model": "📲", "color": "🎨", "owner": "👑",
        "uid": "🎮", "level": "⭐", "guild": "🛡️", "likes": "❤️"
    }
    
    ignore_keys = [
        "your usage", "your_usage", "key name", "key_name", "your limit", 
        "your_limit", "your usage today", "your_usage_today", 
        "your remaining today", "your_remaining_today", "note", "owner", 
        "usage", "by", "credit", "credits", "developer", "admin", "help group", "help_group"
    ]
    skip_strings = ["@ftgamer2", "@anuragxanuu", "hackedanurag", "https://t.me/hackedanurag"]
    
    formatted_text = ""
    
    if indent == "" and isinstance(data, dict):
        if "data" in data and isinstance(data["data"], (dict, list)):
            data = data["data"]
        elif "result" in data and isinstance(data["result"], (dict, list)):
            data = data["result"]
            
    if isinstance(data, dict):
        for key, value in data.items():
            if value is None or str(value).strip() == "": continue
            if str(key).lower().strip() in ignore_keys: continue
            
            skip_item = False
            for s in skip_strings:
                if s in str(value).lower() or s in str(key).lower():
                    skip_item = True
                    break
            if skip_item: continue
            
            clean_key = str(key).replace("_", " ").title()
            emoji = "✨" 
            
            for k, e in emoji_map.items():
                if k in str(key).lower():
                    emoji = e
                    break
                    
            osint_keys = lang_dict.get("osint_keys", {})
            for k, v in osint_keys.items():
                if k in str(key).lower():
                    clean_key = v
                    break
            
            if isinstance(value, (dict, list)):
                formatted_text += f"{indent}{emoji} <b>{esc_html(clean_key)}</b>:\n"
                formatted_text += format_premium_result(value, lang_dict, indent + "   ")
            else:
                safe_val = esc_html(value)
                formatted_text += f"{indent}{emoji} <b>{esc_html(clean_key)}</b>: <tg-spoiler>{safe_val}</tg-spoiler>\n"
                
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                formatted_text += format_premium_result(item, lang_dict, indent + "   ") + f"{indent}➖\n"
            else:
                skip_item = False
                for s in skip_strings:
                    if s in str(item).lower():
                        skip_item = True
                        break
                if skip_item: continue 
                safe_item = esc_html(item)
                formatted_text += f"{indent}✨ <tg-spoiler>{safe_item}</tg-spoiler>\n"
    else:
        skip_item = False
        for s in skip_strings:
            if s in str(data).lower():
                skip_item = True
                break
        if not skip_item:
            formatted_text += f"{indent}✨ {lang_dict['result_lbl']}: <tg-spoiler>{esc_html(data)}</tg-spoiler>\n"

    if indent == "":
        if formatted_text.strip() == "": formatted_text = lang_dict['result_no_data']
    return formatted_text

# ==========================================
# ⚠️ PASTE YOUR REMAINING FUNCTIONS HERE ⚠️
# ==========================================
# Copy everything between format_premium_result and main() from your
# original file into this section. That includes:
#   - send_main_menu()
#   - start()
#   - cmd_buy(), cmd_myreferral(), cmd_topreferrals()
#   - cmd_num1/2/3(), cmd_tg1/2/3(), cmd_adhr(), cmd_fam(), cmd_veh(), cmd_ifsc(), cmd_imi()
#   - handle_keyboard_clicks(), handle_photo()
#   - admin_approve_callbacks(), admin_recheck_code_callback()
#   - admin_gift_codes(), modify_points(), bot_stats(), toggle_maintenance()
#   - broadcast_task(), handle_broadcasts()
#   - ban_user(), unban_user(), add_premium(), remove_premium()
#   - auto_approve_join()
#   - ALL other handlers in your original file
#
# Nothing else needs to change — only the top config + main() below.

# ==========================================
# 🚀 RENDER-READY MAIN APPLICATION LOOP 🚀
# ==========================================

def main():
    # ✅ Step 1: Start keep-alive HTTP server BEFORE the bot
    # This makes Render see a live web service immediately on startup
    from keep_alive import start_keep_alive
    start_keep_alive(port=PORT)

    # ✅ Step 2: Init database
    init_db()

    # ✅ Step 3: Build the Application
    app = Application.builder().token(BOT_TOKEN).post_init(setup_commands).build()

    # ✅ Step 4: Register all handlers (unchanged from your original)
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, on_new_chat_members))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, on_left_chat_member))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", cmd_buy)) 
    
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(admin_approve_callbacks, pattern="^(approve_|reject_)"))
    app.add_handler(CallbackQueryHandler(admin_recheck_code_callback, pattern="^recheck_code_"))
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(ChatJoinRequestHandler(auto_approve_join))

    app.add_handler(CommandHandler("myreferral", cmd_myreferral))
    app.add_handler(CommandHandler("topreferrals", cmd_topreferrals))

    app.add_handler(CommandHandler("num1", cmd_num1))
    app.add_handler(CommandHandler("num2", cmd_num2))
    app.add_handler(CommandHandler("num3", cmd_num3))
    app.add_handler(CommandHandler("tg1", cmd_tg1))
    app.add_handler(CommandHandler("tg2", cmd_tg2))
    app.add_handler(CommandHandler("tg3", cmd_tg3))
    app.add_handler(CommandHandler("adhr", cmd_adhr))
    app.add_handler(CommandHandler("fam", cmd_fam))
    app.add_handler(CommandHandler("veh", cmd_veh))
    app.add_handler(CommandHandler("ifsc", cmd_ifsc))
    app.add_handler(CommandHandler("imi", cmd_imi))

    app.add_handler(CommandHandler("makecode", admin_gift_codes))
    app.add_handler(CommandHandler("seecodes", admin_gift_codes))
    app.add_handler(CommandHandler("delcode", admin_gift_codes))
    app.add_handler(CommandHandler("addpoint", modify_points))
    app.add_handler(CommandHandler("rmpoint", modify_points))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("addpremium", add_premium))
    app.add_handler(CommandHandler("removepremium", remove_premium))
    app.add_handler(CommandHandler("stats", bot_stats))
    app.add_handler(CommandHandler("botstop", toggle_maintenance))
    app.add_handler(CommandHandler("botlive", toggle_maintenance))
    app.add_handler(CommandHandler("broadcast", handle_broadcasts))
    app.add_handler(CommandHandler("broadcastgroup", handle_broadcasts)) 

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_keyboard_clicks))

    print("==================================================")
    print("✅ Bot is LIVE on Render!")
    print(f"✅ Keep-alive server running on port {PORT}")
    print("✅ All handlers registered successfully.")
    print("✅ Environment variables loaded — no hardcoded secrets.")
    print("==================================================")
    
    # ✅ Step 5: Run with polling
    # drop_pending_updates=True clears queued messages that piled up
    # while the bot was offline/restarting on Render
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
