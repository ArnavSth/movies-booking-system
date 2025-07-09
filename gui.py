import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import re
from system import Session, engine, Base, UserDB, MovieDB, BookingDB, RequestHistoryDB, Movie, Booking, save_to_db, load_movies_from_db, load_user_bookings, log_request, validate_email

class MovieBookingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Booking System")
        self.root.geometry("400x300")
        self.session = Session()
        self.current_user = None

        # Apply a modern theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Title.TLabel", font=("Arial", 18, "bold"))

        # Main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill='both', expand=True)

        # Welcome label
        ttk.Label(self.main_frame, text="Movie Booking System", style="Title.TLabel").pack(pady=20)

        # Main menu buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="User Login", command=self.user_login, width=20).pack(pady=5)
        ttk.Button(button_frame, text="User Register", command=self.user_register, width=20).pack(pady=5)
        ttk.Button(button_frame, text="Admin Login", command=self.admin_login, width=20).pack(pady=5)
        ttk.Button(button_frame, text="Exit", command=root.quit, width=20).pack(pady=5)

    def validate_input(self, **kwargs):
        """Validate input fields"""
        errors = []
        
        if 'name' in kwargs and not kwargs['name'].strip():
            errors.append("Name is required")
        
        if 'email' in kwargs:
            if not kwargs['email'].strip():
                errors.append("Email is required")
            elif not validate_email(kwargs['email']):
                errors.append("Invalid email format")
        
        if 'password' in kwargs and len(kwargs['password']) < 6:
            errors.append("Password must be at least 6 characters")
        
        if 'seats' in kwargs:
            try:
                seats = int(kwargs['seats'])
                if seats <= 0:
                    errors.append("Seats must be a positive number")
            except ValueError:
                errors.append("Seats must be a valid number")
        
        if 'price' in kwargs:
            try:
                price = float(kwargs['price'])
                if price < 0:
                    errors.append("Price cannot be negative")
            except ValueError:
                errors.append("Price must be a valid number")
        
        return errors

    def user_register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("User Registration")
        register_window.geometry("350x300")
        register_window.resizable(False, False)

        # Center the window
        register_window.transient(self.root)
        register_window.grab_set()

        main_frame = ttk.Frame(register_window, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Form fields
        ttk.Label(main_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = ttk.Entry(main_frame, width=25)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        email_entry = ttk.Entry(main_frame, width=25)
        email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        password_entry = ttk.Entry(main_frame, show='*', width=25)
        password_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Confirm Password:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        confirm_entry = ttk.Entry(main_frame, show='*', width=25)
        confirm_entry.grid(row=3, column=1, padx=5, pady=5)

        def register():
            data = {
                'name': name_entry.get(),
                'email': email_entry.get(),
                'password': password_entry.get()
            }
            
            errors = self.validate_input(**data)
            
            if password_entry.get() != confirm_entry.get():
                errors.append("Passwords do not match")
            
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            if self.session.query(UserDB).filter_by(email=data['email']).first():
                messagebox.showerror("Error", "Email already registered")
                return
            
            try:
                user_db = UserDB(name=data['name'], email=data['email'], password=data['password'], is_admin=False)
                save_to_db(self.session, user_db)
                messagebox.showinfo("Success", "Registration successful!")
                register_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Register", command=register).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=register_window.destroy).pack(side='left', padx=5)

    def user_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("User Login")
        login_window.geometry("300x200")
        login_window.resizable(False, False)
        login_window.transient(self.root)
        login_window.grab_set()

        main_frame = ttk.Frame(login_window, padding="20")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        email_entry = ttk.Entry(main_frame, width=25)
        email_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        password_entry = ttk.Entry(main_frame, show='*', width=25)
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        def login():
            email, password = email_entry.get().strip(), password_entry.get()
            
            if not email or not password:
                messagebox.showerror("Error", "Please enter both email and password")
                return
            
            try:
                user_db = self.session.query(UserDB).filter_by(email=email, password=password, is_admin=False).first()
                if user_db:
                    self.current_user = user_db
                    login_window.destroy()
                    UserDashboard(self.root, self.current_user, self.session)
                else:
                    messagebox.showerror("Error", "Invalid credentials")
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {str(e)}")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Login", command=login).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=login_window.destroy).pack(side='left', padx=5)

    def admin_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Admin Login")
        login_window.geometry("300x250")
        login_window.resizable(False, False)
        login_window.transient(self.root)
        login_window.grab_set()

        main_frame = ttk.Frame(login_window, padding="20")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        email_entry = ttk.Entry(main_frame, width=25)
        email_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        password_entry = ttk.Entry(main_frame, show='*', width=25)
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Admin ID:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        admin_id_entry = ttk.Entry(main_frame, width=25)
        admin_id_entry.grid(row=2, column=1, padx=5, pady=5)

        def login():
            email, password, admin_id = email_entry.get().strip(), password_entry.get(), admin_id_entry.get().strip()
            
            if not all([email, password, admin_id]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                admin_db = self.session.query(UserDB).filter_by(email=email, password=password, is_admin=True, admin_id=admin_id).first()
                if admin_db:
                    self.current_user = admin_db
                    login_window.destroy()
                    AdminDashboard(self.root, self.current_user, self.session)
                else:
                    messagebox.showerror("Error", "Invalid admin credentials")
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {str(e)}")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Login", command=login).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=login_window.destroy).pack(side='left', padx=5)

