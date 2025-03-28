import re
from collections.abc import Hashable
from typing import Any, Callable, overload

from erech.chains import Chains


class AssertNot:
    def __init__(self, target: Any) -> None:
        _ = target
        self._not_set = False

    @property
    def not_(self):
        self._not_set = True
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


class Comparison(Chains, AssertNot):
    def __init__(self, target) -> None:
        self._target = target
        super().__init__(target)

    def _compare(
        self, comparable: Callable[[], bool], other: int | float, comparison: str
    ):
        result = comparable()
        if self._not_set:
            result = not result

        not_ = "not " if not self._not_set else ""
        negated_error = ", should not be" if self._not_set else ""

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
        return BetweenThisAnd(self._target, this, self._not_set)


class LazyComparison(Chains):
    def __init__(self) -> None:
        self._comparisons: list[Callable[[int | float], None]] = []

    def _register(self, comparison: Callable[[int | float], None]):
        self._comparisons.append(comparison)

        return self

    def less_than(self, other: int | float):
        def fn(target: int | float):
            assert target < other, f"{target} is not less than {other}"

        return self._register(fn)

    def greater_than(self, other: int | float):
        def fn(target: int | float):
            assert target > other, f"{target} is not greater than {other}"

        return self._register(fn)

    def divisible_by(self, other: int | float):
        def fn(target: int | float):
            assert target % other == 0, f"{target} is not divisible by {other}"

        return self._register(fn)

    def equal(self, other: int | float):
        def fn(target: int | float):
            assert target == other, f"{target} does not equal {other}"

        return self._register(fn)

    def _match(self, target: int | float):
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


class DictMatcher(Chains):
    def __init__(self, key: str) -> None:
        self._key = key
        self._match: Callable[[Any], bool]

    def _match_dict(self, dict: dict) -> bool:
        assert self._key in dict, f"key {self._key} not in dict {dict}"
        self._match(dict[self._key])
        return False

    @property
    def uuid(self):
        self._match = lambda val: Matcher(val).uuid
        return self


class Selector(Chains):
    def key(self, key: str) -> DictMatcher:
        return DictMatcher(key)


class DictShould:
    def __init__(self, dict_value: Any) -> None:
        self._dict_value = dict_value

    def __getitem__(self, items: DictMatcher | tuple[DictMatcher, ...]):
        if isinstance(items, tuple):
            for i in items:
                i._match_dict(self._dict_value)
        else:
            items._match_dict(self._dict_value)


class ValueShould(Comparison):
    def __init__(self, value: Any) -> None:
        super().__init__(value)
        self._value = value

    def __getitem__(self, items: LazyComparison | tuple[LazyComparison, ...]):
        if isinstance(items, tuple):
            for i in items:
                i._match(self._value)
        else:
            items._match(self._value)


class AssertKeys(AssertNot):
    def __init__(self, target: dict | set | list) -> None:
        super().__init__(target)
        self._target = target
        self._chech_all = True
        self._check_includes_only = False

    @property
    def include(self):
        """`.include` can also be used as a language chain, causing all `.members` and
        `.keys` assertions that follow in the chain to require the target to be a
        superset of the expected set, rather than an identical set. Note that
        `.members` ignores duplicates in the subset when `.include` is added.

            // Target object's keys are a superset of ['a', 'b'] but not identical
            expect({a: 1, b: 2, c: 3}).to.include.all.keys('a', 'b');
            expect({a: 1, b: 2, c: 3}).to.not.have.all.keys('a', 'b');

            // Target array is a superset of [1, 2] but not identical
            expect([1, 2, 3]).to.include.members([1, 2]);
            expect([1, 2, 3]).to.not.have.members([1, 2]);

            // Duplicates in the subset are ignored
            expect([1, 2, 3]).to.include.members([1, 2, 2, 2]);

        Note that adding `.any` earlier in the chain causes the `.keys` assertion
        to ignore `.include`.

            // Both assertions are identical
            expect({a: 1}).to.include.any.keys('a', 'b');
            expect({a: 1}).to.have.any.keys('a', 'b');

        The aliases `.includes`, `.contain`, and `.contains` can be used
        interchangeably with `.include`."""

        self._check_includes_only = True
        return self

    @property
    def includes(self):
        return self.include

    @property
    def contain(self):
        return self.include

    @property
    def contains(self):
        return self.include

    @property
    def all(self):
        """### .all

        Causes all `.keys` assertions that follow in the chain to require that the
        target have all of the given keys. This is the opposite of `.any`, which
        only requires that the target have at least one of the given keys.

            expect({"a": 1, "b": 2}).to.have.all.keys("a", "b")

        Note that `.all` is used by default when neither `.all` nor `.any` are
        added earlier in the chain. However, it's often best to add `.all` anyway
        because it improves readability.

        See the `.keys` doc for guidance on when to use `.any` or `.all`."""
        self._chech_all = True
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

        self._chech_all = False
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
        result = False

        if self._chech_all:
            result = True

            for k in keys:
                if k not in self._target:
                    result = False

            if not self._check_includes_only:
                for t in self._target:
                    if t not in keys:
                        raise AssertionError(f"Key {t} doesn't exists in the target")
        else:
            for k in keys:
                if k in self._target:
                    result = True
                    break

        if self._not_set:
            result = not result

        assert result

    def key(self, key: Hashable):
        return self.keys(key)


class DictAssertable(Chains, AssertKeys):
    def __init__(self, dict: dict) -> None:
        super().__init__(dict)
        self._dict = dict

    @property
    def should(self):
        return DictShould(self._dict)


class ValueAssertable(Comparison):
    def __init__(self, value: Any) -> None:
        self._value = value
        super().__init__(value)

    @property
    def should(self):
        return ValueShould(self._value)


class Assertable:
    def __init__(self) -> None:
        pass

    @overload
    @staticmethod
    def create(value: dict) -> DictAssertable: ...

    @overload
    @staticmethod
    def create(value: int) -> ValueAssertable: ...

    @staticmethod
    def create(value: dict | int):
        if isinstance(value, dict):
            return DictAssertable(value)
        elif isinstance(value, int):
            return ValueAssertable(value)


@overload
def expect(value: dict[Hashable, Any]) -> DictAssertable: ...


@overload
def expect(value: int) -> ValueAssertable: ...


def expect(value: dict | int):
    if isinstance(value, dict):
        return DictAssertable(value)
    elif isinstance(value, int):
        return ValueAssertable(value)
    else:
        raise NotImplementedError()


be = LazyComparison()

have = Selector()
