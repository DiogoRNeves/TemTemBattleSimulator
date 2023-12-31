import pytest
from hypothesis import given
from hypothesis.strategies import lists, sampled_from

from src.technique import Technique
from src.tem_tem_type import TemTemType

@pytest.mark.parametrize("type_to_choose", [t for t in TemTemType if t != TemTemType.NO_TYPE])
def test_random_tech_from_single_type(type_to_choose: TemTemType) -> None:
    t = Technique.get_random_technique(type_to_choose)
    assert t.type == type_to_choose

def test_random_no_type_technique() -> None:
    with pytest.raises(ValueError):
        Technique.get_random_technique(TemTemType.NO_TYPE)

@given(
    lists(
        elements= sampled_from(TemTemType),
        min_size=2,
        max_size=len(TemTemType),
        unique=True
    )
)
def test_random_tech_from_list(types_to_choose: list[TemTemType]) -> None:
    t = Technique.get_random_technique(*types_to_choose)
    assert t.type in types_to_choose
