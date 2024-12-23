import os
import mysql.connector
from datetime import datetime, date

def create_test_database():
    # Connect to MySQL using environment variables
    cnx = mysql.connector.connect(
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),  # Default to empty password
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', '3306'))  # Add port configuration for Docker
    )
    cursor = cnx.cursor()

    # Create database and table
    cursor.execute("")
    cursor.execute("CREATE DATABASE ibd_parser_test")
    cursor.execute("USE ibd_parser_test")

    # Create table with common column types
    create_table_sql = """
    CREATE TABLE test_table (
        id BIGINT AUTO_INCREMENT,
        tiny_int_col TINYINT,
        small_int_col SMALLINT,
        int_col INT,
        big_int_col BIGINT,
        float_col FLOAT,
        double_col DOUBLE,
        decimal_col DECIMAL(10,2),
        char_col CHAR(10),
        varchar_col VARCHAR(255),
        text_col TEXT,
        date_col DATE,
        time_col TIME,
        datetime_col DATETIME,
        timestamp_col TIMESTAMP,
        bool_col BOOLEAN,
        enum_col ENUM('small', 'medium', 'large'),
        binary_col BINARY(50),
        blob_col BLOB,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_table_sql)

    # Insert test data
    insert_sql = """
    INSERT INTO test_table (
        tiny_int_col, small_int_col, int_col, big_int_col,
        float_col, double_col, decimal_col,
        char_col, varchar_col, text_col,
        date_col, time_col, datetime_col,
        bool_col, enum_col
    ) VALUES (
        %s, %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s, %s
    )
    """

    test_data = [
        (
            127, 32767, 2147483647, 9223372036854775807,
            3.14, 3.141592653589793, 1234.56,
            'CHAR(10)', 'Variable length text', 'Long text content...',
            date(2024, 1, 1), '12:34:56', datetime(2024, 1, 1, 12, 34, 56),
            True, 'medium'
        ),
        # Add more test records here...
    ]

    for data in test_data:
        cursor.execute(insert_sql, data)

    # Commit and close
    cnx.commit()
    cursor.close()
    cnx.close()

if __name__ == '__main__':
    create_test_database()
