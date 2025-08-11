from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.isAdminFilter import IsAdmin
from keyboards.user_ReplyKeyboards import user_main_menu_keyboard
from keyboards.admin_InlineKeyboards import merge_row_keyboard
from utils.db_requests import *

router = Router()
router.callback_query.filter(IsAdmin())  # Исправлено: фильтр для callback

async def remove_inline_keyboard(callback: CallbackQuery):
    """Удаляет инлайн-клавиатуру с сообщения."""
    await callback.message.edit_reply_markup()

@router.callback_query(F.data == "calculate_communal")
async def handle_communal_calculation(
    callback: CallbackQuery, 
    bot: Bot, 
    state: FSMContext
):
    data = await state.get_data()
    flat = data["flat"]
    meters = data["meter"]
    
    bot.google_table.set_new_communal(flat, meters)
    db_set_new_communal(bot, flat, meters)

    await callback.answer(text="Данные успешно внесены в журнал")
    await remove_inline_keyboard(callback)

@router.callback_query(F.data == "login_agree")
async def handle_login_approval(
    callback: CallbackQuery, 
    bot: Bot
):
    user_id, flat = db_get_new_user_login()
    db_agree_user_login()
    bot.google_table.login_agree(user_id, flat)

    await bot.send_message(
        chat_id=user_id,
        text="Вы добавлены в список пользователей",
        reply_markup=user_main_menu_keyboard
    )

    await callback.answer(text="Пользователь успешно добавлен")
    await callback.message.answer(
        text="Добавить запись о заселении в Google таблицу?",
        reply_markup=merge_row_keyboard
    )
    await remove_inline_keyboard(callback)

@router.callback_query(F.data == "merge_row_agree")
async def handle_merge_row_approval(
    callback: CallbackQuery, 
    bot: Bot
):
    user_id, flat = db_get_new_user_login()
    bot.google_table.merge_row("Заселение", flat)
    db_merge_row(bot, "Заселение", flat)
    db_delete_login_users()

    await callback.answer(text="Запись успешно добавлена")
    await callback.message.answer(
        text="Не забудьте снять начальные показания счетчиков!"
    )
    await remove_inline_keyboard(callback)

@router.callback_query(F.data == "extraction_agree")
async def handle_extraction_approval(
    callback: CallbackQuery, 
    bot: Bot, 
    state: FSMContext
):
    data = await state.get_data()
    flat = data["flat"]
    
    try:
        bot.google_table.extraction_agree(flat)
        db_extraction_users(flat)
    except Exception:  # Уточнен тип исключения
        await callback.message.answer(
            text="В этой квартире и так никто не жил"
        )
        await callback.answer()
        await remove_inline_keyboard(callback)
        return

    bot.google_table.merge_row("Выселение", flat)
    db_merge_row(bot, "Выселение", flat)

    await callback.answer(text=f"Жильцы {flat} успешно удалены")
    await callback.message.answer(
        text="Не забудьте снять показания счетчиков"
    )
    await remove_inline_keyboard(callback)

@router.callback_query(F.data == "login_disagree")
async def handle_login_rejection(callback: CallbackQuery):
    db_delete_login_users()
    await callback.answer(text="Действие отклонено")
    await remove_inline_keyboard(callback)

@router.callback_query(F.data == "None")
async def handle_cancel_action(callback: CallbackQuery):
    await callback.answer(text="Действие отклонено")
    await remove_inline_keyboard(callback)
