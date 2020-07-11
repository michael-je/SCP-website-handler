# todo create a gui

from random import randint

import db
import functions

numbers = db.get_available_scp_numbers()

for n in numbers:
    print(db.get_scp(n.get("number")))

functions.debug_display_requests_count()