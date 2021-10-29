from contextlib import contextmanager
from tempfile import TemporaryFile


@contextmanager
def create_test_data_file(data):
    with TemporaryFile() as f:
        f.write(data)
        f.seek(0)
        yield f
