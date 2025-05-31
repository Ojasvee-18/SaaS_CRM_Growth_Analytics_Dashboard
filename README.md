# 🚀 SaaS CRM & Growth Analytics Dashboard

**Your All-in-One Solution for Lead Management, Funnel Optimization & CAC Reduction**  
*Built with Flask, SQLAlchemy & Matplotlib*

---

## 📁 Project Structure
.
├── app.py
├── requirement.txt
├── templates/
│ ├── add_lead.html
│ ├── base.html
│ ├── dashboard.html
│ ├── edit_lead.html
│ ├── experiment.html
│ ├── index.html
│ └── nurture.html
└── migrations/


---


## 📌 Overview
A B2B SaaS-focused CRM system designed to:
- **Track leads** through a 5-stage sales funnel (Lead → MQL → SQL → Champion → Customer)
- **Visualize key metrics**: CAC, LTV, Conversion Rates, **LTV:CAC Ratio**
- **Automate nurturing workflows** based on lead intent
- **Optimize ad spend** through experiment tracking


---

## 🔥 Features

### 📊 **Funnel Analytics**
![image](https://github.com/user-attachments/assets/1c785da1-16f4-40d2-ae6f-f04df6c310be)
- Stage-wise lead tracking
- Automatic performance alerts

### 💸 **CAC Optimization**
![image](https://github.com/user-attachments/assets/07c64251-4025-4e92-b9f9-b8b40920e303)
- Channel-specific cost analysis
- Experimentation framework (A/B testing)

### 📈 **LTV:CAC Ratio Tracking**
![image](https://github.com/user-attachments/assets/134b1995-5aaa-4b8c-9e6c-cac8aba367e9)

- **What is LTV:CAC?**  
  The **LTV:CAC ratio** compares the **lifetime value** (LTV) of a customer to the **cost of acquiring** that customer (CAC).  
  - **LTV**: The total revenue you expect from a customer over their relationship with your business.
  - **CAC**: The total sales and marketing cost to acquire a new customer.
- **Why it matters:**  
  - A ratio **> 3** is considered healthy for SaaS.
  - If the ratio is **too low**, you’re overspending on acquisition or not retaining customers long enough.
- **How we help:**  
  - The dashboard visualizes LTV:CAC by channel, so you can double down on efficient channels and fix underperformers.
  - Example:
    ```
    | Channel         | CAC   | LTV    | LTV:CAC |
    |-----------------|-------|--------|---------|
    | Facebook Ads    | ₹3000 | ₹7500  | 2.5     |
    | Email Campaign  | ₹400  | ₹12000 | 30      |
    | LinkedIn DMs    | ₹2500 | ₹9000  | 3.6     |
    ```
  - **Actionable insights** are shown right on the dashboard!

### 📩 **Smart Nurturing**
- 3-tier email workflows (High/Mid/Low intent)
- AI-powered personalization hooks

---




