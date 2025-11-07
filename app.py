'''
app.py

BRISC GUI code

James Jenkins 2025
'''

# Flask imports
from flask import Flask, request, redirect, render_template

# Other imports
from bitarray import bitarray
from simulator import processor # simulator
from assembler import assemble # assembler

app = Flask(__name__)

ctx = {
        "assembly_error": "",
        "program_text": "",
        "binary_string": "",

        "formatted_text": "",
        "formatted_binary": "",
        "instruction": 0, 
        
        "registers": "",
        "memory": "",
        
}

@app.context_processor
def inject_context():
    return dict(program_text=ctx["program_text"])

@app.route("/", methods=["GET", "POST"])
def route_root():
        return redirect("/edit")

@app.route("/edit", methods=["GET", "POST"]) 
def route_edit():
        if request.method == "POST":
                ctx["program_text"] = request.form["program_text"] # saves program to context for repeated assemblies
                print(ctx["program_text"])
                # attempt assemble
                # if ok, pass to run page
                # if bad, set error value and reload route

        return render_template("edit.html")

@app.route("/run", methods=["GET", "POST"]) 
def route_run():

        # Assemble to binary FIXME move to edit route on post
        binary_string = assembler.assemble(ctx["program_text"])

        # Create processor instance
        proc = processor()

        # Load binary to program memory
        text_mem = bitarray(256 * 8)
        text_mem[0:] = bitarray(binary_string)

        proc.text_memory = text_mem

        # Start simulator
        proc.start()

        return render_template("run.html")

def main():
        app.run(host="0.0.0.0", debug=True)

if __name__ == "__main__":
        main()
