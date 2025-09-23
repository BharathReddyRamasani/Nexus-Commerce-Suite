
🚀Nexus Commerce Suite

An intelligent, command-line-driven business management engine for Small and Medium-sized Businesses (SMBs) in India.

The Nexus Commerce Suite is a backend-focused application designed to replace the operational chaos of manual ledgers and spreadsheets with a centralized, data-driven system. It empowers business owners to manage inventory, sales, and customers with efficiency and precision, providing actionable insights directly through a fast and intuitive Command-Line Interface (CLI).

Core Features
The application is built around a modular architecture, providing a comprehensive set of features to manage core business operations.

📦 Inventory Management
Add, Update & List Products: Full lifecycle management for your product catalog.

Real-Time Stock Control: Inventory levels are automatically and instantly updated with every sale.

Stock Adjustments: A dedicated, audited feature for manual stock corrections (e.g., for damaged goods or count discrepancies).

💰 Sales & CRM
Transactional Sales Recording: Process complex sales with multiple items and split payment methods (Cash, UPI, Card).

Customer Management: Maintain a customer database and view the complete purchase history for any client.

📊 Business Intelligence & Reporting
Financial Reports: Generate reports for profit and revenue over daily, weekly, or monthly periods.

Product Health Analysis: A unique report that visually categorizes stock as "Hot," "Cooling," or "Frozen" based on sales velocity.

Payment Summaries: Track how money is coming into the business.

✨ Unique Standout Features
Sale Simulator: A strategic planning tool to simulate the financial impact of a discount before you run the sale, helping to prevent unprofitable promotions.

Interactive Menu: A user-friendly, menu-driven interface that makes the powerful CLI easy to navigate for non-technical users.

Tech Stack
Backend: Python

CLI Framework: Click

Database: PostgreSQL (hosted on Supabase)

Database Client: supabase-py

Formatting: tabulate

Project Structure
The codebase is organized into a clean, module-wise structure for maintainability and scalability.

nexus_suite/
│
├── nexus_commerce/
│   ├── common/
│   ├── inventory/
│   ├── sales/
│   ├── customers/
│   └── reports/
│
├── main.py
├── requirements.txt
└── .env.example

🚀 Setup and Installation
Follow these steps to get the Nexus Commerce Suite running on your local machine.

1. Prerequisites
Python 3.8 or newer

A free Supabase account

2. Clone the Repository
git clone <your-repository-url>
cd nexus-suite

3. Set Up the Supabase Database
Create a new project in your Supabase dashboard.

Navigate to the SQL Editor.

Copy the entire contents of the provided supabase_schema.sql script and run it to create all the necessary tables.

4. Configure Environment Variables
In the project's root directory, find the .env.example file.

Rename this file to .env.

Go to your Supabase project's Settings > API section.

Copy your Project URL and anon (public) key.

Paste these values into your .env file:

SUPABASE_URL="[https://your-project-url.supabase.co](https://your-project-url.supabase.co)"
SUPABASE_KEY="your-public-anon-key"

5. Install Dependencies
It is highly recommended to use a Python virtual environment.

Run the following command to install all required libraries:

pip install -r requirements.txt

⚙️ Usage
To run the application, execute the main.py script from the root directory.

python main.py

You will be greeted by the interactive main menu:

==================================================
      NEXUS COMMERCE SUITE - MAIN MENU
==================================================

1. Manage Inventory
2. Record a New Sale
3. Manage Customers
4. View Reports
0. Exit
Select an option:
