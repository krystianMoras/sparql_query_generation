from flask import Flask, request, jsonify
from simple_question_answer import answer_simple_direct_question

app = Flask(__name__)

@app.route('/answer_question', methods=['GET'])
def answer_question():
    question = request.args.get('question')
    entity_id = request.args.get('entity_id')
    entity_label = request.args.get('entity_label')
    return answer_simple_direct_question(question, entity_id, entity_label), 200

if __name__ == '__main__':
    app.run(debug=True)