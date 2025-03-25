import pandas as pd
import mysql.connector
from mysql.connector import Error

# CSV file path
csv_file = 'C:/Users/Elyse/Documents/Data Warehouse Module/Practical Assgnment/DW Assignment 1/updated_data_warehouse.csv'  # Update with your correct file path

# MySQL database connection details
config = {
    'user': 'root',                # MySQL username (your username)
    'password': 'Elyse@2050',        # MySQL password
    'host': 'localhost',            # MySQL host (usually localhost)
    'database': 'student_performance_db',  # Your database name
    'raise_on_warnings': True
}

connection = None

try:
    # Read CSV file into pandas DataFrame
    df = pd.read_csv(csv_file)

    # Display columns of the DataFrame for debugging
    print(f"DataFrame Columns: {df.columns}")

    # The updated column names from the saved CSV
    expected_columns = [
        "Age", "Year_of_Study", "Attendance", "Assignment_Score", "Midterm_Score", 
        "Final_Score", "Tuition_Paid", "Outstanding_Balance", "Books_Borrowed", 
        "Library_Visits", "Days_Absent", "Gender_Male", "Department_Computer Science", 
        "Department_Electrical Engineering", "Performance_Pass", "Parents_Education_Primary", 
        "Parents_Education_University", "Chronic_Illness_Yes", "Cluster"
    ]

    # Ensure columns match the expected ones
    if df.columns.tolist() != expected_columns:
        print(f"Warning: The CSV columns don't match the expected columns!")
        print(f"Expected: {expected_columns}")
        print(f"Actual: {df.columns.tolist()}")
        # Optionally, exit the script if needed
        # exit()

    # Establish MySQL connection
    connection = mysql.connector.connect(**config)

    if connection.is_connected():
        cursor = connection.cursor()

        # Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS student_data (
            Age INT,
            Year_of_Study INT,
            Attendance FLOAT,
            Assignment_Score FLOAT,
            Midterm_Score FLOAT,
            Final_Score FLOAT,
            Tuition_Paid INT,
            Outstanding_Balance FLOAT,
            Books_Borrowed INT,
            Library_Visits INT,
            Days_Absent INT,
            Gender_Male INT,
            `Department_Computer_Science` INT,
            `Department_Electrical_Engineering` INT,
            Performance_Pass INT,
            Parents_Education_Primary INT,
            Parents_Education_University INT,
            Chronic_Illness_Yes INT,
            Cluster INT
        );
        """
        cursor.execute(create_table_query)
        print("Table 'student_data' created successfully (if it didn't exist).")

        # Inserting data from the DataFrame to MySQL table
        for row in df.itertuples(index=False, name=None):
            insert_query = """
            INSERT INTO student_data (
                Age, Year_of_Study, Attendance, Assignment_Score, Midterm_Score, Final_Score,
                Tuition_Paid, Outstanding_Balance, Books_Borrowed, Library_Visits, Days_Absent, 
                Gender_Male, `Department_Computer_Science`, `Department_Electrical_Engineering`, 
                Performance_Pass, Parents_Education_Primary, Parents_Education_University, 
                Chronic_Illness_Yes, Cluster
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s);
            """
            cursor.execute(insert_query, row)
        
        # Commit the transaction
        connection.commit()
        print(f"{len(df)} rows inserted successfully into 'student_data'.")

except Error as e:
    print(f"Error: {e}")

finally:
    # Close the connection if it was established
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")
