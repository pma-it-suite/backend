from flask import Flask, jsonify
from routes.user_routes import user_routes
from routes.subscription_routes import subscription_routes
from routes.commands_routes import commands_routes
from flask_cors import CORS
from config.main import SERVER_HOST, SERVER_PORT
import logging
import argparse

logging.basicConfig(filename='logs.txt',
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)
CORS(app,
     resources={
         r"/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": "*"
         }
     })

app.register_blueprint(user_routes, url_prefix='/users')
app.register_blueprint(subscription_routes, url_prefix='/subscriptions')
app.register_blueprint(commands_routes, url_prefix='/commands')


# Test endpoint at root URL
@app.route('/', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Hello, FELIPE!"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the app in debug or production mode.')
    parser.add_argument('--debug', type=bool, default=False, help='Run in debug mode.')
    args = parser.parse_args()

    SERVER_HOST = 'localhost' if args.debug else '0.0.0.0'
    SERVER_PORT = 8080 if args.debug else '8080'
    
    if args.debug:
        app.run(debug=True, host=SERVER_HOST, port=SERVER_PORT)
    else:
        file_base = "/var/lib/caddy/.local/share/caddy/certificates/acme-v02.api.letsencrypt.org-directory/its.kdns.ooo/its.kdns.ooo"
        cert = file_base + ".crt"
        key = file_base + ".key"
        context = (cert, key)
        app.run(debug=False, host=SERVER_HOST, port=SERVER_PORT, ssl_context=context)

