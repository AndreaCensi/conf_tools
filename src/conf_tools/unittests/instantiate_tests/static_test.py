from conf_tools.instantiate_utils import import_name


class MyStatic:
    @staticmethod
    def f(a):
        return a + 1


def test_static_method_1():
    the_class = import_name("conf_tools.unittests.instantiate_tests.static_test.MyStatic")
    print(the_class.__dict__)
    print(the_class)
    the_static = import_name("conf_tools.unittests.instantiate_tests.static_test.MyStatic.f")

    assert the_static(2) == 3


def test_not_existing():
    try:
        import_name("not_existing.a")
    except ValueError:
        pass
    else:
        msg = "Expected ValueError"
        raise Exception(msg)


def test_second():
    try:
        import_name("conf_tools.a")
    except ValueError:
        pass
    else:
        msg = "Expected ValueError"
        raise Exception(msg)
