"""This module defines utilities for working with a lightweight tag query language.

The language is a sequence of clauses separated by whitespace. Each clause is a key-value pair (but the value is optional).
Clauses may also be prefixed with a + or a -. So, the following are valid clauses::

  foo
  foo:bar
  _name:foo
  foo:"this clause includes whitespace"
  +foo:"Add clause"
  -bar:"Subtract clause"

Simplified EBNF notation::

   query = { clause }                     ;
  clause = [ prefix ] key [ delim value ] ;
     key = string | '"' quoted_string '"' ;
   value = string | '"' quoted_string '"' ;
  prefix = "+" | "-"                      ;
   delim = ":"                            ;

"""

import shlex

from .error import TagException

def parse_search_query(db, s, delim=":"):

    ast = emit_query_ast(s, delim)
    tags = {k: v for l, k, v in ast if l == "tag" or l == "tag_add"}
    tag_blacklist = {k: v for l, k, v in ast if l == "tag_sub"}
    names = [v for l, k, v in ast if l == "name"]
    mimes = [v for l, k, v in ast if l == "mime"]

    raise TagException("Not implemented")


def emit_query_ast(s, delim=":"):
    """Accepts a string s_ in the tag query format. Attempts to emit an AST for s_, and raises an exception if it can't. Returns the generated AST.

    The AST is a list of "op" tuples of form (op_name, op_key, op_value). For example::

        # from query string: "foo _name=bar hello=world"
        [
        ('tag', 'foo', None),
        ('name', None, 'bar'),
        ('tag', 'hello', 'world')
        ]

    The following op_names may be emitted: `tag`, `tag_add`, `tag_sub`, `name`, `mime`
    """
    return [c for c in (emit_term(c, delim) for c in shlex.split(s)) if c]


def emit_term(s, delim):
    left, right = s.split(delim, 1) if delim in s else (s, None)

    if not left:
        return None

    if left == "_name":
        return ("name", None, right)

    if left == "_mime":
        return ("mime", None, right)

    if left[0] == "_":
        raise TagException(
            "Cannot parse query string: unknown special clause {}.".format(left)
        )

    if left[0] == "+":
        return ("tag_add", left[1:], right)

    if left[0] == "-":
        return ("tag_sub", left[1:], right)

    return ("tag", left, right)
