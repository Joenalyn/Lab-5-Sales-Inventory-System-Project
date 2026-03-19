import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from database import create_database
from dashboard import SalesInventoryDashboard


if __name__ == "__main__":
    create_database()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = SalesInventoryDashboard()
    window.showMaximized()

    sys.exit(app.exec_())