from hypothesis import assume, given, strategies as st
from src.tem_tem_type import TemTemType, TemType

actual_types = [t for t in TemTemType if t != TemTemType.NO_TYPE]

@given(
        primary=st.sampled_from(actual_types),
        secondary=st.sampled_from(TemTemType),
        move=st.sampled_from(actual_types)
)
def test_tem_dual_type(primary: TemTemType, secondary: TemTemType, move: TemTemType):
    assume(primary != secondary)
    tem_type = TemType(primary_type=primary, secondary_type=secondary)
    assert move.get_multiplier(*tem_type) == \
        move.get_multiplier(primary) * move.get_multiplier(secondary)

@given(
        primary=st.sampled_from(actual_types),
        move=st.sampled_from(actual_types)
)
def test_tem_single_type(primary: TemTemType, move: TemTemType):
    tem_type = TemType(primary_type=primary)
    assert move.get_multiplier(*tem_type) == move.get_multiplier(primary)
