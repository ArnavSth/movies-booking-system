# import re
# import pandas as pd
# from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
# from sqlalchemy.orm import DeclarativeBase, sessionmaker
# from datetime import datetime

# # Database setup
# engine = create_engine('sqlite:///movie_booking.db')

# class Base(DeclarativeBase):
#     __abstract__ = True
    
#     def __repr__(self):
#         return f"<{self.__class__.__name__} id={self.id}>"

# class MovieDB(Base):
#     __tablename__ = 'movies'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     showtime = Column(String)
#     total_seats = Column(Integer)
#     available_seats = Column(Integer)
#     price = Column(Float)
#     description = Column(String)

# class UserDB(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     email = Column(String, unique=True)
#     password = Column(String)
#     is_admin = Column(Integer, default=0)
#     admin_id = Column(String, nullable=True)

# class BookingDB(Base):
#     __tablename__ = 'bookings'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     movie_id = Column(Integer, ForeignKey('movies.id'))
#     num_seats = Column(Integer)
#     booking_time = Column(DateTime, default=datetime.utcnow)

# class RequestHistoryDB(Base):
#     __tablename__ = 'request_history'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     request_type = Column(String)
#     request_time = Column(DateTime, default=datetime.utcnow)

# # Initialize database
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)

# # Email validation function
# def validate_email(email):
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return bool(re.match(pattern, email))

# class Movie:
#     def __init__(self, name, showtime, total_seats, price, description, movie_id=None):
#         self.id = movie_id
#         self.name = name
#         self.showtime = showtime
#         self.total_seats = total_seats
#         self.price = price
#         self.description = description
#         self.available_seats = total_seats

#     def __str__(self):
#         return f"{self.name}\nShowtime: {self.showtime}\nSeats: {self.available_seats}\nPrice: {self.price}\nDescription: {self.description}"

#     def book_seats(self, num_seats):
#         if num_seats <= self.available_seats:
#             self.available_seats -= num_seats
#             return True
#         return False

#     def cancel_seat(self, num_seats):
#         self.available_seats += num_seats

# class User:
#     def __init__(self, name, email, user_id=None):
#         if not validate_email(email):
#             raise ValueError("Invalid email format")
#         self.id = user_id
#         self.name = name
#         self.email = email
#         self.bookings = []

#     def view_bookings(self):
#         if not self.bookings:
#             print("No bookings found.")
#         else:
#             for booking in self.bookings:
#                 print(booking)

#     def view_request_history(self, session):
#         df = pd.read_sql_query(
#             f"SELECT request_type, request_time FROM request_history WHERE user_id = {self.id}",
#             engine
#         )
#         if df.empty:
#             print("No request history found.")
#         else:
#             print(f"\nRequest History for {self.name}:")
#             request_counts = df['request_type'].value_counts()
#             for request_type, count in request_counts.items():
#                 print(f"{request_type}: {count} requests")
#             print("\nDetailed History:")
#             for _, row in df.iterrows():
#                 print(f"Type: {row['request_type']}, Time: {row['request_time']}")

# class Admin(User):
#     def __init__(self, name, email, admin_id, user_id=None):
#         super().__init__(name, email, user_id)
#         self.admin_id = admin_id

# class Booking:
#     def __init__(self, user, movie, num_seats, booking_id=None):
#         self.id = booking_id
#         self.user = user
#         self.movie = movie
#         self.num_seats = num_seats

#     def __str__(self):
#         return f"Booking: {self.user.name}\nMovie: {self.movie.name}\nSeats: {self.num_seats}\nShowtime: {self.movie.showtime}"

# def save_to_db(session, obj):
#     session.add(obj)
#     session.commit()

# def load_movies_from_db(session):
#     movies = []
#     for movie_db in session.query(MovieDB).all():
#         movie = Movie(movie_db.name, movie_db.showtime, movie_db.total_seats, movie_db.price, movie_db.description, movie_db.id)
#         movie.available_seats = movie_db.available_seats
#         movies.append(movie)
#     return movies

# def load_user_bookings(session, user):
#     user.bookings = []
#     bookings = session.query(BookingDB).filter_by(user_id=user.id).all()
#     movies = {m.id: m for m in load_movies_from_db(session)}
#     for booking_db in bookings:
#         movie = movies.get(booking_db.movie_id)
#         if movie:
#             booking = Booking(user, movie, booking_db.num_seats, booking_db.id)
#             user.bookings.append(booking)

