from uuid import uuid4
import pytest
from erech import Assertable, DictAssertable, expect, have


def test_dict_assertable_from_create():
    assertable = Assertable.create({"a": 1, "b": 5})
    assert isinstance(assertable, DictAssertable)


def test_dict_assertable_expect():
    assert isinstance(expect({"a": 1, "b": 5}), DictAssertable)


def test_dict_expect_to_have_all_keys():
    expect({"a": 1, "b": 2}).to.only.have.keys("a", "b")


def test_dict_expect_include_keys_key_alias():
    expect({"a": 1, "b": 2}).to.have.any.key("a")


def test_dict_expect_not_to_have_all_keys_raises_assertionerror():
    with pytest.raises(AssertionError):
        expect({"a": 1, "b": 2}).to.not_.only.have.keys("a", "b")


def test_dict_expect_not_to_have_all_keys___with_extra_keys___raises_assertionerror():
    """By default, the target must have all of the given keys and no more."""

    with pytest.raises(AssertionError):
        expect({"a": 1, "b": 2, "c": 3}).to.only.have.keys("a", "b")


def test_dict_expect_to_include_any_keys():
    abc = {"a": 1, "b": 2, "c": 3}
    expect(abc).to.include.any.keys("a", "b")

    # Also checking aliases includes, contain and contains
    expect(abc).includes.any.of.the.keys("a", "b")
    expect(abc).to.contain.any.key("a", "b")
    expect(abc).contains.any.key("a", "b")


def test_dict_expect_to_not_have_any_keys():
    expect({"a": 1, "b": 2}).to.not_.have.any.keys("c", "d")


def test_dict_expect_to_not_have_any_keys_simpler_syntax():
    expect({"a": 1, "b": 2}).should.not_[have["c"], have["d"]]

    with pytest.raises(AssertionError):
        expect({"a": 1, "b": 2}).should.not_[have["a"], have["b"]]


def test_dict_negated_should_passed_to_children():
    expect({"a": 1, "b": 2}).should.not_[have["a"].that.equal(2)]


def test_dict_should_match_multiple_conditions():
    expect({"gameId": str(uuid4()), "userId": str(uuid4()), "c": 3}).should[
        have["gameId"].that.matches.uuid,
        have["userId"].that.matches.uuid,
    ]
