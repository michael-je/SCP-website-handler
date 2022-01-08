def print_scp(scp_number, debug=False):
    # Finds data on an SCP from the database and displays it to the terminal
    # set debug=True for hidden data
    scp = ORM.get_scp(scp_number)
    if scp == -1:
        print(f"SCP-{scp_number} not in database!")
    else:
        scp.print(debug=True)

def debug_display_requests_count():
    # prints out how many times the code has sent a request to the wiki since it started running
    # counters are stored in global_vars
    print(f'{global_vars.requests_count} requests sent.')
