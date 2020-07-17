from tkinter import *
from tkinter import messagebox

import db
import functions
from classes import SCP
import global_vars

# todo feature: maybe add a notes feature
# todo feature: add scrollable list of SCPS along with some flags, much like the table is stored

background_color = "lightgrey"

window_name = "SCP Handler"
# set up the tkinter root window
root = Tk()
root.title(window_name)
root.iconphoto(False, PhotoImage(file="/Users/michael/PycharmProjects/SCP_website_handler/scp-logo.png"))
root.geometry("658x356+350+350")
root.configure(bg=background_color)
root.resizable(width=False, height=False)


# global variables
current_scp = -1

is_favorite = IntVar()
have_read = IntVar()
dont_want_to_read = IntVar()
read_later = IntVar()

is_favorite_filter = IntVar()
have_read_filter = IntVar()
dont_want_to_read_filter = IntVar()
read_later_filter = IntVar()
exists_filter = IntVar()
is_favorite_filter.set(0)
have_read_filter.set(1)
dont_want_to_read_filter.set(1)
read_later_filter.set(0)
exists_filter.set(1)


def get_display_string(scp_number, include_link=False):
    scp = db.get_scp(scp_number)
    output = f"SCP-{scp.number}\n{scp.name}\nObject Class: {scp.object_class}\nRating: {scp.rating}"
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
    l = read_later.get()
    current_scp.is_favorite = f
    current_scp.have_read = r
    current_scp.dont_want_to_read = w
    current_scp.read_later = l
    db.update_scp(current_scp)


