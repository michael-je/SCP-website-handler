debug_requests_count = 0

# this is used by functions.update_scp when updating multiple SCPS via the gui
# it allows us to skip a few requests to the server
series_links = None
series_sources = {}

# this is used to sleep the program before every request send to avoid spam
sleep_brake = True
delay_time_ms = delay_time_ms_default = 20
