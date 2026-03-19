from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFormLayout,
    QMessageBox, QDialog, QDialogButtonBox
)

from db_functions import (
    get_all_products,
    add_product,
    update_product,
    delete_product,
    search_products,
    get_low_stock_products
)


class ProductDialog(QDialog):
    def __init__(self, parent=None, mode="add", product_data=None):
        super().__init__(parent)
        self.mode = mode
        self.product_data = product_data or {}
        self.setWindowTitle("Add Product" if mode == "add" else "Update Product")
        self.setFixedWidth(420)
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Add Product" if self.mode == "add" else "Update Product")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #111;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_input = QLineEdit()

        inputs = [
            self.name_input,
            self.category_input,
            self.price_input,
            self.stock_input
        ]

        for widget in inputs:
            widget.setMinimumHeight(40)
            widget.setStyleSheet("""
                QLineEdit {
                    background: white;
                    border: 1px solid #dddddd;
                    border-radius: 10px;
                    padding: 0 12px;
                    font-size: 13px;
                }
            """)

        form.addRow("Product Name:", self.name_input)
        form.addRow("Category:", self.category_input)
        form.addRow("Price:", self.price_input)
        form.addRow("Quantity in Stock:", self.stock_input)

        layout.addLayout(form)

        if self.mode == "update":
            self.name_input.setText(str(self.product_data.get("product_name", "")))
            self.category_input.setText(str(self.product_data.get("category", "")))
            self.price_input.setText(str(self.product_data.get("price", "")))
            self.stock_input.setText(str(self.product_data.get("quantity_in_stock", "")))

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QPushButton {
                min-height: 36px;
                min-width: 90px;
                border-radius: 8px;
                font-weight: 600;
            }
        """)

        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name is required.")
            return
        if not self.category_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Category is required.")
            return

        try:
            float(self.price_input.text())
            int(self.stock_input.text())
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Price and stock must be valid numbers.")
            return

        self.accept()

    def get_data(self):
        return {
            "product_name": self.name_input.text().strip(),
            "category": self.category_input.text().strip(),
            "price": self.price_input.text().strip(),
            "quantity_in_stock": self.stock_input.text().strip()
        }

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.resize(1180, 760)
        self.setStyleSheet("background-color: #f4f5f7;")
        self.build_ui()
        self.load_products()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Inventory Management")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #111; background: transparent; border: none;")

        subtitle = QLabel("Manage product records, stock details, and inventory list.")
        subtitle.setStyleSheet("font-size: 13px; color: #374151; background: transparent; border: none;")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFixedHeight(40)
        back_btn.clicked.connect(self.close)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #235268;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: ##2f6f8a;
            }
        """)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)

        main_layout.addLayout(header_layout)

        top_controls = QFrame()
        top_controls.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 16px;
            }
        """)
        controls_layout = QHBoxLayout(top_controls)
        controls_layout.setContentsMargins(16, 16, 16, 16)
        controls_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by product name or category...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #fafafa;
                border: 1px solid #dddddd;
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }
        """)

        search_btn = QPushButton("Search")
        refresh_btn = QPushButton("Refresh")
        add_btn = QPushButton("Add Product")
        update_btn = QPushButton("Update Selected")
        delete_btn = QPushButton("Delete Selected")

        btns = [search_btn, refresh_btn, add_btn, update_btn, delete_btn]
        for btn in btns:
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)

        search_btn.setStyleSheet(self.dark_button_style())
        refresh_btn.setStyleSheet(self.gray_button_style())
        add_btn.setStyleSheet(self.dark_button_style())
        update_btn.setStyleSheet(self.gray_button_style())
        delete_btn.setStyleSheet(self.red_button_style())

        search_btn.clicked.connect(self.handle_search)
        refresh_btn.clicked.connect(self.load_products)
        add_btn.clicked.connect(self.handle_add_product)
        update_btn.clicked.connect(self.handle_update_product)
        delete_btn.clicked.connect(self.handle_delete_product)

        controls_layout.addWidget(self.search_input, 1)
        controls_layout.addWidget(search_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(update_btn)
        controls_layout.addWidget(delete_btn)

        main_layout.addWidget(top_controls)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 16px;
            }
        """)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Product ID",
            "Product Name",
            "Category",
            "Price",
            "Stock",
            "Date Added",
            "Last Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: white;
                gridline-color: #efefef;
                font-size: 13px;
            }
            QHeaderView::section {
                background: #f8f9fb;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #ececec;
                font-weight: 700;
            }
        """)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)

    def dark_button_style(self):
        return """
            QPushButton {
                background: #235268;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: ##2f6f8a;
            }
        """

    def gray_button_style(self):
        return """
            QPushButton {
                background: #f3f4f6;
                color: #235268;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 0 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """

    def red_button_style(self):
        return """
            QPushButton {
                background: #dc2626;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #b91c1c;
            }
        """

    def load_products(self):
        self.show_all_products

    def handle_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_products()
            return
        self.populate_table(search_products(keyword))

    def populate_table(self, products):
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product["product_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(product["product_name"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(product["category"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(product["price"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(product["quantity_in_stock"])))
            self.table.setItem(row, 5, QTableWidgetItem(str(product["date_added"])))
            self.table.setItem(row, 6, QTableWidgetItem(str(product["last_updated"])))

    def get_selected_product(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None

        return {
            "product_id": self.table.item(selected_row, 0).text(),
            "product_name": self.table.item(selected_row, 1).text(),
            "category": self.table.item(selected_row, 2).text(),
            "price": self.table.item(selected_row, 3).text(),
            "quantity_in_stock": self.table.item(selected_row, 4).text(),
        }

    def handle_add_product(self):
        dialog = ProductDialog(self, mode="add")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            success, message = add_product(
                data["product_name"],
                data["category"],
                data["price"],
                data["quantity_in_stock"]
            )
            QMessageBox.information(self, "Add Product", message)
            if success:
                self.load_products()

    def handle_update_product(self):
        product = self.get_selected_product()
        if not product:
            QMessageBox.warning(self, "Update Product", "Please select a product first.")
            return

        dialog = ProductDialog(self, mode="update", product_data=product)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            success, message = update_product(
                product["product_id"],
                data["product_name"],
                data["category"],
                data["price"],
                data["quantity_in_stock"]
            )
            QMessageBox.information(self, "Update Product", message)
            if success:
                self.load_products()

    def handle_delete_product(self):
        product = self.get_selected_product()
        if not product:
            QMessageBox.warning(self, "Delete Product", "Please select a product first.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Product",
            f"Are you sure you want to delete '{product['product_name']}'?"
        )

        if reply == QMessageBox.Yes:
            success, message = delete_product(product["product_id"])
            QMessageBox.information(self, "Delete Product", message)
            if success:
                self.load_products()

    def show_all_products(self):
        self.search_input.clear()
        self.populate_table(get_all_products())

    def show_low_stock_products(self):
        self.search_input.clear()
        self.populate_table(get_low_stock_products())

    def set_search_text(self, text):
        self.search_input.setText(text)
        self.handle_search()