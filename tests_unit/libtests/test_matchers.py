from libtests.matchers import assign, obj_matcher

# dict only


def test__single_level_dict__assign_one_key() -> None:
    fst = {"id": 123, "first-name": "James", "last-name": "Joy"}
    snd = {"id": 123, "first-name": "Bill", "last-name": "Joy"}

    assert fst == obj_matcher(snd, [assign('.["first-name"]', "James")])


def test__single_level_dict__assign_all_keys() -> None:
    fst = {"id": "James", "first-name": "James", "last-name": "James"}
    snd = {"id": 123, "first-name": "Bill", "last-name": "Joy"}

    assert fst == obj_matcher(snd, [assign(".[]", "James")])


def test__two_level_dict__assign_one_key() -> None:
    fst = {"level": 2, "user": {"id": 123, "first-name": "James"}}
    snd = {"level": 2, "user": {"id": 123, "first-name": "Bill"}}

    assert fst == obj_matcher(snd, [assign('.["user"]["first-name"]', "James")])


def test__single_level_dict__set_new_key() -> None:
    fst = {"id": 123, "first-name": "James", "last-name": "Joy"}
    snd = {"id": 123, "last-name": "Joy"}

    assert fst == obj_matcher(snd, [assign('.["first-name"]', "James")])


# list only


def test__single_level_list__assign_one_item__by_pos_index() -> None:
    fst = [1, 2, 3]
    snd = [1, 3, 3]

    assert fst == obj_matcher(snd, [assign(".[1]", 2)])


def test__single_level_list__assign_one_item__by_neg_index() -> None:
    fst = [1, 2, 3]
    snd = [1, 3, 3]

    assert fst == obj_matcher(snd, [assign(".[-2]", 2)])


def test__single_level_list__assign_all_items() -> None:
    fst = [7, 7, 7]
    snd = [1, 2, 3]

    assert fst == obj_matcher(snd, [assign(".[]", 7)])


def test__two_level_list__assign_one_item() -> None:
    fst = [[1, 2], [1, 4]]
    snd = [[1, 2], [3, 4]]

    assert fst == obj_matcher(snd, [assign(".[1][0]", 1)])


# dicts inside lists


def test__dict_inside_list__assign_one_key() -> None:
    fst = [{"id": 123, "first-name": "James"}]
    snd = [{"id": 123, "first-name": "Bill"}]

    assert fst == obj_matcher(snd, [assign('.[0]["first-name"]', "James")])


def test__dict_inside_list__assign_one_key_in_every_dict() -> None:
    fst = [{"id": 123, "first-name": "Barry"}, {"id": 456, "first-name": "Barry"}]
    snd = [{"id": 123, "first-name": "James"}, {"id": 456, "first-name": "Bill"}]

    assert fst == obj_matcher(snd, [assign('.[]["first-name"]', "Barry")])
