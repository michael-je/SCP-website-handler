# todo create a gui
# todo refactor functions.update_scp() to store the SCP in the database

# todo add a last_updated variable to the SCP class
# todo refactor SCPs to be stored as dictionaries instead of classes // or maybe classes are fine? could be useful later

from random import randint

import functions


# test_scp = 173
# display_scp(test_scp, debug=True)




# update_all_scps()

# debug_display_scps(start=2, end=10, include_debug_info=True)

# update_scp(3001)
# debug_display_scps(display_all=True)
# debug_display_requests_count()


# db.set_up_database()
# functions.update_scp(306)

test_scp = randint(1, 6000)
functions.update_scp(test_scp)
functions.display_scp(test_scp, debug=True)
functions.go_to_scp_page(test_scp)
