from flask import Flask, request, jsonify
import subprocess
import os
import uuid
import json
import io
from flask_cors import cross_origin
from hrmcompiler.jsonassembler import Assembler
from hrmcompiler import calculate_optimized_ast
from collections import namedtuple
app = Flask(__name__)

CompilerArgs = namedtuple("CompilerArgs", [
    "no_jump_compression",
    "no_unreachable",
    "no_jmp_then_label",
])

COMPILER_PATH = "/home/winter/projects/hrm-compiler"
INTERPRETER_PATH = "/home/winter/projects/hrm-interpreter"
RELATIVE_INTERPRETER_EXE_PATH = "./target/debug/hrm_interpreter"
# RELATIVE_INTERPRETER_EXE_PATH = "./target/release/hrm_interpreter"

def run_compiler(src_path):
    move_to(COMPILER_PATH)
    options = ["hrmc", src_path]
    print("[run_compiler] running", " ".join(options))
    subprocess.check_call(options, stdout=subprocess.DEVNULL)

def run_interpreter(target_json_path, input_path, dump_path):
    # move_to(INTERPRETER_PATH)
    full_exe_path = os.path.join(INTERPRETER_PATH, RELATIVE_INTERPRETER_EXE_PATH)
    options = [full_exe_path,
               "--code", target_json_path,
               "--input", input_path,
               "--dump", dump_path]
    execution = subprocess.run(options, capture_output=True)
    print("[run_interpreter]", execution)
    return execution.stdout

@app.route("/")
def hello():
    code = os.path.join(COMPILER_PATH, "./examples/script_13.json")
    input = os.path.join(COMPILER_PATH, "./inputs/script_13.json")
    return run_interpreter(code, input)

@app.route("/build", methods=["POST"])
@cross_origin()
def build():
    # data = request.get_data().decode("utf-8")
    data = request.get_json(force=True)
    # data = request.form
    print("/build", data)
    args = CompilerArgs(False, False, False)
    ast = calculate_optimized_ast(io.StringIO(data["code"]), args)
    a = Assembler()
    a.convert(ast)
    print("converted: ", a.code)
    return jsonify({"code": a.code})

@app.route("/run", methods=["POST"])
@cross_origin()
def run():
    try:
        code = request.get_json(force=True)
        print("/run", type(code), code)
    except Exception as e:
        code = {
            "code": [],
            "input": []
        }
        print("/run - could not parse the request body", e)

    code_id = uuid.uuid4()
    input_id = uuid.uuid4()
    dump_id = uuid.uuid4()
    with open("/tmp/hrm-code-"+str(code_id), "w") as dst:
        json.dump(code["code"], dst)
    with open("/tmp/hrm-input-"+str(input_id), "w") as dst:
        json.dump(code["input"], dst)

    result_as_bytes = run_interpreter("/tmp/hrm-code-"+str(code_id), "/tmp/hrm-input-"+str(input_id), "/tmp/hrm-dump-"+str(dump_id))
    result_as_utf8 = result_as_bytes.decode("utf-8")

    states = []
    with open("/tmp/hrm-dump-"+str(dump_id)) as dumpfile: 
        for line in dumpfile:
            try:
                print(">>>", line.strip())
                states.append(json.loads(line.strip()))
            except json.decoder.JSONDecodeError:
                pass

    return jsonify({"states": states})