# used to update multiple SCPs at once
def update_multiple_scps_window():
    global update

    global_vars.delay_time_ms = 200

    # in case the window is already open
    try:
        if update.state() == "zoomed":
            return
    except NameError:
        pass
    except TclError:
        pass

    # function to close the update window, also resets the delay time
    def update_close_window():
        update.destroy()
        global_vars.delay_time_ms = global_vars.delay_time_ms_default

    # used to filter out SCPs that are already in the database
    only_new_filter = IntVar()

    # function called by the update button
    def update_multiple_scps():
        # first try to catch invalid values in the entry fields
        try:
            if int(entry_upper_bound.get()) - int(entry_lower_bound.get()) < 1 or int(entry_lower_bound.get()) < 1:
                messagebox.showerror("Update multiple SCPs", "Please ender a valid range.")
                entry_upper_bound.delete(0, END)
                entry_lower_bound.delete(0, END)
                return
        except ValueError:
            messagebox.showerror("Update multiple SCPs", "Please ender a valid range.")
            entry_upper_bound.delete(0, END)
            entry_lower_bound.delete(0, END)
            return

        # store the number of requests before we update multiple
        before_request_count = global_vars.debug_requests_count

        # construct a list containing the numbers of all scps that should be updated based on the users filtering
        # options
        if only_new_filter.get():
            # generator function for giving the numbers of scps that are currently in the db successively.
            # only returns the numbers of scps that are in the database and that are ALSO within the bound specified
            # by the user. The numbers are sorted in order.
            def numbers_already_in_db():
                i = 0
                scp_nums_to_filter_out = []
                for scp_num in db.get_available_scp_numbers():
                    current_scp_num = scp_num.get("number")
                    if int(entry_lower_bound.get()) <= current_scp_num <= int(entry_upper_bound.get()):
                        scp_nums_to_filter_out.append(current_scp_num)
                scp_nums_to_filter_out = sorted(scp_nums_to_filter_out)
                while i < len(scp_nums_to_filter_out):
                    yield scp_nums_to_filter_out[i]
                    i += 1
            # create an iterator from the generator function we just defined.
            # loop over the range we want to update and check each number if it equals the number in the current
            # iteration of the iterator. if it does, we advance the iterator by one and skip to the next number in
            # the for loop. If the numbers don't match we add them to scp_numbers_to_update. This way we only append
            # numbers to the list that are NOT in the database.
            scp_numbers_to_update = []
            nums_db = numbers_already_in_db()
            try:
                d = next(nums_db)
            # this executes if scp_nums_to_filter_out is an empty list, we set d=0 so that we don't get an error when
            # referencing d later. no scp has the number 0 so this will not filter out anything
            except StopIteration:
                d = 0
            for n in range(int(entry_lower_bound.get()), int(entry_upper_bound.get()) + 1):
                if n == d:
                    try:
                        d = next(nums_db)
                    except StopIteration:
                        pass
                else:
                    scp_numbers_to_update.append(n)
        # if the filter is not set then we simply update all scps in the given range (inclusive)
        else:
            scp_numbers_to_update = list(range(int(entry_lower_bound.get()), int(entry_upper_bound.get()) + 1))

        # show user the update information and ask whether they want to continue
        result = messagebox.askyesno("Update multiple SCPs",
                                     f"Are you sure you wish to update {len(scp_numbers_to_update)} SCPs\n" +
                                     f"with a {global_vars.delay_time_ms} ms delay between requests?")
        if not result:
            return

        # update the scps and store the resulsts to display afterwards
        update_results = []
        for scp_number in scp_numbers_to_update:
            result = functions.update_scp(scp_number)
            update_results.append(result)
            print(f"Updated SCP-{scp_number}")
        # fetch the current request count to compare with the one taken earlier
        current_request_count = global_vars.debug_requests_count

        # display the results of the update
        number_of_scps_added = sum(r == 1 for r in update_results)
        number_of_scps_updated = sum(r == 2 for r in update_results)
        messagebox.showinfo("Update multiple SCPs",
                            "Success!\n" +
                            f"{number_of_scps_added} SCPs added,\n" +
                            f"{number_of_scps_updated} SCPs updated.\n" +
                            f"{current_request_count-before_request_count} requests sent.")
        update_info_var()

    # create the window
    update = Toplevel()
    update.title(f"Update multiple SCPs")
    update.iconphoto(False, PhotoImage(file="/Users/michael/PycharmProjects/SCP_website_handler/scp-logo.png"))
    update.geometry("350x234+1020+350")
    update.resizable(width=False, height=False)
    update.configure(bg=background_color)
    # protocol for when window is closed: call the update_close_window function
    update.protocol("WM_DELETE_WINDOW", update_close_window)

    # create the widgets
    text_frame = LabelFrame(update, bd=2)
    text_label1 = Label(text_frame, text="Update SCPs from")
    entry_lower_bound = Entry(text_frame, width=4)
    text_label2 = Label(text_frame, text="to")
    entry_upper_bound = Entry(text_frame, width=4)
    text_label3 = Label(text_frame, text="(inclusive)")

    delay_frame = LabelFrame(update, bd=2)
    delay_ms_label = Label(delay_frame, text="200 ms delay\nbetween requests")
    # callback function for slider
    def update_slider(var):
        global_vars.delay_time_ms = int(var)
        delay_ms_label.configure(text=f"{global_vars.delay_time_ms}ms delay\nbetween requests")
    delay_slider = Scale(delay_frame, from_=200, to=5000, command=update_slider, showvalue=0, orient=HORIZONTAL,
                         length=158)

    update_frame = LabelFrame(update, bd=2)
    only_new_filter_checkbox = Checkbutton(update_frame, text="Only check for SCPS\nnot currently in database",
                                           variable=only_new_filter, onvalue=1, offvalue=0)
    update_button = Button(update_frame, text="Update SCPs", command=update_multiple_scps)

    close_window_button = Button(update, text="Close Window", command=update_close_window, height=2, width=36)

    # place the widgets
    text_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky=W)
    text_label1.grid(row=0, column=0, pady=5)
    entry_lower_bound.grid(row=0, column=1, pady=5)
    text_label2.grid(row=0, column=2, pady=5)
    entry_upper_bound.grid(row=0, column=3, pady=5)
    text_label3.grid(row=0, column=4, pady=5)

    delay_frame.grid(row=1, column=0, padx=10, pady=5, sticky=W)
    delay_ms_label.grid(row=0, column=0, padx=10, pady=5)
    delay_slider.grid(row=0, column=1, padx=10, pady=5)

    update_frame.grid(row=2, column=0, padx=10, pady=5, sticky=W)
    only_new_filter_checkbox.grid(row=0, column=0, padx=10, pady=5)
    update_button.grid(row=0, column=1, padx=(10, 12), pady=5)

    close_window_button.grid(row=3, column=0, padx=10, pady=5, sticky=W)



# function to set current SCP and display it in the scp_display_frame based on its number
def set_current_scp(scp_number):
    global scp_display_frame
    global scp_label
    global current_scp
    global is_favorite
    global have_read
    global dont_want_to_read
    global read_later

    str_number = functions.reformat_SCP_num(scp_number)

    # this block handles the case of a random search turning up empty, thus calling this function with an
    # argument of -1
    if scp_number == -1:
        current_scp = -1
        scp_label.destroy()
        scp_label = Label(scp_display_frame, text="No SCP found for given criteria", justify=LEFT)
        scp_label.grid(row=0, column=0, sticky=W)
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
        read_later.set(scp.read_later)

    # destroy and redraw the info in scp_display_frame
    scp_label.destroy()
    if scp == -1:
        scp_label = Label(scp_display_frame, text=f"SCP-{str_number} not in database!", justify=LEFT)
    elif scp.exists == False:
        scp_label = Label(scp_display_frame, text=f"SCP-{str_number} doesn't exist yet!", justify=LEFT)
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


