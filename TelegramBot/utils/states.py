from aiogram.fsm.state import State, StatesGroup

class Login(StatesGroup):
    street = State()
    apartment = State()

class Flat(StatesGroup):
    flat = State()
    meter = State()

class lst(StatesGroup):
    lst_flats = State()
    lst_admins = State()
    lst_users = State()

class User_problem(StatesGroup):
    problem = State()
    confirm = State()