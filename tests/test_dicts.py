from uuid import uuid4
import pytest
from erech import Assertable, DictAssertable, expect, have


def test_dict_assertable_from_create():
    assertable = Assertable.create({"a": 1, "b": 5})
    assert isinstance(assertable, DictAssertable)


def test_dict_assertable_expect():
    assert isinstance(expect({"a": 1, "b": 5}), DictAssertable)


def test_dict_expect_to_have_all_keys():
    expect({"a": 1, "b": 2}).to.have.all.keys("a", "b")


def test_dict_expect_include_keys_key_alias():
    expect({"a": 1, "b": 2}).to.have.any.key("a")


def test_dict_expect_to_not_have_any_keys():
    expect({"a": 1, "b": 2}).to.not_.have.any.keys("c", "d")


def test_dict_expect_not_to_have_all_keys_raises_assertionerror():
    with pytest.raises(AssertionError):
        expect({"a": 1, "b": 2}).to.not_.have.all.keys("a", "b")


def test_dict_expect_not_to_have_all_keys___with_extra_keys___raises_assertionerror():
    """By default, the target must have all of the given keys and no more."""

    with pytest.raises(AssertionError):
        expect({"a": 1, "b": 2, "c": 3}).to.have.all.keys("a", "b")


def test_dict_expect_to_include_all_keys():
    """Add `.include` earlier in the chain to require that the target's keys be a
    superset of the expected keys, rather than identical sets."""

    # TODO: Concider using "identical" or "only" instead of "all" ?
    # Target object's keys are a superset of ['a', 'b'] but not identical
    expect({"a": 1, "b": 2, "c": 3}).to.include.all.keys("a", "b")

    # Also checking aliases includes, contain and contains
    expect({"a": 1, "b": 2, "c": 3}).includes.keys("a", "b")
    expect({"a": 1, "b": 2, "c": 3}).to.contain.keys("a", "b")
    expect({"a": 1, "b": 2, "c": 3}).contains.keys("a", "b")


def test_dict_should_match_multiple_conditions():
    expect({"gameId": str(uuid4()), "userId": str(uuid4()), "c": 3}).should[
        have.a.key("gameId").that.matches.uuid,
        have.a.key("userId").that.matches.uuid,
    ]
