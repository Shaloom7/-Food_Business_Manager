import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QVBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
                             QFormLayout, QHBoxLayout, QDialog, QDialogButtonBox,
                             QSpinBox, QDoubleSpinBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate

class FoodBusinessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Food Business Management System")
        self.db_connection = sqlite3.connect("food_business.db")  
        self.initUI()

    def initUI(self):
        
        self.tabs = QTabWidget()

        # Create the individual tabs
        self.ingredients_tab = QWidget()
        self.recipes_tab = QWidget()
        self.sales_tab = QWidget()
        self.predictions_tab = QWidget()

        # Add the tabs to the tab widget
        self.tabs.addTab(self.ingredients_tab, "Ingredients")
        self.tabs.addTab(self.recipes_tab, "Recipes")
        self.tabs.addTab(self.sales_tab, "Sales History")
        self.tabs.addTab(self.predictions_tab, "Predictions & Pricing")

        # Set up the layout for each tab
        self.setup_ingredients_tab()
        self.setup_recipes_tab()
        self.setup_sales_tab()
        self.setup_predictions_tab()

        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def setup_ingredients_tab(self):
        
        layout = QVBoxLayout()

        #  Form Layout (for adding/editing) 
        form_layout = QFormLayout()

        self.ingredient_name_edit = QLineEdit()
        self.ingredient_quantity_edit = QLineEdit()
        self.ingredient_unit_combo = QComboBox()  
        self.ingredient_unit_combo.addItems(["kg", "lbs", "oz", "ml", "liters", "pieces", "cups", "tbsp", "tsp"]) #Add units
        self.ingredient_cost_edit = QLineEdit()
        self.ingredient_threshold_edit = QLineEdit()

        form_layout.addRow("Name:", self.ingredient_name_edit)
        form_layout.addRow("Quantity:", self.ingredient_quantity_edit)
        form_layout.addRow("Unit:", self.ingredient_unit_combo)
        form_layout.addRow("Cost per Unit:", self.ingredient_cost_edit)
        form_layout.addRow("Threshold:", self.ingredient_threshold_edit)


        #  Buttons 
        button_layout = QHBoxLayout()
        self.add_ingredient_button = QPushButton("Add Ingredient")
        self.edit_ingredient_button = QPushButton("Edit Ingredient")  
        self.delete_ingredient_button = QPushButton("Delete Ingredient") 
        button_layout.addWidget(self.add_ingredient_button)
        button_layout.addWidget(self.edit_ingredient_button)
        button_layout.addWidget(self.delete_ingredient_button)

        #  Table 
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(6)  
        self.ingredients_table.setHorizontalHeaderLabels(["ID", "Name", "Quantity", "Unit", "Cost/Unit", "Threshold"])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 

        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.ingredients_table)
        self.ingredients_tab.setLayout(layout)

        #  Connections 
        self.add_ingredient_button.clicked.connect(self.add_ingredient)
        self.edit_ingredient_button.clicked.connect(self.edit_ingredient) 
        self.delete_ingredient_button.clicked.connect(self.delete_ingredient)
        self.load_ingredients() 


    def add_ingredient(self):
        # Get values from input fields
        name = self.ingredient_name_edit.text().strip()
        quantity_str = self.ingredient_quantity_edit.text().strip()
        unit = self.ingredient_unit_combo.currentText()
        cost_str = self.ingredient_cost_edit.text().strip()
        threshold_str = self.ingredient_threshold_edit.text().strip()

        
        if not all([name, quantity_str, unit, cost_str, threshold_str]):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            quantity = float(quantity_str)
            cost_per_unit = float(cost_str)
            threshold = float(threshold_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity, Cost, and Threshold must be numeric.")
            return

        if quantity < 0 or cost_per_unit < 0 or threshold < 0:
            QMessageBox.warning(self, "Error", "Quantity, Cost, and Threshold must be non-negative.")
            return

        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO Ingredients (name, quantity, unit, cost_per_unit, threshold)
                VALUES (?, ?, ?, ?, ?)
            """, (name, quantity, unit, cost_per_unit, threshold))
            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Ingredient added successfully!")
            self.clear_ingredient_form()
            self.load_ingredients()  
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "An ingredient with that name already exists.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def load_ingredients(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, name, quantity, unit, cost_per_unit, threshold FROM Ingredients")
            rows = cursor.fetchall()

            self.ingredients_table.setRowCount(0)  
            for row_num, row_data in enumerate(rows):
                self.ingredients_table.insertRow(row_num)
                for col_num, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    if col_num == 0: 
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.ingredients_table.setItem(row_num, col_num, item)

            self.update_low_stock_indicators() 

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def clear_ingredient_form(self):
        self.ingredient_name_edit.clear()
        self.ingredient_quantity_edit.clear()
        self.ingredient_unit_combo.setCurrentIndex(0)  
        self.ingredient_cost_edit.clear()
        self.ingredient_threshold_edit.clear()

    def update_low_stock_indicators(self):
        try:
            cursor = self.db_connection.cursor()
            for row in range(self.ingredients_table.rowCount()):
                item_id = int(self.ingredients_table.item(row, 0).text())  # Get ID
                cursor.execute("SELECT quantity, threshold FROM Ingredients WHERE id = ?", (item_id,))
                quantity, threshold = cursor.fetchone()

                
                if quantity < threshold:
                    for col in range(self.ingredients_table.columnCount()):
                        self.ingredients_table.item(row, col).setBackground(Qt.red)  # Highlight in red
                else:
                    for col in range(self.ingredients_table.columnCount()):
                        self.ingredients_table.item(row, col).setBackground(Qt.white) #Default color
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")


    def edit_ingredient(self):
        selected_row = self.ingredients_table.currentRow()
        if selected_row == -1:  
            QMessageBox.warning(self, "Error", "Please select an ingredient to edit.")
            return

        
        item_id = int(self.ingredients_table.item(selected_row, 0).text())

        # Fetch the existing data from the database
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT name, quantity, unit, cost_per_unit, threshold FROM Ingredients WHERE id = ?", (item_id,))
            ingredient_data = cursor.fetchone()
            if ingredient_data is None:
                QMessageBox.warning(self, "Error", "Ingredient not found in database.")
                return

            name, quantity, unit, cost_per_unit, threshold = ingredient_data

            
            self.ingredient_name_edit.setText(name)
            self.ingredient_quantity_edit.setText(str(quantity))
            self.ingredient_unit_combo.setCurrentText(unit)
            self.ingredient_cost_edit.setText(str(cost_per_unit))
            self.ingredient_threshold_edit.setText(str(threshold))


            
            self.add_ingredient_button.setText("Update Ingredient")
            self.add_ingredient_button.clicked.disconnect() 
            self.add_ingredient_button.clicked.connect(lambda: self.update_ingredient(item_id)) # Connect to a new function

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def update_ingredient(self, item_id):
        
        name = self.ingredient_name_edit.text().strip()
        quantity_str = self.ingredient_quantity_edit.text().strip()
        unit = self.ingredient_unit_combo.currentText()
        cost_str = self.ingredient_cost_edit.text().strip()
        threshold_str = self.ingredient_threshold_edit.text().strip()

        
        if not all([name, quantity_str, unit, cost_str, threshold_str]):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            quantity = float(quantity_str)
            cost_per_unit = float(cost_str)
            threshold = float(threshold_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity, Cost, and Threshold must be numeric.")
            return

        if quantity < 0 or cost_per_unit < 0 or threshold < 0:
            QMessageBox.warning(self, "Error", "Quantity, Cost, and Threshold must be non-negative.")
            return

        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE Ingredients
                SET name = ?, quantity = ?, unit = ?, cost_per_unit = ?, threshold = ?
                WHERE id = ?
            """, (name, quantity, unit, cost_per_unit, threshold, item_id))
            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Ingredient updated successfully!")
            self.clear_ingredient_form()
            self.load_ingredients()  

            
            self.add_ingredient_button.setText("Add Ingredient")
            self.add_ingredient_button.clicked.disconnect()
            self.add_ingredient_button.clicked.connect(self.add_ingredient) #Restore original function

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "An ingredient with that name already exists.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def delete_ingredient(self):
        selected_row = self.ingredients_table.currentRow()
        if selected_row == -1:  
            QMessageBox.warning(self, "Error", "Please select an ingredient to delete.")
            return

        # Confirmation dialog
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this ingredient?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        
        item_id = int(self.ingredients_table.item(selected_row, 0).text())

        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM Ingredients WHERE id = ?", (item_id,))
            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Ingredient deleted successfully!")
            self.load_ingredients()  
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")




    def setup_recipes_tab(self):
        
        layout = QHBoxLayout() 
        left_layout = QVBoxLayout() 
        right_layout = QVBoxLayout()

        #  Form Layout (for adding/editing recipes) 
        form_layout = QFormLayout()

        self.recipe_name_edit = QLineEdit()
        self.recipe_description_edit = QLineEdit()

        form_layout.addRow("Recipe Name:", self.recipe_name_edit)
        form_layout.addRow("Description:", self.recipe_description_edit)

        
        self.add_ingredient_button_recipe = QPushButton("Add Ingredient to Recipe")
        self.add_ingredient_button_recipe.clicked.connect(self.show_add_ingredient_dialog)
        form_layout.addRow(self.add_ingredient_button_recipe)

        
        self.recipe_ingredients_table = QTableWidget()
        self.recipe_ingredients_table.setColumnCount(3)  
        self.recipe_ingredients_table.setHorizontalHeaderLabels(["ID", "Ingredient Name", "Quantity"])
        self.recipe_ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_layout.addWidget(self.recipe_ingredients_table)


        
        button_layout = QHBoxLayout()
        self.add_recipe_button = QPushButton("Add Recipe")
        self.edit_recipe_button = QPushButton("Edit Recipe") 
        self.delete_recipe_button = QPushButton("Delete Recipe") 

        button_layout.addWidget(self.add_recipe_button)
        button_layout.addWidget(self.edit_recipe_button)
        button_layout.addWidget(self.delete_recipe_button)

        
        self.recipes_table = QTableWidget()
        self.recipes_table.setColumnCount(3) 
        self.recipes_table.setHorizontalHeaderLabels(["ID","Recipe Name", "Cost"])
        self.recipes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.recipes_table)


        
        left_layout.addLayout(form_layout)
        left_layout.addLayout(button_layout)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        self.recipes_tab.setLayout(layout)

        
        self.add_recipe_button.clicked.connect(self.add_recipe)
        self.edit_recipe_button.clicked.connect(self.edit_recipe)
        self.delete_recipe_button.clicked.connect(self.delete_recipe)
        self.load_recipes()
        
        
        self.current_recipe_ingredients = []


    def show_add_ingredient_dialog(self):
        """Shows a dialog to add, update, or delete an ingredient in the current recipe."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add/Edit/Delete Ingredient in Recipe")
        dialog_layout = QFormLayout(dialog)

        
        ingredient_combo = QComboBox()
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, name FROM Ingredients")
            ingredients = cursor.fetchall()
            for ingredient_id, ingredient_name in ingredients:
                ingredient_combo.addItem(ingredient_name, ingredient_id)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            return
        dialog_layout.addRow("Ingredient:", ingredient_combo)

        
        quantity_spinbox = QDoubleSpinBox()
        quantity_spinbox.setMinimum(0.01)
        quantity_spinbox.setValue(1.0)
        quantity_spinbox.setSingleStep(0.1)
        dialog_layout.addRow("Quantity:", quantity_spinbox)

        
        selected_row = self.recipe_ingredients_table.currentRow()
        editing_existing = False  
        existing_ingredient_index = -1  
        if selected_row != -1:
            
            current_ingredient_id = int(self.recipe_ingredients_table.item(selected_row, 0).text())
            
            for i, ing in enumerate(self.current_recipe_ingredients):
                if ing["id"] == current_ingredient_id:
                    
                    ingredient_combo.setCurrentText(ing["name"]) 
                    quantity_spinbox.setValue(ing["quantity"])
                    editing_existing = True
                    existing_ingredient_index = i
                    break

        
        def handle_ok():
            nonlocal existing_ingredient_index  

            selected_ingredient_id = ingredient_combo.currentData()
            selected_ingredient_name = ingredient_combo.currentText()
            quantity = quantity_spinbox.value()

            if editing_existing:
                # Update existing ingredient
                self.current_recipe_ingredients[existing_ingredient_index]["quantity"] = quantity
                
                self.current_recipe_ingredients[existing_ingredient_index]["name"] = selected_ingredient_name
                self.current_recipe_ingredients[existing_ingredient_index]["id"] = selected_ingredient_id

            else:
                
                for ingredient in self.current_recipe_ingredients:
                    if ingredient["id"] == selected_ingredient_id:
                        QMessageBox.warning(dialog, "Error", "This ingredient has already been added to the recipe.")  # Use dialog as parent
                        return
                # Add new ingredient
                self.current_recipe_ingredients.append({
                    "id": selected_ingredient_id,
                    "name": selected_ingredient_name,
                    "quantity": quantity
                })

            self.update_recipe_ingredients_table()
            dialog.accept()

        def handle_delete():
            nonlocal existing_ingredient_index  

            if not editing_existing: 
                QMessageBox.warning(dialog, "Error", "Please select an ingredient to delete.")
                return

            # Confirmation dialog
            confirm = QMessageBox.question(dialog, "Confirm Delete",
                                         "Are you sure you want to delete this ingredient from the recipe?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.No:
                return

            # Remove the ingredient
            del self.current_recipe_ingredients[existing_ingredient_index]
            self.update_recipe_ingredients_table()
            dialog.accept()

        def reject_dialog():
            dialog.reject()

        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
        dialog_layout.addRow(buttons)

        
        delete_button = QPushButton("Delete Ingredient")
        if editing_existing:  
            dialog_layout.addRow(delete_button)

        
        buttons.accepted.connect(handle_ok)
        buttons.rejected.connect(reject_dialog)
        if editing_existing:
            delete_button.clicked.connect(handle_delete)

        dialog.exec_()

    def update_recipe_ingredients_table(self):
        """Updates the table displaying the ingredients added to the recipe."""
        self.recipe_ingredients_table.setRowCount(0)  
        for row_num, ingredient_data in enumerate(self.current_recipe_ingredients):
            self.recipe_ingredients_table.insertRow(row_num)
            self.recipe_ingredients_table.setItem(row_num, 0, QTableWidgetItem(str(ingredient_data["id"])))
            self.recipe_ingredients_table.setItem(row_num, 1, QTableWidgetItem(ingredient_data["name"]))
            self.recipe_ingredients_table.setItem(row_num, 2, QTableWidgetItem(str(ingredient_data["quantity"])))

        
        self.recipe_ingredients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recipe_ingredients_table.setSelectionMode(QTableWidget.SingleSelection)

    def add_recipe(self):
        recipe_name = self.recipe_name_edit.text().strip()
        recipe_description = self.recipe_description_edit.text().strip()

        if not recipe_name:
            QMessageBox.warning(self, "Error", "Recipe name is required.")
            return

        if not self.current_recipe_ingredients:
            QMessageBox.warning(self, "Error", "Please add at least one ingredient to the recipe.")
            return

        try:
            cursor = self.db_connection.cursor()
            
            cursor.execute("INSERT INTO Recipes (name, description) VALUES (?, ?)", (recipe_name, recipe_description))
            recipe_id = cursor.lastrowid  

            
            for ingredient in self.current_recipe_ingredients:
                cursor.execute("""
                    INSERT INTO RecipeIngredients (recipe_id, ingredient_id, quantity_required)
                    VALUES (?, ?, ?)
                """, (recipe_id, ingredient["id"], ingredient["quantity"]))

            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Recipe added successfully!")
            self.clear_recipe_form()
            self.load_recipes()

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "A recipe with that name already exists.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def clear_recipe_form(self):
        self.recipe_name_edit.clear()
        self.recipe_description_edit.clear()
        self.current_recipe_ingredients = []  
        self.update_recipe_ingredients_table() 
    
    def load_recipes(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, name FROM Recipes")
            recipes = cursor.fetchall()

            self.recipes_table.setRowCount(0)
            for row_num, (recipe_id, recipe_name) in enumerate(recipes):
                self.recipes_table.insertRow(row_num)
                self.recipes_table.setItem(row_num, 0, QTableWidgetItem(str(recipe_id)))
                self.recipes_table.setItem(row_num, 1, QTableWidgetItem(recipe_name))

                
                total_cost = self.calculate_recipe_cost(recipe_id)
                self.recipes_table.setItem(row_num, 2, QTableWidgetItem(str(total_cost)))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def calculate_recipe_cost(self, recipe_id):
        """Calculates the total cost of a recipe."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT ri.quantity_required, i.cost_per_unit
                FROM RecipeIngredients ri
                JOIN Ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = ?
            """, (recipe_id,))
            ingredients = cursor.fetchall()

            total_cost = 0
            for quantity_required, cost_per_unit in ingredients:
                total_cost += quantity_required * cost_per_unit
            return round(total_cost, 2)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred during cost calculation: {e}")
            return 0  
        
    def edit_recipe(self):
        selected_row = self.recipes_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a recipe to edit.")
            return

        recipe_id = int(self.recipes_table.item(selected_row, 0).text())

        try:
            cursor = self.db_connection.cursor()
            # Fetch recipe details
            cursor.execute("SELECT name, description FROM Recipes WHERE id = ?", (recipe_id,))
            recipe_data = cursor.fetchone()

            if recipe_data is None:
                 QMessageBox.warning(self, "Error", "Recipe not found in the database.")
                 return

            recipe_name, recipe_description = recipe_data

            
            self.recipe_name_edit.setText(recipe_name)
            self.recipe_description_edit.setText(recipe_description)

            # Fetch and populate ingredients
            self.current_recipe_ingredients = [] # Clear current ingredients
            cursor.execute("""
                SELECT i.id, i.name, ri.quantity_required
                FROM RecipeIngredients ri
                JOIN Ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = ?
            """, (recipe_id,))

            ingredients = cursor.fetchall()
            for ing_id, ing_name, quantity in ingredients:
                self.current_recipe_ingredients.append({
                    "id": ing_id,
                    "name": ing_name,
                    "quantity": quantity
                })
            self.update_recipe_ingredients_table()

            
            self.add_recipe_button.setText("Update Recipe")
            self.add_recipe_button.clicked.disconnect()
            self.add_recipe_button.clicked.connect(lambda: self.update_recipe(recipe_id))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def update_recipe(self, recipe_id):
        recipe_name = self.recipe_name_edit.text().strip()
        recipe_description = self.recipe_description_edit.text().strip()

        if not recipe_name:
            QMessageBox.warning(self, "Error", "Recipe name is required.")
            return
        if not self.current_recipe_ingredients:
            QMessageBox.warning(self, "Error", "The recipe must have ingredients")
            return

        try:
            cursor = self.db_connection.cursor()
            # Update Recipes table
            cursor.execute("UPDATE Recipes SET name = ?, description = ? WHERE id = ?",
                           (recipe_name, recipe_description, recipe_id))

            # Delete old ingredients
            cursor.execute("DELETE FROM RecipeIngredients WHERE recipe_id = ?", (recipe_id,))

            # Insert updated ingredients
            for ingredient in self.current_recipe_ingredients:
                cursor.execute("""
                    INSERT INTO RecipeIngredients (recipe_id, ingredient_id, quantity_required)
                    VALUES (?, ?, ?)
                """, (recipe_id, ingredient["id"], ingredient["quantity"]))

            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Recipe updated successfully!")
            self.clear_recipe_form()
            self.load_recipes()

            
            self.add_recipe_button.setText("Add Recipe")
            self.add_recipe_button.clicked.disconnect()
            self.add_recipe_button.clicked.connect(self.add_recipe)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def delete_recipe(self):
        selected_row = self.recipes_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a recipe to delete.")
            return

        confirm = QMessageBox.question(self, "Confirm Delete",
                                     "Are you sure you want to delete this recipe?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        recipe_id = int(self.recipes_table.item(selected_row, 0).text())

        try:
            cursor = self.db_connection.cursor()
            
            cursor.execute("DELETE FROM RecipeIngredients WHERE recipe_id = ?", (recipe_id,))
            
            cursor.execute("DELETE FROM Recipes WHERE id = ?", (recipe_id,))

            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Recipe deleted successfully!")
            self.load_recipes()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

        
    def populate_recipe_combobox(self):
        """Populates the recipe QComboBox with data from the Recipes table."""
        self.sales_recipe_combo.clear()  
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, name FROM Recipes")
            recipes = cursor.fetchall()
            for recipe_id, recipe_name in recipes:
                self.sales_recipe_combo.addItem(recipe_name, recipe_id)  
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")


    def setup_sales_tab(self):
        
        layout = QVBoxLayout()

        # Form Layout (for adding sales entries)
        form_layout = QFormLayout()

        self.sales_date_edit = QDateEdit(calendarPopup=True)  # Date picker
        self.sales_date_edit.setDate(QDate.currentDate()) 
        self.sales_recipe_combo = QComboBox()
        self.sales_quantity_spinbox = QDoubleSpinBox()  
        self.sales_quantity_spinbox.setMinimum(0.01)
        self.sales_quantity_spinbox.setValue(1.0)
        self.sales_quantity_spinbox.setSingleStep(0.1)

        form_layout.addRow("Date:", self.sales_date_edit)
        form_layout.addRow("Recipe:", self.sales_recipe_combo)
        form_layout.addRow("Quantity Sold:", self.sales_quantity_spinbox)

        
        add_entry_button = QPushButton("Add Sales Entry")
        add_entry_button.clicked.connect(self.add_sales_entry)

        
        self.sales_history_table = QTableWidget()
        self.sales_history_table.setColumnCount(4)  # ID, Date, Recipe, Quantity
        self.sales_history_table.setHorizontalHeaderLabels(["ID", "Date", "Recipe", "Quantity"])
        self.sales_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

         
        layout.addLayout(form_layout)
        layout.addWidget(add_entry_button)
        layout.addWidget(self.sales_history_table)
        self.sales_tab.setLayout(layout)

        # Load Data
        self.load_sales_history()
        self.populate_recipe_combobox() 
    

    def add_sales_entry(self):
        """Adds a new sales entry to the SalesHistory table."""
        sale_date = self.sales_date_edit.date().toString(Qt.ISODate)  
        recipe_id = self.sales_recipe_combo.currentData()  
        quantity_sold = self.sales_quantity_spinbox.value()

        if not recipe_id:
            QMessageBox.warning(self, "Error", "Please select a recipe.")
            return
        if quantity_sold <= 0:
            QMessageBox.warning(self,"Error", "Quantity must be greater than zero")
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO SalesHistory (sale_date, recipe_id, quantity_sold)
                VALUES (?, ?, ?)
            """, (sale_date, recipe_id, quantity_sold))

            # Deduct Ingredients
            self.deduct_ingredients(recipe_id, quantity_sold)

            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Sales entry added successfully!")
            self.load_sales_history()  
            # self.clear_sales_form()  # might want a function to clear the form
            self.update_low_stock_indicators()  # Update low stock indicators
            self.load_ingredients() 

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
    

    def load_sales_history(self):
        """Loads and displays the sales history in the table."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT sh.id, sh.sale_date, r.name, sh.quantity_sold
                FROM SalesHistory sh
                JOIN Recipes r ON sh.recipe_id = r.id
                ORDER BY sh.sale_date DESC
            """)  # Added ORDER BY
            sales_data = cursor.fetchall()

            self.sales_history_table.setRowCount(0)  
            for row_num, (sale_id, sale_date, recipe_name, quantity_sold) in enumerate(sales_data):
                self.sales_history_table.insertRow(row_num)
                self.sales_history_table.setItem(row_num, 0, QTableWidgetItem(str(sale_id)))
                self.sales_history_table.setItem(row_num, 1, QTableWidgetItem(sale_date))
                self.sales_history_table.setItem(row_num, 2, QTableWidgetItem(recipe_name))
                self.sales_history_table.setItem(row_num, 3, QTableWidgetItem(str(quantity_sold)))

                # Make ID column read-only.
                item = QTableWidgetItem(str(sale_id))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.sales_history_table.setItem(row_num, 0, item)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
    


    def deduct_ingredients(self, recipe_id, quantity_sold):
        """Deducts ingredients from inventory based on a recipe and quantity sold."""
        try:
            cursor = self.db_connection.cursor()

            
            cursor.execute("""
                SELECT ingredient_id, quantity_required
                FROM RecipeIngredients
                WHERE recipe_id = ?
            """, (recipe_id,))
            ingredients = cursor.fetchall()

            for ingredient_id, quantity_required in ingredients:
                # Calculate the total quantity of the ingredient needed
                total_quantity_needed = quantity_required * quantity_sold

                # Get the current quantity of the ingredient
                cursor.execute("SELECT quantity FROM Ingredients WHERE id = ?", (ingredient_id,))
                current_quantity = cursor.fetchone()[0]

                # Check if there's enough of the ingredient
                if current_quantity < total_quantity_needed:
                    cursor.execute("SELECT name FROM Ingredients WHERE id = ?", (ingredient_id,))
                    ingredient_name = cursor.fetchone()[0]
                    QMessageBox.warning(self, "Insufficient Inventory",
                                        f"Not enough {ingredient_name} in stock to fulfill the order.\n"
                                        f"Available: {current_quantity}, Required: {total_quantity_needed}")
                    
                    continue  # Skip to the next ingredient

                # Deduct the quantity from the inventory
                new_quantity = current_quantity - total_quantity_needed
                cursor.execute("UPDATE Ingredients SET quantity = ? WHERE id = ?", (new_quantity, ingredient_id))

            

        except sqlite3.Error as e:
            
            self.db_connection.rollback()
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            raise  
    



    def setup_predictions_tab(self):
        # Layout
        layout = QVBoxLayout()

        # Controls (Prediction Period and Profit Margin)
        controls_layout = QHBoxLayout()

        self.prediction_period_combo = QComboBox()
        self.prediction_period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days"])
        controls_layout.addWidget(QLabel("Prediction Period:"))
        controls_layout.addWidget(self.prediction_period_combo)

        self.profit_margin_spinbox = QDoubleSpinBox()
        self.profit_margin_spinbox.setMinimum(0.0)
        self.profit_margin_spinbox.setMaximum(100.0)  # Percentage
        self.profit_margin_spinbox.setSingleStep(1.0)
        self.profit_margin_spinbox.setValue(20.0)  
        self.profit_margin_spinbox.setSuffix("%")  
        controls_layout.addWidget(QLabel("Desired Profit Margin:"))
        controls_layout.addWidget(self.profit_margin_spinbox)

        # Refresh button

        self.refresh_predictions_button = QPushButton("Refresh Predictions")
        self.refresh_predictions_button.clicked.connect(self.load_predictions)
        controls_layout.addWidget(self.refresh_predictions_button)

        # Table 
        self.predictions_table = QTableWidget()
        self.predictions_table.setColumnCount(5)  # ID, Recipe, Cost, Predicted Demand, Suggested Price
        self.predictions_table.setHorizontalHeaderLabels(["ID", "Recipe", "Cost", "Predicted Demand", "Suggested Price"])
        self.predictions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #Add to Layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.predictions_table)
        self.predictions_tab.setLayout(layout)

        #Load Data
        self.load_predictions()


    def load_predictions(self):
        """Loads and displays recipe predictions and pricing."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, name FROM Recipes")
            recipes = cursor.fetchall()

            self.predictions_table.setRowCount(0)  
            for row_num, (recipe_id, recipe_name) in enumerate(recipes):
                self.predictions_table.insertRow(row_num)

                
                item_id = QTableWidgetItem(str(recipe_id))
                item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable)
                self.predictions_table.setItem(row_num, 0, item_id)
                self.predictions_table.setItem(row_num, 1, QTableWidgetItem(recipe_name))

                # Cost
                cost = self.calculate_recipe_cost(recipe_id)
                self.predictions_table.setItem(row_num, 2, QTableWidgetItem(str(cost)))

                # Predicted Demand
                predicted_demand = self.calculate_predicted_demand(recipe_id)
                self.predictions_table.setItem(row_num, 3, QTableWidgetItem(str(predicted_demand)))

                # Suggested Price
                suggested_price = self.calculate_suggested_price(recipe_id)
                self.predictions_table.setItem(row_num, 4, QTableWidgetItem(str(suggested_price)))


        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
    


    def calculate_predicted_demand(self, recipe_id):
        """Calculates the predicted demand for a recipe using a simple moving average."""
        try:
            cursor = self.db_connection.cursor()

            # Get the selected prediction period
            period_text = self.prediction_period_combo.currentText()
            if period_text == "Last 7 Days":
                days = 7
            elif period_text == "Last 30 Days":
                days = 30
            elif period_text == "Last 90 Days":
                days = 90
            else:
                days = 7  # Default to 7 days

            # Calculate the date 'days' days ago
            start_date = QDate.currentDate().addDays(-days)
            start_date_str = start_date.toString(Qt.ISODate)


            # Fetch sales history for the recipe within the time period
            cursor.execute("""
                SELECT sale_date, quantity_sold
                FROM SalesHistory
                WHERE recipe_id = ? AND sale_date >= ?
                ORDER BY sale_date
            """, (recipe_id, start_date_str))

            sales_data = cursor.fetchall()

            # Calculate the moving average
            if not sales_data:
                return 0 

            total_sold = 0
            for _, quantity_sold in sales_data:
                total_sold += quantity_sold

            average_daily_sales = total_sold / days #Could be 0 if days between first and last sale is 0
            predicted_demand = round(average_daily_sales * days, 2) 

            return predicted_demand

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred during demand prediction: {e}")
            return 0
    


    def calculate_suggested_price(self, recipe_id):
        """Calculates the suggested price based on cost and profit margin."""
        cost = self.calculate_recipe_cost(recipe_id) 
        profit_margin = self.profit_margin_spinbox.value() / 100.0 

        if cost == 0:  # Avoid division by zero
            return 0

        suggested_price = cost * (1 + profit_margin)
        return round(suggested_price, 2)



    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    ex = FoodBusinessApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()