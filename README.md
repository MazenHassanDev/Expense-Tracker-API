# Expense-Tracker-API

A Flask-based REST API for a personal expense tracker with user authentication, JWT tokens, and full CRUD operations backed by a MySQL database.

## How It Works

```
Request → Check JWT Token → Validate Input → Connect to MySQL → Execute Query
                                                                      ├── Success → Return JSON Response
                                                                      └── Error   → Return Error Message
```

- All users and expenses are stored in a **MySQL database**
- Routes are protected using **JWT access tokens**
- Access tokens expire in **24 hours**, refresh tokens expire in **7 days**
- Supports **date filtering** on expenses (past week, past month, last 3 months, custom)
- **Rate limiting** is applied to all routes to prevent abuse

## Prerequisites

- Python 3.8+
- MySQL server running locally

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/MazenHassanDev/Expense-Tracker-API.git
cd Expense-Tracker-API
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up the database**

Open MySQL and run:
```sql
CREATE DATABASE expense_tracker;
```

Tables are created automatically when you run the app.

**5. Set up environment variables**

Create a `.env` file in the root of the project:
```
DB_USERNAME=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_NAME=expense_tracker
SECRET_KEY=your-long-random-secret-key
```

**6. Run the app**
```bash
python app.py
```

## API Endpoints

### Register
```
POST /register
```
**Body:**
```json
{
    "name": "John Doe",
    "email": "john@doe.com",
    "password": "password123"
}
```
**Response `201 Created`:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "a3f8c2d1e4b7..."
}
```

---

### Login
```
POST /login
```
**Body:**
```json
{
    "email": "john@doe.com",
    "password": "password123"
}
```
**Response `200 OK`:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "a3f8c2d1e4b7..."
}
```

---

### Refresh Token
```
POST /refresh
```
**Body:**
```json
{
    "refresh_token": "a3f8c2d1e4b7..."
}
```
**Response `200 OK`:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Logout
```
POST /logout
```
**Body:**
```json
{
    "refresh_token": "a3f8c2d1e4b7..."
}
```
**Response `200 OK`:**
```json
{
    "message": "Logged out successfully"
}
```

---

### Get All Expenses
```
GET /expenses?page=1&limit=10
```
All expense routes require the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```
**Optional query parameters:**
| Parameter | Description |
|-----------|-------------|
| `page` | Page number (default: 1) |
| `limit` | Items per page (default: 10) |
| `filter` | `past_week`, `past_month`, `last_3_months`, or `custom` |
| `start_date` | Required if filter is `custom` (format: `DD-MM-YYYY`) |
| `end_date` | Required if filter is `custom` (format: `DD-MM-YYYY`) |

**Response `200 OK`:**
```json
{
    "data": [
        {
            "id": 1,
            "title": "Grocery run",
            "amount": 45.99,
            "category": "Groceries",
            "description": "Weekly groceries",
            "date": "19-03-2026"
        }
    ],
    "page": 1,
    "limit": 10,
    "total": 1
}
```

---

### Create an Expense
```
POST /expenses
```
**Body:**
```json
{
    "title": "Grocery run",
    "amount": 45.99,
    "category": "Groceries",
    "description": "Weekly groceries",
    "date": "19-03-2026"
}
```
**Response `201 Created`:**
```json
{
    "id": 1,
    "title": "Grocery run",
    "amount": 45.99,
    "category": "Groceries",
    "description": "Weekly groceries",
    "date": "19-03-2026"
}
```

**Available categories:** `Groceries`, `Leisure`, `Electronics`, `Utilities`, `Clothing`, `Health`, `Others`

---

### Update an Expense
```
PUT /expenses/<id>
```
**Body (all fields optional):**
```json
{
    "title": "Grocery run",
    "amount": 55.99,
    "category": "Groceries",
    "description": "Weekly groceries and household items",
    "date": "19-03-2026"
}
```
**Response `200 OK`:** Updated expense or `404 Not Found` or `403 Forbidden`

---

### Delete an Expense
```
DELETE /expenses/<id>
```
**Response `204 No Content`** or `404 Not Found` or `403 Forbidden`

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK — request succeeded |
| 201 | Created — resource successfully created |
| 204 | No Content — expense successfully deleted |
| 400 | Bad Request — missing or invalid fields |
| 401 | Unauthorized — missing or invalid token |
| 403 | Forbidden — you don't own this expense |
| 404 | Not Found — expense does not exist |
| 429 | Too Many Requests — rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limits

| Route | Limit |
|-------|-------|
| `POST /register` | 5 per minute (by IP) |
| `POST /login` | 5 per minute (by IP) |
| `POST /refresh` | 10 per minute (by IP) |
| `POST /logout` | 10 per minute (by IP) |
| `GET /expenses` | 60 per minute (by user) |
| `POST /expenses` | 30 per minute (by user) |
| `PUT /expenses/<id>` | 30 per minute (by user) |
| `DELETE /expenses/<id>` | 30 per minute (by user) |

## Project Structure

```
Expense-Tracker-API/
├── models/
│   ├── users_model.py          # User table
│   ├── expense_model.py        # Expense table
│   └── refresh_token_model.py  # Refresh token table
├── routes/
│   ├── auth_routes.py          # /register, /login, /refresh, /logout
│   └── expense_routes.py       # /expenses CRUD endpoints
├── utils/
│   ├── database.py             # Database connection and Base
│   ├── extensions.py           # Flask extensions (bcrypt, limiter)
│   └── jwt_authentication.py   # JWT token logic and decorators
├── app.py                      # Main Flask application
├── .env                        # Database credentials (not committed)
├── .gitignore                  # Prevents secrets from being committed
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_USERNAME` | MySQL username (default: `root`) |
| `DB_PASSWORD` | MySQL password |
| `DB_HOST` | MySQL host (default: `localhost`) |
| `DB_NAME` | Database name (default: `expense_tracker`) |
| `SECRET_KEY` | Secret key used to sign JWT tokens |