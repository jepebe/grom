def assert_exhaustive_enum(enum_class, expected_count):
    message = (f"non-exhaustive implementation of {enum_class.__name__}, "
               f"expected '{expected_count}' but found '{len(enum_class)}'")
    assert len(enum_class) == expected_count, message
