""" Testing wheels2dmg_cmd module
"""

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)

from .scriptrunner import ScriptRunner

run_cmd = ScriptRunner().run_command


def test_exit_codes():
    # Test invalid calls to main
    # Too few argumets
    code, stdout, stderr = run_cmd(['wheels2dmg'], check_code=False)
    assert_equal(code, 2)
    code, stdout, stderr = run_cmd(['wheels2dmg', 'mypackage'],
                                   check_code=False)
    assert_equal(code, 2)
    # Test non-zero exit code for no requirements
    code, stdout, stderr = run_cmd(['wheels2dmg', 'mypackage', '1'],
                                   check_code=False)
    assert_equal(code, 12)
