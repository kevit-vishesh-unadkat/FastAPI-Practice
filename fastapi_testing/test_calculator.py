# from calculator import add, subtract,mul, div

# def test_add():
#     assert add(10,5)==15

# def test_sub():
#     assert subtract(10,5)==5

from calculator import get_user

def test_get_user():
    user = get_user()

    assert user["id"] == 1
    assert user["name"] == "vishesh"
    assert user["active"] is True