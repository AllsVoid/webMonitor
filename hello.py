from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/print', methods=['POST'])
def print_message():
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({'message': message})

@app.route('/click', methods=['POST'])
def handle_click():
    print("user clicked")
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)