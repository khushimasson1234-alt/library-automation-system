# Library Management System

Console-based Python library system with Student, Teacher, and Admin sections.

Students log in with a roll number and password. Student roll numbers must start with `120925` and finish with digits, such as `120925001`. Teachers use a unique ID in the format `TCH-00125` plus their password.

Admins use `admin123` and can find a student's data with only the roll number; a student password is never requested for this lookup. The Admin menu can create student and teacher accounts.

The catalog shows a student's name and enrollment number, or a teacher's name and teacher ID. The Admin catalog also shows those details for each active borrower.

Students can have a maximum of three active borrowed books at a time.

Books are due 15 days after borrowing. An overdue book receives an automatic ₹50 fine, then ₹15 more after each full additional overdue week (₹50 for overdue days 1–7, ₹65 for days 8–14, etc.). The system refreshes active overdue fines whenever it opens or a menu action occurs, and it finalizes the amount when the book is returned.

Run with:

```bash
python main.py
```

Existing saved name-based students are automatically assigned valid roll numbers when the app starts.
