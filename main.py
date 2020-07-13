from tkinter import *
from tkinter import messagebox
from math import floor

import db
import functions
from classes import SCP
import global_vars

# todo maybe add a notes feature
# todo add read later feature
# todo add view favorites feature
# todo also add button to update multiple scps at once, but be careful with that one

# debug info
print(db.get_available_scp_numbers())


window_name = "SCP Handler"
# set up the tkinter root window
root = Tk()
root.title(window_name)
root.iconphoto(False, PhotoImage(file="scp-logo.png"))
root.geometry("620x334+400+350")


# global variables
current_scp = -1
window_open = False

is_favorite = IntVar()
have_read = IntVar()
dont_want_to_read = IntVar()

is_favorite_filter = IntVar()
have_read_filter = IntVar()
dont_want_to_read_filter = IntVar()
exists_filter = IntVar()
is_favorite_filter.set(0)
have_read_filter.set(1)
dont_want_to_read_filter.set(1)
exists_filter.set(1)


def get_display_string(scp_number, include_link=False):
    scp = db.get_scp(scp_number)
    output = f"# {scp.number}\n{scp.name}\nObject Class: {scp.object_class}\nRating: {scp.rating}"
    if include_link:
        output += f"\n{scp.URL}"
    return output


# function to update the database with current information from the gui
def update_current_scp():
    global current_scp
    global is_favorite
    global have_read
    global dont_want_to_read

    # first check whether current_scp is a valid SCP object or an integer of value -1 (representing an error)
    if current_scp == -1:
        return

    f = is_favorite.get()
    r = have_read.get()
    w = dont_want_to_read.get()
    current_scp.is_favorite = f
    current_scp.have_read = r
    current_scp.dont_want_to_read = w
    db.update_scp(current_scp)


# function to set current SCP and display it in the scp_display_frame based on its number
def set_current_scp(scp_number):
    global scp_display_frame
    global scp_label
    global current_scp
    global is_favorite
    global have_read
    global dont_want_to_read

    # this block handles the case of a random search turning up empty, thus calling this function with an
    # argument of -1
    if scp_number == -1:
        current_scp = -1
        scp_label.destroy()
        scp_label = Label(scp_display_frame, text="No SCP found for given criteria")
        scp_label.pack()
        return

    # setup an scp class with current scp
    scp = db.get_scp(scp_number)
    current_scp = scp

    # set checkbox variables to reflect state of current_scp
    # first check whether current_scp is a valid SCP object or simply an int of value -1 (representing an error)
    if scp != -1:
        is_favorite.set(scp.is_favorite)
        have_read.set(scp.have_read)
        dont_want_to_read.set(scp.dont_want_to_read)

    # destroy and redraw the info in scp_display_frame
    scp_label.destroy()
    if scp == -1:
        scp_label = Label(scp_display_frame, text="SCP not in database!", justify=LEFT)
    elif scp.exists == False:
        scp_label = Label(scp_display_frame, text=f"{scp_number} - doesn't exist yet!", justify=LEFT)
    else:
        text = get_display_string(scp.number)
        scp_label = Label(scp_display_frame, text=text, justify=LEFT)
    scp_label.grid(row=0, column=0, sticky=W)


# function that returns codes based on the user input
# 1 = valid input
# -1 = invalid input format
def sanitize_input(input):
    if not input:
        return -1
    try:
        input_int = int(input)
    except ValueError:
        return -1
    if len(input) > 5:
        return -1
    if input_int < 0:
        return -1
    return 1


# used by find_scp_button to put an scp on the screen based on what is in the entry field
def find_scp():
    global entry_field

    scp_number = entry_field.get()
    input_flag = sanitize_input(scp_number)
    if input_flag == -1:
        messagebox.showerror(window_name, "Invalid SCP number.")
        entry_field.delete(0, END)
        return
    set_current_scp(scp_number)


