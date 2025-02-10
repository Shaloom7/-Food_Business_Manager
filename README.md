# Food Business Management System

This is a desktop application built with Python, PyQt5, and SQLite, designed to help home chefs and small food businesses manage their operations more efficiently.

**Key Features:**

*   **Ingredient Management:**
    *   Add, edit, and delete ingredients.
    *   Track ingredient quantities, units, costs, and low-stock thresholds.
    *   Receive visual alerts for low-stock ingredients.
    *   Search and filter ingredients.
*   **Recipe Management:**
    *   Create and manage recipes with detailed ingredient lists and quantities.
    *   Automatically calculate the total cost of each recipe.
*   **Sales History Tracking:**
    *   Record sales data (date, recipe, quantity sold).
    *   This data is used for demand prediction.
*   **Demand Prediction:**
    *   Uses a simple moving average to predict future demand for each recipe.
    *   User-adjustable prediction period (last 7, 30, or 90 days).
*   **Menu Pricing:**
    *   Suggests selling prices for recipes based on ingredient costs and a user-defined profit margin.


**Installation:**
             

1.  **Clone the repository:**

    ```bash
    git clone <https://github.com/Shaloom7/-Food_Business_Manager.git>
    cd <-Food_Business_Manager>
    ```

2.  **Install dependencies:**

    ```bash
    pip install PyQt5
    ```

3.  **Create the database:**
     Run `db_setup.py`
    ```bash
     python db_setup.py
    ```

**Usage:**

1.  Run the application:

    ```bash
    python main.py
    ```

2.  Navigate through the tabs to manage ingredients, recipes, sales history, and view predictions/pricing.
