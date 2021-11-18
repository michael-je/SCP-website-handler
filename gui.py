from tkinter import *


class TkinterGUI():
    """
    """
    def __init__(self):
        self.root = TK()
        root.title(cfg.WINDOW_NAME)
        root.geometry(cfg.WINDOW_GEOMETRY + "+" + cfg.WINDOW_SPAWN_XY)
        root.configure(bg=cfg.BACKGROUND_COLOR)
        root.resizable(width=False, height=False)
        try:
            root.iconphoto(False, PhotoImage(file=logo_path))
        except TclError:
            pass

        self.current_scp = -1

        # tkinter variables
        self.scp_display_frame
        self.scp_label

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

    def update_current_scp(self):
        """
        Update the database with the information which is currently in the gui.
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

    def update_multiple_scps_window():
        """
        Update multiple SCPs at once.
        """
        global update

        global_vars.delay_time_ms = 200

        # in case the window is already open
        try:
            if self.update.state() == "zoomed":
                return
        except NameError:
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
                "Are you sure you wish to update {len(scp_numbers_to_update)} SCPs\n" +
                "with a {global_vars.delay_time_ms} ms delay between requests?"
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
        try:
            self.update.iconphoto(False, PhotoImage(file=cfg.LOGO_PATH))
        except TclError:
            pass
        self.update.geometry("350x234+1020+350")
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
        def self.update_slider(var):
            global_vars.delay_time_ms = int(var)
            delay_ms_label.configure(
                text=f"{global_vars.delay_time_ms}ms delay\nbetween requests"
            )
        delay_slider = Scale(
            delay_frame,
            from_=200,
            to=5000,
            command=self.update_slider,
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
            update_frame, text="Update SCPs", command=self.update_multiple_scps
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
