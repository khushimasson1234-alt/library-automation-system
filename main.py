import json, os, re
from datetime import date, timedelta

DATA_FILE = "library_data.json"
ROLL = re.compile(r"^120925\d+$")
TEACHER = re.compile(r"^TCH-\d{5}$", re.I)

def initial_data():
    return {"books": [{"id": 1, "title": "Python Basics", "author": "A. Smith", "genre": "Programming", "total_copies": 3, "available_copies": 3}, {"id": 2, "title": "Data Structures", "author": "M. Khan", "genre": "Computer Science", "total_copies": 2, "available_copies": 2}, {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classic", "total_copies": 2, "available_copies": 2}], "students": [], "teachers": [], "loans": [], "fines": []}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)

def legacy_roll(students):
    n, used = 1, {x.get("roll_number") for x in students}
    while f"120925{n:03d}" in used: n += 1
    return f"120925{n:03d}"

def migrate(data):
    changed = False
    data.setdefault("students", []); data.setdefault("teachers", []); data.setdefault("loans", []); data.setdefault("fines", [])
    for s in data["students"]:
        if "roll_number" not in s: s["roll_number"], changed = legacy_roll(data["students"]), True
        s.setdefault("fines", 0)
    for t in data["teachers"]:
        t.setdefault("fines", 0)
        if t.get("teacher_id"): t["teacher_id"] = t["teacher_id"].upper()
    names = {s["name"].lower(): s for s in data["students"]}
    for num, loan in enumerate(data["loans"], 1):
        if "id" not in loan: loan["id"], changed = num, True
        if "borrower_type" not in loan:
            s = names.get(loan.get("student_name", "").lower())
            loan.update({"borrower_type":"student", "borrower_id":s["roll_number"] if s else "UNKNOWN", "borrower_name":loan.get("student_name", "Unknown")}); changed = True
    for fine in data["fines"]:
        if "borrower_type" not in fine:
            s = names.get(fine.get("student_name", "").lower())
            fine.update({"borrower_type":"student", "borrower_id":s["roll_number"] if s else "UNKNOWN", "borrower_name":fine.get("student_name", "Unknown")}); changed = True
    return changed

def fine_amount(loan, today=None):
    if loan.get("returned"): return 0
    overdue = ((today or date.today()) - date.fromisoformat(loan["due_date"])).days
    return 0 if overdue <= 0 else 50 + ((overdue - 1) // 7) * 15

def refresh_fines(data):
    changed, today, active_ids = False, date.today(), set()
    for loan in data["loans"]:
        amount = fine_amount(loan, today)
        if not amount: continue
        active_ids.add(loan["id"])
        old = next((x for x in data["fines"] if x.get("automatic") and x.get("loan_id") == loan["id"]), None)
        if old is None:
            data["fines"].append({"borrower_type":loan["borrower_type"], "borrower_id":loan["borrower_id"], "borrower_name":loan["borrower_name"], "loan_id":loan["id"], "automatic":True, "amount":amount, "reason":f"Overdue: {loan['book_title']}"}); changed = True
        elif old["amount"] != amount: old["amount"], changed = amount, True
    before = len(data["fines"])
    data["fines"][:] = [x for x in data["fines"] if not x.get("automatic") or x.get("loan_id") in active_ids]
    changed |= len(data["fines"]) != before
    for typ, key in (("student", "roll_number"), ("teacher", "teacher_id")):
        for p in data[typ + "s"]:
            total = sum(x["amount"] for x in data["fines"] if x.get("borrower_type") == typ and x.get("borrower_id", "").upper() == p[key].upper())
            if p.get("fines") != total: p["fines"], changed = total, True
    if changed: save(data)

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f: data = json.load(f)
    else: data = initial_data()
    changed = migrate(data); refresh_fines(data)
    if changed: save(data)
    return data

def find(data, typ, ident):
    key = "roll_number" if typ == "student" else "teacher_id"
    return next((x for x in data[typ + "s"] if x.get(key, "").upper() == ident.upper()), None)

def borrower_details(loan):
    """Return the appropriate borrower name and identifier for catalog displays."""
    if loan["borrower_type"] == "student":
        return f"Student name: {loan['borrower_name']} | Enrollment number: {loan['borrower_id']}"
    return f"Teacher name: {loan['borrower_name']} | Teacher ID: {loan['borrower_id']}"

def show_books(data, person=None, typ=None, show_borrowers=False):
    print("\nCatalog")
    if person and typ == "student":
        print(f"Student name: {person['name']} | Enrollment number: {person['roll_number']}")
    elif person and typ == "teacher":
        print(f"Teacher name: {person['name']} | Teacher ID: {person['teacher_id']}")

    for b in data["books"]:
        print(f"{b['id']}. {b['title']} | {b['author']} | Available: {b['available_copies']}")
        if show_borrowers:
            borrowers = [x for x in data["loans"] if x["book_id"] == b["id"] and not x["returned"]]
            for loan in borrowers:
                print(f"   Borrowed by: {borrower_details(loan)}")

def add_account(data, typ):
    name = input(f"Enter {typ} name: ").strip()
    label, pattern = ("roll number (must begin 120925)", ROLL) if typ == "student" else ("teacher ID (e.g. TCH-00125)", TEACHER)
    ident = input(f"Enter {label}: ").strip().upper() if typ == "teacher" else input(f"Enter {label}: ").strip()
    password = input(f"Enter {typ} password: ").strip()
    if not name or not password or not pattern.fullmatch(ident): print("Invalid or missing details."); return
    if find(data, typ, ident): print("That ID already exists."); return
    data[typ + "s"].append({"name":name, "password":password, "fines":0, "roll_number":ident} if typ == "student" else {"name":name, "password":password, "fines":0, "teacher_id":ident})
    save(data); print(f"{typ.title()} account created: {name} ({ident})")

def account_menu(data, person, typ):
    key, ident = ("roll_number", person["roll_number"]) if typ == "student" else ("teacher_id", person["teacher_id"])
    while True:
        refresh_fines(data)
        if typ == "student":
            print(f"\nStudent account: {person['name']} | Enrollment number: {ident}")
        else:
            print(f"\nTeacher account: {person['name']} | Teacher ID: {ident}")
        print(f"\n{typ.title()} menu: 1 Books  2 Borrow  3 Return  4 My loans  5 My fines  6 Overdue  0 Logout")
        choice = input("Choice: ").strip()
        active = [x for x in data["loans"] if x["borrower_type"] == typ and x["borrower_id"].upper() == ident.upper() and not x["returned"]]
        if choice == "1": show_books(data, person, typ)
        elif choice == "2":
            if typ == "student" and len(active) >= 3:
                print("Borrowing limit reached: students can borrow a maximum of 3 books at a time.")
                continue
            show_books(data, person, typ)
            try: book_id = int(input("Book ID: "))
            except ValueError: print("Invalid book ID."); continue
            book = next((b for b in data["books"] if b["id"] == book_id), None)
            if not book or book["available_copies"] < 1: print("Book unavailable."); continue
            due = date.today() + timedelta(days=15)
            data["loans"].append({"id":max((x["id"] for x in data["loans"]), default=0)+1, "borrower_type":typ, "borrower_id":ident, "borrower_name":person["name"], "book_id":book_id, "book_title":book["title"], "borrowed_date":date.today().isoformat(), "due_date":due.isoformat(), "returned":False})
            book["available_copies"] -= 1; save(data); print(f"Borrowed. Return by {due}.")
        elif choice == "3":
            for n, loan in enumerate(active, 1): print(f"{n}. {loan['book_title']} (due {loan['due_date']})")
            try: loan = active[int(input("Loan number: ")) - 1]
            except (ValueError, IndexError): print("Invalid loan."); continue
            amount = fine_amount(loan)
            if amount:
                current = next((x for x in data["fines"] if x.get("automatic") and x.get("loan_id") == loan["id"]), None)
                if current: current.update({"automatic":False, "amount":amount, "reason":f"Late return: {loan['book_title']}"})
                else: data["fines"].append({"borrower_type":typ, "borrower_id":ident, "borrower_name":person["name"], "loan_id":loan["id"], "automatic":False, "amount":amount, "reason":f"Late return: {loan['book_title']}"})
            loan["returned"], loan["returned_date"] = True, date.today().isoformat()
            next(b for b in data["books"] if b["id"] == loan["book_id"])["available_copies"] += 1
            refresh_fines(data); save(data); print(f"Returned. Fine: Rs. {amount}")
        elif choice == "4":
            for x in active: print(f"{x['book_title']} | Due: {x['due_date']}")
            if not active: print("No active loans.")
        elif choice == "5": print(f"Outstanding fines: Rs. {person['fines']}")
        elif choice == "6":
            overdue = [x for x in active if fine_amount(x)]
            for x in overdue: print(f"{x['book_title']}: Rs. {fine_amount(x)}")
            if not overdue: print("No overdue books.")
        elif choice == "0": return
        else: print("Invalid choice.")

def admin_menu(data):
    while True:
        refresh_fines(data)
        print("\nAdmin: 1 Inventory  2 Loans  3 Overdue  4 Add student  5 Find student by roll no  6 Add teacher  7 Find teacher  8 Fines  0 Logout")
        choice = input("Choice: ").strip()
        if choice == "1": show_books(data, show_borrowers=True)
        elif choice == "2":
            for x in data["loans"]: print(f"{borrower_details(x)} | {x['book_title']} | {'Returned' if x['returned'] else 'Active'}")
        elif choice == "3":
            for x in data["loans"]:
                if fine_amount(x): print(f"{borrower_details(x)} | {x['book_title']} | Rs. {fine_amount(x)}")
        elif choice == "4": add_account(data, "student")
        elif choice == "5":
            s = find(data, "student", input("Student roll number: ").strip())
            print(f"{s['name']} | {s['roll_number']} | Fines: Rs. {s['fines']}" if s else "Student not found.")
        elif choice == "6": add_account(data, "teacher")
        elif choice == "7":
            t = find(data, "teacher", input("Teacher ID: ").strip())
            print(f"{t['name']} | {t['teacher_id']} | Fines: Rs. {t['fines']}" if t else "Teacher not found.")
        elif choice == "8":
            for x in data["fines"]: print(f"{borrower_details(x)} | Rs. {x['amount']} | {x['reason']}")
        elif choice == "0": return
        else: print("Invalid choice.")

def main():
    data = load(); print("Welcome to the Library Management System")
    while True:
        role = input("\n1 Student  2 Teacher  3 Admin  0 Exit\nChoice: ").strip()
        if role == "0": return
        if role == "3":
            if input("Admin password: ").strip() == "admin123": admin_menu(data)
            else: print("Incorrect credentials.")
            continue
        typ = "student" if role == "1" else "teacher" if role == "2" else None
        if not typ: print("Invalid choice."); continue
        ident = input("Roll number: " if typ == "student" else "Teacher ID: ").strip()
        person = find(data, typ, ident)
        if person and person["password"] == input("Password: ").strip(): account_menu(data, person, typ)
        else: print("Incorrect credentials.")

if __name__ == "__main__": main()
