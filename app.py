'''
app.py

BRISC GUI code

James Jenkins 2025
'''

# Flask imports
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"]) 
def root():
        if request.method == "POST":
                print(request.form["program_text"])


        return open("html/index.html", "r").read()


def main():
        app.run(host="0.0.0.0", debug=True)

if __name__ == "__main__":
        main()
