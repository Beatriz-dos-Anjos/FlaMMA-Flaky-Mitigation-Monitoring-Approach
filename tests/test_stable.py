def test_upper():
    assert "hello".upper() == "HELLO"

def test_split():
    assert "a,b,c".split(",") == ["a", "b", "c"]

def test_join():
    assert "-".join(["a", "b", "c"]) == "a-b-c"
