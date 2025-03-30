import re
from collections.abc import Hashable
from typing import Any, Callable, overload

from erech.chains import Chains

HIDE_TRACEBACK = False


class Negatable:
    def __init__(self, *_) -> None:
        self._negated = False

    @property
    def not_(self):
        self._negated = True
        return self


class BetweenThisAnd:
    def __init__(self, target: int | float, this: int | float, negated: bool) -> None:
        self._target = target
        self._this = this
        self._negated = negated

    def and_(self, other: int | float):
        not_ = "not " if not self._negated else ""
        negated_error = ", should not be" if self._negated else ""

        error_text = (
            f"{self._target} is {not_}between {self._this} and {other}{negated_error}"
        )

        if self._this < other:
            result = self._this < self._target and self._target < other
        else:
            result = other < self._target and self._target < self._this

        if self._negated:
            result = not result

        assert result, error_text


class Comparison(Chains, Negatable):
    def __init__(self, target) -> None:
        self._target = target
        super().__init__(target)

    def _compare(
        self, comparable: Callable[[], bool], other: int | float, comparison: str
    ):
        result = comparable()
        if self._negated:
            result = not result

        not_ = "not " if not self._negated else ""
        negated_error = ", should not be" if self._negated else ""

        error_text = f"{self._target} is {not_}{comparison} {other}{negated_error}"

        return result, error_text

    def less_than(self, other: int | float):
        res, err = self._compare(
            lambda: self._target < other,
            other,
            "less than",
        )
        assert res, err

    def greater_than(self, other: int | float):
        res, err = self._compare(
            lambda: self._target > other,
            other,
            "greater than",
        )
        assert res, err

    def divisible_by(self, other: int | float):
        res, err = self._compare(
            lambda: self._target % other == 0,
            other,
            "divisible by",
        )
        assert res, err

    def equal(self, other: int | float):
        res, err = self._compare(
            lambda: self._target == other,
            other,
            "equal to",
        )
        assert res, err

    def between(self, this: int | float):
        return BetweenThisAnd(self._target, this, self._negated)


class LazyComparison(Chains, Negatable):
    def __init__(self) -> None:
        self._comparisons: list[Callable[[int | float], bool]] = []
        super().__init__()

    def _register(
        self,
        comparable: Callable[[int | float], bool],
        other: int | float,
        comparison: str,
    ):
        def _comparison(target: int | float):
            result = comparable(target)
            if self._negated:
                result = not result

            not_ = "not " if not self._negated else ""
            negated_error = ", should not be" if self._negated else ""

            error_text = f"{target} is {not_}{comparison} {other}{negated_error}"

            assert result, error_text

            return result

        self._comparisons.append(_comparison)

    def less_than(self, other: int | float):
        self._register(
            lambda target: target < other,
            other,
            "less than",
        )
        return self

    def greater_than(self, other: int | float):
        self._register(
            lambda target: target > other,
            other,
            "greater than",
        )
        return self

    def divisible_by(self, other: int | float):
        self._register(
            lambda target: target % other == 0,
            other,
            "divisible by",
        )
        return self

    def equal(self, other: int | float):
        self._register(
            lambda target: target == other,
            other,
            "equal to",
        )
        return self

    def _match(self, target: int | float, negated: bool):
        if negated:
            self._negated = negated
        for c in self._comparisons:
            c(target)


class Matcher:
    def __init__(self, value: Any) -> None:
        self._value = value

    @property
    def that(self):
        return self

    @property
    def matches(self):
        return self

    def regex(self, regex: str) -> bool:
        assert isinstance(self._value, str)
        pattern = re.compile(regex)
        match = bool(pattern.fullmatch(self._value))
        assert match
        return match

    @property
    def uuid(self) -> bool:
        UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return self.regex(UUID_PATTERN)

    @property
    def short_game_id(self) -> bool:
        assert isinstance(self._value, int)
        match = 100000 < self._value and self._value < 999999
        assert match
        return match


