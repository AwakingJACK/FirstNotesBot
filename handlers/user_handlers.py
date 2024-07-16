from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from keyboards.buttons import choose_action

from database.orm_query import set_user
from database.models import User

from database.orm_query import orm_add_annotation, orm_deleate_annotation, orm_view_annotation
 



router = Router()


class Note(StatesGroup):
    write_annotation = State()
    deleate_annotation = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(tg_id=message.from_user.id)
    await message.answer(text='Привет😁\nЭто бот для записи заметок🧳')
    await message.answer(
        text='⬇️Выбери действие ниже⬇️',
        reply_markup=choose_action)


@router.message(Command('about'))
async def cmd_about(message: Message):
    await message.reply(text='Это простой бот который поможет тебе с ведением заметок')


@router.message(Command('menu'))
async def cmd_menu(message: Message):
    await message.reply(
        text='Выберите действие ниже⬇️',
        reply_markup=choose_action)


@router.message(StateFilter(None), F.text.casefold() == 'записать заметку')
async def cmd_write(message: Message, state: FSMContext, session: AsyncSession):
    query = select(exists().where(User.annotation != None))
    annotation_availability = await session.execute(query)
    result_annotation_availability = annotation_availability.scalar()

    if not result_annotation_availability:
        await message.answer(text='Запишите вашу заметку:', reply_markup=ReplyKeyboardRemove())
        await state.set_state(Note.write_annotation)
    else:
        await message.answer(
            text='Ваша заметка уже записана, вы можете посмотреть\изменить или удалить её',
            reply_markup=choose_action)


@router.message(Note.write_annotation, F.text)
async def write_hw(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(annotation=message.text)
    await state.update_data(tg_id=message.from_user.id)
    data = await state.get_data()
    await orm_add_annotation(session=session, annotation=data['annotation'],
                              tg_id=message.from_user.id)
    await message.answer(
        text=f'Ваша заметка записана📝\n\n{data["annotation"]}',
        reply_markup=choose_action)
    await state.clear()


@router.message(StateFilter(None), F.text.casefold() == 'удалить заметку')
async def cmd_write(message: Message, state: FSMContext, session: AsyncSession):
    await state.set_state(Note.deleate_annotation)
    await message.answer(
        text='Вы точно желаете удалить заметку?\n(Напишите  "Да" если желаете удалить заметку)',
        reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(Note.deleate_annotation), F.text.casefold() == 'да')
async def cmd_deleate(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(tg_id=message.from_user.id)
    data = await state.get_data()
    await orm_deleate_annotation(session=session, tg_id=data['tg_id'])
    await state.clear()
    await message.answer(
        text='Ваша заметка удалена',
        reply_markup=choose_action)


@router.message(StateFilter(Note.deleate_annotation))
async def cmd_deleate_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text='Вы вернулись назад в главное меню\n\nВыберите действие ниже⬇️',
        reply_markup=choose_action)


@router.message(StateFilter(None), F.text.casefold() == 'посмотреть заметку')
async def cmd_view(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        text=await orm_view_annotation(session=session,
                                       tg_id=message.from_user.id))


@router.message(F.text)
async def idk_message(message: Message):
    await message.reply(
        text='Я не знаю данной команды😢\n\nВыберите день недели ниже⬇️',
        reply_markup=choose_action)
