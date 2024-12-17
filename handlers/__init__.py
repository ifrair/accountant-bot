from .handlers_change_balances import router as router_change_balances
from .handlers_main import router as router_main
from .handlers_recount_balances import router as router_recount_balances
from .handlers_report_balances import router as router_report_balances
from .handlers_students import router as router_students

handlers = [
    router_change_balances,
    router_recount_balances,
    router_report_balances,
    router_students,
    router_main,
]
