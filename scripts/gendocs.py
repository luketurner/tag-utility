from sys import argv
from ast import parse, iter_child_nodes, get_docstring, FunctionDef, unparse
import subprocess
import re

# Setup variables
README_PATH = "README.md"
MODULE_PATH = "tag/__init__.py"

def module_ast(filename):
  with open(filename) as f:
    source = f.read()
  return parse(source, filename)
  

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
    yield f"#### **{desc['name']}**({unparse(desc['args'])})\n\n{desc['docstring']}\n"


def module_markdown(filename):
  ast = module_ast(filename)
  api_descriptions = describe_nodes(iter_child_nodes(ast))
  return "\n".join(markdownify(api_descriptions))

def tag_help():
  # TODO -- get helptext with import instead of subprocess
  tag_run = subprocess.run(["tag", "--help"], capture_output=True)
  return str(tag_run.stdout, encoding="utf8").replace("\\r\\n", "\n")


def block_regex(block_name):
  return re.compile(r"(?<=<\!-- " + block_name + r" start -->\n).*(?=\n<\!-- " + block_name + r" end -->)", re.DOTALL)

def update_readme():
  with open(README_PATH, "r") as f:
    content = f.read()
  with open(README_PATH, "wb") as f:
    content = content.replace("\\r\\n", "\n")
    content = re.sub(block_regex("gendocs cli help"), "```\n" + tag_help() + "```", content)
    content = re.sub(block_regex("gendocs api"), module_markdown(MODULE_PATH), content)
    print("content")
    print(content)
    f.write(bytes(content, encoding="utf8"))


update_readme()
print("done")
