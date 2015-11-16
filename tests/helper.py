class DeedModelMock:
    id = 1
    deed = {"deed": {"title_number": "DN100", "id": 1}}


class DeedHelper:
    _json_doc = {"title_number": "DN100"}

    _invalid_title = {"title_number": "BBBB12313212BB"}
