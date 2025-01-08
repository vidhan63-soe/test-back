from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        # Create orders table with a foreign key reference to customers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_description TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

# Home route
@app.route('/')
def home():
    return "Welcome to the Customer Management API!"

# CRUD Operations for Customers
@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.json  # This should be a dictionary
    if isinstance(data, dict):  # Check if data is a dictionary
        with sqlite3.connect('customers.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
                           (data['name'], data['email'], data['phone']))
            conn.commit()
            return jsonify({'id': cursor.lastrowid, **data}), 201
    else:
        return jsonify({'error': 'Invalid input format'}), 400  # Return an error for invalid input


@app.route('/customers', methods=['GET'])
def read_customers():
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers')
        customers = cursor.fetchall()
        return jsonify([{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3]} for row in customers])

@app.route('/customers/<int:id>', methods=['GET'])
def read_customer(id):
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = ?', (id,))
        customer = cursor.fetchone()
        if customer:
            return jsonify({'id': customer[0], 'name': customer[1], 'email': customer[2], 'phone': customer[3]})
        return jsonify({'error': 'Customer not found'}), 404

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.json
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE customers SET name = ?, email = ?, phone = ? WHERE id = ?',
                       (data['name'], data['email'], data['phone'], id))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({'id': id, **data})
        return jsonify({'error': 'Customer not found'}), 404

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM customers WHERE id = ?', (id,))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({'message': 'Customer deleted'})
        return jsonify({'error': 'Customer not found'}), 404

# CRUD Operations for Orders
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO orders (customer_id, order_description) VALUES (?, ?)',
                       (data['customer_id'], data['order_description']))
        conn.commit()
        return jsonify({'id': cursor.lastrowid, **data}), 201

@app.route('/orders', methods=['GET'])
def read_orders():
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders')
        orders = cursor.fetchall()
        
        # Include customer details in the response
        result = []
        for order in orders:
            result.append({
                'id': order[0],
                'customer_id': order[1],
                'order_description': order[2]
            })
        
        return jsonify(result)

@app.route('/orders/<int:id>', methods=['GET'])
def read_order(id):
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (id,))
        order = cursor.fetchone()
        
        if order:
            return jsonify({
                'id': order[0],
                'customer_id': order[1],
                'order_description': order[2]
            })
        
        return jsonify({'error': 'Order not found'}), 404

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.json
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        
        # Update the order details
        cursor.execute('UPDATE orders SET customer_id = ?, order_description = ? WHERE id = ?',
                       (data['customer_id'], data['order_description'], id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'id': id, **data})
        
    return jsonify({'error': 'Order not found'}), 404

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    with sqlite3.connect('customers.db') as conn:
        cursor = conn.cursor()
        
        # Delete the specified order
        cursor.execute('DELETE FROM orders WHERE id = ?', (id,))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'message': 'Order deleted'})
        
    return jsonify({'error': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
