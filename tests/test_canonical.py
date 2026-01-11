from tools.autopilot.lib.jsoncanon import CanonicalJsonOptions, dumps_canonical


def test_canonical_newline():
    s = dumps_canonical({"b": 1, "a": 2}, opt=CanonicalJsonOptions(sort_keys=True, compact=True, ensure_ascii=False, newline=True))
    assert s.endswith("\n")
    assert s.strip() == '{"a":2,"b":1}'
