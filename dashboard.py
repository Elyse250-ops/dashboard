import streamlit as st
import pandas as pd
import joblib
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns

# Load the trained model
model_filename = "random_forest_model.pkl"
try:
    model = joblib.load(model_filename)
except FileNotFoundError:
    st.error(f"Error: Model file '{model_filename}' not found!")
    st.stop()

# Expected features from training (excluding 'Cluster')
trained_features = [
    'Age', 'Year_of_Study', 'Attendance', 'Assignment_Score',
    'Midterm_Score', 'Final_Score', 'Tuition_Paid', 'Outstanding_Balance',
    'Books_Borrowed', 'Library_Visits', 'Days_Absent', 'Gender_Male',
    'Department_Computer Science', 'Department_Electrical Engineering',
    'Parents_Education_Primary', 'Parents_Education_University',
    'Chronic_Illness_Yes'
]

# MySQL connection details
config = {
    'user': 'root',                # MySQL username
    'password': 'Elyse@2050',       # MySQL password
    'host': 'localhost',           # MySQL host (usually localhost)
    'database': 'student_performance_db',  # Your database name
    'raise_on_warnings': True
}

# Function to insert data into MySQL
def insert_prediction_data(prediction_data, prediction_result):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # SQL query to insert data
        insert_query = """
        INSERT INTO student_data (
            Age, Year_of_Study, Attendance, Assignment_Score, Midterm_Score, Final_Score,
            Tuition_Paid, Outstanding_Balance, Books_Borrowed, Library_Visits, Days_Absent, 
            Gender_Male, Department_Computer_Science, Department_Electrical_Engineering,
            Performance_Pass, Parents_Education_Primary, Parents_Education_University, 
            Chronic_Illness_Yes
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # Append the prediction result to the data (1 for Pass, 0 for Fail)
        prediction_data.append(prediction_result)
        
        cursor.execute(insert_query, tuple(prediction_data))
        connection.commit()  # Commit the transaction
        st.success("Data Warehouse is being updated automatically!")
    except Error as e:
        st.error(f"Error during database insertion: {e}")
    finally:
        connection.close()

# Streamlit UI
st.set_page_config(page_title="Student Performance Dashboard", layout="centered")

st.markdown("<h1 style='color: teal;'>📊 Student Performance Prediction</h1>", unsafe_allow_html=True)
st.write("Enter student details to predict performance.")

# Sidebar input form
with st.sidebar:
    st.markdown("<h2 style='color: orange;'>Input Student Details 📝</h2>", unsafe_allow_html=True)
    input_data = {}

    input_data["Age"] = st.number_input("Age", min_value=15, max_value=30, value=20)
    input_data["Year_of_Study"] = st.selectbox("Year of Study", [1, 2, 3, 4])
    input_data["Attendance"] = st.slider("Attendance (%)", 0, 100, 75)
    input_data["Assignment_Score"] = st.slider("Assignment Score", 0, 100, 70)
    input_data["Midterm_Score"] = st.slider("Midterm Score", 0, 100, 50)
    input_data["Final_Score"] = st.slider("Final Score", 0, 100, 50)
    input_data["Tuition_Paid"] = 1 if st.radio("Tuition Paid?", ["Yes", "No"], key="tuition") == "Yes" else 0
    input_data["Outstanding_Balance"] = st.number_input("Outstanding Balance (RWF)", min_value=0, max_value=500000, value=0)
    input_data["Books_Borrowed"] = st.number_input("Books Borrowed", min_value=0, max_value=20, value=5)
    input_data["Library_Visits"] = st.number_input("Library Visits per Semester", min_value=0, max_value=50, value=10)
    input_data["Days_Absent"] = st.number_input("Days Absent", min_value=0, max_value=30, value=2)
    input_data["Gender_Male"] = 1 if st.radio("Gender", ["Male", "Female"], key="gender") == "Male" else 0
    
    department = st.radio("Department", ["Computer Science", "Electrical Engineering"], key="department_radio")
    input_data["Department_Computer Science"] = 1 if department == "Computer Science" else 0
    input_data["Department_Electrical Engineering"] = 1 if department == "Electrical Engineering" else 0

    parents_education = st.radio("Parents' Education Level", ["Primary", "University"], key="parents_education")
    input_data["Parents_Education_Primary"] = 1 if parents_education == "Primary" else 0
    input_data["Parents_Education_University"] = 1 if parents_education == "University" else 0

    input_data["Chronic_Illness_Yes"] = 1 if st.radio("Chronic Illness?", ["Yes", "No"], key="chronic_illness") == "Yes" else 0

# Convert input to DataFrame
input_df = pd.DataFrame([input_data])

# Ensure input_df matches training features
for col in trained_features:
    if col not in input_df:
        input_df[col] = 0  # Add missing features as 0

# Reorder columns to match training data
input_df = input_df[trained_features]

# Make prediction
if st.button("Predict Performance"):
    try:
        prediction = model.predict(input_df)[0]
        prediction_result = int(prediction)  # Convert to int (0 or 1)
        
        performance_label = "Pass ✅" if prediction_result == 1 else "Fail ❌"
        st.success(f"Prediction: {performance_label}")

        # Insert data into the database after prediction
        insert_prediction_data(list(input_data.values()), prediction_result)

    except Exception as e:
        st.error(f"Error during prediction: {e}")

# Display visualizations for training and awareness
def visualize_performance():
    st.subheader("Student Performance Overview 📊")
    
    # Example: Displaying a mock score distribution visualization
    # (In a real scenario, use actual data)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot([70, 85, 65, 55, 90, 78, 92, 66], kde=True, color='blue', ax=ax)  # Example data
    ax.set_title("Distribution of Final Scores")
    ax.set_xlabel("Final Score")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    # Example: Displaying pass/fail count
    st.subheader("Pass/Fail Overview 📊")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x=[1, 0, 1, 0, 1], ax=ax, palette="Set1")  # Example pass/fail data
    ax.set_title("Pass/Fail Distribution")
    ax.set_xlabel("Prediction (1 = Pass, 0 = Fail)")
    ax.set_ylabel("Count")
    st.pyplot(fig)

visualize_performance()

