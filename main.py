import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('data.sqlite')

# --- Part 1: Join and Filter ---
# Q1: Boston employees
part1_q1 = pd.read_sql("""
    SELECT e.firstName, e.lastName, e.jobTitle
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston';
""", conn)
print("\n--- Part 1, Q1: Boston Employees ---")
print(part1_q1)

# Q2: Ghost offices (offices with 0 employees)
part1_q2 = pd.read_sql("""
    SELECT o.officeCode, o.city
    FROM offices o
    LEFT JOIN employees e ON o.officeCode = e.officeCode
    GROUP BY o.officeCode, o.city
    HAVING COUNT(e.employeeNumber) = 0;
""", conn)
print("\n--- Part 1, Q2: Offices with Zero Employees ---")
print(part1_q2)

# --- Part 2: Type of Join ---
# Q1: Employee audit
part2_q1 = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees e
    LEFT JOIN offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""", conn)
print("\n--- Part 2, Q1: Employee Audit ---")
print(part2_q1.head())

# Q2: Customers who have not placed an order
part2_q2 = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
    FROM customers c
    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName;
""", conn)
print("\n--- Part 2, Q2: Customers with No Orders ---")
print(part2_q2.head())

# --- Part 3: Built-In Function ---
# Customer payments sorted by amount
part3_q1 = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, p.amount, p.paymentDate
    FROM customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC;
""", conn)
print("\n--- Part 3: Customer Payments ---")
print(part3_q1.head())

# --- Part 4: Joining and Grouping ---
# Q1: High credit limit sales reps
part4_q1 = pd.read_sql("""
    SELECT 
        e.employeeNumber, 
        e.firstName, 
        e.lastName, 
        COUNT(c.customerNumber) AS num_customers
    FROM employees e
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY num_customers DESC;
""", conn)
print("\n--- Part 4, Q1: Sales Reps with High Credit Limits ---")
print(part4_q1)

# Q2: Top selling products
part4_q2 = pd.read_sql("""
    SELECT 
        p.productName, 
        COUNT(od.orderNumber) AS numorders, 
        SUM(od.quantityOrdered) AS totalunits
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC;
""", conn)
print("\n--- Part 4, Q2: Top Selling Products ---")
print(part4_q2.head())

# --- Part 5: Multiple Joins ---
# Q1: Unique customer reach per product
part5_q1 = pd.read_sql("""
    SELECT 
        p.productName, 
        p.productCode, 
        COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    JOIN orders o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC;
""", conn)
print("\n--- Part 5, Q1: Unique Customer Reach ---")
print(part5_q1.head())

# Q2: Customers per office location
part5_q2 = pd.read_sql("""
    SELECT 
        COUNT(c.customerNumber) AS n_customers, 
        o.officeCode, 
        o.city
    FROM offices o
    JOIN employees e ON o.officeCode = e.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode, o.city;
""", conn)
print("\n--- Part 5, Q2: Customers per Office ---")
print(part5_q2)

# --- Part 6: Subquery ---
# Sales reps for underperforming products
part6_q1 = pd.read_sql("""
    SELECT DISTINCT 
        e.employeeNumber, 
        e.firstName, 
        e.lastName, 
        o.city, 
        o.officeCode
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders ord ON c.customerNumber = ord.customerNumber
    JOIN orderdetails od ON ord.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT od_sub.productCode
        FROM orderdetails od_sub
        JOIN orders o_sub ON od_sub.orderNumber = o_sub.orderNumber
        GROUP BY od_sub.productCode
        HAVING COUNT(DISTINCT o_sub.customerNumber) < 20
    );
""", conn)
print("\n--- Part 6: Underperforming Product Reps ---")
print(part6_q1)

# Close connection
conn.close()
# Force update for CodeGrade submission