class UserDashboard:
    def __init__(self, parent, user, session):
        self.user = user
        self.session = session
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(f"User Dashboard - {user.name}")
        self.window.geometry("1000x700")
        self.window.transient(parent)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Define tabs
        self.movies_tab = ttk.Frame(self.notebook)
        self.book_tab = ttk.Frame(self.notebook)
        self.bookings_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.profile_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.movies_tab, text="Movies")
        self.notebook.add(self.book_tab, text="Book Ticket")
        self.notebook.add(self.bookings_tab, text="My Bookings")
        self.notebook.add(self.history_tab, text="Request History")
        self.notebook.add(self.profile_tab, text="Profile")

        # Initialize variables
        self.movies_tree = None
        self.bookings_tree = None
        self.history_listbox = None

        # Populate tabs
        self.populate_movies_tab()
        self.populate_book_tab()
        self.populate_bookings_tab()
        self.populate_history_tab()
        self.populate_profile_tab()

        # Status bar
        self.status_var = tk.StringVar(value=f"Logged in as {user.name}")
        status_frame = ttk.Frame(self.window)
        status_frame.pack(fill='x', side='bottom', pady=5)
        
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken").pack(side='left', fill='x', expand=True)
        ttk.Button(status_frame, text="Refresh All", command=self.refresh_all_tabs).pack(side='right', padx=5)
        ttk.Button(status_frame, text="Logout", command=self.logout).pack(side='right', padx=5)

    def refresh_all_tabs(self):
        """Refresh all tabs data"""
        try:
            self.populate_movies_tab()
            self.populate_bookings_tab()
            self.populate_history_tab()
            self.status_var.set("Data refreshed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")

    def logout(self):
        """Logout and close window"""
        self.window.destroy()

    def populate_movies_tab(self):
        # Clear existing content
        for widget in self.movies_tab.winfo_children():
            widget.destroy()

        log_request(self.session, self.user, "VIEW_MOVIES")
        
        # Search frame
        search_frame = ttk.Frame(self.movies_tab)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        def search_movies():
            self.filter_movies(search_var.get())
        
        ttk.Button(search_frame, text="Search", command=search_movies).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Clear", command=lambda: [search_var.set(''), self.filter_movies('')]).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Refresh", command=self.populate_movies_tab).pack(side='right', padx=5)

        # Movies tree
        columns = ("ID", "Name", "Showtime", "Seats Available", "Price", "Description")
        self.movies_tree = ttk.Treeview(self.movies_tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.movies_tree.heading(col, text=col)
            self.movies_tree.column(col, width=130)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.movies_tab, orient="vertical", command=self.movies_tree.yview)
        self.movies_tree.configure(yscrollcommand=scrollbar.set)
        
        self.movies_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.filter_movies('')

    def filter_movies(self, search_term):
        """Filter movies based on search term"""
        # Clear existing items
        for item in self.movies_tree.get_children():
            self.movies_tree.delete(item)
        
        try:
            movies = load_movies_from_db(self.session)
            for movie in movies:
                if not search_term or search_term.lower() in movie.name.lower():
                    self.movies_tree.insert("", "end", values=(
                        movie.id, movie.name, movie.showtime, 
                        movie.available_seats, f"${movie.price:.2f}", movie.description
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load movies: {str(e)}")

    def populate_book_tab(self):
        # Clear existing content
        for widget in self.book_tab.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.book_tab, padding="20")
        main_frame.pack(fill='both', expand=True)

        try:
            movies = load_movies_from_db(self.session)
            available_movies = [m for m in movies if m.available_seats > 0]
            movie_names = [m.name for m in available_movies]

            if not movie_names:
                ttk.Label(main_frame, text="No movies available for booking", font=("Arial", 12)).pack(pady=50)
                return

            # Movie selection
            ttk.Label(main_frame, text="Select Movie:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=10, sticky="e")
            self.movie_var = tk.StringVar()
            movie_combo = ttk.Combobox(main_frame, textvariable=self.movie_var, values=movie_names, state="readonly", width=30)
            movie_combo.grid(row=0, column=1, padx=5, pady=10)

            # Seats selection
            ttk.Label(main_frame, text="Number of Seats:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=10, sticky="e")
            self.seats_var = tk.StringVar()
            seats_spinbox = ttk.Spinbox(main_frame, from_=1, to=10, textvariable=self.seats_var, width=30)
            seats_spinbox.grid(row=1, column=1, padx=5, pady=10)

            # Movie details
            self.movie_details_var = tk.StringVar(value="Select a movie to see details")
            details_label = ttk.Label(main_frame, textvariable=self.movie_details_var, wraplength=400, justify="left")
            details_label.grid(row=2, column=0, columnspan=2, pady=10)

            # Total price
            self.total_var = tk.StringVar(value="Total: $0.00")
            total_label = ttk.Label(main_frame, textvariable=self.total_var, font=("Arial", 14, "bold"))
            total_label.grid(row=3, column=0, columnspan=2, pady=10)

            def update_details_and_total(*args):
                movie_name = self.movie_var.get()
                seats = self.seats_var.get()
                if movie_name:
                    movie = next((m for m in available_movies if m.name == movie_name), None)
                    if movie:
                        details = f"Showtime: {movie.showtime}\nAvailable Seats: {movie.available_seats}\nPrice per seat: ${movie.price:.2f}\nDescription: {movie.description}"
                        self.movie_details_var.set(details)
                        if seats:
                            try:
                                num_seats = int(seats)
                                if num_seats > movie.available_seats:
                                    self.total_var.set(f"Only {movie.available_seats} seats available!")
                                else:
                                    self.total_var.set(f"Total: ${movie.price * num_seats:.2f}")
                            except ValueError:
                                self.total_var.set("Total: $0.00")
                else:
                    self.movie_details_var.set("Select a movie to see details")
                    self.total_var.set("Total: $0.00")

            self.movie_var.trace("w", update_details_and_total)
            self.seats_var.trace("w", update_details_and_total)

            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=4, column=0, columnspan=2, pady=20)
            ttk.Button(button_frame, text="Book Ticket", command=self.book_ticket).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Refresh Movies", command=self.populate_book_tab).pack(side='left', padx=5)
        
        except Exception as e:
            ttk.Label(main_frame, text=f"Failed to load booking form: {str(e)}", font=("Arial", 12)).pack(pady=20)

    def book_ticket(self):
        movie_name = self.movie_var.get()
        num_seats = self.seats_var.get()
        if not movie_name or not num_seats:
            messagebox.showerror("Error", "Please select a movie and enter seats")
            return
        try:
            num_seats = int(num_seats)
            if num_seats <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Seats must be a positive integer")
            return
        movies = load_movies_from_db(self.session)
        movie = next((m for m in movies if m.name == movie_name), None)
        if not movie:
            messagebox.showerror("Error", "Movie not found")
            return
        if movie.book_seats(num_seats):
            booking_db = BookingDB(user_id=self.user.id, movie_id=movie.id, num_seats=num_seats)
            movie_db = self.session.query(MovieDB).filter_by(id=movie.id).first()
            movie_db.available_seats = movie.available_seats
            save_to_db(self.session, booking_db)
            messagebox.showinfo("Success", "Booking successful!")
            self.populate_movies_tab()
            self.populate_bookings_tab()
            if hasattr(self, 'status_var'):
                self.status_var.set("Booking successful!")
        else:
            messagebox.showerror("Error", "Not enough seats available")

    def cancel_booking(self):
        if not self.bookings_tree.selection():
            messagebox.showerror("Error", "Please select a booking to cancel")
            return
        if not messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
            return
        try:
            selected_item = self.bookings_tree.selection()[0]
            booking_id = self.bookings_tree.item(selected_item)["values"][0]
            booking = self.session.query(BookingDB).filter_by(id=booking_id).first()
            if booking:
                movie_db = self.session.query(MovieDB).filter_by(id=booking.movie_id).first()
                if movie_db:
                    movie_db.available_seats += booking.num_seats
                self.session.delete(booking)
                self.session.commit()
                messagebox.showinfo("Success", "Booking canceled successfully")
                self.populate_bookings_tab()
                self.populate_movies_tab()
                if hasattr(self, 'status_var'):
                    self.status_var.set("Booking canceled")
            else:
                messagebox.showerror("Error", "Booking not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel booking: {str(e)}")

    def populate_bookings_tab(self):
        # Clear existing content
        for widget in self.bookings_tab.winfo_children():
            widget.destroy()

        log_request(self.session, self.user, "VIEW_BOOKINGS")
        
        # Control buttons
        control_frame = ttk.Frame(self.bookings_tab)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Cancel Booking", command=self.cancel_booking).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.populate_bookings_tab).pack(side='right', padx=5)

        try:
            bookings = self.session.query(BookingDB).filter_by(user_id=self.user.id).all()
            movies = {m.id: m for m in load_movies_from_db(self.session)}
            users = {u.id: u for u in self.session.query(UserDB).all()}

            if not bookings:
                ttk.Label(self.bookings_tab, text="No bookings found", 
                         font=("Arial", 12)).pack(pady=50)
                return

            columns = ("ID", "User", "Movie", "Seats", "Total Price", "Booking Time")
            self.bookings_tree = ttk.Treeview(self.bookings_tab, columns=columns, show="headings", height=15)
            
            for col in columns:
                self.bookings_tree.heading(col, text=col)
                self.bookings_tree.column(col, width=150)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(self.bookings_tab, orient="vertical", command=self.bookings_tree.yview)
            self.bookings_tree.configure(yscrollcommand=scrollbar.set)
            
            for booking in bookings:
                user = users.get(booking.user_id)
                movie = movies.get(booking.movie_id)
                total_price = movie.price * booking.num_seats if movie else 0
                self.bookings_tree.insert("", "end", values=(
                    booking.id, user.name if user else "Unknown", 
                    movie.name if movie else "Unknown", booking.num_seats, 
                    f"${total_price:.2f}", booking.booking_time
                ))
            
            self.bookings_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bookings: {str(e)}")

    def populate_history_tab(self):
        # Clear existing content
        for widget in self.history_tab.winfo_children():
            widget.destroy()

        log_request(self.session, self.user, "VIEW_HISTORY")
        
        # Control buttons
        control_frame = ttk.Frame(self.history_tab)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Refresh", command=self.populate_history_tab).pack(side='right', padx=5)

        try:
            history = self.session.query(RequestHistoryDB).order_by(RequestHistoryDB.request_time.desc()).all()
            users = {u.id: u for u in self.session.query(UserDB).all()}

            if not history:
                ttk.Label(self.history_tab, text="No history found", 
                         font=("Arial", 12)).pack(pady=50)
                return

            self.history_listbox = tk.Listbox(self.history_tab, height=20, font=("Arial", 10))
            scrollbar = ttk.Scrollbar(self.history_tab, orient="vertical", command=self.history_listbox.yview)
            self.history_listbox.configure(yscrollcommand=scrollbar.set)
            
            for h in history:
                user = users.get(h.user_id)
                self.history_listbox.insert("end", 
                    f"{h.request_time.strftime('%Y-%m-%d %H:%M:%S')} - {user.name if user else 'Unknown'} - {h.request_type}")
            
            self.history_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {str(e)}")

    def populate_profile_tab(self):
        # Clear existing content
        for widget in self.profile_tab.winfo_children():
            widget.destroy()
        main_frame = ttk.Frame(self.profile_tab, padding="20")
        main_frame.pack(fill='both', expand=True)
        ttk.Label(main_frame, text="User Profile", font=("Arial", 16, "bold")).pack(pady=20)
        info_frame = ttk.LabelFrame(main_frame, text="Profile Information", padding="10")
        info_frame.pack(fill='x', pady=10)
        ttk.Label(info_frame, text=f"Name: {self.user.name}", font=("Arial", 12)).pack(anchor='w', pady=5)
        ttk.Label(info_frame, text=f"Email: {self.user.email}", font=("Arial", 12)).pack(anchor='w', pady=5)
        ttk.Label(info_frame, text=f"Account Type: User", font=("Arial", 12)).pack(anchor='w', pady=5)
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.pack(fill='x', pady=10)
        try:
            total_bookings = self.session.query(BookingDB).filter_by(user_id=self.user.id).count()
            total_requests = self.session.query(RequestHistoryDB).filter_by(user_id=self.user.id).count()
            ttk.Label(stats_frame, text=f"Total Bookings: {total_bookings}", font=("Arial", 12)).pack(anchor='w', pady=5)
            ttk.Label(stats_frame, text=f"Total Requests: {total_requests}", font=("Arial", 12)).pack(anchor='w', pady=5)
        except Exception as e:
            ttk.Label(stats_frame, text="Unable to load statistics", font=("Arial", 12)).pack(anchor='w', pady=5)

class AdminDashboard:
    def __init__(self, parent, admin, session):
        self.admin = admin
        self.session = session
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(f"Admin Dashboard - {admin.name}")
        self.window.geometry("1200x800")
        self.window.transient(parent)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Define tabs
        self.movies_tab = ttk.Frame(self.notebook)
        self.bookings_tab = ttk.Frame(self.notebook)
        self.users_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.movies_tab, text="Manage Movies")
        self.notebook.add(self.bookings_tab, text="All Bookings")
        self.notebook.add(self.users_tab, text="User Management")
        self.notebook.add(self.history_tab, text="Request History")
        self.notebook.add(self.stats_tab, text="Statistics")

        # Initialize variables
        self.movies_tree = None
        self.bookings_tree = None
        self.users_tree = None
        self.history_listbox = None

        # Populate tabs
        self.populate_movies_tab()
        self.populate_bookings_tab()
        self.populate_users_tab()
        self.populate_history_tab()
        self.populate_stats_tab()

        # Status bar
        self.status_var = tk.StringVar(value=f"Logged in as {admin.name} (Admin)")
        status_frame = ttk.Frame(self.window)
        status_frame.pack(fill='x', side='bottom', pady=5)
        
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken").pack(side='left', fill='x', expand=True)
        ttk.Button(status_frame, text="Refresh All", command=self.refresh_all_tabs).pack(side='right', padx=5)
        ttk.Button(status_frame, text="Logout", command=self.logout).pack(side='right', padx=5)

    def refresh_all_tabs(self):
        """Refresh all tabs data"""
        try:
            self.populate_movies_tab()
            self.populate_bookings_tab()
            self.populate_users_tab()
            self.populate_history_tab()
            self.populate_stats_tab()
            self.status_var.set("All data refreshed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")

    def logout(self):
        """Logout and close window"""
        self.window.destroy()

    def populate_movies_tab(self):
        # Clear existing content
        for widget in self.movies_tab.winfo_children():
            widget.destroy()

        log_request(self.session, self.admin, "VIEW_MOVIES")
        
        # Control buttons
        control_frame = ttk.Frame(self.movies_tab)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Add Movie", command=self.add_movie).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Edit Movie", command=self.edit_movie).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Delete Movie", command=self.delete_movie).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.populate_movies_tab).pack(side='right', padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.movies_tab)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.movie_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.movie_search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_movies).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Clear", command=lambda: [self.movie_search_var.set(''), self.search_movies()]).pack(side='left', padx=5)

        try:
            movies = load_movies_from_db(self.session)

            columns = ("ID", "Name", "Showtime", "Total Seats", "Available Seats", "Price", "Description")
            self.movies_tree = ttk.Treeview(self.movies_tab, columns=columns, show="headings", height=15)
            
            for col in columns:
                self.movies_tree.heading(col, text=col)
                self.movies_tree.column(col, width=120)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(self.movies_tab, orient="vertical", command=self.movies_tree.yview)
            self.movies_tree.configure(yscrollcommand=scrollbar.set)
            
            for movie in movies:
                self.movies_tree.insert("", "end", values=(
                    movie.id, movie.name, movie.showtime, movie.total_seats, 
                    movie.available_seats, f"${movie.price:.2f}", movie.description
                ))
            
            self.movies_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load movies: {str(e)}")

    def search_movies(self):
        """Search movies based on search term"""
        search_term = self.movie_search_var.get().lower()
        
        # Clear existing items
        for item in self.movies_tree.get_children():
            self.movies_tree.delete(item)
        
        try:
            movies = load_movies_from_db(self.session)
            for movie in movies:
                if not search_term or search_term in movie.name.lower() or search_term in movie.description.lower():
                    self.movies_tree.insert("", "end", values=(
                        movie.id, movie.name, movie.showtime, movie.total_seats, 
                        movie.available_seats, f"${movie.price:.2f}", movie.description
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search movies: {str(e)}")

    def add_movie(self):
        """Add new movie"""
        self.movie_form_window("Add Movie", None)

    def edit_movie(self):
        """Edit selected movie"""
        if not self.movies_tree.selection():
            messagebox.showerror("Error", "Please select a movie to edit")
            return
        
        selected_item = self.movies_tree.selection()[0]
        movie_id = self.movies_tree.item(selected_item)["values"][0]
        
        try:
            movie = self.session.query(MovieDB).filter_by(id=movie_id).first()
            if movie:
                self.movie_form_window("Edit Movie", movie)
            else:
                messagebox.showerror("Error", "Movie not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load movie: {str(e)}")

    def movie_form_window(self, title, movie=None):
        """Movie form window for add/edit"""
        form_window = tk.Toplevel(self.window)
        form_window.title(title)
        form_window.geometry("450x400")
        form_window.resizable(False, False)
        form_window.transient(self.window)
        form_window.grab_set()

        main_frame = ttk.Frame(form_window, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Form fields
        fields = {
            "Name": tk.StringVar(value=movie.name if movie else ""),
            "Showtime": tk.StringVar(value=movie.showtime if movie else ""),
            "Total Seats": tk.StringVar(value=str(movie.total_seats) if movie else ""),
            "Price": tk.StringVar(value=str(movie.price) if movie else ""),
            "Description": tk.StringVar(value=movie.description if movie else "")
        }

        entries = {}
        for i, (field, var) in enumerate(fields.items()):
            ttk.Label(main_frame, text=f"{field}:", font=("Arial", 11)).grid(row=i, column=0, padx=5, pady=8, sticky="e")
            
            if field == "Description":
                entry = tk.Text(main_frame, height=4, width=30, font=("Arial", 10))
                entry.insert("1.0", var.get())
                entry.grid(row=i, column=1, padx=5, pady=8)
            else:
                entry = ttk.Entry(main_frame, textvariable=var, width=30, font=("Arial", 10))
                entry.grid(row=i, column=1, padx=5, pady=8)
            
            entries[field] = entry

        def save_movie():
            try:
                # Get values
                name = fields["Name"].get().strip()
                showtime = fields["Showtime"].get().strip()
                total_seats = int(fields["Total Seats"].get())
                price = float(fields["Price"].get())
                description = entries["Description"].get("1.0", tk.END).strip()

                # Validate
                if not all([name, showtime, description]):
                    messagebox.showerror("Error", "Please fill all fields")
                    return
                
                if total_seats <= 0:
                    messagebox.showerror("Error", "Total seats must be positive")
                    return
                    
                if price < 0:
                    messagebox.showerror("Error", "Price cannot be negative")
                    return

                if movie:  # Edit existing movie
                    movie.name = name
                    movie.showtime = showtime
                    # Only update total seats if it's not less than booked seats
                    booked_seats = movie.total_seats - movie.available_seats
                    if total_seats < booked_seats:
                        messagebox.showerror("Error", f"Total seats cannot be less than booked seats ({booked_seats})")
                        return
                    movie.available_seats = total_seats - booked_seats
                    movie.total_seats = total_seats
                    movie.price = price
                    movie.description = description
                    
                    self.session.commit()
                    messagebox.showinfo("Success", "Movie updated successfully")
                else:  # Add new movie
                    movie_db = MovieDB(
                        name=name,
                        showtime=showtime,
                        total_seats=total_seats,
                        available_seats=total_seats,
                        price=price,
                        description=description
                    )
                    save_to_db(self.session, movie_db)
                    messagebox.showinfo("Success", "Movie added successfully")

                form_window.destroy()
                self.populate_movies_tab()
                self.status_var.set("Movie saved successfully")

            except ValueError as e:
                messagebox.showerror("Error", "Please enter valid numbers for seats and price")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save movie: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_movie).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=form_window.destroy).pack(side='left', padx=5)

    def delete_movie(self):
        """Delete selected movie"""
        if not self.movies_tree.selection():
            messagebox.showerror("Error", "Please select a movie to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this movie?\nThis action cannot be undone."):
            return
        
        try:
            selected_item = self.movies_tree.selection()[0]
            movie_id = self.movies_tree.item(selected_item)["values"][0]
            
            # Check if movie has bookings
            if self.session.query(BookingDB).filter_by(movie_id=movie_id).first():
                messagebox.showerror("Error", "Cannot delete movie with existing bookings")
                return
            
            movie = self.session.query(MovieDB).filter_by(id=movie_id).first()
            if movie:
                self.session.delete(movie)
                self.session.commit()
                messagebox.showinfo("Success", "Movie deleted successfully")
                self.populate_movies_tab()
                self.status_var.set("Movie deleted successfully")
            else:
                messagebox.showerror("Error", "Movie not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete movie: {str(e)}")

    def populate_bookings_tab(self):
        # Clear existing content
        for widget in self.bookings_tab.winfo_children():
            widget.destroy()

        log_request(self.session, self.admin, "VIEW_BOOKINGS")
        
        # Control buttons
        control_frame = ttk.Frame(self.bookings_tab)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Cancel Booking", command=self.cancel_user_booking).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.populate_bookings_tab).pack(side='right', padx=5)

        try:
            bookings = self.session.query(BookingDB).all()
            movies = {m.id: m for m in load_movies_from_db(self.session)}
            users = {u.id: u for u in self.session.query(UserDB).all()}

            if not bookings:
                ttk.Label(self.bookings_tab, text="No bookings found", 
                         font=("Arial", 12)).pack(pady=50)
                return

            columns = ("ID", "User", "Movie", "Seats", "Total Price", "Booking Time")
            self.bookings_tree = ttk.Treeview(self.bookings_tab, columns=columns, show="headings", height=15)
            
            for col in columns:
                self.bookings_tree.heading(col, text=col)
                self.bookings_tree.column(col, width=150)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(self.bookings_tab, orient="vertical", command=self.bookings_tree.yview)
            self.bookings_tree.configure(yscrollcommand=scrollbar.set)
            
            for booking in bookings:
                user = users.get(booking.user_id)
                movie = movies.get(booking.movie_id)
                total_price = movie.price * booking.num_seats if movie else 0
                self.bookings_tree.insert("", "end", values=(
                    booking.id, user.name if user else "Unknown", 
                    movie.name if movie else "Unknown", booking.num_seats, 
                    f"${total_price:.2f}", booking.booking_time
                ))
            
            self.bookings_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bookings: {str(e)}")

    def cancel_user_booking(self):
        """Cancel selected booking"""
        if not self.bookings_tree.selection():
            messagebox.showerror("Error", "Please select a booking to cancel")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
            return
        
        try:
            selected_item = self.bookings_tree.selection()[0]
            booking_id = self.bookings_tree.item(selected_item)["values"][0]
            
            booking = self.session.query(BookingDB).filter_by(id=booking_id).first()
            if booking:
                # Return seats to movie
                movie_db = self.session.query(MovieDB).filter_by(id=booking.movie_id).first()
                if movie_db:
                    movie_db.available_seats += booking.num_seats
                
                # Delete booking
                self.session.delete(booking)
                self.session.commit()
                
                messagebox.showinfo("Success", "Booking canceled successfully")
                self.populate_bookings_tab()
                self.status_var.set("Booking canceled successfully")
            else:
                messagebox.showerror("Error", "Booking not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel booking: {str(e)}")

    def populate_users_tab(self):
        """Populate users management tab"""
        # Clear existing content
        for widget in self.users_tab.winfo_children():
            widget.destroy()

        # Control buttons
        control_frame = ttk.Frame(self.users_tab)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="View User Details", command=self.view_user_details).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.populate_users_tab).pack(side='right', padx=5)

        try:
            users = self.session.query(UserDB).filter_by(is_admin=False).all()

            if not users:
                ttk.Label(self.users_tab, text="No users found", 
                         font=("Arial", 12)).pack(pady=50)
                return

            columns = ("ID", "Name", "Email", "Total Bookings", "Last Activity")
            self.users_tree = ttk.Treeview(self.users_tab, columns=columns, show="headings", height=15)
            
            for col in columns:
                self.users_tree.heading(col, text=col)
                self.users_tree.column(col, width=150)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(self.users_tab, orient="vertical", command=self.users_tree.yview)
            self.users_tree.configure(yscrollcommand=scrollbar.set)
            
            for user in users:
                booking_count = self.session.query(BookingDB).filter_by(user_id=user.id).count()
                last_activity = self.session.query(RequestHistoryDB).filter_by(user_id=user.id).order_by(RequestHistoryDB.request_time.desc()).first()
                last_activity_str = last_activity.request_time.strftime('%Y-%m-%d %H:%M') if last_activity else "Never"
                
                self.users_tree.insert("", "end", values=(
                    user.id, user.name, user.email, booking_count, last_activity_str
                ))
            
            self.users_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")

    def view_user_details(self):
        """View detailed information about selected user"""
        if not self.users_tree.selection():
            messagebox.showerror("Error", "Please select a user to view details")
            return
        
        try:
            selected_item = self.users_tree.selection()[0]
            user_id = self.users_tree.item(selected_item)["values"][0]
            
            user = self.session.query(UserDB).filter_by(id=user_id).first()
            if not user:
                messagebox.showerror("Error", "User not found")
                return
            
            # Create details window
            details_window = tk.Toplevel(self.window)
            details_window.title(f"User Details - {user.name}")
            details_window.geometry("600x500")
            details_window.transient(self.window)
            details_window.grab_set()
            
            main_frame = ttk.Frame(details_window, padding="20")
            main_frame.pack(fill='both', expand=True)
            
            # User info
            info_frame = ttk.LabelFrame(main_frame, text="User Information", padding="10")
            info_frame.pack(fill='x', pady=10)
            
            ttk.Label(info_frame, text=f"Name: {user.name}", font=("Arial", 12)).pack(anchor='w', pady=2)
            ttk.Label(info_frame, text=f"Email: {user.email}", font=("Arial", 12)).pack(anchor='w', pady=2)
            ttk.Label(info_frame, text=f"User ID: {user.id}", font=("Arial", 12)).pack(anchor='w', pady=2)
            
            # Booking history
            bookings_frame = ttk.LabelFrame(main_frame, text="Booking History", padding="10")
            bookings_frame.pack(fill='both', expand=True, pady=10)
            
            bookings = self.session.query(BookingDB).filter_by(user_id=user.id).all()
            movies = {m.id: m for m in load_movies_from_db(self.session)}
            
            if bookings:
                # Create treeview for bookings
                columns = ("Movie", "Seats", "Price", "Date")
                bookings_tree = ttk.Treeview(bookings_frame, columns=columns, show="headings", height=8)
                
                for col in columns:
                    bookings_tree.heading(col, text=col)
                    bookings_tree.column(col, width=120)
                
                for booking in bookings:
                    movie = movies.get(booking.movie_id)
                    price = movie.price * booking.num_seats if movie else 0
                    bookings_tree.insert("", "end", values=(
                        movie.name if movie else "Unknown",
                        booking.num_seats,
                        f"${price:.2f}",
                        booking.booking_time.strftime('%Y-%m-%d %H:%M')
                    ))
                
                bookings_tree.pack(fill='both', expand=True)
            else:
                ttk.Label(bookings_frame, text="No bookings found", font=("Arial", 12)).pack(pady=20)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=details_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user details: {str(e)}")

    def populate_history_tab(self):
        # Clear existing content
        for widget in self.history_tab.winfo_children():
            widget.destroy()

        log_request(self.session, self.admin, "VIEW_HISTORY")
        
        # Control buttons
        control_frame = ttk.Frame(self.history_tab)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Refresh", command=self.populate_history_tab).pack(side='right', padx=5)

        try:
            history = self.session.query(RequestHistoryDB).order_by(RequestHistoryDB.request_time.desc()).all()
            users = {u.id: u for u in self.session.query(UserDB).all()}

            if not history:
                ttk.Label(self.history_tab, text="No history found", 
                         font=("Arial", 12)).pack(pady=50)
                return

            self.history_listbox = tk.Listbox(self.history_tab, height=20, font=("Arial", 10))
            scrollbar = ttk.Scrollbar(self.history_tab, orient="vertical", command=self.history_listbox.yview)
            self.history_listbox.configure(yscrollcommand=scrollbar.set)
            
            for h in history:
                user = users.get(h.user_id)
                self.history_listbox.insert("end", 
                    f"{h.request_time.strftime('%Y-%m-%d %H:%M:%S')} - {user.name if user else 'Unknown'} - {h.request_type}")
            
            self.history_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {str(e)}")

    def populate_stats_tab(self):
        """Populate statistics tab"""
        # Clear existing content
        for widget in self.stats_tab.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.stats_tab, padding="20")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="System Statistics", font=("Arial", 16, "bold")).pack(pady=20)

        try:
            # Get statistics
            total_users = self.session.query(UserDB).filter_by(is_admin=False).count()
            total_movies = self.session.query(MovieDB).count()
            total_bookings = self.session.query(BookingDB).count()
            total_requests = self.session.query(RequestHistoryDB).count()
            
            # Revenue calculation
            total_revenue = 0
            bookings = self.session.query(BookingDB).all()
            movies = {m.id: m for m in load_movies_from_db(self.session)}
            
            for booking in bookings:
                movie = movies.get(booking.movie_id)
                if movie:
                    total_revenue += movie.price * booking.num_seats

            # Create statistics display
            stats_frame = ttk.LabelFrame(main_frame, text="Overview", padding="20")
            stats_frame.pack(fill='x', pady=10)
            
            # Create a grid layout for stats
            stats_data = [
                ("Total Users", total_users),
                ("Total Movies", total_movies),
                ("Total Bookings", total_bookings),
                ("Total Requests", total_requests),
                ("Total Revenue", f"${total_revenue:.2f}"),
                ("Active Movies", len([m for m in movies.values() if m.available_seats > 0]))
            ]
            
            for i, (label, value) in enumerate(stats_data):
                row = i // 2
                col = i % 2
                
                frame = ttk.Frame(stats_frame)
                frame.grid(row=row, column=col, padx=20, pady=10, sticky='w')
                
                ttk.Label(frame, text=label + ":", font=("Arial", 12)).pack(anchor='w')
                ttk.Label(frame, text=str(value), font=("Arial", 14, "bold")).pack(anchor='w')

            # Popular movies
            popular_frame = ttk.LabelFrame(main_frame, text="Popular Movies", padding="20")
            popular_frame.pack(fill='x', pady=10)
            
            # Get booking counts by movie
            movie_bookings = {}
            for booking in bookings:
                movie_id = booking.movie_id
                movie = movies.get(movie_id)
                if movie:
                    movie_name = movie.name
                    if movie_name not in movie_bookings:
                        movie_bookings[movie_name] = 0
                    movie_bookings[movie_name] += booking.num_seats
            
            # Sort and display top 5
            sorted_movies = sorted(movie_bookings.items(), key=lambda x: x[1], reverse=True)[:5]
            
            if sorted_movies:
                for i, (movie_name, seats) in enumerate(sorted_movies, 1):
                    ttk.Label(popular_frame, text=f"{i}. {movie_name} - {seats} seats booked", 
                             font=("Arial", 11)).pack(anchor='w', pady=2)
            else:
                ttk.Label(popular_frame, text="No bookings yet", font=("Arial", 11)).pack(anchor='w', pady=2)

            # Refresh button
            ttk.Button(main_frame, text="Refresh Statistics", command=self.populate_stats_tab).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")

if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        root = tk.Tk()
        app = MovieBookingGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
