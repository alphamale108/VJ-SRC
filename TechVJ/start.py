# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram

from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
    UserAlreadyParticipant,
    InviteHashExpired,
    UsernameNotOccupied
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from config import (
    API_ID,
    API_HASH,
    ERROR_MESSAGE,
    LOGIN_SYSTEM,
    STRING_SESSION,
    CHANNEL_ID,
    WAITING_TIME
)

from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser


class batch_temp(object):
    IS_BATCH = {}


# =========================
# DOWNLOAD STATUS
# =========================

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()

        try:
            await client.edit_message_text(
                chat,
                message.id,
                f"**Downloaded:** **{txt}**"
            )
            await asyncio.sleep(10)

        except Exception:
            await asyncio.sleep(5)


# =========================
# UPLOAD STATUS
# =========================

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()

        try:
            await client.edit_message_text(
                chat,
                message.id,
                f"**Uploaded:** **{txt}**"
            )
            await asyncio.sleep(10)

        except Exception:
            await asyncio.sleep(5)


# =========================
# PROGRESS
# =========================

def progress(current, total, message, type):
    with open(
        f"{message.id}{type}status.txt",
        "w"
    ) as fileup:
        fileup.write(
            f"{current * 100 / total:.1f}%"
        )


# =========================
# START COMMAND
# =========================

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(
            message.from_user.id,
            message.from_user.first_name
        )

    buttons = [
        [
            InlineKeyboardButton(
                "❣️ Developer",
                url="https://t.me/kingvj01"
            )
        ],
        [
            InlineKeyboardButton(
                "🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ",
                url="https://t.me/vj_bot_disscussion"
            ),
            InlineKeyboardButton(
                "🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ",
                url="https://t.me/vj_botz"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await client.send_message(
        chat_id=message.chat.id,
        text=(
            f"<b>👋 Hi {message.from_user.mention}, "
            f"I am Save Restricted Content Bot, I can send you "
            f"restricted content by its post link.\n\n"
            f"For downloading restricted content /login first.\n\n"
            f"Know how to use bot by - /help</b>"
        ),
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )


# =========================
# HELP COMMAND
# =========================

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):

    await client.send_message(
        chat_id=message.chat.id,
        text=HELP_TXT
    )


# =========================
# CANCEL COMMAND
# =========================

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):

    batch_temp.IS_BATCH[message.from_user.id] = True

    await client.send_message(
        chat_id=message.chat.id,
        text="**Batch Successfully Cancelled.**"
    )


# =========================
# SAVE
# =========================

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):

    # =========================
    # JOIN CHAT
    # =========================

    if (
        (
            "https://t.me/+" in message.text
            or "https://t.me/joinchat/" in message.text
        )
        and LOGIN_SYSTEM == False
    ):

        if TechVJUser is None:
            await client.send_message(
                message.chat.id,
                "String Session is not Set",
                reply_to_message_id=message.id
            )
            return

        try:

            await TechVJUser.join_chat(message.text)

            await client.send_message(
                message.chat.id,
                "Chat Joined",
                reply_to_message_id=message.id
            )

        except UserAlreadyParticipant:

            await client.send_message(
                message.chat.id,
                "Chat already Joined",
                reply_to_message_id=message.id
            )

        except InviteHashExpired:

            await client.send_message(
                message.chat.id,
                "Invalid Link",
                reply_to_message_id=message.id
            )

        except Exception as e:

            await client.send_message(
                message.chat.id,
                f"Error : {e}",
                reply_to_message_id=message.id
            )

        return

    # =========================
    # TELEGRAM LINK
    # =========================

    if "https://t.me/" not in message.text:
        return

    # =========================
    # CHECK BATCH
    # =========================

    if batch_temp.IS_BATCH.get(message.from_user.id) == False:

        return await message.reply_text(
            "**One Task Is Already Processing. "
            "Wait For Complete It. "
            "If You Want To Cancel This Task Then Use - /cancel**"
        )

    # =========================
    # PARSE LINK
    # =========================

    datas = message.text.split("/")

    temp = (
        datas[-1]
        .replace("?single", "")
        .split("-")
    )

    try:

        fromID = int(temp[0].strip())

    except Exception:

        return await message.reply_text(
            "**Invalid Telegram post link.**"
        )

    try:

        toID = int(temp[1].strip())

    except Exception:

        toID = fromID

    # Check if it's a batch
    is_batch = (toID - fromID) > 0
    if is_batch:
        await client.send_message(
            message.chat.id,
            f"**📦 Processing Batch:** {fromID} to {toID}\n"
            f"Total: {toID - fromID + 1} messages\n"
            f"Use /cancel to stop."
        )

    # =========================
    # LOGIN SYSTEM
    # =========================

    acc = None  # Initialize acc

    if LOGIN_SYSTEM == True:

        user_data = await db.get_session(
            message.from_user.id
        )

        if user_data is None:

            await message.reply(
                "**For downloading restricted content "
                "you have to /login first.**"
            )

            return

        api_id = int(
            await db.get_api_id(
                message.from_user.id
            )
        )

        api_hash = await db.get_api_hash(
            message.from_user.id
        )

        try:

            acc = Client(
                "saverestricted",
                session_string=user_data,
                api_hash=api_hash,
                api_id=api_id
            )

            await acc.connect()

        except Exception as e:

            return await message.reply(
                f"**Your Login Session Expired. "
                f"So /logout First Then Login Again By - /login**\n"
                f"Error: {e}"
            )

    else:

        # Use main bot session for public links
        if TechVJUser is None:
            await client.send_message(
                message.chat.id,
                "**String Session is not Set. Cannot process restricted content.**",
                reply_to_message_id=message.id
            )
            return
        
        acc = TechVJUser

    # =========================
    # START BATCH
    # =========================

    batch_temp.IS_BATCH[
        message.from_user.id
    ] = False

    processed_count = 0
    total_messages = toID - fromID + 1

    try:

        for msgid in range(
            fromID,
            toID + 1
        ):

            # =========================
            # CANCEL CHECK
            # =========================

            if batch_temp.IS_BATCH.get(
                message.from_user.id
            ):
                await client.send_message(
                    message.chat.id,
                    "**⛔ Batch Cancelled by User.**"
                )
                break

            # =========================
            # PROGRESS UPDATE (for batches)
            # =========================
            
            if is_batch and (processed_count % 5 == 0 or processed_count == total_messages - 1):
                await client.send_message(
                    message.chat.id,
                    f"**📊 Progress:** {processed_count}/{total_messages} messages processed"
                )

            # =========================
            # PRIVATE CHANNEL
            # =========================

            if "https://t.me/c/" in message.text:

                if acc is None:

                    await client.send_message(
                        message.chat.id,
                        "**This type of link requires "
                        "a String Session. Please /login first.**",
                        reply_to_message_id=message.id
                    )

                    break

                try:

                    chatid = int(
                        "-100" + datas[4]
                    )

                    await handle_private(
                        client,
                        acc,
                        message,
                        chatid,
                        msgid
                    )

                except Exception as e:

                    if ERROR_MESSAGE == True:

                        await client.send_message(
                            message.chat.id,
                            f"Error on message {msgid}: {e}",
                            reply_to_message_id=message.id
                        )

            # =========================
            # BOT LINK
            # =========================

            elif "https://t.me/b/" in message.text:

                if acc is None:

                    await client.send_message(
                        message.chat.id,
                        "**This type of link requires "
                        "a String Session. Please /login first.**",
                        reply_to_message_id=message.id
                    )

                    break

                try:

                    username = datas[4]

                    await handle_private(
                        client,
                        acc,
                        message,
                        username,
                        msgid
                    )

                except Exception as e:

                    if ERROR_MESSAGE == True:

                        await client.send_message(
                            message.chat.id,
                            f"Error on message {msgid}: {e}",
                            reply_to_message_id=message.id
                        )

            # =========================
            # PUBLIC CHANNEL
            # =========================

            else:

                try:

                    username = datas[3]

                    msg = await client.get_messages(
                        username,
                        msgid
                    )

                except UsernameNotOccupied:

                    await client.send_message(
                        message.chat.id,
                        f"Username '{username}' is not occupied by anyone.",
                        reply_to_message_id=message.id
                    )

                    break

                except Exception as e:

                    if ERROR_MESSAGE == True:

                        await client.send_message(
                            message.chat.id,
                            f"Error getting public post {msgid}: {e}",
                            reply_to_message_id=message.id
                        )

                    break

                # =========================
                # COPY PUBLIC MESSAGE
                # =========================

                try:

                    await client.copy_message(
                        message.chat.id,
                        msg.chat.id,
                        msg.id,
                        reply_to_message_id=message.id
                    )

                except Exception as e:

                    # If can't copy, try using account
                    if acc is not None:
                        try:
                            await handle_private(
                                client,
                                acc,
                                message,
                                username,
                                msgid
                            )
                        except Exception as e2:
                            if ERROR_MESSAGE == True:
                                await client.send_message(
                                    message.chat.id,
                                    f"Error on message {msgid}: {e2}",
                                    reply_to_message_id=message.id
                                )
                    else:
                        if ERROR_MESSAGE == True:
                            await client.send_message(
                                message.chat.id,
                                f"Unable to copy public post {msgid}: {e}",
                                reply_to_message_id=message.id
                            )

            processed_count += 1

            # =========================
            # WAIT
            # =========================

            if is_batch and processed_count < total_messages:
                await asyncio.sleep(
                    WAITING_TIME
                )

    except Exception as e:
        await client.send_message(
            message.chat.id,
            f"**❌ Error in batch processing:** {e}",
            reply_to_message_id=message.id
        )

    finally:

        # =========================
        # DISCONNECT USER SESSION
        # =========================

        if LOGIN_SYSTEM == True and acc is not None:

            try:

                await acc.disconnect()

            except Exception:

                pass

        # =========================
        # RESET BATCH
        # =========================

        batch_temp.IS_BATCH[
            message.from_user.id
        ] = True

        # =========================
        # COMPLETION MESSAGE
        # =========================

        if is_batch:
            status = "✅" if processed_count == total_messages else "⚠️"
            await client.send_message(
                message.chat.id,
                f"{status} **Batch Processing Complete!**\n"
                f"Processed: {processed_count}/{total_messages} messages"
            )


