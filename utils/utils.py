def is_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def take_balances(money):
    message_text = ''
    for name in sorted(money):
        message_text += (('Долг' if money[name] < 0 else 'Остаток') +
                         f' {name} равен: {money[name]} руб\n')
    return message_text


def take_names(money):
    message_text = ''
    for name in sorted(money):
        message_text += f'`{name}`\n'
    return message_text


# controls state cleaning with context manager
class StateGuard:
    def __init__(self, state):
        self.state = state
        self.is_locked = False

    async def __aenter__(self):
        self.is_locked = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.is_locked:
            await self.state.clear()

    def unlock(self):
        self.is_locked = False