# def log_request(session, user, request_type):
#     request = RequestHistoryDB(user_id=user.id, request_type=request_type)
#     save_to_db(session, request)

# def user_menu(user, session):
#     while True:
#         print("\n-------Box Office------")
#         print("1. Now Showing")
#         print("2. Book Ticket")
#         print("3. Cancel Booking")
#         print("4. View My Bookings")
#         print("5. View Request History")
#         print("6. Logout")
#         choice = input("Choose an option: ")

#         if choice == '1':
#             log_request(session, user, "VIEW_MOVIES")
#             print("\nAvailable Movies")
#             for movie in load_movies_from_db(session):
#                 print(movie)

#         elif choice == '2':
#             log_request(session, user, "BOOK")
#             print("\nSelect a movie to book")
#             movies = load_movies_from_db(session)
#             for m in movies:
#                 print(m)
#             movie_name = input("Enter movie name: ")
#             selected_movie = None
#             for movie in movies:
#                 if movie.name.lower() == movie_name.lower():
#                     selected_movie = movie
#                     break
#             if selected_movie:
#                 num_seats = int(input("No. of seats? "))
#                 if selected_movie.book_seats(num_seats):
#                     booking = Booking(user, selected_movie, num_seats)
#                     user.bookings.append(booking)
#                     movie_db = session.query(MovieDB).filter_by(id=selected_movie.id).first()
#                     movie_db.available_seats = selected_movie.available_seats
#                     booking_db = BookingDB(user_id=user.id, movie_id=selected_movie.id, num_seats=num_seats)
#                     save_to_db(session, booking_db)
#                     print("Booked successfully")
#                 else:
#                     print("Not enough seats available")
#             else:
#                 print("Movie not found. Please check movie name and try again.")
        
#         elif choice == '3':
#             log_request(session, user, "CANCEL")
#             if not user.bookings:
#                 print("You have no bookings to cancel.")
#                 continue
#             print("\nYour Bookings")
#             for booking in user.bookings:
#                 print(booking)
#             movie_name = input("Enter the movie name of the booking to cancel: ")
#             found = False
#             for booking in user.bookings[:]:
#                 if booking.movie.name.lower() == movie_name.lower():
#                     user.bookings.remove(booking)
#                     booking.movie.cancel_seat(booking.num_seats)
#                     movie_db = session.query(MovieDB).filter_by(id=booking.movie.id).first()
#                     movie_db.available_seats = booking.movie.available_seats
#                     session.query(BookingDB).filter_by(id=booking.id).delete()
#                     session.commit()
#                     print("Booking cancelled")
#                     found = True
#                     break
#             if not found:
#                 print(f"No booking found for '{movie_name}'.")
        
#         elif choice == '4':
#             log_request(session, user, "VIEW_BOOKINGS")
#             load_user_bookings(session, user)
#             user.view_bookings()
        
#         elif choice == '5':
#             log_request(session, user, "VIEW_HISTORY")
#             user.view_request_history(session)
        
#         elif choice == '6':
#             print("Logging out, Bye!")
#             break
        
#         else:
#             print("Invalid choice. Try again.")

# def admin_menu(admin, session):
#     while True:
#         print("\n-------Admin Area------")
#         print("1. Add Movie")
#         print("2. Remove Movie")
#         print("3. View All Movies")
#         print("4. View All Bookings")
#         print("5. View Request History")
#         print("6. Logout")
#         choice = input("Enter your choice: ")

#         if choice == '1':
#             log_request(session, admin, "ADD_MOVIE")
#             name = input("Movie name: ")
#             showtime = input("Showtime (e.g., 4:00 PM): ")
#             seats = int(input("Total seats: "))
#             price = float(input("Ticket price: "))
#             description = input("Movie description: ")
#             new_movie = Movie(name, showtime, seats, price, description)
#             movie_db = MovieDB(name=name, showtime=showtime, total_seats=seats, available_seats=seats, price=price, description=description)
#             save_to_db(session, movie_db)
#             print("Movie added successfully")

