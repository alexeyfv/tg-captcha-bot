import asyncio
import logging
import os
import random
from dataclasses import dataclass
from enum import Enum

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus
from aiogram.types import (
    CallbackQuery,
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from dotenv import load_dotenv

load_dotenv()

class CaptchaMode(Enum):
    SUBSCRIPTION = "subscription"
    EQUATION = "equation"
    BOTH = "both"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_STR = os.getenv("CHAT_ID")
CHANNEL_ID_STR = os.getenv("CHANNEL_ID")
INSTRUCTION_TEXT = os.getenv("INSTRUCTION_TEXT")
SUCCESS_TEXT = os.getenv("SUCCESS_TEXT")
BUTTON_TEXT = os.getenv("BUTTON_TEXT")
ANSWER_INCORRECT = os.getenv("ANSWER_INCORRECT")
NOT_SUBSCRIBED = os.getenv("NOT_SUBSCRIBED")

MODE = os.getenv("MODE", "subscription")
mode = CaptchaMode(MODE.lower())


# Bot setup
props = DefaultBotProperties(protect_content=True)
bot = Bot(token=BOT_TOKEN, default=props)
router = Router()
dp = Dispatcher()


@dataclass
class JoinRequestState:
    chat_id: int
    user_id: int
    expected_answer: int
    options: list[dict[str, int | str]]
    left: int
    right: int
    mode: CaptchaMode


join_states: dict[int, JoinRequestState] = {}


def _build_challenge() -> tuple[int, list[dict[str, int | str]], int, int]:
    left = random.randint(2, 9)
    right = random.randint(1, 8)
    expected = left + right
    options = {expected}
    while len(options) < 4:
        options.add(expected + random.randint(-5, 5))
    option_values = list(options)
    random.shuffle(option_values)
    formatted = [
        {"value": value, "label": f"{BUTTON_TEXT} {value}"} for value in option_values
    ]
    return expected, formatted, left, right


@router.chat_join_request()
async def handle_join_request(req: ChatJoinRequest):
    if req.chat.id != int(CHAT_ID_STR):
        return

    if mode in (CaptchaMode.EQUATION, CaptchaMode.BOTH):
        expected, options, left, right = _build_challenge()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=option["label"], callback_data=str(option["value"])
                    )
                ]
                for option in options
            ]
        )

        message_text = f"{INSTRUCTION_TEXT}\n\n{left} + {right} = ?"
    elif mode == CaptchaMode.SUBSCRIPTION:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=BUTTON_TEXT, callback_data="verify_subscription")]
            ]
        )
        message_text = INSTRUCTION_TEXT
    else:
        return

    await bot.send_message(req.from_user.id, message_text, reply_markup=keyboard)

    join_state = JoinRequestState(
        chat_id=req.chat.id,
        user_id=req.from_user.id,
        expected_answer=expected if mode in (CaptchaMode.EQUATION, CaptchaMode.BOTH) else 0,
        options=options if mode in (CaptchaMode.EQUATION, CaptchaMode.BOTH) else [],
        left=left if mode in (CaptchaMode.EQUATION, CaptchaMode.BOTH) else 0,
        right=right if mode in (CaptchaMode.EQUATION, CaptchaMode.BOTH) else 0,
        mode=mode,
    )

    join_states[req.from_user.id] = join_state


@router.callback_query()
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = join_states.get(user_id)

    if not state:
        await callback.answer("No active request.", show_alert=True)
        return

    # Check the answer if mode requires
    if state.mode in (CaptchaMode.EQUATION, CaptchaMode.BOTH):
        if not callback.data.isdigit():
            await callback.answer("Invalid response.", show_alert=True)
            return
        answer = int(callback.data)
        if answer != state.expected_answer:
            await bot.decline_chat_join_request(state.chat_id, state.user_id)
            del join_states[user_id]
            await callback.answer(ANSWER_INCORRECT, show_alert=True)
            return

    # Check subscription if mode requires
    if state.mode in (CaptchaMode.SUBSCRIPTION, CaptchaMode.BOTH):
        member = await bot.get_chat_member(CHANNEL_ID_STR, user_id)
        if member.status != ChatMemberStatus.MEMBER:
            await bot.decline_chat_join_request(state.chat_id, state.user_id)
            del join_states[user_id]
            await callback.answer(NOT_SUBSCRIBED, show_alert=True)
            return

    # Approve the join request
    await bot.approve_chat_join_request(state.chat_id, user_id)
    del join_states[user_id]
    await callback.answer(SUCCESS_TEXT, show_alert=True)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
