from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox
)

from db_functions import get_all_products, restock_product


class RestockProductWindow(QWidget):
    window_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restock Product")
        self.setStyleSheet("background-color: #f4f5f7;")
        self.build_ui()
        self.load_products()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        top_row = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Restock Product")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #111; background: transparent; border: none;")
        subtitle = QLabel("Select a product, enter quantity to add, then restock inventory.")
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

        top_row.addLayout(title_box)
        top_row.addStretch()
        top_row.addWidget(back_btn)

        main_layout.addLayout(top_row)

        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 16px;
            }
        """)
        info_layout = QHBoxLayout(info_card)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(12)

        self.selected_label = QLabel("Selected Product ID: None")
        self.selected_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #111; background: transparent; border: none;")

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Enter quantity to add")
        self.qty_input.setFixedHeight(40)
        self.qty_input.setStyleSheet("""
            QLineEdit {
                background: #fafafa;
                border: 1px solid #dddddd;
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
                color: #111;
            }
        """)

        save_btn = QPushButton("Restock Product")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.handle_restock)

        info_layout.addWidget(self.selected_label, 1)
        info_layout.addWidget(self.qty_input)
        info_layout.addWidget(save_btn)

        main_layout.addWidget(info_card)

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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Category", "Price", "Stock"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self.update_selected_product)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: white;
                gridline-color: #efefef;
                font-size: 13px;
                color: #111;
            }
            QHeaderView::section {
                background: #f8f9fb;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #ececec;
                font-weight: 700;
                color: #111;
            }
        """)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)

    def load_products(self):
        products = get_all_products()
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product["product_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(product["product_name"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(product["category"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(product["price"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(product["quantity_in_stock"])))

    def update_selected_product(self):
        row = self.table.currentRow()
        if row >= 0:
            product_id = self.table.item(row, 0).text()
            product_name = self.table.item(row, 1).text()
            self.selected_label.setText(f"Selected Product ID: {product_id} | {product_name}")

    def handle_restock(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Restock Product", "Please select a product first.")
            return

        product_id = self.table.item(row, 0).text()
        quantity = self.qty_input.text().strip()

        success, message = restock_product(product_id, quantity)
        QMessageBox.information(self, "Restock Product", message)

        if success:
            self.qty_input.clear()
            self.load_products()
            self.selected_label.setText("Selected Product ID: None")

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)