# displays a random SCP from the database
def find_random_scp():
    scp = functions.get_random_scp(not_read_yet=have_read_filter.get(), want_to_read=dont_want_to_read_filter.get(),
                                   does_exist=exists_filter.get(), is_favorite=is_favorite_filter.get(),
                                   read_later=read_later_filter.get())
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
def show_top_x(highest_rank_index, lowest_rank_index):
    global top
    global main_frame

    # check to see if the window is already open
    try:
        # if it is, then
        if top.state() == "zoomed":
            main_frame.destroy()
    except TclError:
        top = Toplevel()
        top.title(f"Top SCPs")
        top.iconphoto(False, PhotoImage(file="/Users/michael/PycharmProjects/SCP_website_handler/scp-logo.png"))
        top.geometry("399x500+950+300")
        top.resizable(width=False, height=False)
    except NameError:
        top = Toplevel()
        top.title(f"Top SCPs")
        top.iconphoto(False, PhotoImage(file="/Users/michael/PycharmProjects/SCP_website_handler/scp-logo.png"))
        top.geometry("399x500+950+300")
        top.resizable(width=False, height=False)

    # filter search based on checkboxes
    extra_filters = []
    if is_favorite_filter.get():
        extra_filters.append("is_favorite")
    if have_read_filter.get():
        extra_filters.append("have_read")
    if dont_want_to_read_filter.get():
        extra_filters.append("dont_want_to_read")
    if read_later_filter.get():
        extra_filters.append("read_later")

    scps = db.get_available_scp_numbers(["rating"] + extra_filters)

    filtered_scps = []
    for scp in scps:
        try:
            int(scp.get("rating"))
        except ValueError:
            continue
        if is_favorite_filter.get() and scp["is_favorite"] == 0:
            continue
        if have_read_filter.get() and scp["have_read"] == 1:
            continue
        if dont_want_to_read_filter.get() and scp["dont_want_to_read"] == 1:
            continue
        if read_later_filter.get() and scp["read_later"] == 0:
            continue
        filtered_scps.append(scp)

    sorted_scps = sorted(filtered_scps, key=top_rated_sort, reverse=True)
    sorted_scps_numbers = [scp.get("number") for scp in sorted_scps]
    try:
        sorted_scps_numbers = sorted_scps_numbers[highest_rank_index:lowest_rank_index]
    except IndexError:
        pass

    # draw the scp information in the window
    main_frame = LabelFrame(top, bd=0)
    main_frame.grid(row=0, column=0, columnspan=3)
    for i, scp_number in enumerate(sorted_scps_numbers):
        text = get_display_string(scp_number)


        new_frame = LabelFrame(main_frame, height=87, width=400, bd=1)
        new_frame.grid_propagate(0)
        new_rank_label = Label(new_frame, text="# " + str(highest_rank_index+i+1))
        # create a high-class function so that the callback function sends the user to the correct link when the button
        # is pressed later. If we simply used a variable here then the variable would be overwritten during later loop
        # iterations and thus every button would send the user to the same page. This way we can keep the scp_number
        # within the scope of the higher function so that it is stored until the callback function is called.
        def higher_function(var):
            return lambda: functions.go_to_scp_page(var)
        new_browser_button = Button(new_frame, text="Open in\nBrowser",
                            command=higher_function(scp_number),
                            height=2, width=7)
        new_label = Label(new_frame, text=text, justify=LEFT)

        new_frame.grid(row=i, column=0, columnspan=3, padx=0, pady=0, sticky=W)
        new_rank_label.grid(row=0, column=0)
        new_browser_button.grid(row=1, column=0, padx=10, sticky=N)
        new_label.grid(row=0, column=1, rowspan=2, padx=(0, 10), pady=5, sticky=W)
    # draw buttons for the bottom of the frame
    close_button = Button(top, text="Close Window", command=top.destroy, width=20)
    previous_button = Button(top, text="<<",
                         command=lambda: show_top_x(highest_rank_index-5, lowest_rank_index-5))
    if highest_rank_index == 0:
        previous_button.configure(state=DISABLED)
    next_button = Button(top, text=">>",
                             command=lambda: show_top_x(highest_rank_index+5, lowest_rank_index+5))
    if lowest_rank_index > len(sorted_scps):
        next_button.configure(state=DISABLED)

    close_button.grid(row=lowest_rank_index-highest_rank_index+1, column=1, padx=10, pady=(20, 10))
    previous_button.grid(row=lowest_rank_index-highest_rank_index+1, column=0, padx=10, pady=(20, 10))
    next_button.grid(row=lowest_rank_index-highest_rank_index+1, column=2, padx=10, pady=(20, 10))


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
read_later_checkbox = Checkbutton(root, text="Read later", variable=read_later, onvalue=1, offvalue=0,
                                  command=update_current_scp)

