--Assignment Tasks
--Task 1 — Build the Sales Detail Dataset (6 marks)
--Management needs a detailed sales dataset for analysis. Return one row per order item containing:
--order_id and order_date
--customer full name
--store name
--staff full name
--product name
--category name
--brand name
--quantity, list_price, discount
--calculated net_line_revenue

--Include only completed orders (order_status = 4). Sort the result from newest order to oldest.

SELECT
	o.order_id,
	o.order_date,
    c.first_name + ' ' + c.last_name as customer_full_name,
    s.store_name,
    st.first_name + ' ' + st.last_name as staff_full_name,
    p.product_name,
    cat.category_name,
    b.brand_name,
    oi.quantity,
    oi.list_price,
    oi.discount,
    oi.quantity * oi.list_price * (1 - oi.discount) as net_line_revenue
FROM sales.orders as o
INNER JOIN sales.order_items as oi
    ON o.order_id = oi.order_id
INNER JOIN sales.customers as c
    ON o.customer_id = c.customer_id
INNER JOIN sales.staffs as st
    ON o.staff_id = st.staff_id
INNER JOIN sales.stores as s
    ON o.store_id = s.store_id
INNER JOIN production.products as p
    ON oi.product_id = p.product_id
INNER JOIN production.categories as cat
    ON p.category_id = cat.category_id
INNER JOIN production.brands as b
    ON p.brand_id = b.brand_id
WHERE o.order_status = 4
ORDER BY o.order_date DESC;

--Task 2 — Store Performance Summary (5 marks)
--Create a store-level performance report for completed orders showing:
--store name
--number of distinct orders
--total units sold
--total net revenue
--average order value

--Return one row per store and order the stores from highest to lowest total net revenue.

SELECT
    s.store_name,
    COUNT(DISTINCT o.order_id) as number_of_orders,
    SUM(oi.quantity) as total_units_sold,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) as total_net_revenue,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) / COUNT(DISTINCT o.order_id) as average_order_value
FROM sales.orders as o
INNER JOIN sales.order_items as oi
    ON o.order_id = oi.order_id
INNER JOIN sales.stores as s
    ON o.store_id = s.store_id
GROUP BY s.store_name
ORDER BY total_net_revenue DESC;

--Task 3 — High-Value Customers (5 marks)
--Management wants to identify high-value customers. Return customers whose total completed-order spending is greater than the average total spending of customers who have completed orders.

--Show customer_id, customer name, completed order count, and total spending. Order the result by total spending descending.

WITH customer_spending as (
    SELECT
        c.customer_id,
        c.first_name + ' ' + c.last_name as customer_name,
        COUNT(DISTINCT o.order_id) as completed_order_count,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) as total_spending
    FROM sales.customers as c
    INNER JOIN sales.orders as o
        ON c.customer_id = o.customer_id
    INNER JOIN sales.order_items as oi
        ON o.order_id = oi.order_id
    GROUP BY
        c.customer_id,
        c.first_name,
        c.last_name
)
SELECT
    customer_id,
    customer_name,
    completed_order_count,
    total_spending
FROM customer_spending
WHERE total_spending > (
    SELECT
        AVG(total_spending)
    FROM customer_spending
)
ORDER BY total_spending DESC;

--Task 4 — Inventory Risk Report (5 marks)
--Operations wants to identify inventory risk. Return products where the stock quantity is below 5 in at least one store.

--Show product name, store name, current quantity, category name, and brand name. Products with zero stock should appear first, followed by the lowest remaining quantities.

SELECT
    p.product_name,
    s.store_name,
    st.quantity as current_quantity,
    c.category_name,
    b.brand_name
FROM production.stocks as st
INNER JOIN production.products as p
    ON st.product_id = p.product_id
INNER JOIN sales.stores as s
    ON st.store_id = s.store_id
INNER JOIN production.categories as c
    ON p.category_id = c.category_id
INNER JOIN production.brands as b
    ON p.brand_id = b.brand_id
WHERE st.quantity < 5
ORDER BY
    st.quantity,
    p.product_name

--Task 5 — Top Products Within Each Category (6 marks)
--For each product category, identify the top 3 products by total net revenue from completed orders.

--Return category name, product name, total units sold, total net revenue, and the product's position within its category. Tied products must receive the same position and the next position should not contain gaps.

WITH product_sales as (
    SELECT
        c.category_id,
        c.category_name,
        p.product_id,
        p.product_name,
        SUM(oi.quantity) as total_units_sold,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) as total_net_revenue
    FROM sales.orders as o
    INNER JOIN sales.order_items as oi
        ON o.order_id = oi.order_id
    INNER JOIN production.products as p
        ON oi.product_id = p.product_id
    INNER JOIN production.categories as c
        ON p.category_id = c.category_id
    GROUP BY
        c.category_id,
        c.category_name,
        p.product_id,
        p.product_name
),
ranked_products as (
    SELECT
        category_name,
        product_name,
        total_units_sold,
        total_net_revenue,
        DENSE_RANK() over(PARTITION BY category_id ORDER BY total_net_revenue DESC) as category_position
    FROM product_sales
)
SELECT
    category_name,
    product_name,
    total_units_sold,
    total_net_revenue,
    category_position
FROM ranked_products
WHERE category_position <= 3
ORDER BY
    category_name,
    category_position,
    total_net_revenue DESC;

--Task 6 — Monthly Sales Trend (6 marks)
--Create a monthly sales trend for completed orders.

--For each calendar month return:
--year
--month
--total net revenue
--previous month's total net revenue
--revenue change from the previous month

--The first month may have NULL for the previous-month comparison. Sort chronologically.

WITH monthly_sales as (
    SELECT
        YEAR(o.order_date) as sales_year,
        MONTH(o.order_date) as sales_month,
        SUM(
            oi.quantity * oi.list_price * (1 - oi.discount)
        ) as total_net_revenue
    FROM sales.orders as o
    INNER JOIN sales.order_items as oi
        ON o.order_id = oi.order_id
    GROUP BY
        YEAR(o.order_date),
        MONTH(o.order_date)
),
monthly_comparison as (
    SELECT
        sales_year,
        sales_month,
        total_net_revenue,
        LAG(total_net_revenue) over(ORDER BY sales_year, sales_month) as previous_month_revenue
    FROM monthly_sales
)
SELECT
    sales_year as year,
    sales_month as month,
    total_net_revenue,
    previous_month_revenue,
    total_net_revenue - previous_month_revenue as revenue_change
FROM monthly_comparison
ORDER BY
    sales_year,
    sales_month;