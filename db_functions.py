import sqlite3
from datetime import datetime

DB_NAME = "sales_inventory.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def add_product(product_name, category, price, quantity_in_stock):
    try:
        if not product_name.strip():
            return False, "Product name is required."
        if not category.strip():
            return False, "Category is required."
        if float(price) < 0:
            return False, "Price cannot be negative."
        if int(quantity_in_stock) < 0:
            return False, "Quantity cannot be negative."

        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO products (
                product_name,
                category,
                price,
                quantity_in_stock,
                date_added,
                last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            product_name.strip(),
            category.strip(),
            float(price),
            int(quantity_in_stock),
            now,
            now
        ))

        conn.commit()
        conn.close()
        return True, "Product added successfully."

    except Exception as e:
        return False, f"Error adding product: {e}"

def get_all_products():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM products
            ORDER BY product_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving products: {e}")
        return []

def get_product_by_id(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM products
            WHERE product_id = ?
        """, (product_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    except Exception as e:
        print(f"Error getting product: {e}")
        return None

def update_product(product_id, product_name, category, price, quantity_in_stock):
    try:
        if not product_name.strip():
            return False, "Product name is required."
        if not category.strip():
            return False, "Category is required."
        if float(price) < 0:
            return False, "Price cannot be negative."
        if int(quantity_in_stock) < 0:
            return False, "Quantity cannot be negative."

        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE products
            SET product_name = ?,
                category = ?,
                price = ?,
                quantity_in_stock = ?,
                last_updated = ?
            WHERE product_id = ?
        """, (
            product_name.strip(),
            category.strip(),
            float(price),
            int(quantity_in_stock),
            now,
            product_id
        ))

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return False, "Product not found."

        conn.close()
        return True, "Product updated successfully."

    except Exception as e:
        return False, f"Error updating product: {e}"


def delete_product(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) AS total_sales
            FROM sales
            WHERE product_id = ?
        """, (product_id,))
        sales_count = cursor.fetchone()["total_sales"]

        if sales_count > 0:
            conn.close()
            return False, "Cannot delete product because it already has sales records."

        cursor.execute("""
            DELETE FROM products
            WHERE product_id = ?
        """, (product_id,))

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return False, "Product not found."

        conn.close()
        return True, "Product deleted successfully."

    except Exception as e:
        return False, f"Error deleting product: {e}"

def search_products(keyword):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        search_value = f"%{keyword.strip()}%"

        cursor.execute("""
            SELECT *
            FROM products
            WHERE product_name LIKE ?
               OR category LIKE ?
            ORDER BY product_name ASC
        """, (search_value, search_value))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def record_sale(product_id, quantity_sold):
    try:
        quantity_sold = int(quantity_sold)

        if quantity_sold <= 0:
            return False, "Quantity sold must be greater than 0."

        conn = get_connection()
        cursor = conn.cursor()

        # Get product details
        cursor.execute("""
            SELECT *
            FROM products
            WHERE product_id = ?
        """, (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return False, "Product not found."

        current_stock = product["quantity_in_stock"]
        unit_price = product["price"]
        product_name = product["product_name"]

        if quantity_sold > current_stock:
            conn.close()
            return False, "Insufficient stock."

        total_amount = float(unit_price) * quantity_sold
        now = datetime.now()
        sale_date = now.strftime("%Y-%m-%d")
        sale_time = now.strftime("%H:%M:%S")
        updated_stock = current_stock - quantity_sold
        last_updated = now.strftime("%Y-%m-%d %H:%M:%S")

        # Insert into sales table
        cursor.execute("""
            INSERT INTO sales (
                product_id,
                product_name,
                quantity_sold,
                unit_price,
                total_amount,
                sale_date,
                sale_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            product_name,
            quantity_sold,
            unit_price,
            total_amount,
            sale_date,
            sale_time
        ))

        # Update stock in products table
        cursor.execute("""
            UPDATE products
            SET quantity_in_stock = ?,
                last_updated = ?
            WHERE product_id = ?
        """, (
            updated_stock,
            last_updated,
            product_id
        ))

        conn.commit()
        conn.close()

        return True, "Sale recorded successfully."

    except Exception as e:
        return False, f"Error recording sale: {e}"

