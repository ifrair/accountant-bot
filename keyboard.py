from maxapi.types.attachments.buttons import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

main_keyboard_builder = InlineKeyboardBuilder()
main_keyboard_builder.row(
    CallbackButton(text="Показать балансы", payload="show_balances"),
    CallbackButton(text="Сделать отчет", payload="make_report"),
)
main_keyboard_builder.row(
    CallbackButton(text="Пополнить баланс", payload="add_balance"),
    CallbackButton(text="Вычесть баланс", payload="subtract_balance"),
)
main_keyboard_builder.row(
    CallbackButton(text="Добавить ученика", payload="add_student"),
    CallbackButton(text="Удалить ученика", payload="delete_student"),
)
main_keyboard_builder.row(
    CallbackButton(text="Пересчитать балансы", payload="recalculate_balances"),
    CallbackButton(text="Откатить последний пересчет", payload="rollback_recalculation"),
)
main_keyboard = main_keyboard_builder.as_markup()

change_edit_builder = InlineKeyboardBuilder()
change_edit_builder.row(CallbackButton(text="Заново давай", payload="wrong_changes"))
change_edit_builder.row(CallbackButton(text="Все ок", payload="approved_changes"))
change_edit = change_edit_builder.as_markup()

add_student_builder = InlineKeyboardBuilder()
add_student_builder.row(CallbackButton(text="Заново давай", payload="wrong_adding"))
add_student_builder.row(CallbackButton(text="Да", payload="approved_adding"))
add_student = add_student_builder.as_markup()

delete_student_builder = InlineKeyboardBuilder()
delete_student_builder.row(CallbackButton(text="Заново давай", payload="wrong_deleting"))
delete_student_builder.row(CallbackButton(text="Да", payload="approved_deleting"))
delete_student = delete_student_builder.as_markup()


def get_students_keyboard(students):
    builder = InlineKeyboardBuilder()
    buttons = [CallbackButton(text=student, payload=student) for student in sorted(students)]
    builder.row(*buttons)
    builder.adjust(3)
    builder.row(CallbackButton(text="Отмена", payload="cancel_operation"))
    return builder.as_markup()
