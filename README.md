# Lab 2: Login & To-Do Application

## 1. Team

| Name | ID | Contribution |
|------|----|----|
| Ahmed Khaled Habib | 2204153 | Database schema, backend routes, register/login |
| Mohamed El Hussiny Fares | 2204073 | To-do CRUD, front end, styling, README |

## 2. Technology

- **Back end:** Python, Flask
- **Front end:** Jinja2 templates (server-rendered HTML), vanilla CSS, vanilla JavaScript
- **Database:** MySQL, accessed with PyMySQL using parameterized queries (`%s` placeholders) — no ORM
- **Auth:** bcrypt for password hashing, Flask's signed-cookie session for login state

## 3. How to run it (from an empty machine)

1. **Install prerequisites:** Python 3.10+, MySQL Server (running locally), `pip`.
2. **Clone the repository** and open a terminal in its root folder.
3. **Create a virtual environment and install dependencies:**
   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (macOS/Linux)
   pip install -r requirements.txt
   ```
4. **Create the database:** run the DDL script against your MySQL server:
   ```
   mysql -u root -p < database/schema.sql
   ```
   (or open `database/schema.sql` in MySQL Workbench / your client and execute it).
5. **Configure environment variables:** copy `.env.example` to `.env` and fill in your real MySQL credentials:
   ```
   copy .env.example .env     (Windows)
   cp .env.example .env       (macOS/Linux)
   ```
6. **Start the server:**
   ```
   python app.py
   ```
7. **Open the app** at `http://localhost:3000` (or the `PORT` set in `.env`).

## 4. Features built

- **R1 — Register:** name, email, password, confirm password. Duplicate email shows `Email Already Exists`. Successful registration logs the user in and redirects to the to-do list.
- **R2 — Login / Logout:** email + password; wrong email and wrong password both show `Invalid email or password`. Logout destroys the session.
- **R3 — Private list:** unauthenticated visitors are redirected to `/login`; each user sees only their own to-dos, newest first.
- **R4–R7 — To-do CRUD:** add, edit title, mark done/not done, delete (with a confirm prompt) — all using the exact parameterized queries from the handout, scoped with `AND user_id = ?`.
- **R8 — Validation:** client-side JavaScript checks before submit; identical rules re-checked on the server (works with JavaScript disabled too). On a server-side error, the same page re-renders with the messages and the database is not touched.
- **R9 — Security:** passwords stored as bcrypt hashes; all SQL uses placeholders; `user_id` is always read from the session, never from form/URL input.
- **R10 — UI:** one consistent stylesheet across all pages, responsive down to ~360px, clear error messages, empty-state text, logged-in header with name + logout.
- **Bonus — Filters & open count:** All / Open / Done filter links on the to-do list, plus a live count of open vs. total to-dos.

## 5. Screenshots

See `screenshots/`:
1. Register page with validation error messages
2. Login page
3. To-do list with several items (at least one marked done)
4. The site in a phone-sized (≈360px) window

## 6. Answers

**(a) Why do UPDATE and DELETE contain `AND user_id = ?`, and what changes if you remove it?**
The `todo_id` sent by the browser is just a number anyone could guess or tamper with (e.g. editing the URL or a hidden field). Adding `AND user_id = ?`, where the value comes from the server-side session (not the form), ensures the statement only affects a row if it both matches that `todo_id` **and** belongs to the logged-in user — otherwise it updates/deletes zero rows. Without it, any logged-in user could edit or delete *any other user's* to-dos just by guessing/iterating `todo_id` values, which breaks the privacy requirement (R3).

**(b) What happens if you insert a to-do for a user_id that does not exist, and which constraint of the lecture is that?**
MySQL rejects the insert with a foreign key constraint violation (error 1452), because `todos.user_id` references `users.user_id` and there is no matching row. This is **referential integrity**, enforced by the `FOREIGN KEY` constraint — it guarantees every to-do points to a real, existing user.

**(c) Why do you store a hash and not the password?**
If the database were ever leaked or read by someone unauthorized, a stored plaintext (or even a plain MD5/SHA) password would let an attacker log in directly, and since many people reuse passwords, it could compromise their other accounts too. A bcrypt hash is salted and intentionally slow, so even with the hash an attacker cannot feasibly recover the original password or brute-force it at scale. Login just compares the typed password against the hash — the real password is never stored or needed again.

**(d) The name column is NOT NULL: why did you still need your own check for an empty name?**
`NOT NULL` only forbids the value being absent (`NULL`); it does not forbid an empty string `''`, which is a perfectly valid value as far as MySQL is concerned. So a form submitted with an empty "Name" field would pass straight through into the database as `''` unless the application itself checks that the trimmed input is non-empty before inserting.

## Project structure

```
db-lab2-<names>/
  README.md
  .gitignore            # lists .env
  .env.example           # fake values only. NEVER commit .env
  requirements.txt
  app.py                 # Flask routes
  db.py                  # MySQL connection helper
  database/schema.sql     # DDL: both tables, re-runnable, no data
  templates/              # Jinja2 HTML templates
  static/css/style.css
  static/js/validate.js
  screenshots/
```
