import pytest
from erech import BASE_TYPES, DictMatcher, expect as _expect
import httpx


class HTTPXAssertible(DictMatcher):
    def __init__(self, value: httpx.Response) -> None:
        self._value = value

    @property
    def status_code(self):
        return self

    @property
    def should(self):
        return self


def expect(value: BASE_TYPES | httpx.Response):
    if isinstance(value, httpx.Response):
        return HTTPXAssertible(value)
    else:
        return _expect(value)


@pytest.mark.skip
def test_httpx_response_assertions(have):
    response = httpx.Response(200, text="OK")
    # expect(response).should[have.status_code.equal(200)] # type: ignore

    assert False
