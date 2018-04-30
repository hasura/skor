from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/", methods=["POST"])
def notification_handler():
    print(request.json)
    with open("/tmp/serverlog", "a") as f:        
        f.write(json.dumps(request.json)+"\n")
        f.flush()
    return 'Received'
    
    

if __name__ == "__main__":
    app.debug = False
    app.run(host="0.0.0.0")