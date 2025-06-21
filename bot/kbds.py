from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardMarkup



def createkb(d:dict[str,str],adj1:int=1,adj2:int=1,back=None,mod=None):
    if mod:
        ckb = InlineKeyboardBuilder()
        buttons = [InlineKeyboardButton(text=i, callback_data=str(j)) for i, j in d.items()]

        # Добавляем первые 4 кнопки по 2 в строке
        first_four = buttons[:4]
        if first_four:
            ckb.row(*first_four[:2])  # Первая строка (2 кнопки)
            ckb.row(*first_four[2:4])  # Вторая строка (2 кнопки)

        # Добавляем оставшиеся кнопки по одной
        for button in buttons[4:]:
            ckb.row(button)

        # Добавляем кнопку "Назад", если указано
        # if back:
        #     ckb.add(InlineKeyboardButton(text="Назад", callback_data="menu"))

        return ckb.as_markup(resize_keyboard=True)
    else:
        ckb=InlineKeyboardBuilder()
        for i,j in d.items():
            ckb.add(
                InlineKeyboardButton(text=i,callback_data=str(j))

            )
        # if back:
        #
        #     ckb.add(
        #
        #         InlineKeyboardButton(text="Назад", callback_data="menu")
        #     )
        ckb.adjust(adj1,adj2)
        return ckb.as_markup(resize_keyboard=True)

def sharekb(d: dict[str, str], mod: bool = False):
    buttons = []
    for text, url in d.items():
        if url.startswith("url*"):
            url = url.split("*")[1]
            buttons.append(
                InlineKeyboardButton(text=text, switch_inline_query=url)
            )
        elif url.startswith("url>>"):
            url = url.split(">>")[1]
            buttons.append(
                InlineKeyboardButton(text=text, url=url)
            )
        else:
            buttons.append(
                InlineKeyboardButton(text=text, callback_data=url)
            )

    if mod:
        # Формируем специальный порядок кнопок: одна, две, одна
        layout = []
        if len(buttons) >= 1:
            layout.append([buttons[0]])  # Первая строка: одна кнопка
        if len(buttons) > 1:
            layout.append(buttons[1:3])  # Вторая строка: две кнопки
        if len(buttons) > 3:
            layout.append(buttons[3:])  # Остальные кнопки в одной строке
    else:
        # Каждая кнопка в своей строке
        layout = [[button] for button in buttons]

    return InlineKeyboardMarkup(inline_keyboard=layout)