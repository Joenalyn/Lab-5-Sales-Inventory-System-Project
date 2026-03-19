from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from db_functions import get_all_sales


class SalesRecordsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("View Sales Records")
        self.setStyleSheet("background-color: #f4f5f7;")
        self.build_ui()
        self.refresh_data()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        top_row = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Sales Records")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #111; background: transparent; border: none;")
        subtitle = QLabel("View all recorded sales transactions.")
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Sale ID", "Product ID", "Product Name", "Quantity Sold",
            "Unit Price", "Total Amount", "Sale Date", "Sale Time"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
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

    def refresh_data(self):
        sales = get_all_sales()
        self.table.setRowCount(len(sales))

        for row, item in enumerate(sales):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["sale_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(item["product_name"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(item["quantity_sold"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(item["unit_price"])))
            self.table.setItem(row, 5, QTableWidgetItem(str(item["total_amount"])))
            self.table.setItem(row, 6, QTableWidgetItem(str(item["sale_date"])))
            self.table.setItem(row, 7, QTableWidgetItem(str(item["sale_time"])))