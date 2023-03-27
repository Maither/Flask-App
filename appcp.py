from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def homepage():
    return "Home page"
    
@app.route("/get_json", methods=['POST'])
def get_post_temp():
    data = request.get_json()
    d = data['date']
    h = data['hour']
    m = data['min']
    s = data['sec']
    t = data['temp']
    data = [d, h, m, s, t]
    
    return jsonify('200')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
