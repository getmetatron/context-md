import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "harness"))
from templates_p2 import consultation, STRICT_READ_RE, DEEP_READ_RE

T = lambda *cmds: [{"turn": i, "cmd": c} for i, c in enumerate(cmds)]

def test_cat_context_is_deep_read():
    r = consultation(T("cat context.md", "cat context/decisions/topic-a.md", "sed -i s/a/b/ x.py"))
    assert r == {"consulted": True, "first_read_turn": 0, "deep_read": True,
                 "deep_read_turn": 0, "read_before_edit": True}

def test_ls_is_consult_but_not_deep():
    r = consultation(T("ls context/decisions/", "grep -r foo src/"))
    assert r["consulted"] and not r["deep_read"]

def test_code_comment_is_not_a_read():
    # the FINDINGS-06 false positive: 'context/' inside a python heredoc comment
    r = consultation(T("python3 - <<'EOF'\n# we lack the full context/imports here\nEOF"))
    assert not r["consulted"]

def test_read_after_edit_flagged():
    r = consultation(T("sed -i s/a/b/ x.py", "cat context.md"))
    assert r["consulted"] and not r["read_before_edit"]

def test_grep_decisions_counts_as_consult():
    assert consultation(T("grep -rn autodoc context/decisions/"))["consulted"]

def test_no_context_commands():
    r = consultation(T("ls -F", "cat src/module.py", "submit"))
    assert r == {"consulted": False, "first_read_turn": None, "deep_read": False,
                 "deep_read_turn": None, "read_before_edit": False}
