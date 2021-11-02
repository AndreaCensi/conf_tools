import os

__all__ = [
    "dir_from_package_name",
]


def dir_from_package_name(d: str):
    """This works for "package.sub" format."""
    tokens = d.split(".")
    if len(tokens) == 1:
        package = d
        sub = "__init__"
    else:
        package = ".".join(tokens[:-1])
        sub = tokens[-1]
    try:
        from pkg_resources import resource_filename  # @UnresolvedImport

        res = resource_filename(package, sub)

        if len(tokens) == 1:
            res = os.path.dirname(res)

        return res
    except BaseException as e:
        raise ValueError(f"Cannot resolve package name {d}") from e