# =========================
# HANDLE PRIVATE
# =========================

async def handle_private(
    client: Client,
    acc,
    message: Message,
    chatid,
    msgid: int
):

    # Check if acc is None
    if acc is None:
        await client.send_message(
            message.chat.id,
            "**Error: No active session. Please /login first.**",
            reply_to_message_id=message.id
        )
        return

    msg: Message = await acc.get_messages(
        chatid,
        msgid
    )

    if msg.empty:
        return

    msg_type = get_message_type(msg)

    if not msg_type:
        return

    # =========================
    # DESTINATION CHAT
    # =========================

    if CHANNEL_ID:

        try:

            chat = int(CHANNEL_ID)

        except Exception:

            chat = message.chat.id

    else:

        chat = message.chat.id

    # =========================
    # CANCEL
    # =========================

    if batch_temp.IS_BATCH.get(
        message.from_user.id
    ):
        return

    # =========================
    # TEXT
    # =========================

    if msg_type == "Text":

        try:

            await client.send_message(
                chat,
                msg.text,
                entities=msg.entities,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML
            )

            return

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

            return

    # =========================
    # DOWNLOADING
    # =========================

    smsg = await client.send_message(
        message.chat.id,
        f"**📥 Downloading** message {msgid}",
        reply_to_message_id=message.id
    )

    asyncio.create_task(
        downstatus(
            client,
            f"{message.id}downstatus.txt",
            smsg,
            chat
        )
    )

    try:

        file = await acc.download_media(
            msg,
            progress=progress,
            progress_args=[message, "down"]
        )

        if os.path.exists(
            f"{message.id}downstatus.txt"
        ):
            os.remove(
                f"{message.id}downstatus.txt"
            )

    except Exception as e:

        if ERROR_MESSAGE == True:

            await client.send_message(
                message.chat.id,
                f"Error: {e}",
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML
            )

        await smsg.delete()
        return

    # =========================
    # CANCEL
    # =========================

    if batch_temp.IS_BATCH.get(
        message.from_user.id
    ):
        if file and os.path.exists(file):
            os.remove(file)
        return

    asyncio.create_task(
        upstatus(
            client,
            f"{message.id}upstatus.txt",
            smsg,
            chat
        )
    )

    # =========================
    # CAPTION
    # =========================

    if msg.caption:
        caption = msg.caption
    else:
        caption = None

    if batch_temp.IS_BATCH.get(
        message.from_user.id
    ):
        if file and os.path.exists(file):
            os.remove(file)
        return

    # =========================
    # DOCUMENT
    # =========================

    if msg_type == "Document":

        try:

            ph_path = await acc.download_media(
                msg.document.thumbs[0].file_id
            )

        except Exception:

            ph_path = None

        try:

            await client.send_document(
                chat,
                file,
                thumb=ph_path,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"]
            )

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

        if ph_path is not None:

            try:
                os.remove(ph_path)
            except Exception:
                pass

    # =========================
    # VIDEO
    # =========================

    elif msg_type == "Video":

        try:

            ph_path = await acc.download_media(
                msg.video.thumbs[0].file_id
            )

        except Exception:

            ph_path = None

        try:

            await client.send_video(
                chat,
                file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=ph_path,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"]
            )

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

        if ph_path is not None:

            try:
                os.remove(ph_path)
            except Exception:
                pass

    # =========================
    # ANIMATION
    # =========================

    elif msg_type == "Animation":

        try:

            await client.send_animation(
                chat,
                file,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

    # =========================
    # STICKER
    # =========================

    elif msg_type == "Sticker":

        try:

            await client.send_sticker(
                chat,
                file,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

    # =========================
    # VOICE
    # =========================

    elif msg_type == "Voice":

        try:

            await client.send_voice(
                chat,
                file,
                caption=caption,
                caption_entities=msg.caption_entities,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"]
            )

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

    # =========================
    # AUDIO
    # =========================

    elif msg_type == "Audio":

        try:

            ph_path = await acc.download_media(
                msg.audio.thumbs[0].file_id
            )

        except Exception:

            ph_path = None

        try:

            await client.send_audio(
                chat,
                file,
                thumb=ph_path,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"]
            )

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

        if ph_path is not None:

            try:
                os.remove(ph_path)
            except Exception:
                pass

    # =========================
    # PHOTO
    # =========================

    elif msg_type == "Photo":

        try:

            await client.send_photo(
                chat,
                file,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:

            if ERROR_MESSAGE == True:

                await client.send_message(
                    message.chat.id,
                    f"Error: {e}",
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML
                )

    # =========================
    # CLEANUP
    # =========================

    if os.path.exists(
        f"{message.id}upstatus.txt"
    ):

        try:
            os.remove(
                f"{message.id}upstatus.txt"
            )
        except Exception:
            pass

    if file and os.path.exists(file):

        try:
            os.remove(file)
        except Exception:
            pass

    try:

        await client.delete_messages(
            message.chat.id,
            [smsg.id]
        )

    except Exception:

        pass


# =========================
# GET MESSAGE TYPE
# =========================

def get_message_type(
    msg: pyrogram.types.messages_and_media.message.Message
):

    try:

        msg.document.file_id
        return "Document"

    except Exception:
        pass

    try:

        msg.video.file_id
        return "Video"

    except Exception:
        pass

    try:

        msg.animation.file_id
        return "Animation"

    except Exception:
        pass

    try:

        msg.sticker.file_id
        return "Sticker"

    except Exception:
        pass

    try:

        msg.voice.file_id
        return "Voice"

    except Exception:
        pass

    try:

        msg.audio.file_id
        return "Audio"

    except Exception:
        pass

    try:

        msg.photo.file_id
        return "Photo"

    except Exception:
        pass

    try:

        msg.text
        return "Text"

    except Exception:
        pass

    return None
