from libddog.metrics import Filter, Tag


def test_combining_filters() -> None:
    region = Filter(conds=[Tag(tag="region", value="us-west-2")])
    role = Filter(conds=[Tag(tag="role", value="cache")])

    combined = region & role

    assert combined.codegen() == "{region:us-west-2, role:cache}"