#         elif choice == '2':
#             log_request(session, admin, "REMOVE_MOVIE")
#             print("\nCurrent Movies:")
#             movies = load_movies_from_db(session)
#             for movie in movies:
#                 print(f"- {movie.name}")
#             movie_name = input("Enter the name of the movie to remove: ").strip()
#             found = False
#             for movie in movies:
#                 if movie.name.lower() == movie_name.lower():
#                     session.query(MovieDB).filter_by(id=movie.id).delete()
#                     session.commit()
#                     print(f"Movie '{movie.name}' removed successfully.")
#                     found = True
#                     break
#             if not found:
#                 print(f"No movie found with the name '{movie_name}'.")

#         elif choice == '3':
#             log_request(session, admin, "VIEW_MOVIES")
#             print("\nAll Movies")
#             for movie in load_movies_from_db(session):
#                 print(movie)

#         elif choice == '4':
#             log_request(session, admin, "VIEW_BOOKINGS")
#             print("\nShowing All Bookings")
#             bookings = session.query(BookingDB).all()
#             if not bookings:
#                 print("No bookings made yet.")
#             else:
#                 movies = {m.id: m for m in load_movies_from_db(session)}
#                 users = {u.id: u for u in session.query(UserDB).all()}
#                 for booking in bookings:
#                     user = users.get(booking.user_id)
#                     movie = movies.get(booking.movie_id)
#                     if user and movie:
#                         print(Booking(user, movie, booking.num_seats, booking.id))

#         elif choice == '5':
#             log_request(session, admin, "VIEW_HISTORY")
#             admin.view_request_history(session)

#         elif choice == '6':
#             print("Logging out, Bye!")
#             break

#         else:
#             print("Invalid choice. Try again.")

# def main_page():
#     session = Session()
    
#     # Reset database for testing
#     Base.metadata.drop_all(engine)
#     Base.metadata.create_all(engine)

#     # Add initial admin user
#     admin = session.query(UserDB).filter_by(email="admin@example.com").first()
#     if not admin:
#         admin = UserDB(name="Admin", email="admin@example.com", password="admin123", is_admin=1, admin_id="ADM001")
#         save_to_db(session, admin)

#     # Initialize sample movies if database is empty
#     if not session.query(MovieDB).first():
#         initial_movies = [
#             MovieDB(name="Avengers", showtime="7:00 PM", total_seats=50, available_seats=50, price=300, description="Superhero action movie"),
#             MovieDB(name="Inception", showtime="9:00 PM", total_seats=40, available_seats=40, price=250, description="Mind-bending sci-fi thriller")
#         ]
#         for movie in initial_movies:
#             save_to_db(session, movie)

#     while True:
#         print("\n=== ++++Movie Ticket Booking System ++++===")
#         print("1. User")
#         print("2. Admin")
#         print("3. Exit")
#         choice = input("Enter 1 for User, 2 for Admin, 3 to Exit: ")

#         if choice == '1':
#             print("\nDo you want to (1) Login or (2) Register?")
#             sub_choice = input("Enter 1 or 2: ")
#             if sub_choice == '2':
#                 # Registration
#                 name = input("Enter your name: ")
#                 email = input("Enter your email: ")
#                 if not validate_email(email):
#                     print("Invalid email format.")
#                     continue
#                 password = input("Enter your password: ")
#                 existing_user = session.query(UserDB).filter_by(email=email).first()
#                 if existing_user:
#                     print("Email already registered. Please login.")
#                 else:
#                     user_db = UserDB(name=name, email=email, password=password, is_admin=0)
#                     save_to_db(session, user_db)
#                     print("Registration successful. You can now login.")
#             elif sub_choice == '1':
#                 # Login
#                 email = input("Enter your email: ")
#                 password = input("Enter your password: ")
#                 user_db = session.query(UserDB).filter_by(email=email, password=password, is_admin=0).first()
#                 if user_db:
#                     user = User(user_db.name, user_db.email, user_db.id)
#                     load_user_bookings(session, user)
#                     user_menu(user, session)
#                 else:
#                     print("Invalid email or password.")
#             else:
#                 print("Invalid choice.")

#         elif choice == '2':
#             email = input("Enter admin email: ")
#             password = input("Enter admin password: ")
#             admin_id = input("Enter admin ID: ")
#             admin_db = session.query(UserDB).filter_by(email=email, password=password, is_admin=1, admin_id=admin_id).first()
#             if admin_db:
#                 admin = Admin(admin_db.name, admin_db.email, admin_db.admin_id, admin_db.id)
#                 load_user_bookings(session, admin)
#                 admin_menu(admin, session)
#             else:
#                 print("Invalid admin credentials.")

