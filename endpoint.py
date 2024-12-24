from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# MySQL database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Madhu@29',
            database='StudentDB'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Function to format date for SQL (YYYY-MM-DD)
def format_date(date_obj):
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Expected 'YYYY-MM-DD'")
    elif not isinstance(date_obj, datetime):
        raise TypeError("Date should be a datetime object or a string in 'YYYY-MM-DD' format")
    
    return date_obj.strftime('%Y-%m-%d')

# Route to add a new student (POST)
@app.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json()

        # Format date fields
        data['DOB'] = format_date(data['DOB'])
        data['DateOfJoining'] = format_date(data['DateOfJoining'])
        data['DateOfRecordCreation'] = format_date(data['DateOfRecordCreation'])

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO StudentsMaster (UniqueStudentRegNo, StudentName, Gender, DOB, FatherName, 
                   MotherName, FathersOccupation, FathersIncome, BloodGroup, Address, City, State, 
                   DateOfJoining, DateOfRecordCreation) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['UniqueStudentRegNo'], data['StudentName'], data['Gender'], data['DOB'], data['FatherName'],
            data['MotherName'], data['FathersOccupation'], data['FathersIncome'], data['BloodGroup'], 
            data['Address'], data['City'], data['State'], data['DateOfJoining'], data['DateOfRecordCreation']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Student added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to get all students (GET)
@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM StudentsMaster")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get a student by registration number (GET)
@app.route('/students/<string:reg_no>', methods=['GET'])
def get_student_by_reg_no(reg_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM StudentsMaster WHERE UniqueStudentRegNo = %s", (reg_no,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        if student:
            return jsonify(student)
        return jsonify({"message": "Student not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update student information (PUT)
@app.route('/students/<string:reg_no>', methods=['PUT'])
def update_student(reg_no):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        UPDATE StudentsMaster SET StudentName = %s, Gender = %s, DOB = %s, FatherName = %s, 
                   MotherName = %s, FathersOccupation = %s, FathersIncome = %s, BloodGroup = %s, 
                   Address = %s, City = %s, State = %s, DateOfJoining = %s, DateOfRecordCreation = %s
        WHERE UniqueStudentRegNo = %s
        """
        cursor.execute(query, (
            data['StudentName'], data['Gender'], data['DOB'], data['FatherName'], data['MotherName'],
            data['FathersOccupation'], data['FathersIncome'], data['BloodGroup'], data['Address'], data['City'],
            data['State'], data['DateOfJoining'], data['DateOfRecordCreation'], reg_no
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Student updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to delete a student (DELETE)
@app.route('/students/<string:reg_no>', methods=['DELETE'])
def delete_student(reg_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM StudentsMaster WHERE UniqueStudentRegNo = %s", (reg_no,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Student deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/students/admitted_in_2024', methods=['GET'])
def get_students_admitted_in_2024():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM StudentsMaster WHERE YEAR(DateOfJoining) = 2024")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/students/above_grade_b_term2', methods=['GET'])
def get_students_above_grade_b_term2():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        SELECT * FROM StudentsMaster sm
        JOIN StudentsMarks smk ON sm.UniqueStudentRegNo = smk.UniqueStudentRegNo
        WHERE smk.TestTerm = 1 AND smk.Grade > 'B'
        """)
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500        

if __name__ == '__main__':
    app.run(debug=True)
