

# makes report about this and prev month, prev 30 days and prev 4 weeks
def make_report():
    return "report"


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
