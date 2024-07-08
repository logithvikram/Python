import psycopg2
conn = psycopg2.connect(database="flask_db",  
                        user="postgres", 
                        password="logi2002",  
                        host="localhost", port="5432") 

  
cur = conn.cursor() 


cur.execute(
    '''CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        price FLOAT
    );'''
)
cur.execute(
    '''INSERT INTO products (name, price) VALUES
    ('Apple', 1.99),
    ('Orange', 0.99),
    ('Banana', 0.59)
    ON CONFLICT (id) DO NOTHING;'''
)  
conn.commit() 
  
cur.close() 
conn.close() 