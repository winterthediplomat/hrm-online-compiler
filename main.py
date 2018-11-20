import io
from flask import Flask, request, jsonify
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


@app.route("/build", methods=["POST"])
@cross_origin()
def build():
    # data = request.get_data().decode("utf-8")
    data = request.get_json(force=True)
    # print("/build", data)
    args = CompilerArgs(False, False, False)
    ast = calculate_optimized_ast(io.StringIO(data["code"]), args)
    a = Assembler()
    a.convert(ast)
    # print("converted: ", a.code)
    return jsonify({"code": a.code})
