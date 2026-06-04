from flask import Flask, render_template, request

app = Flask(__name__)
token_counter = 0

@app.route("/", methods=["GET", "POST"])
def home():
    global token_counter
    if request.method == "POST":
        name = request.form.get("name")
        token_counter += 1
        waiting = token_counter - 1
        return render_template("index.html", token=token_counter, waiting=waiting)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
