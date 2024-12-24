import streamlit as st
import pandas as pd
import requests
import cohere
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit import components

# Cohere API setup for the AI Assistant functionality
cohere_api_key = 'gEVvUkArxJxDkXxwZnRCAVEWWZSkOMygCXSu0xdX'  # Replace with your actual Cohere API Key
co = cohere.Client(cohere_api_key)

# Paths to your CSV files
studentsmaster_file = r"C:\Users\Admin\Downloads\studentsmaster.csv"
studentsmarks_file = r"C:\Users\Admin\Downloads\studentsmarks.csv"

# Load the CSV files into pandas DataFrames
def load_students_data():
    """Load the students master and marks data from CSV files."""
    studentsmaster_df = pd.read_csv(studentsmaster_file)
    studentsmarks_df = pd.read_csv(studentsmarks_file)
    return studentsmaster_df, studentsmarks_df

# Ensure that dates are parsed correctly into datetime objects
def format_date(date_obj):
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%a, %d %b %Y %H:%M:%S GMT')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return None
    elif isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d')
    return None

# Function to generate context for AI Assistant
def generate_context_from_data(studentsmaster_df, studentsmarks_df):
    # Merge student details and marks data
    merged_df = pd.merge(studentsmaster_df, studentsmarks_df, on='UniqueStudentRegNo', how='left')
    
    # Calculate Total and Average Marks
    subject_columns = ['Tamil', 'English', 'Maths', 'Science', 'SocialScience']
    merged_df['Total'] = merged_df[subject_columns].sum(axis=1)
    merged_df['Average'] = merged_df[subject_columns].mean(axis=1)
    
    # Add a Grade based on Average Marks
    def calculate_grade(avg_marks):
        if avg_marks >= 90:
            return 'A+'
        elif avg_marks >= 80:
            return 'A'
        elif avg_marks >= 70:
            return 'B+'
        elif avg_marks >= 60:
            return 'B'
        elif avg_marks >= 50:
            return 'C+'
        elif avg_marks >= 40:
            return 'C'
        else:
            return 'F'

    merged_df['Grade'] = merged_df['Average'].apply(calculate_grade)

    # Generate the context for AI Assistant
    context = ""
    for index, row in merged_df.iterrows():
        context += f"Student Name: {row['StudentName']}, Gender: {row['Gender']}, " \
                   f"Father's Income: {row['FathersIncome']}, Address: {row['Address']}, " \
                   f"Total Marks: {row['Total']}, Average Marks: {row['Average']}, " \
                   f"Grade: {row['Grade']}\n"
    
    return context

# Function to ask a question to Cohere API
def ask_question_to_cohere(question, context):
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    response = co.generate(
        prompt=prompt,
        max_tokens=1000,
        temperature=0.7,
    )
    answer = response.generations[0].text.strip()
    return answer

# Flask API URL for student CRUD operations
API_URL = 'http://127.0.0.1:5000/students'