choose_scp_frame = LabelFrame(root)
entry_field = Entry(choose_scp_frame, width=19)
find_scp_button = Button(choose_scp_frame, text="Find SCP", command=find_scp)
add_update_database_button = Button(choose_scp_frame, text="Add/update SCP", command=add_update_database)

random_scp_frame = LabelFrame(root)
is_favorite_filter_checkbox = Checkbutton(random_scp_frame, text="Only include favorite SCPs", variable=is_favorite_filter)
have_read_filter_checkbox = Checkbutton(random_scp_frame, text="Exclude SCPs I have already read", variable=have_read_filter)
dont_want_to_read_filter_checkbox = Checkbutton(random_scp_frame, text="Exclude SCPs I don't want to read",
                                                variable=dont_want_to_read_filter)
read_later_filter_checkbox = Checkbutton(random_scp_frame, text="Only include SCPs I want to read later",
                                         variable=read_later_filter)
exists_filter_checkbox = Checkbutton(random_scp_frame, text="Exclude SPCs that don't exist yet", variable=exists_filter)
random_scp_button = Button(random_scp_frame, text="Get Random SCP", command=find_random_scp,
                           width=15, height=2)
display_top_10_button = Button(random_scp_frame, text="Top SCPs", command=lambda: show_top_x(0, 5),
                               width=15, height=2)

side_frame = LabelFrame(root)
open_scp_in_browser_button = Button(side_frame, text="Open in\nBrowser", command=open_scp_in_browser,
                                    width=15, height=3)
info_label_scp_count = Label(side_frame, textvariable=info_var,
                             width=15, height=4)
update_multiple_button = Button(side_frame, text="Update\nmultiple SCps", command=update_multiple_scps_window,
                                width=15, height=4)
quit_button = Button(side_frame, text="Quit", command=root.quit,
                     width=15, height=3)

# place widgets
scp_display_frame.grid(row=0, column=0, columnspan=4, ipadx=170, padx=10, pady=10)
favorite_checkbox.grid(row=1, column=0, sticky=W, padx=(10, 5))
read_later_checkbox.grid(row=1, column=1, sticky=W, padx=5)
have_read_checkbox.grid(row=1, column=2, sticky=W, padx=5)
dont_want_to_read_checkbox.grid(row=1, column=3, sticky=W, padx=(5, 10))

choose_scp_frame.grid(row=2, column=0, columnspan=5, padx=10, pady=10, ipadx=18, sticky=W)
entry_field.grid(row=4, column=0, padx=10, pady=10)
find_scp_button.grid(row=4, column=1, padx=10, pady=10)
add_update_database_button.grid(row=4, column=2, padx=10, pady=10)

random_scp_frame.grid(row=3, column=0, columnspan=5, padx=10, pady=(0, 20), ipadx=5, sticky=W)
is_favorite_filter_checkbox.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=W)
read_later_filter_checkbox.grid(row=1, column=0, padx=10, sticky=W)
have_read_filter_checkbox.grid(row=2, column=0, padx=10, sticky=W)
dont_want_to_read_filter_checkbox.grid(row=3, column=0, padx=10, sticky=W)
exists_filter_checkbox.grid(row=4, column=0, padx=10, pady=(0,10), sticky=W)
random_scp_button.grid(row=0, column=1, rowspan=2, padx=10, pady=(20, 0))
display_top_10_button.grid(row=3, column=1, rowspan=2, padx=10, sticky=N)

side_frame.grid(row=0, column=4, rowspan=4, pady=10, sticky=N)
open_scp_in_browser_button.grid(row=0, column=0, padx=10, pady=(10, 12))
info_label_scp_count.grid(row=2, column=0, padx=10, pady=12)
update_multiple_button.grid(row=3, column=0, padx=10, pady=12)
quit_button.grid(row=4, column=0, padx=10, pady=(12, 11))


root.mainloop()
