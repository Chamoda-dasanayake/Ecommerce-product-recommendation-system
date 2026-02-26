from flask import Flask, request, jsonify
from model import recommend_products
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow requests from React frontend

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    user_id = data.get("user_id")

    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400

    recs = recommend_products(user_id)
    if not recs:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"recommendations": recs})


if __name__ == "__main__":
    app.run(debug=True)