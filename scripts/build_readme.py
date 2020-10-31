from sys import argv
from ast import parse, iter_child_nodes, get_docstring, FunctionDef, get_source_segment

filename = argv[1]

with open(filename) as f:
  source = f.read()

def describe_function(node):
    return {
      "name": node.name,
      "args": node.args, 
      "returns": node.returns,
      "docstring": get_docstring(node)
    }

def describe_nodes(nodes):
  for node in nodes:
    if isinstance(node, FunctionDef):
      yield describe_function(node)

def markdownify(descriptions):
  for desc in descriptions:
    yield f"- **{desc['name']}**({get_source_segment(source, desc['args'])})\n{desc['docstring']}"

ast = parse(source, filename)
api_descriptions = describe_nodes(iter_child_nodes(ast))
api_md = "\n".join(markdownify(api_descriptions))
print(api_md)
