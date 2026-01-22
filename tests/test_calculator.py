import pytest
from tools.calculator import eval_expression

def test_eval_expression_simple_math():
    assert eval_expression.invoke("2 + 2") == "4"
    assert eval_expression.invoke("10 - 3") == "7"
    assert eval_expression.invoke("5 * 5") == "25"
    assert eval_expression.invoke("10 / 2") == "5.0"

def test_eval_expression_complex_math():
    assert eval_expression.invoke("(2 + 3) * 4") == "20"
    # Test power operator replacement
    assert eval_expression.invoke("2 ^ 3") == "8" 

def test_eval_expression_invalid_chars():
    assert "Error: arithmetic only" in eval_expression.invoke("2 + 2 + import os")
    assert "Error: arithmetic only" in eval_expression.invoke("print('hello')")

def test_eval_expression_error_handling():
    # Division by zero
    result = eval_expression.invoke("1 / 0")
    assert "Error" in result

def test_eval_expression_whitespace():
    assert eval_expression.invoke("  1 +   1  ") == "2"
