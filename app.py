from flask import Flask, jsonify
from routes.user_routes import user_routes
from routes.subscription_routes import subscription_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(user_routes, url_prefix='/users')
app.register_blueprint(subscription_routes, url_prefix='/subscriptions')

# Test endpoint at root URL
@app.route('/', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Hello, World!"})


if __name__ == '__main__':
    app.run(debug=True, port=5001)