#         elif choice == '3':
#             print("Thank you for using the system! Bye")
#             session.close()
#             break

#         else:
#             print("Invalid choice. Please select again.")

# if __name__ == "__main__":
#     main_page()



import re
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database setup
engine = create_engine('sqlite:///movie_booking.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Database models
class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    admin_id = Column(String, nullable=True)
    bookings = relationship("BookingDB", back_populates="user")
    request_history = relationship("RequestHistoryDB", back_populates="user")

class MovieDB(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    showtime = Column(String)
    total_seats = Column(Integer)
    available_seats = Column(Integer)
    price = Column(Float)
    description = Column(String)
    bookings = relationship("BookingDB", back_populates="movie")

class BookingDB(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    num_seats = Column(Integer)
    booking_time = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserDB", back_populates="bookings")
    movie = relationship("MovieDB", back_populates="bookings")

class RequestHistoryDB(Base):
    __tablename__ = 'request_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    request_type = Column(String)
    request_time = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserDB", back_populates="request_history")

# Movie class for business logic
class Movie:
    def __init__(self, name, showtime, total_seats, price, description, movie_id=None):
        self.id = movie_id
        self.name = name
        self.showtime = showtime
        self.total_seats = total_seats
        self.available_seats = total_seats
        self.price = price
        self.description = description

    def book_seats(self, num_seats):
        if num_seats <= self.available_seats:
            self.available_seats -= num_seats
            return True
        return False

    def cancel_seat(self, num_seats):
        self.available_seats += num_seats

    def __str__(self):
        return f"{self.name}\nShowtime: {self.showtime}\nSeats: {self.available_seats}\nPrice: ${self.price}\nDescription: {self.description}"

# Booking class for business logic
class Booking:
    def __init__(self, user, movie, num_seats, booking_id=None):
        self.id = booking_id
        self.user = user
        self.movie = movie
        self.num_seats = num_seats

    def __str__(self):
        return f"Booking: {self.user.name}\nMovie: {self.movie.name}\nSeats: {self.num_seats}\nShowtime: {self.movie.showtime}"

# Utility functions
def save_to_db(session, obj):
    session.add(obj)
    session.commit()

def load_movies_from_db(session):
    movies = []
    for movie_db in session.query(MovieDB).all():
        movie = Movie(movie_db.name, movie_db.showtime, movie_db.total_seats, movie_db.price, movie_db.description, movie_db.id)
        movie.available_seats = movie_db.available_seats
        movies.append(movie)
    return movies

def load_user_bookings(session, user):
    user.bookings = []
    bookings = session.query(BookingDB).filter_by(user_id=user.id).all()
    movies = {m.id: m for m in load_movies_from_db(session)}
    for booking_db in bookings:
        movie = movies.get(booking_db.movie_id)
        if movie:
            booking = Booking(user, movie, booking_db.num_seats, booking_db.id)
            user.bookings.append(booking)

def log_request(session, user, request_type):
    request = RequestHistoryDB(user_id=user.id, request_type=request_type)
    save_to_db(session, request)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Initialize database with dummy data
def initialize_db():
    session = Session()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Add admin user
    admin = session.query(UserDB).filter_by(email="admin@example.com").first()
    if not admin:
        admin = UserDB(name="Admin User", email="admin@example.com", password="admin123", is_admin=True, admin_id="ADM001")
        save_to_db(session, admin)

    # Add sample movies
    if not session.query(MovieDB).first():
        initial_movies = [
            MovieDB(name="Avengers: Endgame", showtime="7:00 PM", total_seats=50, available_seats=50, price=300.0, description="Superhero epic"),
            MovieDB(name="Inception", showtime="9:00 PM", total_seats=40, available_seats=40, price=250.0, description="Sci-fi thriller"),
            MovieDB(name="The Matrix", showtime="5:00 PM", total_seats=60, available_seats=60, price=200.0, description="Cyberpunk action")
        ]
        for movie in initial_movies:
            save_to_db(session, movie)

    session.close()

if __name__ == "__main__":
    initialize_db()