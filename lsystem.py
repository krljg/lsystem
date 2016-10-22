__author__ = 'Krister'

# import bpy
# from turtle import Turtle
# from . import turtle


class ProductionRule():
    def __init__(self, pattern, result):
        self.pattern = pattern
        self.result = result

    def get_pattern(self):
        return self.pattern

    def get_result(self):
        return self.result

    def __str__(self):
        return self.pattern + "->" + self.result


def exec_rules(input, rules):
    result = ""
    i = 0
    while i < len(input):
        new_substring = str(input[i])
        step = 1
        for rule in rules:
            pattern = rule.get_pattern()
            if input[i:].startswith(pattern):
                new_substring = rule.get_result()
                step = len(pattern)
                break
        result += new_substring
        i += step

    # for i in range(0, len(input)):
    #     newSubstring = str(input[i])
    #     for rule in rules:
    #         if input[i:].startswith(rule.get_pattern()):
    #             newSubstring = rule.get_result()
    #     result += newSubstring
    return result


def iterate(axiom, iterations, rules):
    result = axiom
    for i in range(0, iterations):
        result = exec_rules(result, rules)
    return result


def test_algae():
    axiom = "A"
    rule1 = ProductionRule("A", "AB")
    rule2 = ProductionRule("B", "A")
    result = iterate(axiom, 5, [rule1, rule2])
    expected = "ABAABABAABAAB"
    if result != expected:
        raise Exception("Expected '"+expected+"' but got '"+result+"'")


def test_para():
    axiom = "X"
    rule1 = ProductionRule("X", "F+(45)X")
    rule2 = ProductionRule("+(45)", "-(30)")
    result = iterate(axiom, 1, [rule1, rule2])
    expected = "F+(45)X"
    assert_equals(expected, result)
    result = iterate(axiom, 2, [rule1, rule2])
    expected = "F-(30)F+(45)X"
    assert_equals(expected, result)
    result = iterate(axiom, 3, [rule1, rule2])
    expected = "F-(30)F-(30)F+(45)X"
    assert_equals(expected, result)


def assert_equals(expected, actual):
    if actual != expected:
        raise Exception("Expected '" + expected + "' but got '" + actual + "'")

if __name__ == "__main__":

    test_algae()
    test_para()
