--JOINS

--Task 1:

SELECT
    o.order_id,
    c.first_name + ' ' + c.last_name AS customer_full_name,
    s.store_name,
    st.first_name + ' ' + st.last_name AS staff_full_name
FROM sales.orders AS o
INNER JOIN sales.customers AS c
    ON o.customer_id = c.customer_id
INNER JOIN sales.stores AS s
    ON o.store_id = s.store_id
INNER JOIN sales.staffs AS st
    ON o.staff_id = st.staff_id;

--Task 2:

SELECT
    p.product_id,
    p.product_name,
    b.brand_name,
    c.category_name
FROM production.products AS p
LEFT JOIN production.brands AS b
    ON p.brand_id = b.brand_id
LEFT JOIN production.categories AS c
    ON p.category_id = c.category_id;

--Task 3:

SELECT
    c.first_name,
    c.last_name,
    c.city,
    c.email
FROM sales.customers AS c
LEFT JOIN sales.orders AS o
    ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

--GROUP BY

--Task 4:

SELECT
    s.store_name,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_revenue
FROM sales.stores AS s
INNER JOIN sales.orders AS o
    ON s.store_id = o.store_id
INNER JOIN sales.order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY
    s.store_name
ORDER BY
    total_revenue DESC;

--Task 5:

SELECT
    b.brand_name,
    COUNT(p.product_id) AS number_of_products,
    AVG(p.list_price) AS average_list_price,
    MAX(p.list_price) AS highest_list_price
FROM production.brands AS b
INNER JOIN production.products AS p
    ON b.brand_id = p.brand_id
GROUP BY
    b.brand_name
HAVING COUNT(p.product_id) > 5;

--Task 6:

SELECT
    MONTH(o.order_date) AS order_month,
    COUNT(DISTINCT o.order_id) AS number_of_orders,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_revenue
FROM sales.orders AS o
INNER JOIN sales.order_items AS oi
    ON o.order_id = oi.order_id
WHERE YEAR(o.order_date) = 2017
GROUP BY MONTH(o.order_date)
ORDER BY order_month;

--Subqueries

--Task 7:

SELECT
    p.product_id,
    p.product_name,
    p.category_id,
    p.list_price
FROM production.products AS p
WHERE p.list_price > (
    SELECT AVG(p2.list_price)
    FROM production.products AS p2
    WHERE p2.category_id = p.category_id
);

--Task 8:

SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) AS order_count
FROM sales.customers AS c
INNER JOIN sales.orders AS o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
HAVING COUNT(o.order_id) > (
    SELECT AVG(order_count)
    FROM (
        SELECT
            customer_id,
            COUNT(order_id) AS order_count
        FROM sales.orders
        GROUP BY customer_id
    ) AS customer_orders
)
ORDER BY order_count DESC;

--CTEs

--Task 9:

WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_spend
    FROM sales.customers AS c
    INNER JOIN sales.orders AS o
        ON c.customer_id = o.customer_id
    INNER JOIN sales.order_items AS oi
        ON o.order_id = oi.order_id
    GROUP BY
        c.customer_id,
        c.first_name,
        c.last_name
),
customer_labels AS (
    SELECT
        customer_id,
        first_name,
        last_name,
        total_spend,
        CASE
            WHEN total_spend > (SELECT AVG(total_spend) FROM customer_spend)
                THEN 'High'
            ELSE 'Regular'
        END AS spend_label
    FROM customer_spend
)
SELECT
    customer_id,
    first_name,
    last_name,
    total_spend,
    RANK() OVER (ORDER BY total_spend DESC) AS spend_rank,
    spend_label
FROM customer_labels
ORDER BY total_spend DESC
OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;