# Streamlit UI for the Frontend
def main():
    st.set_page_config(page_title="Student Management System", layout="wide")
    st.sidebar.title("Student Management System")

    menu = ["Add Student", "View All Students", "Update Student", "Delete Student","Above B Grade Term 2" ,"Students Admitted in 2024","AI Assistant", "Dashboard" ]
    choice = st.sidebar.selectbox("Select Operation", menu)

    # Header for the page
    st.title("Student Management System")
    
    if choice == "Add Student":
        st.subheader("Add New Student")
        with st.form(key="add_student_form"):
            unique_reg_no = st.text_input("Registration No.")
            name = st.text_input("Name")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.date_input("Date of Birth")
            father_name = st.text_input("Father's Name")
            mother_name = st.text_input("Mother's Name")
            fathers_occupation = st.text_input("Father's Occupation")
            fathers_income = st.number_input("Father's Income", min_value=0)
            blood_group = st.selectbox("Blood Group", ["A", "B", "O", "AB"])
            address = st.text_area("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            date_of_joining = st.date_input("Date of Joining")
            date_of_record_creation = st.date_input("Date of Record Creation")
            submit_button = st.form_submit_button("Add Student")

        if submit_button:
            student_data = {
                "UniqueStudentRegNo": unique_reg_no,
                "StudentName": name,
                "Gender": gender,
                "DOB": dob.strftime('%Y-%m-%d'),
                "FatherName": father_name,
                "MotherName": mother_name,
                "FathersOccupation": fathers_occupation,
                "FathersIncome": fathers_income,
                "BloodGroup": blood_group,
                "Address": address,
                "City": city,
                "State": state,
                "DateOfJoining": date_of_joining.strftime('%Y-%m-%d'),
                "DateOfRecordCreation": date_of_record_creation.strftime('%Y-%m-%d')
            }
            response = requests.post(API_URL, json=student_data)
            if response.status_code == 201:
                st.success("Student added successfully!")
            else:
                st.error(f"Error: {response.json()['error']}")

    elif choice == "View All Students":
        st.subheader("All Students")
        response = requests.get(API_URL)
        if response.status_code == 200:
            students = response.json()
            st.write(students)
        else:
            st.error(f"Error: {response.json()['error']}")

    elif choice == "Update Student":
        st.subheader("Update Student")
        reg_no = st.text_input("Enter Registration Number to Update")
        if reg_no:
            response = requests.get(f"{API_URL}/{reg_no}")
            if response.status_code == 200:
                student_data = response.json()
                new_name = st.text_input("Name", student_data["StudentName"])
                new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(student_data["Gender"]))
                new_fathers_occupation = st.text_input("Father's Occupation", student_data["FathersOccupation"])
                update_button = st.button("Update Student")

                if update_button:
                    updated_data = {
                        "StudentName": new_name,
                        "Gender": new_gender,
                        "FatherName": student_data["FatherName"],
                        "MotherName": student_data["MotherName"],
                        "FathersOccupation": new_fathers_occupation,
                        "FathersIncome": student_data["FathersIncome"],
                        "BloodGroup": student_data["BloodGroup"],
                        "Address": student_data["Address"],
                        "City": student_data["City"],
                        "State": student_data["State"],
                        "DOB": format_date(student_data["DOB"]),
                        "DateOfJoining": format_date(student_data["DateOfJoining"]),
                        "DateOfRecordCreation": format_date(student_data["DateOfRecordCreation"])
                    }

                    # Sending the updated data to the API
                    response = requests.put(f"{API_URL}/{reg_no}", json=updated_data)
                    if response.status_code == 200:
                        st.success("Student updated successfully!")
                    else:
                        st.error(f"Error: {response.json()['error']}")

    elif choice == "Delete Student":
        st.subheader("Delete Student")
        reg_no_to_delete = st.text_input("Enter Registration Number to Delete")
        if reg_no_to_delete:
            delete_button = st.button("Delete Student")
            if delete_button:
                response = requests.delete(f"{API_URL}/{reg_no_to_delete}")
                if response.status_code == 200:
                    st.success("Student deleted successfully!")
                else:
                    st.error(f"Error: {response.json()['error']}")

    elif choice == "Students Admitted in 2024":
        st.subheader("Students Admitted in 2024")
        response = requests.get(f"{API_URL}/admitted_in_2024")
        if response.status_code == 200:
            students = response.json()
            st.write(students)
        else:
            st.error(f"Error: {response.json()['error']}")

    elif choice == "Above B Grade Term 2":
        st.subheader("Students with Grades Above B in Term 2")
        response = requests.get(f"{API_URL}/above_grade_b_term2")
        if response.status_code == 200:
            students = response.json()
            st.write(students)
        else:
            st.error(f"Error: {response.json()['error']}")

    elif choice == "AI Assistant":
        st.subheader("AI Assistant")
        studentsmaster_df, studentsmarks_df = load_students_data()
        context = generate_context_from_data(studentsmaster_df, studentsmarks_df)
        question = st.text_input("Ask a question about students data:")
        if question:
            answer = ask_question_to_cohere(question, context)
            st.write(f"Answer: {answer}")

    elif choice == "Dashboard":
        studentsmaster_df, studentsmarks_df = load_students_data()

        # Admission statistics per year
        st.subheader("Admission Statistics per Year")
        if 'DateOfJoining' in studentsmaster_df.columns:
            studentsmaster_df['DateOfJoining'] = pd.to_datetime(studentsmaster_df['DateOfJoining'], errors='coerce')
            studentsmaster_df['YearOfAdmission'] = studentsmaster_df['DateOfJoining'].dt.year
            admission_counts = studentsmaster_df.groupby('YearOfAdmission').size()

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(admission_counts.index, admission_counts.values, marker='o', color='b', linewidth=2)
            ax.set_title('Admission Statistics per Year', fontsize=14, fontweight='bold')
            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.write("Column 'DateOfJoining' is missing.")

        # Gender Breakdown
        st.subheader("Gender Breakdown")
        if 'Gender' in studentsmaster_df.columns:
            gender_counts = studentsmaster_df['Gender'].value_counts()

            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
            ax.set_title('Gender Distribution', fontsize=14, fontweight='bold')
            st.pyplot(fig)
        else:
            st.write("Column 'Gender' is missing.")
        
        # Grade Distribution
        st.subheader("Grade Distribution")
        if 'Grade' in studentsmarks_df.columns:
            grade_counts = studentsmarks_df['Grade'].value_counts()

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(grade_counts.index, grade_counts.values, color='c')
            ax.set_title('Grade Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Grade', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
            ax.grid(True, axis='y')
            st.pyplot(fig)
        else:
            st.write("Column 'Grade' is missing.")
        
        # Marks Distribution by Subject
        st.subheader("Marks Distribution by Subject")
        if 'Tamil' in studentsmarks_df.columns:
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            subject_columns = ['Tamil', 'English', 'Maths', 'Science', 'SocialScience']
            axes = axes.flatten()

            for i, subject in enumerate(subject_columns):
                sns.histplot(studentsmarks_df[subject], kde=True, ax=axes[i], bins=15, color="skyblue")
                axes[i].set_title(f'{subject} Marks Distribution', fontsize=12, fontweight='bold')
                axes[i].set_xlabel('Marks', fontsize=10)
                axes[i].set_ylabel('Frequency', fontsize=10)

            st.pyplot(fig)
        else:
            st.write("Columns for subjects are missing.")
        
        # Father's Income Distribution
        st.subheader("Father's Income Distribution")
        if 'FathersIncome' in studentsmaster_df.columns:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(studentsmaster_df['FathersIncome'], kde=True, bins=20, color="green")
            ax.set_title("Father's Income Distribution", fontsize=14, fontweight='bold')
            ax.set_xlabel("Income", fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
            st.pyplot(fig)
        else:
            st.write("Column 'FathersIncome' is missing.")
        
        # Performance Trend Over Time (Average Marks per Year)
        st.subheader("Performance Trend Over Time")
        if 'YearOfAdmission' in studentsmaster_df.columns and 'Average' in studentsmarks_df.columns:
            students_df_with_avg = pd.merge(studentsmaster_df, studentsmarks_df[['UniqueStudentRegNo', 'Average']], on='UniqueStudentRegNo', how='left')
            students_df_with_avg = students_df_with_avg.dropna(subset=['YearOfAdmission', 'Average'])
            avg_performance = students_df_with_avg.groupby('YearOfAdmission')['Average'].mean()

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(avg_performance.index, avg_performance.values, marker='o', color='purple', linestyle='-', linewidth=2)
            ax.set_title('Performance Trend Over Time (Average Marks)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Year of Admission', fontsize=12, fontweight='bold')
            ax.set_ylabel('Average Marks', fontsize=12, fontweight='bold')
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.write("Columns 'YearOfAdmission' or 'Average' are missing.")

if __name__ == "__main__":
    main()
