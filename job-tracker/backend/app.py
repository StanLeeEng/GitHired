from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route("/api/jobs")
def get_jobs():
    return jsonify([
        {"company": "Google", "role": "SWE", "location": "NYC"}
    ])

if __name__ == "__main__":
    app.run(debug=True)