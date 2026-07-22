# 🏡 Boston Housing Valuation App (End-to-End ML SaaS)

A full-stack Machine Learning web application deployed as a SaaS. This app predicts the median value of homes in the Boston area based on various environmental and structural features. It includes secure user authentication, a live cloud database, and a personalized prediction history dashboard.

🔴 **Live Demo:** https://bostonhousepricing-6908.onrender.com

## 🛠️ Tech Stack & Tools
* **Machine Learning:** Python, Scikit-Learn, Pandas, NumPy
* **Backend:** Flask, Flask-Login, SQLAlchemy
* **Database:** PostgreSQL (hosted on Supabase)
* **Frontend:** HTML5, CSS3, Jinja2 (Jinja Templates)
* **Deployment & Cloud:** Render, Environment Variables (.env) for security

## ✨ Key Features
* **User Authentication:** Secure Sign-Up, Log-In, and Log-Out functionality.
* **Live Cloud Database:** Integrated with Supabase to store user credentials and prediction data.
* **Personalized Dashboard:** Users can view their past valuations perfectly formatted with currency ($) in a private history ledger.
* **Data Privacy:** Handled database relationships to ensure user data is private and prevented orphaned data.

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nidhichaura/bostonhousepricing.git
   cd bostonhousepricing
   
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
3. **Activate the virtual environment:**
(On Windows: venv\Scripts\activate)
(On Mac/Linux: source venv/bin/activate)

4. **Install required packages:**
   ```bash
   pip install -r requirements.txt

5. **Set up Environment Variables:**
Create a .env file in the root directory and add your Supabase credentials:
DATABASE_URL=your_supabase_postgresql_url
SECRET_KEY=your_secret_key

6. **Run the Flask application:**
    ```bash
    python app.py
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.    
