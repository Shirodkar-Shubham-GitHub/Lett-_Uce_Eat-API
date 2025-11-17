# 🍽️ Lett' uce Eat – Online Food Ordering System (Backend API)

Lett' uce Eat is a **Django-based backend system** for an online food ordering platform.  
This repository contains a **REST API-only backend**, ready for frontend integration.

> ⚠️ **Note:** This is the backend API version of a previously deployed Django templates project: [Live website](https://shubham373shirodkar.pythonanywhere.com/).  
> The live website uses Django templates for full-stack functionality, but this repository contains **only the API**.

---

# 🌐 Live Website (Previous Version)
- Deployed using Django templates (full-stack)
- Live URL: [https://shubham373shirodkar.pythonanywhere.com/](https://shubham373shirodkar.pythonanywhere.com/)
- Current GitHub repo **does not have a live deployment**; it contains **backend APIs only**.

---

# ⚙️ Backend-Only Project
> 🧩 *This repository contains only the backend logic.*  
> The frontend UI is **not implemented**, but all APIs are ready for integration with any frontend framework.

---

# 🚀 Features

## 👤 Authentication
- **JWT Authentication** (Secure token-based login system)  
- **Email Verification**  
- **Google Authentication / Login**  
- After registration, **emails are sent to both the user and the admin** notifying successful signup  

---

## 🍔 User Features
- Browse **Menu Items** (MenuCard with search + pagination)  
- **Add to Cart / Update Cart**  
- **Cart Auto-Clear After Successful Order**  
- **Place Orders**  
- **Order Payments via Razorpay (Test Mode)**  
- **Emails sent to user & admin with order details and payment confirmation**  
- View **Active Orders**  
- View **Past Orders**  
- Review Food Items  
- Contact for order cancellation  
- User Dashboard APIs:
  - Profile
  - My Orders
  - My Cart
  - Change Password  

---

## 🛠️ Admin Features
- **Session Management** (users & admins)  
- Manage User Profiles  
- Manage Food Items  
- Manage Orders (active/pending/delivered)  
- Manage Contacts / Cancellation requests  
- Add / Update Menu Items  

---

# 🔄 Latest Updates
- JWT Authentication added  
- Email notifications to admin and user after registration  
- Google Login integration  
- MenuCard Module: search bar + pagination (6 items per page)  
- Dashboard APIs: My Cart, My Orders, Profile, Change Password  
- Database migrated from **SQLite ➝ MySQL**  
- Cart auto-clear after order placement  
- **Razorpay Payment Gateway (Test Mode) integrated**  
- **Email notifications for order payments and order details**  
- API-only backend deployed on GitHub (no live version yet)  

---

# 🧑‍💻 Technologies Used
- Python  
- Django & Django REST Framework  
- MySQL  
- JWT Authentication (SimpleJWT)  
- Google OAuth  
- SMTP Email  
- Razorpay API (Test Mode)  

---

# 📁 Project Structure
```bash
Online_Food_Ordering_System/
│
├── Foods_Ordering/            
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── main/                      
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── admin.py
│   ├── razorpay_test.html
│   ├── static/
│
├── media/                    
├── manage.py                 
├── requirements.txt          
└── README.md
```             

# 🛠️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Shirodkar-Shubham-GitHub/Online_Food_Ordering_System
cd Online_Food_Ordering_System
```   
2️⃣ Create Virtual Environment
```bash
python -m venv my_env
my_env\Scripts\activate      # Windows
# or
source my_env/bin/activate   # Linux/Mac
```
3️⃣ Install Requirements
```bash
pip install -r requirements.txt
```
4️⃣ Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
5️⃣ Create Superuser
```
python manage.py createsuperuser
```
6️⃣ Run the Server
```
python manage.py runserver
```
# 📦 Usage
## 🔐 Authentication
Register → Emails sent to admin & user
Login → JWT Access + Refresh token
Google Login → Quick OAuth login

# 🍽️ Ordering Flow
#### 1. Browse menu items
#### 2. Add items to Cart
#### 3. Review cart
#### 4. Place order
#### 5. Complete payment (Razorpay Test Mode)
#### 6. Emails sent to user & admin with order details + payment confirmation
#### 7. View Active Orders
#### 8. After delivery → Moved to Past Orders
#### 9. Cart gets cleared automatically

# 🧪 Testing
```bash
python manage.py test
```
# 🔮 Future Improvements
#### 🔗 Real payment gateway integration (live)
#### 📱 Frontend UI development (React / Angular / Django templates)
#### 🧾 Downloadable invoice PDFs
#### 📦 Live order tracking
#### 🛒 Saved addresses & multi-address support
#### ⭐ Enhanced review & rating system
