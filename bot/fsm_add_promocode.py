from datetime import timedelta
from aiogram import Router, Bot, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
import kbds
from get_data import *
fsm_company=Router()
class AddCompany(StatesGroup):
    name=State()
    promo=State()
    days=State()
    slug=State()


@fsm_company.message(AddCompany.name,F.text)
async def company_name(message:types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    print(data["name"])
    await message.answer("ID рекламной кампании")
    await state.set_state(AddCompany.slug)


# @fsm_company.message(AddCompany.promo,F.text)
# async def company_name(message:types.Message, state:FSMContext):
#     await state.update_data(promo=message.text)
#     await message.answer("Количество дней промокода")
#     await state.set_state(AddCompany.days)
# @fsm_company.message(AddCompany.days,F.text)
# async def company_name(message:types.Message, state:FSMContext):
#     await state.update_data(days=message.text)
#     if message.text.isdigit() and int(message.text) <= 30:
#         await message.answer("ID рекламной кампании")
#         # await message.answer("Выберите действие",reply_markup=kbds.createkb({"Сохранить":"podtv_","Отменить":"otmena_"}))
#         await state.set_state(AddCompany.slug)
#
#
#     else:
#         await message.answer("Введите число от 1 до 30 календарных дней")

@fsm_company.message(AddCompany.slug,F.text)
async def company_name(message:types.Message, state:FSMContext):
    await state.update_data(slug=message.text)
    await message.answer("Выберите действие",
                         reply_markup=kbds.createkb({"Сохранить": "podtv_", "Отменить": "otmena_"}))
@fsm_company.callback_query(F.data.startswith("podtv_"))
async def podtv(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Кампания сохранена")
    await call.message.delete()
    await company_finish(state)

@fsm_company.callback_query(F.data.startswith("otmena_"))
async def otmena(call: types.CallbackQuery, state: FSMContext):
    await call.answer("Действие отменено")
    await state.clear()
    await call.message.delete()
async def company_finish(state:FSMContext):
    data = await state.get_data()
    print(data["name"])
    add_data={
        "name":data["name"],
        "promo":"null",
        "days":0,
        "slug":data["slug"]
    }
    await postpromo(add_data)
    await state.clear()