def get_all_sales():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM sales
            ORDER BY sale_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving sales: {e}")
        return []

def get_sales_by_product(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM sales
            WHERE product_id = ?
            ORDER BY sale_id DESC
        """, (product_id,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving sales by product: {e}")
        return []

def restock_product(product_id, quantity_added):
    try:
        quantity_added = int(quantity_added)

        if quantity_added <= 0:
            return False, "Restock quantity must be greater than 0."

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM products
            WHERE product_id = ?
        """, (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return False, "Product not found."

        product_name = product["product_name"]
        previous_stock = product["quantity_in_stock"]
        new_stock = previous_stock + quantity_added

        now = datetime.now()
        restock_date = now.strftime("%Y-%m-%d")
        restock_time = now.strftime("%H:%M:%S")
        last_updated = now.strftime("%Y-%m-%d %H:%M:%S")

        # update stock in products table
        cursor.execute("""
            UPDATE products
            SET quantity_in_stock = ?,
                last_updated = ?
            WHERE product_id = ?
        """, (
            new_stock,
            last_updated,
            product_id
        ))

        # save restock history
        cursor.execute("""
            INSERT INTO restock_history (
                product_id,
                product_name,
                quantity_added,
                previous_stock,
                new_stock,
                restock_date,
                restock_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            product_name,
            quantity_added,
            previous_stock,
            new_stock,
            restock_date,
            restock_time
        ))

        conn.commit()
        conn.close()

        return True, "Product restocked successfully."

    except Exception as e:
        return False, f"Error restocking product: {e}"

def get_all_restock_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM restock_history
            ORDER BY restock_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving restock history: {e}")
        return []

def get_dashboard_summary():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total_products FROM products")
        total_products = cursor.fetchone()["total_products"]

        cursor.execute("SELECT COALESCE(SUM(quantity_in_stock), 0) AS total_stocks FROM products")
        total_stocks = cursor.fetchone()["total_stocks"]

        cursor.execute("SELECT COUNT(*) AS total_sales FROM sales")
        total_sales = cursor.fetchone()["total_sales"]

        cursor.execute("""
            SELECT COUNT(*) AS low_stock_count
            FROM products
            WHERE quantity_in_stock <= 5
        """)
        low_stock_count = cursor.fetchone()["low_stock_count"]

        conn.close()

        return {
            "total_products": total_products,
            "total_stocks": total_stocks,
            "total_sales": total_sales,
            "low_stock_count": low_stock_count
        }

    except Exception as e:
        print(f"Error getting dashboard summary: {e}")
        return {
            "total_products": 0,
            "total_stocks": 0,
            "total_sales": 0,
            "low_stock_count": 0
        }

def get_low_stock_products(threshold=5):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM products
            WHERE quantity_in_stock <= ?
            ORDER BY quantity_in_stock ASC, product_name ASC
        """, (threshold,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving low stock products: {e}")
        return []

def get_product_counts_by_category():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, COUNT(*) AS total_products
            FROM products
            GROUP BY category
            ORDER BY total_products DESC, category ASC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving category counts: {e}")
        return []

def get_recent_sales(limit=10):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM sales
            ORDER BY sale_id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving recent sales: {e}")
        return []

def get_daily_sales_summary(limit=7):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sale_date, COALESCE(SUM(total_amount), 0) AS total_sales
            FROM sales
            GROUP BY sale_date
            ORDER BY sale_date DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        rows = [dict(row) for row in rows]
        rows.reverse()
        return rows

    except Exception as e:
        print(f"Error retrieving daily sales summary: {e}")
        return []

def get_top_low_stock_items(limit=5):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT product_name, quantity_in_stock
            FROM products
            ORDER BY quantity_in_stock ASC, product_name ASC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"Error retrieving top low stock items: {e}")
        return []

if __name__ == "__main__":
    print("ALL PRODUCTS:")
    print(get_all_products())

    print("\nDASHBOARD SUMMARY:")
    print(get_dashboard_summary())