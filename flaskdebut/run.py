from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    username = request.form['username']
    password = request.form['password']
    if username == "jxz" and password == "jxz":
        return f"<html><body>Welcome {username}</body></html>"
    else:
        return f"<html><body>Welcome!</body></html>"


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)