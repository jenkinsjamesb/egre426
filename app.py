'''
app.py

BRISC GUI code

James Jenkins 2025
'''

# Flask imports
from flask import Flask, request, redirect, render_template

# Other imports
from bitarray import bitarray
from bitarray.util import ba2int
from brisc_logging import init_log, log
from common import int_to_bits, insert_every
from simulator import processor # simulator
from assembler import assemble, format_program_text # assembler

app = Flask(__name__)
init_log("log/app.log")

ctx = {
        "assembly_error": "",
        "program_text": "",
        "binary_string": "",

        "formatted_text": "",
        "formatted_binary": "",

        "processor": None,
}

@app.context_processor
def inject_context():
    return dict(ctx=ctx) # pass ctx pieces to html

@app.route("/", methods=["GET", "POST"])
def route_root():
        return redirect("/edit")

@app.route("/edit", methods=["GET", "POST"]) 
def route_edit():
        if request.method == "POST":
                ctx["program_text"] = request.form["program_text"] # saves program to context for repeated assemblies
 
                # Attempt assembly on program text
                try:
                        ctx["binary_string"] = assemble(ctx["program_text"]) # assemble
                        return redirect("/run") # Go to run page

                # if bad, set error value and reload route
                except Exception as err:
                        ctx["assembly_error"] = err

        return render_template("edit.html")

@app.route("/run", methods=["GET", "POST"]) 
def route_run():

        # Reset processor and text memory on GET (initial load from /edit or reset)
        if request.method == "GET":
                ctx["processor"] = processor() # initialize processor
                text_mem = bitarray(256 * 8)
                text_mem[0:len(ctx["binary_string"])] = bitarray(ctx["binary_string"])

                ctx["processor"].text_memory = text_mem
        
        # On POST, step or step repeatedly
        if request.method == "POST":
                print(processor)
                if "continue_run" in request.form:
                        ctx["processor"].start()
                else:
                        ctx["processor"].step()

        # Format program text and binary for display. This is horrifically inefficient and should instead be assigning the class to the appropriate instruction
        formatted_text = format_program_text(ctx["program_text"])

        # Clear formatted buffers. Needs to be done every reload.
        ctx["formatted_text"] = ""
        ctx["formatted_binary"] = ""

        # Loop over program lines
        for index, line in enumerate(formatted_text.strip().split("\n")):
                # Check if PC matches instruction index and add highlight class if so
                highlight_class = " class=\"highlight\"" if ba2int(ctx["processor"].pc) / 2 == index else ""
                ctx["formatted_text"] += f"<span{highlight_class}>{line}</span>" # format instruction as span

                # Extract binary instruction, convert to hex, and pretty print
                instruction = ctx["binary_string"][index * 16:index * 16 + 16] 
                hex_string = format(int(instruction, 2), f"04x")
                binary_line = f"0x{hex_string}: {insert_every(instruction, " ", 4)}\n"

                ctx["formatted_binary"] += f"<span{highlight_class}>{binary_line}</span>"

        # Format registers and memory for display. This does need to be done per-cycle unlike the above
        
        
        return render_template("run.html")

def main():
        app.run(host="0.0.0.0", debug=True)

if __name__ == "__main__":
        main()
