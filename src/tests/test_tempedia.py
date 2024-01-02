from hypothesis import given, event, strategies as st
from src.tempedia import Tempedia, _tems, TemTemType

tem_names = [t['name'] for t in _tems.values()]

def test_size():
    assert len(tem_names) == Tempedia.size()

def test_get_names():
    assert tem_names == Tempedia.get_names()

@given(temtem_name=st.sampled_from(tem_names))
def test_get_name(temtem_name: str):
    assert Tempedia.get_name(Tempedia.get_id_from_name(temtem_name)) == temtem_name

@given(generated=st.random_module())
def test_get_random_atk_id(generated):
    event(generated)
    generated_id = Tempedia.get_random_atk_id()
    tem_info = _tems[generated_id]
    assert tem_info['stats']['atk'] > tem_info['stats']['spatk']

@given(generated=st.random_module())
def test_get_random_spatk_id(generated):
    event(generated)
    generated_id = Tempedia.get_random_spatk_id()
    tem_info = _tems[generated_id]
    assert tem_info['stats']['spatk'] > tem_info['stats']['atk']

@given(generated_id=st.integers(min_value=1, max_value=len(_tems)))
def test_get_types(generated_id: int):
    tps = list(
        tp.name.lower() for tp in Tempedia.get_types(generated_id)
            if tp != TemTemType.NO_TYPE
    )
    original_tp_strings = list(t.lower() for t in _tems[generated_id]['types'])

    assert tps == original_tp_strings

# TODO Tempedia.get_base_value_initializer(generated_id)
# TODO Tempedia.get_latest_learnable_technique_names(generated_id)
