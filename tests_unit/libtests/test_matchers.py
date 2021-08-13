from libtests.matchers import obj_matcher

# single level dict


def test__single_level_dict__noop() -> None:
    fst = {"id": 123, "first-name": "James", "last-name": "Joy"}
    snd = {"id": 123, "first-name": "James", "last-name": "Joy"}

    assert fst == obj_matcher(snd, {})


def test__single_level_dict__single_assignment() -> None:
    fst = {"id": 123, "first-name": "James", "last-name": "Joy"}
    snd = {"id": 123, "first-name": "Bill", "last-name": "Joy"}

    assert fst == obj_matcher(snd, {"= /first-name": "James"})


def test__single_level_dict__multiple_assignments() -> None:
    fst = {"id": 123, "first-name": "James", "last-name": "Joy"}
    snd = {"id": 456, "first-name": "Bill", "last-name": "Joy"}

    assert fst == obj_matcher(snd, {"= /id": 123, "= /first-name": "James"})


def test__single_level_dict__single_delete() -> None:
    fst = {"id": 123, "last-name": "Joy"}
    snd = {"id": 123, "first-name": "Bill", "last-name": "Joy"}

    assert fst == obj_matcher(snd, {"- /first-name": None})


def test__single_level_dict__assign_and_delete() -> None:
    fst = {"id": 123, "last-name": "Joy"}
    snd = {"id": 456, "first-name": "Bill", "last-name": "Joy"}

    assert fst == obj_matcher(snd, {"= /id": 123, "- /first-name": None})


# single level list


def test__single_level_list__noop() -> None:
    fst = [1, 2, 3]
    snd = [1, 2, 3]

    assert fst == obj_matcher(snd, {})


def test__single_level_list__single_delete() -> None:
    fst = [1, 3]
    snd = [1, 2, 3]

    assert fst == obj_matcher(snd, {"- /[1]": None})


def _test__single_level_list__multiple_deletions() -> None:
    fst = [2]
    snd = [1, 2, 3]

    assert fst == obj_matcher(snd, {"- /[2]": None, "- /[0]": None})

    # assert fst == dict_matcher(snd, {"= /persons[*]/name": None})
    # assert fst == dict_matcher(snd, {"= /persons[2]/name": None})
    # assert fst == dict_matcher(snd, {"= /persons[-1]/name": None})
    # assert fst == dict_matcher(snd, {"- /persons[*]/name": None})


# def test_two_top_level_keys() -> None:
#     fst = {"id": 123, "name": "James"}
#     snd = {"id": 456, "name": "Bill"}

#     assert fst == dict_matcher(snd, id=123, name="James")


# def test_nested_key() -> None:
#     fst = {"level": 2, "person": {"id": 123, "name": "James"}}
#     snd = {"level": 2, "person": {"id": 123, "name": "Bill"}}

#     assert fst == dict_matcher(snd, {"person.name": "James"})
