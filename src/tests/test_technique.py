from contextlib import AbstractContextManager, nullcontext as does_not_raise
import pytest

from hypothesis import event, given, strategies as st

from src.technique import Technique
from src.tem_tem_type import TemTemType

# TODO merge both tests by forcing hypothesis to run all the lists with len()==1
# not sure i can make a parameter depend on the other. must check.

@pytest.mark.parametrize(
    "type_to_choose, expectation",
    [
        (
            t,
            pytest.raises(ValueError) if t == TemTemType.NO_TYPE else does_not_raise()
        ) for t in TemTemType
    ]
)
@given(
    seed=st.random_module()
)
def test_random_tech_from_single_type(
    type_to_choose: TemTemType,
    expectation: AbstractContextManager[BaseException],
    seed
) -> None:
    event(seed)
    with expectation:
        t = Technique.get_random_technique(type_to_choose)
        assert t.type == type_to_choose

@given(
    types_to_choose=st.lists(
        elements=st.sampled_from(TemTemType),
        min_size=2,
        max_size=len(TemTemType),
        unique=True
    ),
    seed=st.random_module()
)
def test_random_tech_from_list(
    types_to_choose: list[TemTemType],
    seed
) -> None:
    event(seed)
    t = Technique.get_random_technique(*types_to_choose)
    assert t.type in types_to_choose
