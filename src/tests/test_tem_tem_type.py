# TODO replace the __name__=="__main__" with proper testing
"""

if __name__=='__main__':
    from icecream import ic

    effectiveness_table = {
        attacker: {
            defender1: {
                defender2: attacker.get_multiplier(defender1, defender2)
                for defender2 in TemTemType if defender1 != defender2
            }
            for defender1 in TemTemType
        }
        for attacker in TemTemType
    }

    count: int = 0
    for atacker, val1 in effectiveness_table.items():
        for defender1, val2 in val1.items():
            for defender2, multiplier in val2.items():
                if multiplier != 1:
                    ic(f"{atacker} -> {defender1}, {defender2} = {multiplier}")
                    count += 1

    ic(count)

"""
