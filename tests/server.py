from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=["POST"])
def notification_handler():
    print (request.json)
    return 'Received'

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
