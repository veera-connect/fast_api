from fastapi import FastAPI

app = FastAPI()

students = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "David"}
]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student API"}

# GET - Read all students
@app.get("/students")
def get_students():
    return students


# GET - Read one student
@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    return {"message": "Student not found"}


# POST - Create student
@app.post("/students")
def add_student(name: str):
    student = {
        "id": len(students) + 1,
        "name": name
    }

    students.append(student)

    return student


# PUT - Update student
@app.put("/students/{student_id}")
def update_student(student_id: int, name: str):
    for student in students:
        if student["id"] == student_id:
            student["name"] = name
            return student

    return {"message": "Student not found"}


# DELETE - Delete student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            students.remove(student)
            return {"message": "Student deleted"}

    return {"message": "Student not found"}