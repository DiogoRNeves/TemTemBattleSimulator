![Pylint status](https://github.com/DiogoRNeves/TemTemBattleSimulator/actions/workflows/pylint.yml/badge.svg)

The aim of this repo is to provide an API for temtem battle simulation.

ATM there's a script for damage calculation (nuzlocke helper), but it doesn't take traits into account yet.

Requires python >= 3.11, developed on 3.11.3

To run a file in the src folder (say battle.py) use

```bash
$ py src.battle
```

You should run pytest via python, so that it will add the current directory to sys.path:

```bash
$ py -m pytest
```
