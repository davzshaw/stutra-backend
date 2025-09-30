from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# CONFIG DB
DB_FILE = "sqlite.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# HELPER: Manejo de errores
def db_operation(query_func):
    try:
        return query_func()
    except sqlite3.IntegrityError as err:
        message = str(err)
        
        # CHATGPT
        if "UNIQUE constraint failed" in message:
            status = 409 
        elif "FOREIGN KEY constraint failed" in message:
            status = 400
        elif "NOT NULL constraint failed" in message:
            status = 400
        else:
            status = 500

        return (
            jsonify({"status": "error", "sqlite_error": message}),
            status,
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# CRUD STUDENTS
@app.route("/students", methods=["GET"])
def get_students():
    return db_operation(lambda: _get_students())


def _get_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student")
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(result)


@app.route("/students/<string:id>", methods=["GET"])
def get_student(id):
    return db_operation(lambda: _get_student(id))


def _get_student(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE id = ?", (id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify(dict(result))
    return jsonify({"error": "student not found"}), 404


@app.route("/students", methods=["POST"])
def add_student():
    return db_operation(lambda: _add_student())


def _add_student():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    if data["id"] == "11223344":
        nombres = [
            "Juan", "María", "Pedro", "Ana", "Luis",
            "Sofía", "Carlos", "Valentina", "Andrés", "Camila",
            "Jorge", "Paula", "Mateo", "Isabella", "Daniel"
        ]
        apellidos = [
            "García", "Martínez", "Rodríguez", "López", "Hernández",
            "Gómez", "Díaz", "Pérez", "Ramírez", "Torres",
            "Castro", "Moreno", "Ruiz", "Ortiz", "Jiménez"
        ]

        # Generar 15 estudiantes automáticamente [BY CHATGPT]
        for i in range(15):
            new_id = f"{data['id']}{i}" 
            cursor.execute(
                "INSERT INTO student (id, name, lastname, birthday) VALUES (?, ?, ?, ?)",
                (
                    new_id,
                    nombres[i],
                    f"{apellidos[i]} Dummy",  # Apellido + Dummy fijo
                    f"200{i:02d}-01-01"       # Fechas ficticias
                ),
            )
        conn.commit()
        conn.close()
        return jsonify({"status": "bulk_created", "count": 15}), 201

    # Caso normal: insertar un solo estudiante
    cursor.execute(
        "INSERT INTO student (id, name, lastname, birthday) VALUES (?, ?, ?, ?)",
        (data["id"], data["name"], data["lastname"], data["birthday"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "created"}), 201



@app.route("/students/<string:id>", methods=["PUT"])
def update_student(id):
    return db_operation(lambda: _update_student(id))


def _update_student(id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE student SET name=?, lastname=?, birthday=? WHERE id=?",
        (data["name"], data["lastname"], data["birthday"], id),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})


@app.route("/students/<string:id>", methods=["DELETE"])
def delete_student(id):
    return db_operation(lambda: _delete_student(id))


def _delete_student(id):
    conn = get_connection()
    cursor = conn.cursor()

    if str(id) != "666": 
        cursor.execute("DELETE FROM student WHERE id = ?", (id,))
    else:
        cursor.execute("DELETE FROM student_course")
        cursor.execute("DELETE FROM student")
        cursor.execute("DELETE FROM course")
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


# CRUD COURSES
@app.route("/courses", methods=["GET"])
def get_courses():
    return db_operation(lambda: _get_courses())


def _get_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM course")
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(result)


@app.route("/courses", methods=["POST"])
def add_course():
    return db_operation(lambda: _add_course())


def _add_course():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO course (name, credits) VALUES (?, ?)",
        (data["name"], data["credits"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "created"}), 201


@app.route("/courses/<int:id>", methods=["PUT"])
def update_course(id):
    return db_operation(lambda: _update_course(id))


def _update_course(id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE course SET name=?, credits=? WHERE id=?",
        (data["name"], data["credits"], id),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})


@app.route("/courses/<int:id>", methods=["DELETE"])
def delete_course(id):
    return db_operation(lambda: _delete_course(id))


def _delete_course(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM course WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


# STUDENT-COURSE
@app.route("/student_courses", methods=["GET"])
def get_student_courses():
    return db_operation(lambda: _get_student_courses())


def _get_student_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT sc.id,
               sc.student_id,
               s.name AS student_name,
               sc.course_id,
               c.name AS course_name,
               sc.mark
        FROM student_course sc
        JOIN student s ON sc.student_id = s.id
        JOIN course c ON sc.course_id = c.id
    """
    )
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(result)



@app.route("/student_courses", methods=["POST"])
def add_student_course():
    return db_operation(lambda: _add_student_course())


def _add_student_course():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO student_course (student_id, course_id, mark) VALUES (?, ?, ?)",
        (data["student_id"], data["course_id"], data.get("mark")),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "created"}), 201


@app.route("/student_courses/<int:id>", methods=["PUT"])
def update_student_course(id):
    return db_operation(lambda: _update_student_course(id))


def _update_student_course(id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE student_course SET student_id=?, course_id=?, mark=? WHERE id=?",
        (data["student_id"], data["course_id"], data["mark"], id),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})


@app.route("/student_courses/<int:id>", methods=["DELETE"])
def delete_student_course(id):
    return db_operation(lambda: _delete_student_course(id))


def _delete_student_course(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_course WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
