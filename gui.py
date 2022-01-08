from tkinter import *
from tkinter import messagebox

import scraper
import global_vars
import cfg
import db

ORM = db.SCPDatabase(cfg.DB_NAME)
scraper = scraper.WikiScraper()


class TkinterGUI():
    """
    """
    def __init__(self):
        pass

    def start(self):
        # set up tkinter root window
        self.root = Tk()
        self.root.title(cfg.WINDOW_NAME)
        self.root.geometry(cfg.WINDOW_GEOMETRY + "+" + cfg.WINDOW_SPAWN_XY)
        self.root.configure(bg=cfg.BACKGROUND_COLOR)
        self.root.resizable(width=False, height=False)

        # tkinter variables
        self.current_scp = -1
        self.scp_display_frame = LabelFrame(self.root, height=100, width=124)
        self.scp_label = None

        self.is_favorite = IntVar()
        self.have_read = IntVar()
        self.dont_want_to_read = IntVar()
        self.read_later = IntVar()

        self.is_favorite_filter = IntVar()
        self.have_read_filter = IntVar()
        self.dont_want_to_read_filter = IntVar()
        self.read_later_filter = IntVar()
        self.exists_filter = IntVar()
        self.is_favorite_filter.set(0)
        self.have_read_filter.set(1)
        self.dont_want_to_read_filter.set(1)
        self.read_later_filter.set(0)
        self.exists_filter.set(1)

        # create and update the info variable
        self.info_var = StringVar()
        self.update_info_var()

        # create widgets
        self.scp_display_frame = LabelFrame(self.root, height=100, width=124)
        self.scp_display_frame.grid_propagate(0) # fixes the frame size
        self.scp_label = Label(self.scp_display_frame)
        self.favorite_checkbox = Checkbutton(
            self.root, text="Favorite",
            variable=self.is_favorite,
            onvalue=1,
            offvalue=0,
            command=self.update_current_scp
        )
        self.have_read_checkbox = Checkbutton(
            self.root,
            text="Mark as read",
            variable=self.have_read,
            onvalue=1,
            offvalue=0,
            command=self.update_current_scp
        )
        self.dont_want_to_read_checkbox = Checkbutton(
            self.root,
            text="Don't want to read",
            variable=self.dont_want_to_read,
            onvalue=1,
            offvalue=0,
            command=self.update_current_scp
        )
        self.read_later_checkbox = Checkbutton(
            self.root,
            text="Read later",
            variable=self.read_later,
            onvalue=1,
            offvalue=0,
            command=self.update_current_scp
        )

        self.choose_scp_frame = LabelFrame(self.root)
        self.entry_field = Entry(self.choose_scp_frame, width=19)
        self.find_scp_button = Button(
            self.choose_scp_frame, text="Find SCP", command=self.find_scp
        )
        self.add_update_database_button = Button(
            self.choose_scp_frame,
            text="Add/update SCP",
            command=self.add_update_database
        )

        self.random_scp_frame = LabelFrame(self.root)
        self.is_favorite_filter_checkbox = Checkbutton(
            self.random_scp_frame,
            text="Only include favorite SCPs",
            variable=self.is_favorite_filter
        )
        self.have_read_filter_checkbox = Checkbutton(
            self.random_scp_frame,
            text="Exclude SCPs I have already read",
            variable=self.have_read_filter
        )
        self.dont_want_to_read_filter_checkbox = Checkbutton(
            self.random_scp_frame,
            text="Exclude SCPs I don't want to read",
            variable=self.dont_want_to_read_filter
        )
        self.read_later_filter_checkbox = Checkbutton(
            self.random_scp_frame,
            text="Only include SCPs I want to read later",
            variable=self.read_later_filter
        )
        self.exists_filter_checkbox = Checkbutton(
            self.random_scp_frame,
            text="Exclude SPCs that don't exist yet",
            variable=self.exists_filter
        )
        self.random_scp_button = Button(
            self.random_scp_frame,
            text="Get Random SCP",
            command=self.find_random_scp,
            width=15,
            height=2
        )
        self.display_top_10_button = Button(
            self.random_scp_frame,
            text="Top SCPs",
            command=lambda: self.show_top_x(0, 5),
            width=15,
            height=2
        )

        self.side_frame = LabelFrame(self.root)
        self.open_scp_in_browser_button = Button(
            self.side_frame,
            text="Open in\nBrowser",
            command=self.open_scp_in_browser,
            width=15,
            height=3
        )
        self.info_label_scp_count = Label(
            self.side_frame,
            textvariable=self.info_var,
            width=15,
            height=4
        )
        self.update_multiple_button = Button(
            self.side_frame,
            text="Update\nmultiple SCps",
            command=self.update_multiple_scps_window,
            width=15,
            height=4
        )
        self.quit_button = Button(
            self.side_frame,
            text="Quit",
            command=self.root.quit,
            width=15,
            height=3
        )

        # place widgets
        self.scp_display_frame.grid(
            row=0, column=0, columnspan=4, ipadx=170, padx=10, pady=10
        )
        self.favorite_checkbox.grid(row=1, column=0, sticky=W, padx=(10, 5))
        self.read_later_checkbox.grid(row=1, column=1, sticky=W, padx=5)
        self.have_read_checkbox.grid(row=1, column=2, sticky=W, padx=5)
        self.dont_want_to_read_checkbox.grid(row=1, column=3, sticky=W, padx=(5, 10))
        
        self.choose_scp_frame.grid(
            row=2, column=0, columnspan=5, padx=10, pady=10, ipadx=18, sticky=W
        )
        self.entry_field.grid(row=4, column=0, padx=10, pady=10)
        self.find_scp_button.grid(row=4, column=1, padx=10, pady=10)
        self.add_update_database_button.grid(row=4, column=2, padx=10, pady=10)
        
        self.random_scp_frame.grid(
            row=3, column=0, columnspan=5, padx=10, pady=(0, 20), ipadx=5, sticky=W
        )
        self.is_favorite_filter_checkbox.grid(
            row=0, column=0, padx=10, pady=(10, 0), sticky=W
        )
        self.read_later_filter_checkbox.grid(row=1, column=0, padx=10, sticky=W)
        self.have_read_filter_checkbox.grid(row=2, column=0, padx=10, sticky=W)
        self.dont_want_to_read_filter_checkbox.grid(row=3, column=0, padx=10, sticky=W)
        self.exists_filter_checkbox.grid(
            row=4, column=0, padx=10, pady=(0,10), sticky=W
        )
        self.random_scp_button.grid(row=0, column=1, rowspan=2, padx=10, pady=(20, 0))
        self.display_top_10_button.grid(row=3, column=1, rowspan=2, padx=10, sticky=N)
        
        self.side_frame.grid(row=0, column=4, rowspan=4, pady=10, sticky=N)
        self.open_scp_in_browser_button.grid(row=0, column=0, padx=10, pady=(10, 12)) 
        self.info_label_scp_count.grid(row=2, column=0, padx=10, pady=12)
        self.update_multiple_button.grid(row=3, column=0, padx=10, pady=12)
        self.quit_button.grid(row=4, column=0, padx=10, pady=(12, 11))

        # run mainloop
        self.root.mainloop()

    def update_current_scp(self):
        """
        Update the database with the information that is currently in the gui.
        """
        # first check whether current_scp is a valid SCP object
        # or an integer of value -1 (representing an error).
        if self.current_scp == -1:
            return

        self.current_scp.is_favorite = self.is_favorite.get()
        self.current_scp.have_read = self.have_read.get()
        self.current_scp.dont_want_to_read = self.dont_want_to_read.get()
        self.current_scp.read_later = self.read_later.get()
        ORM.update_scp_in_database(self.current_scp)

    def update_multiple_scps_window(self):
        """
        Update multiple SCPs at once.
        """
        global update

        global_vars.delay_time_ms = 200

        # in case the window is already open
        try:
            if self.update.state() == "zoomed":
                return
        except AttributeError:
            pass
        except TclError:
            pass

        # function to close the update window, also resets the delay time
        def update_close_window():
            self.update.destroy()
            global_vars.delay_time_ms = cfg.DELAY_TIME_MS_DEFAULT

        # used to filter out SCPs that are already in the database
        only_new_filter = IntVar()

        # function called by the update button
        def update_multiple_scps():
            # first try to catch invalid values in the entry fields
            try:
                if (
                    int(entry_upper_bound.get()) - int(entry_lower_bound.get()) < 1
                    or int(entry_lower_bound.get()) < 1
                ):
                    messagebox.showerror(
                        "Update multiple SCPs", "Please ender a valid range."
                    )
                    entry_upper_bound.delete(0, END)
                    entry_lower_bound.delete(0, END)
                    return
            except ValueError:
                messagebox.showerror(
                    "Update multiple SCPs", "Please ender a valid range."
                )
                entry_upper_bound.delete(0, END)
                entry_lower_bound.delete(0, END)
                return

            # Store the number of requests before we update multiple.
            before_request_count = global_vars.requests_count

            # Construct a list containing the numbers of all scps that should be updated
            # based on the users filtering options.
            if only_new_filter.get():
                # Generator function for giving the numbers of scps that are currently
                # in the db successively. Only returns the numbers of scps that are in 
                # the database and that are ALSO within the bound specified by the user.
                # The numbers are sorted in order.
                def numbers_already_in_db():
                    i = 0
                    scp_nums_to_filter_out = []
                    for scp_num in ORM.get_available_scp_numbers():
                        current_scp_num = scp_num.get("number")
                        if (
                            int(entry_lower_bound.get())
                            <= current_scp_num
                            <= int(entry_upper_bound.get())
                        ):
                            scp_nums_to_filter_out.append(current_scp_num)
                    scp_nums_to_filter_out = sorted(scp_nums_to_filter_out)
                    while i < len(scp_nums_to_filter_out):
                        yield scp_nums_to_filter_out[i]
                        i += 1
                # Create an iterator from the generator function we just defined.
                # Loop over the range we want to update and check each number if it 
                # equals the number in the current iteration of the iterator. if it 
                # does, we advance the iterator by one and skip to the next number in 
                # the for loop.  If the numbers don't match we add them to 
                # scp_numbers_to_update. This way we only append numbers to the list 
                # that are NOT in the database.
                scp_numbers_to_update = []
                nums_db = numbers_already_in_db()
                try:
                    d = next(nums_db)
                # This executes if scp_nums_to_filter_out is an empty list, 
                # we set d=0 so that we don't get an error when referencing d later.
                # No scp has the number 0 so this will not filter out anything.
                except StopIteration:
                    d = 0
                for n in range(
                        int(entry_lower_bound.get()), int(entry_upper_bound.get()) + 1
                ):
                    if n == d:
                        try:
                            d = next(nums_db)
                        except StopIteration:
                            pass
                    else:
                        scp_numbers_to_update.append(n)
            # If the filter is not set then we simply update all scps in the 
            # given range (inclusive).
            else:
                scp_numbers_to_update = list(
                    range(
                        int(entry_lower_bound.get()), int(entry_upper_bound.get()) + 1
                    )
                )

            # show user the update information and ask whether they want to continue
            result = messagebox.askyesno(
                "Update multiple SCPs",
                f"Are you sure you wish to update {len(scp_numbers_to_update)} SCPs\n" +
                f"with a {global_vars.delay_time_ms} ms delay between requests?"
            )
            if not result:
                return

            # update the scps and store the resulsts to display afterwards
            update_results = []
            for scp_number in scp_numbers_to_update:
                result = scraper.update_scp(scp_number)
                update_results.append(result)
                print(f"Updated SCP-{scp_number}")
            # fetch the current request count to compare with the one taken earlier
            current_request_count = global_vars.requests_count

            # display the results of the update
            number_of_scps_added = sum(r == 1 for r in update_results)
            number_of_scps_updated = sum(r == 2 for r in update_results)
            messagebox.showinfo(
                "Update multiple SCPs",
                "Success!\n" +
                f"{number_of_scps_added} SCPs added,\n" +
                f"{number_of_scps_updated} SCPs updated.\n" +
                f"{current_request_count-before_request_count} requests sent."
            )
            self.update_info_var()

        # create the window
        self.update = Toplevel()
        self.update.title(f"Update multiple SCPs")
        self.update.geometry("350x234+1020+1000")
        self.update.resizable(width=False, height=False)
        self.update.configure(bg=cfg.BACKGROUND_COLOR)
        # protocol for when window is closed: call the update_close_window function
        self.update.protocol("WM_DELETE_WINDOW", update_close_window)

        # create the widgets
        text_frame = LabelFrame(self.update, bd=2)
        text_label1 = Label(text_frame, text="Update SCPs from")
        entry_lower_bound = Entry(text_frame, width=4)
        text_label2 = Label(text_frame, text="to")
        entry_upper_bound = Entry(text_frame, width=4)
        text_label3 = Label(text_frame, text="(inclusive)")

        delay_frame = LabelFrame(self.update, bd=2)
        delay_ms_label = Label(delay_frame, text="200 ms delay\nbetween requests")
        # callback function for slider
        def update_slider(var):
            global_vars.delay_time_ms = int(var)
            delay_ms_label.configure(
                text=f"{global_vars.delay_time_ms}ms delay\nbetween requests"
            )

        delay_slider = Scale(
            delay_frame,
            from_=200,
            to=5000,
            command=update_slider,
            showvalue=0,
            orient=HORIZONTAL,
            length=158
        )

        update_frame = LabelFrame(self.update, bd=2)
        only_new_filter_checkbox = Checkbutton(
            update_frame,
            text="Only check for SCPs\nnot currently in database",
            variable=only_new_filter,
            onvalue=1,
            offvalue=0
        )
        update_button = Button(
            update_frame, text="Update SCPs", command=update_multiple_scps
        )

        close_window_button = Button(
            self.update,
            text="Close Window",
            command=update_close_window,
            height=2,
            width=36
        )

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
        self.scp_label.grid(row=0, column=0, sticky=W)

    def set_current_scp(self, scp_number):
        """
        Sets current_scp and displays it in the scp_display_frame

        (based on its number ?)
        """
        str_number = scraper.reformat_scp_num(scp_number)

        # This block handles the case of a random search turning up empty,
        # thus calling this function with an argument of -1.
        if scp_number == -1:
            current_scp = -1
            self.scp_label.destroy()
            self.scp_label = Label(
                self.scp_display_frame,
                text="No SCP found for given criteria",
                justify=LEFT
            )
            self.scp_label.grid(row=0, column=0, sticky=W)
            return

        # Set up an scp class with current scp.
        scp = ORM.get_scp(scp_number)
        self.current_scp = scp

        # Set checkbox variables to reflect state of current_scp.
        # First check whether current_scp is a valid SCP object or 
        # simply an int of value -1 (representing an error).
        if scp != -1:
            self.is_favorite.set(scp.is_favorite)
            self.have_read.set(scp.have_read)
            self.dont_want_to_read.set(scp.dont_want_to_read)
            self.read_later.set(scp.read_later)

        # Destroy and redraw the info in scp_display_frame.
        self.scp_label.destroy()
        if scp == -1:
            self.scp_label = Label(
                self.scp_display_frame,
                text=f"SCP-{str_number} not in database!",
                justify=LEFT
            )
        elif scp.exists == False:
            scp_label = Label(
                self.scp_display_frame,
                text=f"SCP-{str_number} doesn't exist yet!",
                justify=LEFT
            )
        else:
            text = scp.get_display_string()
            self.scp_label = Label(self.scp_display_frame, text=text, justify=LEFT)
        self.scp_label.grid(row=0, column=0, sticky=W)

    def sanitize_input(self, input):
        """
        Returns codes based on user input. 1 means that the input format is valid, -1 means
        invalid.
        """
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

    def find_scp(self):
        """
        Used by find_scp_button to put an scp on the screen based on what is in the
        entry field.

        (?)
        """
        scp_number = self.entry_field.get()
        input_flag = self.sanitize_input(scp_number)
        if input_flag == -1:
            messagebox.showerror(cfg.WINDOW_NAME, "Invalid SCP number.")
            self.entry_field.delete(0, END)
            return

        self.set_current_scp(scp_number)

    def find_random_scp(self):
        """
        Displays a random SCP from the database.
        """
        scp = ORM.get_random_scp(
            not_read_yet=self.have_read_filter.get(),
            want_to_read=self.dont_want_to_read_filter.get(),
            does_exist=self.exists_filter.get(),
            is_favorite=self.is_favorite_filter.get(),
            read_later=self.read_later_filter.get()
        )
        if scp == -1:
            self.set_current_scp(-1)
        else:
            self.set_current_scp(scp.number)

    def open_scp_in_browser(self):
        """
        Opens current_scp in a browser
        """
        if self.current_scp == -1:
            return

        scraper.go_to_scp_page(self.current_scp.number)

    def add_update_database(self):
        """
        Takes the scp_number from the entry field and adds/updates the corresponding SCP
        in the database.
        """
        scp_number = self.entry_field.get()
        input_flag = self.sanitize_input(scp_number)

        if input_flag == -1:
            messagebox.showerror(cfg.WINDOW_NAME, "Invalid SCP number!")
            self.entry_field.delete(0, END)
            return

        result = scraper.update_scp(scp_number)
        self.set_current_scp(scp_number)

        if result == 1:
            messagebox.showinfo(cfg.WINDOW_NAME, "SCP successfully added to database!")
        if result == 2:
            messagebox.showinfo(cfg.WINDOW_NAME, "SCP successfully updated in database!")

        self.update_info_var()

    def show_top_x(self, highest_rank_index, lowest_rank_index):
        """
        Shows the top 10 SCPs currently in the database.
        This can be displayed in a seperate window.
        """
        # TODO top should be an instance attribute
        # check to see if the window is already open
        try:
            # if it is, then
            if top.state() == "zoomed":
                self.main_frame.destroy()
        except TclError:
            top = Toplevel()
            top.title(f"Top SCPs")
            top.geometry("399x500+950+300")
            top.resizable(width=False, height=False)
        except NameError:
            top = Toplevel()
            top.title(f"Top SCPs")
            try:
                top.iconphoto(False, PhotoImage(file=cfg.LOGO_PATH))
            except TclError:
                pass
            top.geometry("399x500+950+300")
            top.resizable(width=False, height=False)

        # filter search based on checkboxes
        extra_filters = []
        if self.is_favorite_filter.get():
            extra_filters.append("is_favorite")
        if self.have_read_filter.get():
            extra_filters.append("have_read")
        if self.dont_want_to_read_filter.get():
            extra_filters.append("dont_want_to_read")
        if self.read_later_filter.get():
            extra_filters.append("read_later")

        filters = ["rating"] + extra_filters
        scps = ORM.get_available_scps(filters)

        filtered_scps = []
        for scp in scps:
            try:
                int(scp.rating)
            except ValueError:
                continue
            if self.is_favorite_filter.get() and scp.is_favorite== 0:
                continue
            if self.have_read_filter.get() and scp.have_read == 1:
                continue
            if self.dont_want_to_read_filter.get() and scp.dont_want_to_read == 1:
                continue
            if self.read_later_filter.get() and scp.read_later == 0:
                continue
            filtered_scps.append(scp)

        def top_rated_sort(scp):
            """
            Given a list of scp instances, sorts the list based on "rating" and
            returns it.
            """
            try:
                return int(scp.rating)
            except ValueError:
                pass

        sorted_scps = sorted(filtered_scps, key=top_rated_sort, reverse=True)
        # sorted_scps_numbers = [scp.number for scp in sorted_scps]
        try:
            sorted_scps = sorted_scps[highest_rank_index:lowest_rank_index]
        except IndexError:
            pass

        # draw the scp information in the window
        self.main_frame = LabelFrame(top, bd=0)
        self.main_frame.grid(row=0, column=0, columnspan=3)
        for i, scp in enumerate(sorted_scps):
            text = scp.get_display_string()


            new_frame = LabelFrame(self.main_frame, bd=0)
            new_rank_label = Label(
                new_frame, text="# " + str(highest_rank_index+i+1)
            )
            # create a high-class function so that the callback function sends the user 
            # to the correct link when the button is pressed later. If we simply used a 
            # variable here then the variable would be overwritten during later loop
            # iterations and thus every button would send the user to the same page. 
            # This way we can keep the scp_number within the scope of the higher function 
            # so that it is stored until the callback function is called.
            def higher_function(var):
                return lambda: scraper.go_to_scp_page(var)

            new_browser_button = Button(
                new_frame,
                text="Open in\nBrowser",
                command=higher_function(scp.number),
                height=2,
                width=7
            )
            new_label = Label(new_frame, text=text, justify=LEFT)

            new_frame.grid(row=i, column=0, columnspan=3, padx=0, pady=0, sticky=W)
            new_rank_label.grid(row=0, column=0, pady=(2, 0))
            new_browser_button.grid(row=1, column=0, padx=10, sticky=N)
            new_label.grid(row=0, column=1, rowspan=2, padx=(0, 10), pady=5, sticky=W)
        # draw buttons for the bottom of the frame
        self.close_button = Button(
            top, text="Close Window",
            command=top.destroy,
            width=20
        )
        self.previous_button = Button(
            top,
            text="<<",
            command=lambda: show_top_x(
                highest_rank_index - 5,
                lowest_rank_index - 5
            )
        )
        if highest_rank_index == 0:
            self.previous_button.configure(state=DISABLED)
        self.next_button = Button(
            top,
            text=">>",
            command=lambda: self.show_top_x(
                highest_rank_index + 5,
                lowest_rank_index + 5
            )
        )
        if lowest_rank_index > len(sorted_scps):
            self.next_button.configure(state=DISABLED)

        self.close_button.grid(
            row=lowest_rank_index - highest_rank_index + 1,
            column=1,
            padx=10,
            pady=(20, 10)
        )
        self.previous_button.grid(
            row=lowest_rank_index - highest_rank_index + 1,
            column=0,
            padx=10,
            pady=(20, 10)
        )
        self.next_button.grid(
            row=lowest_rank_index - highest_rank_index + 1,
            column=2,
            padx=10,
            pady=(20, 10)
        )
    def update_info_var(self):
        """
        Updates info_labels variable with desired info.
        """
        num_scps_in_db = len(ORM.get_available_scp_numbers())
        total_requests = global_vars.requests_count
        self.info_var.set(
            f"{num_scps_in_db} SCPs\nin database\n\n{total_requests} requests sent"
        )
