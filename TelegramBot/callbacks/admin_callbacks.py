from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.isAdminFilter import IsAdmin
from keyboards.user_ReplyKeyboards import user_main_menu_keyboard
from keyboards.admin_InlineKeyboards import merge_row_keyboard
from utils.db_requests import *

router = Router()
router.message.filter(IsAdmin())

@router.callback_query(F.data == "calculate_communal")
async def calculate_log(callback: CallbackQuery, bot: Bot, state: FSMContext):
    
    data = await state.get_data()
    
    flat = data["flat"]
    meters = data["meter"]
    
    bot.google_table.set_new_communal(flat, meters)
    db_set_new_communal(bot, flat, meters)

    await callback.message.edit_reply_markup()
    await callback.answer(text=f"Данные успешно внесены в журнал")



@router.callback_query(F.data == "login_agree")
async def login_log(callback: CallbackQuery, bot: Bot):
    
    user_id, flat = db_get_new_user_login()
    db_agree_user_login()

    bot.google_table.login_agree(user_id, flat)

    await bot.send_message(chat_id = user_id,
                            text = f"Вы добавлены в список пользователей",
                            reply_markup=user_main_menu_keyboard)

    await callback.answer(text=f"Пользователь успешно добавлен")
    await callback.message.answer(text=f"Добавить запись о заселении в Google таблицу?", reply_markup=merge_row_keyboard)
    

    await callback.message.edit_reply_markup()
    

@router.callback_query(F.data == "merge_row_agree")
async def merge_row_log(callback: CallbackQuery, bot: Bot):
    
    user_id, flat = db_get_new_user_login()

    bot.google_table.merge_row("Заселение", flat)
    db_merge_row(bot, "Заселение", flat)
    
    db_delete_login_users()

    await callback.answer(text=f"Запись успешно добавлена")
    await callback.message.answer(text=f"Не забудьте снять начальные показания счетчиков!")

    await callback.message.edit_reply_markup()


@router.callback_query(F.data == "extraction_agree")
async def extraction_log(callback: CallbackQuery, bot: Bot, state: FSMContext):

    data = await state.get_data()
    flat = data["flat"]

    try:
        bot.google_table.extraction_agree(flat)
        db_extraction_users(flat)
    except:
        await callback.message.answer(text=f"В этой квартире и так никто не жил")
        await callback.answer(text=f"")
        await callback.message.edit_reply_markup()  
        return

    bot.google_table.merge_row("Выселение", flat)
    db_merge_row(bot, "Выселение", flat)

    await callback.answer(text=f"Жильцы {flat} успешно удалены")
    await callback.message.answer(text=f"Не забудьте снять показания счетчиков")
    
    
    await callback.message.edit_reply_markup()


@router.callback_query(F.data == "login_disagree")
async def new_users_disagree(callback: CallbackQuery):

    db_delete_login_users()

    await callback.answer(text=f"Действие отклонено")
    await callback.message.edit_reply_markup()


@router.callback_query(F.data == "None")
async def cancel_log(callback: CallbackQuery):
    await callback.answer(text=f"Действие отклонено")
    await callback.message.edit_reply_markup()
