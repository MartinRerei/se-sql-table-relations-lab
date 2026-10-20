import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('data.sqlite')

# ==========================================
# Part 1: Join and Filter
# ==========================================

# 1. Employees in Boston (Pytest expects shape (2, 2))
df_boston = pd.read_sql("""
    SELECT e.firstName, e.lastName
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston';
""", conn)

# 2. Ghost offices
df_zero_emp = pd.read_sql("""
    SELECT o.officeCode, o.city
    FROM offices o
    LEFT JOIN employees e ON o.officeCode = e.officeCode
    GROUP BY o.officeCode, o.city
    HAVING COUNT(e.employeeNumber) = 0;
""", conn)

# ==========================================
# Part 2: Type of Join
# ==========================================

# 1. Employee audit
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees e
    LEFT JOIN offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""", conn)

# 2. Customers with no orders
df_contacts = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
    FROM customers c
    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName;
""", conn)

# ==========================================
# Part 3: Built-In Function
# ==========================================

df_payments = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, p.amount, p.paymentDate
    FROM customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC;
""", conn)

# ==========================================
# Part 4: Joining and Grouping
# ==========================================

# 1. High credit limit sales reps
df_credit = pd.read_sql("""
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

# 2. Top selling products
df_product_sold = pd.read_sql("""
    SELECT 
        p.productName, 
        COUNT(od.orderNumber) AS numorders, 
        SUM(od.quantityOrdered) AS totalunits
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC;
""", conn)

# ==========================================
# Part 5: Multiple Joins
# ==========================================

# 1. Unique customer reach per product
df_total_customers = pd.read_sql("""
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

# 2. Customers per office
df_customers = pd.read_sql("""
    SELECT 
        COUNT(c.customerNumber) AS n_customers, 
        o.officeCode, 
        o.city
    FROM offices o
    JOIN employees e ON o.officeCode = e.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode, o.city;
""", conn)

# ==========================================
# Part 6: Subquery
# ==========================================

df_under_20 = pd.read_sql("""
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