class DictMatcher(LazyComparison):
    def __init__(self, key: Hashable) -> None:
        self._key = key
        super().__init__()

    def _match_dict(self, dict: dict, negated: bool) -> bool:
        if negated and not self._comparisons:
            assert self._key not in dict, (
                f"key {self._key} in dict {dict}, should not be"
            )

            return False

        assert self._key in dict, f"key {self._key} not in dict {dict}"
        if self._comparisons:
            self._match(dict[self._key], negated)
        return False

    @property
    def uuid(self):
        self._comparisons.append(lambda val: Matcher(val).uuid)
        return self


class MetaHave(type):
    def __getitem__(cls, index: Hashable):
        return DictMatcher(index)


class have(Chains, metaclass=MetaHave):
    def key(self, key: str) -> DictMatcher:
        return DictMatcher(key)


class DictShould(Chains, Negatable):
    def __init__(self, dict_value: Any) -> None:
        __tracebackhide__ = HIDE_TRACEBACK
        self._dict_value = dict_value
        super().__init__(self._dict_value)

    def __getitem__(self, items: DictMatcher | tuple[DictMatcher, ...]):
        __tracebackhide__ = HIDE_TRACEBACK
        if isinstance(items, tuple):
            for i in items:
                i._match_dict(self._dict_value, self._negated)
        else:
            items._match_dict(self._dict_value, self._negated)


class ValueShould(Comparison, Negatable):
    def __init__(self, value: Any) -> None:
        __tracebackhide__ = HIDE_TRACEBACK
        self._value = value
        super().__init__(value)

    def __getitem__(self, items: LazyComparison | tuple[LazyComparison, ...]):
        __tracebackhide__ = HIDE_TRACEBACK
        if isinstance(items, tuple):
            for i in items:
                i._match(self._value, self._negated)
        else:
            items._match(self._value, self._negated)


