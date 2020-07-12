from tkinter import *

import db
import functions
from classes import SCP

# debug info
print(db.get_available_scp_numbers())


# set up the tkinter root window
root = Tk()
root.title("SCP Handler")
root.iconphoto(False, PhotoImage(file="scp-logo.png"))
root.geometry("400x400")


# global variables
current_scp = None
is_favorite = IntVar()
have_read = IntVar()
dont_want_to_read = IntVar()


# function to update the database with current information from the gui
def update_current_scp():
    global current_scp
    global is_favorite
    global have_read
    global dont_want_to_read

    f = is_favorite.get()
    r = have_read.get()
    w = dont_want_to_read.get()
    current_scp.is_favorite = f
    current_scp.have_read = r
    current_scp.dont_want_to_read = w
    current_scp.display(debug=True)
    db.update_scp(current_scp)


# function to set current SCP and display it in the scp_display_frame based on its number
def set_current_scp(scp_number):
    global scp_label
    global current_scp
    global is_favorite
    global have_read
    global dont_want_to_read

    # setup an scp class with current scp
    scp = db.get_scp(scp_number)
    current_scp = scp

    # set checkbox variables to reflect state of current_scp
    is_favorite.set(scp.is_favorite)
    have_read.set(scp.have_read)
    dont_want_to_read.set(scp.dont_want_to_read)

    # destroy and redraw the info in scp_display_frame
    scp_label.destroy()
    if scp == -1:
        scp_label = Label(scp_display_frame, text="SCP not in database!")
    elif scp.exists == False:
        scp_label = Label(scp_display_frame, text="SCP doesn't exist yet!")
    else:
        scp_label = Label(scp_display_frame, text=f"{scp.number} - {scp.name}")
    scp_label.pack()


# function that returns codes based on the user input
# 1 = valid input
# -1 = invalid input format
def sanitize_input(input):
    if not input:
        return -1
    try:
        int(input)
    except ValueError:
        return -1
    if len(str(input)) > 5:
        return -1
    if input < 0:
        return -1
    return 1


# used by find_scp_button to put an scp on the screen based on what is in the entry field
def find_scp():
    scp_number = entry_field.get()
    set_current_scp(scp_number)


# function to display all info for current_scp
def show_debug_info():
    global debug_label
    global current_scp

    if current_scp is None:
        return
    info = current_scp.debug_info()
    text = "\n".join(str(i) for i in info)
    debug_label = Label(root, text=text)
    debug_label.pack()


# todo add a random scp button and function
# displays a random SCP from the database
# accompanying checkboxes should allow for filtering via have_read, dont_want_to_read and exists
def find_random_scp():
    pass


quit_button = Button(root, text="Quit", command=root.quit)
entry_field = Entry(root)
find_scp_button = Button(root, text="Find SCP", command=find_scp)
scp_display_frame = LabelFrame(root)
scp_label = Label(scp_display_frame)
favorite_checkbox = Checkbutton(root, text="Favorite", variable=is_favorite, onvalue=1, offvalue=0,
                                command=update_current_scp)
have_read_checkbox = Checkbutton(root, text="Mark as read", variable=have_read, onvalue=1, offvalue=0,
                                 command=update_current_scp)
dont_want_to_read_checkbox = Checkbutton(root, text="Don't want to read", variable=dont_want_to_read,
                                         onvalue=1, offvalue=0, command=update_current_scp)
debug_button = Button(root, text="debug info", command=show_debug_info)

quit_button.pack()
entry_field.pack()
find_scp_button.pack()
scp_display_frame.pack()
scp_label.pack()
favorite_checkbox.pack()
have_read_checkbox.pack()
dont_want_to_read_checkbox.pack()
debug_button.pack()


root.mainloop()

functions.debug_display_requests_count()
