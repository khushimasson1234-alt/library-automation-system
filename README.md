# Library Automation System

A Python-based Library Management System designed to automate common library operations through a console-based interface.

## Features

- Student, Teacher, and Admin roles
- Role-based authentication
- Book catalog management
- Book borrowing and returning
- Active loan tracking
- Overdue book detection
- Automated fine calculation
- Student borrowing limit
- Student and Teacher account management
- Input validation
- JSON-based data persistence
- Data migration for existing records

## Technologies Used

- Python
- JSON
- File Handling
- Regular Expressions
- Date & Time Handling

## User Roles

### Student
- Login
- View available books
- Borrow books
- Return books
- View active loans
- View fines
- Check overdue books

### Teacher
- Login
- View books
- Borrow and return books
- View loans and fines
- Check overdue books

### Admin
- Manage student and teacher accounts
- View library catalog
- View active loans
- View overdue books
- View fines
- Find users

## Borrowing Rules

- Students can have a maximum of 3 active books.
- Books are due 15 days after borrowing.
- Overdue fines are calculated automatically.

## Fine Calculation

- No fine when returned on time.
- ₹50 for overdue days 1–7.
- ₹15 is added after each full additional overdue week.

## How to Run

1. Clone the repository.
2. Open the project folder.
3. Make sure Python is installed.
4. Future Improvements
Graphical user interface
Database integration
Email reminders
Book search and filtering
Barcode/QR code integration
Advanced reports and analytics
Author

Khushboo Masson

BCA Student | Python & Software Development
5. Run:

```bash
python main.py