# function to display all info for current_scp
def show_debug_info():
    global debug_label
    global current_scp

    if current_scp == -1:
        return
    info = current_scp.debug_info()
    text = "\n".join(str(i) for i in info)
    debug_label = Label(root, text=text)
    debug_label.pack()


# displays a random SCP from the database
def find_random_scp():
    global is_favorite_filter
    global have_read_filter
    global dont_want_to_read_filter
    global exists_filter

    scp = functions.get_random_scp(not_read_yet=have_read_filter.get(), want_to_read=dont_want_to_read_filter.get(),
                                   does_exist=exists_filter.get(), is_favorite=is_favorite_filter.get())
    if scp == -1:
        set_current_scp(-1)
    else:
        set_current_scp(scp.number)


def open_scp_in_browser():
    global current_scp

    # in the case that no valid scp is currently being shown
    if current_scp == -1:
        return
    functions.go_to_scp_page(current_scp.number)


# function that takes the scp_number from the entry field and adds/updates that SCP in the database
def add_update_database():
    global num_scps_in_db

    scp_number = entry_field.get()
    input_flag = sanitize_input(scp_number)

    if input_flag == -1:
        messagebox.showerror(window_name, "Invalid SCP number!")
        entry_field.delete(0, END)
        return

    result = functions.update_scp(scp_number)
    set_current_scp(scp_number)

    if result == 1:
        messagebox.showinfo(window_name, "SCP successfully added to database!")
    if result == 2:
        messagebox.showinfo(window_name, "SCP successfully updated in database!")

    update_info_var()





def top_rated_sort(scp_dict):
    try:
        return int(scp_dict.get("rating"))
    except ValueError:
        pass



# function that shows the top 10 SCPs burrently in the database, this can be displayed in a
# seperate window
# todo add filters (exists is not necessary since they dont have a rating) along with main button into seperate frame
def show_top_x(num):
    global window_open

    top = Toplevel()
    top.title(f"Top {num} SCPs")
    top.iconphoto(False, PhotoImage(file="scp-logo.png"))
    top.geometry("800x500+650+200")

    scps = db.get_available_scp_numbers(["rating"])
    filtered_scps = []
    for scp in scps:
        try:
            int(scp.get("rating"))
            filtered_scps.append(scp)
        except ValueError:
            continue
    sorted_scps = sorted(filtered_scps, key=top_rated_sort, reverse=True)
    sorted_scps_numbers = [scp.get("number") for scp in sorted_scps]
    try:
        sorted_scps_numbers = sorted_scps_numbers[:num]
    except IndexError:
        pass

    # draw the scp information in the window
    for i, scp_number in enumerate(sorted_scps_numbers):
        text = get_display_string(scp_number)

        new_frame = LabelFrame(top, height=87, width=400, bd=1)
        new_frame.grid_propagate(0)
        new_button = Button(new_frame, text="Open in\nBrowser", command=lambda: functions.go_to_scp_page(scp_number),
                            height=3, width=7)
        new_label = Label(new_frame, text=text, justify=LEFT)

        new_frame.grid(row=i%5, column=floor(i/5), padx=0, pady=0, sticky=W)
        new_button.grid(row=0, column=0, padx=10, pady=(16, 0), sticky=N)
        new_label.grid(row=0, column=1, padx=(0, 10), pady=5, sticky=W)
    # draw a close button at the bottom
    close_button = Button(top, text="Close Window", command=top.destroy, width=20)
    close_button.grid(row=num+1, column=0, columnspan=2, sticky=W, padx=10, pady=(20, 10))


# function to update info_labels variable with desired info
def update_info_var():
    global info_var

    num_scps_in_db = len(db.get_available_scp_numbers())
    total_requests = global_vars.debug_requests_count
    info_var.set(f"{num_scps_in_db} SCPs\nin database\n\n{total_requests} requests sent")



# create and update the info variable
info_var = StringVar()
update_info_var()


