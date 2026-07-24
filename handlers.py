from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from analyzer import rewrite_resume, run_analysis
from file_parser import extract_text
from formatter import build_messages
from state import session


def _followup_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Analyze another JD", callback_data="action:reanalyze")],
        [InlineKeyboardButton("✏️ Rewrite my resume", callback_data="action:rewrite")],
        [InlineKeyboardButton("📊 Compare with another resume", callback_data="action:compare")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    session[chat_id] = {"stage": "awaiting_resume", "resume_text": None, "jd_text": None}
    await update.message.reply_text(
        "Welcome to ResumeBot! 🤖\n\n"
        "Please upload your resume as a PDF or DOCX file."
    )


async def _do_analysis(update: Update, user_state: dict) -> None:
    user_state["stage"] = "analyzing"
    status_msg = await update.message.reply_text("Analyzing... 🔍")
    try:
        result = await run_analysis(user_state["resume_text"], user_state["jd_text"])
        await status_msg.delete()
        messages = build_messages(result)
        for i, msg in enumerate(messages):
            if i == len(messages) - 1:
                await update.message.reply_text(msg, parse_mode="MarkdownV2", reply_markup=_followup_keyboard())
            else:
                await update.message.reply_text(msg, parse_mode="MarkdownV2")
    except Exception as e:
        await status_msg.delete()
        await update.message.reply_text(f"Analysis failed: {e}")
    user_state["stage"] = "done"


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_state = session.get(chat_id)
    if not user_state:
        await update.message.reply_text("Please start with /start first.")
        return

    file = await update.message.effective_attachment.get_file()
    content = await file.download_as_bytearray()
    text = extract_text(file.file_path or update.message.document.file_name, bytes(content))

    if not text or len(text.strip()) < 50:
        await update.message.reply_text(
            "The file seems unreadable (likely a scanned/image PDF). "
            "Please try another file with selectable text."
        )
        return

    if user_state["stage"] == "awaiting_resume":
        user_state["resume_text"] = text
        user_state["stage"] = "awaiting_jd"
        await update.message.reply_text(
            f"Resume received! ✅ (extracted {len(text)} characters)\n\n"
            "Now please paste the job description as text or upload a PDF/DOCX file."
        )
    elif user_state["stage"] == "awaiting_jd":
        user_state["jd_text"] = text
        await _do_analysis(update, user_state)
    else:
        await update.message.reply_text("Resume received!")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_state = session.get(chat_id)
    if not user_state:
        await update.message.reply_text("Please start with /start first.")
        return

    text = update.message.text

    if user_state["stage"] == "awaiting_resume":
        await update.message.reply_text(
            "Please upload your resume as a PDF or DOCX file."
        )
    elif user_state["stage"] == "awaiting_jd":
        user_state["jd_text"] = text
        await _do_analysis(update, user_state)
    else:
        await update.message.reply_text(
            "I'm not sure what to do with that. Use /start to begin again."
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    user_state = session.get(chat_id)

    if not user_state:
        await query.edit_message_text("Please start with /start first.")
        return

    action = query.data

    if action == "action:reanalyze":
        user_state["stage"] = "awaiting_jd"
        await query.edit_message_text(
            "I'll keep your resume loaded. Please paste a new job description or upload a PDF/DOCX."
        )

    elif action == "action:rewrite":
        await query.edit_message_text("Rewriting your resume... ✏️")
        try:
            result = await rewrite_resume(user_state["resume_text"], user_state["jd_text"])
            bullets = result.get("rewritten_bullets", [])
            if bullets:
                text = "*✏️ Rewritten Resume Bullets*\n\n" + "\n".join(
                    f"• {b}" for b in bullets
                )
            else:
                text = "No rewrite suggestions were generated."
            await query.message.reply_text(text, parse_mode="MarkdownV2")
        except Exception as e:
            await query.message.reply_text(f"Resume rewrite failed: {e}")

    elif action == "action:compare":
        await query.edit_message_text("Coming soon! 🚧")
