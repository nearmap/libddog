from libtests.matchers import dict_matcher


def test_single_top_level_key() -> None:
    fst = {"id": 123, "name": "James"}
    snd = {"id": 123, "name": "Bill"}

    assert fst == dict_matcher(snd, name="James")


def test_single_top_level_key__contains_dash__using_args() -> None:
    fst = {"id": 123, "first-name": "James"}
    snd = {"id": 123, "first-name": "Bill"}

    assert fst == dict_matcher(snd, {"first-name": "James"})


def test_single_top_level_key__contains_dash__using_kwargs() -> None:
    fst = {"id": 123, "first-name": "James"}
    snd = {"id": 123, "first-name": "Bill"}

    assert fst == dict_matcher(snd, **{"first-name": "James"})


def test_two_top_level_keys() -> None:
    fst = {"id": 123, "name": "James"}
    snd = {"id": 456, "name": "Bill"}

    assert fst == dict_matcher(snd, id=123, name="James")


def test_nested_key() -> None:
    fst = {"level": 2, "person": {"id": 123, "name": "James"}}
    snd = {"level": 2, "person": {"id": 123, "name": "Bill"}}

    assert fst == dict_matcher(snd, {"person.name": "James"})
