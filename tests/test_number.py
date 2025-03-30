import pytest
from erech import be, expect


def test_number_for_equality():
    expect(8).to.equal(8)
    expect(8).should.equal(8)

    with pytest.raises(AssertionError) as err:
        expect(8).should.equal(9)
    assert "8 is not equal to 9" == str(err.value)


def test_number_for_non_equality():
    expect(8).not_.to.equal(9)

    with pytest.raises(AssertionError) as err:
        expect(8).should.not_.equal(8)
    assert "8 is equal to 8, should not be" == str(err.value)


def test_number_between_x_and_y():
    expect(2).to.be.between(1).and_(3)
    expect(3).not_.to.be.between(1).and_(2)

    with pytest.raises(AssertionError) as err:
        expect(3).to.be.between(1).and_(2)
    assert "3 is not between 1 and 2" == str(err.value)

    with pytest.raises(AssertionError) as err:
        expect(3).to.be.between(4).and_(6)
    assert "3 is not between 4 and 6" == str(err.value)

    with pytest.raises(AssertionError) as err:
        expect(2).to.not_.be.between(1).and_(3)
    assert "2 is between 1 and 3, should not be" == str(err.value)


def check_condition(input: int):
    expect(input).should[
        be.less_than(10).and_.be.divisible_by(3),
        be.greater_than(8),
    ]


def test_number_against_multiple_comparisons():
    check_condition(9)

    with pytest.raises(AssertionError) as err:
        check_condition(11)
    assert "11 is not less than 10" == str(err.value)

    with pytest.raises(AssertionError) as err:
        check_condition(6)
    assert "6 is not greater than 8" == str(err.value)

    with pytest.raises(AssertionError) as err:
        check_condition(7)
    assert "7 is not divisible by 3" == str(err.value)


@pytest.mark.skip("not implemented yet")
def test_number_have_condition_too():
    # expect(4).should[
    #     have.value.between(1).and_(3),
    #     be.greater_than(0),
    # ]

    assert False
