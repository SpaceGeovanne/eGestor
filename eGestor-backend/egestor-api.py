from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas

DATA_FILE = 'data.json'

def read_data():
    """Lê os dados do arquivo JSON."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def write_data(data):
    """Escreve os dados no arquivo JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/v1/students', methods=['GET'])
def get_students():
    """Retorna a lista de todos os alunos."""
    students = read_data()
    return jsonify(students)

@app.route('/v1/students/<string:student_id>', methods=['GET'])
def get_student_by_id(student_id):
    """Retorna um aluno específico pelo ID."""
    students = read_data()
    student = next((s for s in students if s['_id'] == student_id), None)
    if student:
        return jsonify(student)
    return jsonify({"message": "Aluno não encontrado"}), 404

@app.route('/v1/students', methods=['POST'])
def add_student():
    """Adiciona um novo aluno."""
    new_student = request.json
    students = read_data()

    # Gerar um ID único para o novo aluno
    new_student['_id'] = str(uuid.uuid4())
    new_student['createdAt'] = datetime.utcnow().isoformat() + 'Z'
    new_student['updatedAt'] = datetime.utcnow().isoformat() + 'Z'
    new_student['status'] = new_student.get('status', 'active') # Define status padrão se não fornecido

    students.append(new_student)
    write_data(students)
    return jsonify(new_student), 201

@app.route('/v1/students/<string:student_id>', methods=['PUT'])
def update_student(student_id):
    """Atualiza um aluno existente pelo ID."""
    updated_data = request.json
    students = read_data()
    
    for i, student in enumerate(students):
        if student['_id'] == student_id:
            # Atualiza apenas os campos fornecidos, mantendo os existentes
            student.update(updated_data)
            student['updatedAt'] = datetime.utcnow().isoformat() + 'Z'
            write_data(students)
            return jsonify(student)
    return jsonify({"message": "Aluno não encontrado"}), 404

@app.route('/v1/students/<string:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Deleta um aluno pelo ID."""
    students = read_data()
    initial_len = len(students)
    students = [s for s in students if s['_id'] != student_id]
    
    if len(students) < initial_len:
        write_data(students)
        return jsonify({"message": "Aluno excluído com sucesso"}), 200
    return jsonify({"message": "Aluno não encontrado"}), 404

@app.route('/v1/students/search', methods=['GET'])
def search_students():
    """Busca alunos por nome ou matrícula."""
    query = request.args.get('q', '').lower()
    students = read_data()
    
    if not query:
        return jsonify(students) # Retorna todos se a query estiver vazia

    filtered_students = [
        s for s in students 
        if query in s['name'].lower() or query in s['registration'].lower()
    ]
    return jsonify(filtered_students)

@app.route('/v1/classrooms', methods=['GET'])
def get_classrooms():
    """Retorna uma lista de turmas disponíveis."""
    return jsonify(["Ciência da Computação", "Engenharia de Computação", "Engenharia de Software", "Análise e Desenvolvimento de Sistemas"])

@app.route('/v1/subjects', methods=['GET'])
def get_subjects():
    """Retorna uma lista de disciplinas disponíveis."""
    return jsonify(["Algoritmos e Estruturas de Dados", "Banco de Dados", "Calculo I", "Engenharia de Software", "Redes de Computadores"])

if __name__ == '__main__':
    # Cria o arquivo data.json se não existir
    if not os.path.exists(DATA_FILE):
        write_data([])
    app.run(debug=True, port=5000)

