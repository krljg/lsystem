__author__ = 'Krister'

import bpy
#from turtle import Turtle
from . import turtle


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
    for i in range(0, len(input)):
        newSubstring = str(input[i])
        for rule in rules:
            if input[i:].startswith(rule.get_pattern()):
                newSubstring = rule.get_result()
        result += newSubstring
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
    print(result)

if __name__ == "__main__":

    test_algae()