# create widgets
scp_display_frame = LabelFrame(root, height=100, width=124)
# fixes the frames size
scp_display_frame.grid_propagate(0)
scp_label = Label(scp_display_frame)
favorite_checkbox = Checkbutton(root, text="Favorite", variable=is_favorite, onvalue=1, offvalue=0,
                                command=update_current_scp)
have_read_checkbox = Checkbutton(root, text="Mark as read", variable=have_read, onvalue=1, offvalue=0,
                                 command=update_current_scp)
dont_want_to_read_checkbox = Checkbutton(root, text="Don't want to read", variable=dont_want_to_read,
                                         onvalue=1, offvalue=0, command=update_current_scp)

choose_scp_frame = LabelFrame(root)
entry_field = Entry(choose_scp_frame, width=19)
find_scp_button = Button(choose_scp_frame, text="Find SCP", command=find_scp)
add_update_database_button = Button(choose_scp_frame, text="Add/update SCP", command=add_update_database)

random_scp_frame = LabelFrame(root)
is_favorite_filter_checkbox = Checkbutton(random_scp_frame, text="Only include favorite SCPs", variable=is_favorite_filter)
have_read_filter_checkbox = Checkbutton(random_scp_frame, text="Exclude SCPs I have already read", variable=have_read_filter)
dont_want_to_read_filter_checkbox = Checkbutton(random_scp_frame, text="Exclude SCPs I don't want to read",
                                                variable=dont_want_to_read_filter)
exists_filter_checkbox = Checkbutton(random_scp_frame, text="Exclude SPCs that don't exist yet", variable=exists_filter)
random_scp_button = Button(random_scp_frame, text="Get Random SCP", command=find_random_scp,
                           width=15, height=5)

side_frame = LabelFrame(root)
open_scp_in_browser_button = Button(side_frame, text="Open in\nBrowser", command=open_scp_in_browser,
                                    width=15, height=3)
display_top_10_button = Button(side_frame, text="Top 10 SCPs", command=lambda: show_top_x(10),
                               width=15, height=3)
quit_button = Button(side_frame, text="Quit", command=root.quit,
                     width=15, height=3)
info_label_scp_count = Label(side_frame, textvariable=info_var,
                             width=15, height=4)

# debug_button = Button(root, text="debug info", command=show_debug_info)

# place widgets
scp_display_frame.grid(row=0, column=0, columnspan=3, ipadx=152, padx=10, pady=10)
favorite_checkbox.grid(row=1, column=0, sticky=W, padx=10)
have_read_checkbox.grid(row=1, column=1, sticky=W, padx=10)
dont_want_to_read_checkbox.grid(row=1, column=2, sticky=W, padx=10)

choose_scp_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky=W)
entry_field.grid(row=4, column=0, padx=10, pady=10)
find_scp_button.grid(row=4, column=1, padx=10, pady=10)
add_update_database_button.grid(row=4, column=2, padx=10, pady=10)

random_scp_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=(0, 20), sticky=W)
is_favorite_filter_checkbox.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=W)
have_read_filter_checkbox.grid(row=1, column=0, padx=10, sticky=W)
dont_want_to_read_filter_checkbox.grid(row=2, column=0, padx=10, sticky=W)
exists_filter_checkbox.grid(row=3, column=0, padx=10, pady=(0,10), sticky=W)
random_scp_button.grid(row=0, column=1, rowspan=4, padx=10)

side_frame.grid(row=0, column=3, rowspan=4, pady=10, sticky=N)
open_scp_in_browser_button.grid(row=0, column=0, padx=10, pady=10)
display_top_10_button.grid(row=1, column=0, padx=10, pady=11)
info_label_scp_count.grid(row=2, column=0, padx=10, pady=11)
quit_button.grid(row=3, column=0, padx=10, pady=11)

# debug_button.pack()

root.mainloop()

functions.debug_display_requests_count()
