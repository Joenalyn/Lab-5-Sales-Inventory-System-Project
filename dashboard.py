import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPushButton, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy,
    QSpacerItem, QStackedLayout, QLineEdit
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from inventory import InventoryWindow
from record_sale import RecordSaleWindow
from restock_product import RestockProductWindow
from sales_record import SalesRecordsWindow
from db_functions import (
    get_dashboard_summary,
    get_product_counts_by_category,
    get_daily_sales_summary,
    get_recent_sales,
    get_top_low_stock_items
)


class MenuButton(QPushButton):
    def __init__(self, text, active=False):
        super().__init__(text)
        self.setFixedHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self.get_style(active))

    def get_style(self, active):
        if active:
            return """
                QPushButton {
                    background-color: #235268;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 18px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #2f6f8;
                }
            """
        return """
            QPushButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding-left: 18px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1b3f52;
                color: white;
            }
        """


class ClickableStatCard(QPushButton):
    def __init__(self, title, value):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(135)
        self.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #ececec;
                border-radius: 20px;
                text-align: left;
            }
            QPushButton:hover {
                border: 1px solid #d7d7d7;
                background: #fcfcfc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            "color: #374151; font-size: 13px; font-weight: 600; "
            "background: transparent; border: none;"
        )
        self.title_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(
            "color: #235268; font-size: 30px; font-weight: 800; "
            "background: transparent; border: none;"
        )
        self.value_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

    def set_value(self, value):
        self.value_label.setText(str(value))


class GraphCard(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #ececec;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            "color: #235268; font-size: 16px; font-weight: 700; "
            "background: transparent; border: none;"
        )

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.canvas, 1)


class OverlaySidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setStyleSheet("""
            QFrame {
                background-color: #0f0f10;
                border-right: 1px solid #1b3f52;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 24, 22, 24)
        layout.setSpacing(10)

        top_bar = QHBoxLayout()

        logo_box = QVBoxLayout()

        logo = QLabel("Sales Inventory")
        logo.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Management System")
        subtitle.setStyleSheet("""
            color: #9ca3af;
            font-size: 14px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)

        logo_box.addWidget(logo)
        logo_box.addWidget(subtitle)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(34, 34)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #1b3f52;
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #2d2d2d;
            }
        """)

        top_bar.addLayout(logo_box)
        top_bar.addStretch()
        top_bar.addWidget(self.close_btn)

        layout.addLayout(top_bar)
        layout.addSpacing(20)

        section1 = QLabel("MAIN MENU")
        section1.setStyleSheet("color: #7a7a7a; font-size: 11px; font-weight: 700; background: transparent; border: none;")
        layout.addWidget(section1)
        layout.addSpacing(6)

        self.dashboard_btn = MenuButton("Dashboard", active=True)
        self.view_inventory_btn = MenuButton("View Inventory")

        layout.addWidget(self.dashboard_btn)
        layout.addWidget(self.view_inventory_btn)

        layout.addSpacing(18)

        section2 = QLabel("TRANSACTIONS")
        section2.setStyleSheet("color: #7a7a7a; font-size: 11px; font-weight: 700; background: transparent; border: none;")
        layout.addWidget(section2)
        layout.addSpacing(6)

        self.record_sale_btn = MenuButton("Record Sale")
        self.restock_btn = MenuButton("Restock Product")
        self.sales_records_btn = MenuButton("View Sales Records")

        layout.addWidget(self.record_sale_btn)
        layout.addWidget(self.restock_btn)
        layout.addWidget(self.sales_records_btn)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        section3 = QLabel("SETTINGS")
        section3.setStyleSheet("color: #7a7a7a; font-size: 11px; font-weight: 700; background: transparent; border: none;")
        layout.addWidget(section3)
        layout.addSpacing(6)

        self.logout_btn = MenuButton("Exit")
        layout.addWidget(self.logout_btn)


class SalesInventoryDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inventory_window = None
        self.record_sale_window = None
        self.restock_window = None
        self.sales_records_window = None
        self.sidebar_visible = False

        self.setWindowTitle("Sales Inventory Management System")
        self.setMinimumSize(1400, 850)
        self.setStyleSheet("background-color: #f3f4f6;")

        self.init_ui()
        self.refresh_dashboard()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.root_layout = QStackedLayout(central)
        self.root_layout.setStackingMode(QStackedLayout.StackAll)

        self.main_content = self.create_main_content()
        self.root_layout.addWidget(self.main_content)

        self.overlay_layer = QWidget()
        self.overlay_layer.setStyleSheet("background: rgba(0, 0, 0, 60);")
        self.overlay_layer.hide()
        self.root_layout.addWidget(self.overlay_layer)

        self.sidebar = OverlaySidebar(self.overlay_layer)
        self.sidebar.move(-320, 0)

        self.sidebar.close_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar.view_inventory_btn.clicked.connect(self.open_inventory_window)
        self.sidebar.record_sale_btn.clicked.connect(self.open_record_sale_window)
        self.sidebar.restock_btn.clicked.connect(self.open_restock_window)
        self.sidebar.sales_records_btn.clicked.connect(self.open_sales_records_window)
        self.sidebar.logout_btn.clicked.connect(self.close)

    def create_main_content(self):
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(26, 24, 26, 24)
        container_layout.setSpacing(22)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(14)

        self.menu_toggle_btn = QPushButton("☰")
        self.menu_toggle_btn.setFixedSize(44, 44)
        self.menu_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.menu_toggle_btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 14px;
                font-size: 18px;
                font-weight: 700;
                color: #111;
            }
            QPushButton:hover {
                background: #f9fafb;
            }
        """)
        self.menu_toggle_btn.clicked.connect(self.toggle_sidebar)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search products...")
        self.search_bar.setFixedHeight(44)
        self.search_bar.returnPressed.connect(self.handle_dashboard_search)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 14px;
                padding: 0 14px;
                font-size: 13px;
                color: #222;
            }
        """)

        user_box = QFrame()
        user_box.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        user_layout = QHBoxLayout(user_box)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(10)

        avatar = QLabel("A")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet("""
            background: #d9d9d9;
            color: #222;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        """)

        name_role = QVBoxLayout()
        name_role.setSpacing(1)

        name = QLabel("Admin User")
        name.setStyleSheet("color: #235268; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        role = QLabel("System Administrator")
        role.setStyleSheet("color: #6b7280; font-size: 12px; background: transparent; border: none;")

        name_role.addWidget(name)
        name_role.addWidget(role)

        user_layout.addWidget(avatar)
        user_layout.addLayout(name_role)

        top_bar.addWidget(self.menu_toggle_btn)
        top_bar.addWidget(self.search_bar, 1)
        top_bar.addStretch()
        top_bar.addWidget(user_box)

        container_layout.addLayout(top_bar)

        header = QLabel("Hello, Admin")
        header.setStyleSheet("""
            color: #235268;
            font-size: 40px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        container_layout.addWidget(header)

        stats_layout = QGridLayout()
        stats_layout.setHorizontalSpacing(18)
        stats_layout.setVerticalSpacing(18)

        self.total_products_card = ClickableStatCard("Total Products", "0")
        self.available_stocks_card = ClickableStatCard("Available Stocks", "0")
        self.low_stocks_card = ClickableStatCard("Low Stocks", "0")
        self.sales_records_card = ClickableStatCard("Sales Records", "0")

        self.total_products_card.clicked.connect(self.open_inventory_window)
        self.available_stocks_card.clicked.connect(self.open_inventory_window)
        self.low_stocks_card.clicked.connect(self.open_low_stock_inventory)
        self.sales_records_card.clicked.connect(self.open_sales_records_window)

        stats_layout.addWidget(self.total_products_card, 0, 0)
        stats_layout.addWidget(self.available_stocks_card, 0, 1)
        stats_layout.addWidget(self.low_stocks_card, 0, 2)
        stats_layout.addWidget(self.sales_records_card, 0, 3)

        container_layout.addLayout(stats_layout)

        content_grid = QGridLayout()
        content_grid.setHorizontalSpacing(18)
        content_grid.setVerticalSpacing(18)

        self.system_overview_card = GraphCard("System Overview")
        self.recent_sales_card = GraphCard("Recent Sales")
        self.low_stock_graph_card = GraphCard("Top Low Stock Items")
        self.sales_preview_graph_card = GraphCard("Sales Activity")

        content_grid.addWidget(self.system_overview_card, 0, 0)
        content_grid.addWidget(self.recent_sales_card, 0, 1)
        content_grid.addWidget(self.low_stock_graph_card, 1, 0)
        content_grid.addWidget(self.sales_preview_graph_card, 1, 1)

        container_layout.addLayout(content_grid, 1)
        return container

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay_layer.setGeometry(0, 0, self.width(), self.height())
        self.sidebar.setFixedHeight(self.height())
        if self.sidebar_visible:
            self.sidebar.move(0, 0)
        else:
            self.sidebar.move(-self.sidebar.width() - 20, 0)

    def mousePressEvent(self, event):
        if self.sidebar_visible:
            if not self.sidebar.geometry().contains(event.pos()):
                self.toggle_sidebar()
        super().mousePressEvent(event)

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        self.overlay_layer.setVisible(True)

        end_x = 0 if self.sidebar_visible else -self.sidebar.width() - 20

        self.animation = QPropertyAnimation(self.sidebar, b"pos")
        self.animation.setDuration(220)
        self.animation.setStartValue(self.sidebar.pos())
        self.animation.setEndValue(QPoint(end_x, 0))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.handle_animation_finished)
        self.animation.start()

        if self.sidebar_visible:
            self.overlay_layer.raise_()
            self.sidebar.raise_()

    def handle_animation_finished(self):
        if not self.sidebar_visible:
            self.overlay_layer.hide()

    def get_inventory_window(self):
        if self.inventory_window is None:
            self.inventory_window = InventoryWindow()
        return self.inventory_window

    def get_sales_records_window(self):
        if self.sales_records_window is None:
            self.sales_records_window = SalesRecordsWindow()
        return self.sales_records_window

    def handle_dashboard_search(self):
        keyword = self.search_bar.text().strip()
        if not keyword:
            self.open_inventory_window()
            return

        inventory = self.get_inventory_window()
        inventory.showMaximized()
        inventory.raise_()
        inventory.activateWindow()
        inventory.set_search_text(keyword)

    def open_inventory_window(self):
        if self.sidebar_visible:
            self.toggle_sidebar()

        inventory = self.get_inventory_window()
        inventory.showMaximized()
        inventory.raise_()
        inventory.activateWindow()
        inventory.show_all_products()
        self.refresh_dashboard()

    def open_low_stock_inventory(self):
        if self.sidebar_visible:
            self.toggle_sidebar()

        inventory = self.get_inventory_window()
        inventory.showMaximized()
        inventory.raise_()
        inventory.activateWindow()
        inventory.show_low_stock_products()
        self.refresh_dashboard()

    def open_record_sale_window(self):
        if self.sidebar_visible:
            self.toggle_sidebar()

        if self.record_sale_window is None:
            self.record_sale_window = RecordSaleWindow()
            self.record_sale_window.window_closed.connect(self.refresh_dashboard)

        self.record_sale_window.load_products()
        self.record_sale_window.showMaximized()
        self.record_sale_window.raise_()
        self.record_sale_window.activateWindow()

    def open_restock_window(self):
        if self.sidebar_visible:
            self.toggle_sidebar()

        if self.restock_window is None:
            self.restock_window = RestockProductWindow()
            self.restock_window.window_closed.connect(self.refresh_dashboard)

        self.restock_window.load_products()
        self.restock_window.showMaximized()
        self.restock_window.raise_()
        self.restock_window.activateWindow()

    def open_sales_records_window(self):
        if self.sidebar_visible:
            self.toggle_sidebar()

        sales_window = self.get_sales_records_window()
        sales_window.refresh_data()
        sales_window.showMaximized()
        sales_window.raise_()
        sales_window.activateWindow()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        summary = get_dashboard_summary()
        self.total_products_card.set_value(summary["total_products"])
        self.available_stocks_card.set_value(summary["total_stocks"])
        self.low_stocks_card.set_value(summary["low_stock_count"])
        self.sales_records_card.set_value(summary["total_sales"])

        self.draw_category_chart()
        self.draw_recent_sales_chart()
        self.draw_low_stock_snapshot()
        self.draw_sales_activity_chart()

    def draw_category_chart(self):
        data = get_product_counts_by_category()

        fig = self.system_overview_card.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "No product data available", ha="center", va="center")
            ax.axis("off")
        else:
            labels = [item["category"] for item in data]
            values = [item["total_products"] for item in data]
            ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
            ax.set_title("Products by Category", fontsize=11)

        fig.tight_layout()
        self.system_overview_card.canvas.draw()

    def draw_recent_sales_chart(self):
        data = get_daily_sales_summary(7)

        fig = self.recent_sales_card.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "No sales data available", ha="center", va="center")
            ax.axis("off")
        else:
            labels = [item["sale_date"] for item in data]
            values = [item["total_sales"] for item in data]
            ax.plot(labels, values, marker="o", color="#235268", linewidth=2.5)
            ax.set_title("Daily Sales Summary", fontsize=11)
            ax.set_ylabel("Sales Amount")
            ax.tick_params(axis="x", rotation=25)

        fig.tight_layout()
        self.recent_sales_card.canvas.draw()

    def draw_low_stock_snapshot(self):
        items = get_top_low_stock_items(5)

        fig = self.low_stock_graph_card.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if not items:
            ax.text(0.5, 0.5, "No product data available", ha="center", va="center")
            ax.axis("off")
        else:
            names = [item["product_name"] for item in items]
            stocks = [item["quantity_in_stock"] for item in items]

            names.reverse()
            stocks.reverse()

            ax.barh(names, stocks, color="#235268")
            ax.set_title("Top Low Stock Items", fontsize=11)
            ax.set_xlabel("Remaining Stock")

        fig.tight_layout()
        self.low_stock_graph_card.canvas.draw()

    def draw_sales_activity_chart(self):
        sales = get_recent_sales(8)

        fig = self.sales_preview_graph_card.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if not sales:
            ax.text(0.5, 0.5, "No sales records available", ha="center", va="center")
            ax.axis("off")
        else:
            labels = [str(item["sale_id"]) for item in sales]
            labels.reverse()
            values = [item["total_amount"] for item in sales]
            values.reverse()

            ax.bar(labels, values, color="#235268")
            ax.set_title("Recent Sales Amounts", fontsize=11)
            ax.set_xlabel("Sale ID")
            ax.set_ylabel("Amount")

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#9ca3af")
            ax.spines["bottom"].set_color("#9ca3af")
            ax.tick_params(colors="#374151")
            ax.title.set_color("#111827")

        fig.tight_layout()
        self.sales_preview_graph_card.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = SalesInventoryDashboard()
    window.showMaximized()

    sys.exit(app.exec_())