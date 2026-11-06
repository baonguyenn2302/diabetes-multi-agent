from rl.threshold_qlearning import reward

IN = {"scope": "in_scope", "must": [["khát"], ["mệt"]]}
OUT = {"scope": "out_of_scope"}


def hit(distance, text):
    return {"distance": distance, "document": text}


def test_in_scope_full_coverage():
    hits = [hit(0.2, "khát nhiều"), hit(0.3, "mệt mỏi")]
    assert reward(IN, hits, 0.5) == 1.0


def test_in_scope_partial_coverage():
    hits = [hit(0.2, "khát nhiều")]
    assert reward(IN, hits, 0.5) == 0.5


def test_in_scope_no_source_is_penalized():
    assert reward(IN, [hit(0.9, "khát")], 0.5) == -1.0


def test_out_of_scope_no_source_is_rewarded():
    assert reward(OUT, [hit(0.9, "x")], 0.5) == 1.0


def test_out_of_scope_with_source_is_penalized():
    assert reward(OUT, [hit(0.2, "x")], 0.5) == -1.0