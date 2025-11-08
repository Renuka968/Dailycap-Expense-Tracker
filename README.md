# 🪙 DailyCap — Smart Daily Expense Tracker

**DailyCap** is a professional, dark-themed web application built with **Flask (Python)** that helps users **track daily expenses**, **set budgets**, and receive **smart alerts** when nearing or exceeding spending limits.

It combines simplicity, analytics, and intelligent design to make personal finance management effortless and stylish.

---

## 🌟 Features

- 💰 **Daily Expense Tracking** — Log and categorize your daily spending.  
- ⚙️ **Smart Budget Alerts** — Instant notifications when you’re nearing or exceeding your budget.  
- 📊 **Analytics Dashboard** — Interactive charts for daily, weekly, and category-based spending.  
- 🖤 **Dark Theme Design** — Elegant UI with animated emoji background (💸 🛒 🍔 💵 🧾).  
- 📧 **Email Notifications** — Optional email alerts for overspending.  
- 🔐 **User Authentication** — Secure login and registration using Flask-Login.  
- 🧮 **Database Integration** — SQLite + SQLAlchemy ORM for smooth and efficient storage.

---

## 🧩 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | HTML, Tailwind CSS, Chart.js |
| **Backend** | Python, Flask, Flask-SQLAlchemy, Flask-Login |
| **Database** | SQLite |
| **Notifications** | Flask-Mail (SMTP) |
| **Theme** | Dark mode with animated and parallax emoji background |

---

## 🧠 How It Works

1. Users sign up and set a **daily budget limit**.  
2. Each expense is recorded with **amount, category, and note**.  
3. When spending hits 90% of the limit → ⚠️ **Warning alert**.  
4. When spending exceeds the limit → 🚫 **Over-budget alert** (+ optional email).  
5. Dashboard visualizes spending trends with charts and KPIs.

---

## ⚡ Run Locally

```bash
git clone https://github.com/<your-username>/dailycap-expense-tracker.git
cd dailycap-expense-tracker/backend-flask
pip install -r requirements.txt
python app.py

🧰 Project Structure

dailycap-expense-tracker/
│
├── backend-flask/
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   ├── static/
│   └── .env.example
│
├── frontend-mockup/
│   └── index.html
│
└── README.md