class AssertKeys(Negatable):
    def __init__(self, target: dict | set | list) -> None:
        __tracebackhide__ = HIDE_TRACEBACK
        super().__init__(target)
        self._target = target
        self._should_only_include_given_keys = True
        self._include_was_specified = False

    @property
    def include(self):
        """
        The aliases `.includes`, `.contain`, and `.contains` can be used
        interchangeably with `.include`."""
        __tracebackhide__ = HIDE_TRACEBACK
        self._include_was_specified = True
        return self

    @property
    def includes(self):
        __tracebackhide__ = HIDE_TRACEBACK
        return self.include

    @property
    def contain(self):
        __tracebackhide__ = HIDE_TRACEBACK
        return self.include

    @property
    def contains(self):
        __tracebackhide__ = HIDE_TRACEBACK
        return self.include

    @property
    def only(self):
        """
        ### .only

        Causes all `.keys` assertions that follow in the chain to require that the
        target have all of the given keys, and no other keys. This is the opposite of `.any`,
        only requires that the target have at least one of the given keys.

            expect({"a": 1, "b": 2}).to.only.have.keys("a", "b")
        """
        __tracebackhide__ = HIDE_TRACEBACK

        self._should_only_include_given_keys = True
        return self

    @property
    def any(self):
        """
        ### .any

        Causes all `.keys` assertions that follow in the chain to only require that
        the target have at least one of the given keys. This is the opposite of
        `.all`, which requires that the target have all of the given keys.

            expect({"a": 1, "b": 2}).to.not_.have.any.keys("c", "d")

        See the `.keys` doc for guidance on when to use `.any` or `.all`.
        """
        __tracebackhide__ = HIDE_TRACEBACK

        self._should_only_include_given_keys = False
        return self

    def keys(self, *keys: Hashable):
        """
        ### .keys(*keys: Hashable)

        Asserts that the target object, array, map, or set has the given keys.

            expect({"a": 1, "b": 2}).to.have.all.keys('a', 'b')
            expect(['x', 'y']).to.have.all.keys(0, 1)

        By default, the target must have all of the given keys and no more. Add
        `.any` earlier in the chain to only require that the target have at least
        one of the given keys. Also, add `.not` earlier in the chain to negate
        `.keys`. It's often best to add `.any` when negating `.keys`, and to use
        `.all` when asserting `.keys` without negation.

        When negating `.keys`, `.any` is preferred because `.not.any.keys` asserts
        exactly what's expected of the output, whereas `.not.all.keys` creates
        uncertain expectations.

        When asserting `.keys` without negation, `.all` is preferred because
        `.all.keys` asserts exactly what's expected of the output, whereas
        `.any.keys` creates uncertain expectations.

            # Recommended; asserts that target has all the given keys
            expect({"a": 1, "b": 2}).to.have.all.keys("a", "b")

            # Not recommended; asserts that target has at least one of the given
            # keys but may or may not have more of them
            expect({"a": 1, "b": 2}).to.have.any.keys("a", "b")

        Note that `.all` is used by default when neither `.all` nor `.any` appear
        earlier in the chain. However, it's often best to add `.all` anyway because
        it improves readability.

            # Both assertions are identical
            expect({"a": 1, "b": 2}).to.have.all.keys("a", "b") # Recommended
            expect({"a": 1, "b": 2}).to.have.keys("a", "b") # Not recommended

        Add `.include` earlier in the chain to require that the target's keys be a
        superset of the expected keys, rather than identical sets.

            # Target object's keys are a superset of ['a', 'b'] but not identical
            expect({"a": 1, "b": 2, "c": 3}).to.include.all.keys("a", "b");

        The alias `.key` can be used interchangeably with `.keys`.
        """
        __tracebackhide__ = HIDE_TRACEBACK
        result = False

        if self._should_only_include_given_keys:
            result = True

            for k in keys:
                if k not in self._target:
                    result = False

            if self._should_only_include_given_keys:
                for t in self._target:
                    if t not in keys:
                        raise AssertionError(f"Key {t} doesn't exists in the target")
        else:
            for k in keys:
                if k in self._target:
                    result = True
                    break

        if self._negated:
            result = not result

        assert result

    def key(self, *key: Hashable | tuple[Hashable, ...]):
        __tracebackhide__ = HIDE_TRACEBACK
        return self.keys(*key)


class DictAssertable(Chains, AssertKeys):
    def __init__(self, dict: dict) -> None:
        __tracebackhide__ = HIDE_TRACEBACK
        super().__init__(dict)
        self._dict = dict

    @property
    def should(self):
        __tracebackhide__ = HIDE_TRACEBACK
        return DictShould(self._dict)


class ValueAssertable(Comparison):
    def __init__(self, value: Any) -> None:
        __tracebackhide__ = HIDE_TRACEBACK
        self._value = value
        super().__init__(value)

    @property
    def should(self):
        __tracebackhide__ = HIDE_TRACEBACK
        return ValueShould(self._value)


class Assertable:
    def __init__(self) -> None:
        __tracebackhide__ = HIDE_TRACEBACK
        pass

    @overload
    @staticmethod
    def create(value: dict) -> DictAssertable: ...

    @overload
    @staticmethod
    def create(value: int) -> ValueAssertable: ...

    @staticmethod
    def create(value: dict | int):
        __tracebackhide__ = HIDE_TRACEBACK
        if isinstance(value, dict):
            return DictAssertable(value)
        elif isinstance(value, int):
            return ValueAssertable(value)


@overload
def expect(value: dict[Any, Any]) -> DictAssertable: ...


@overload
def expect(value: int) -> ValueAssertable: ...


def expect(value: dict | int):
    __tracebackhide__ = HIDE_TRACEBACK
    if isinstance(value, dict):
        return DictAssertable(value)
    elif isinstance(value, int):
        return ValueAssertable(value)
    else:
        raise NotImplementedError()


be = LazyComparison()
