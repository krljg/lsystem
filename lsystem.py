import random


class ProductionRule():
    def __init__(self, pattern, result):
        self.pattern = pattern
        self.result = result

    def get_pattern(self):
        return self.pattern

    def get_consumed(self):
        return len(self.pattern)

    def matches(self, input):
        return input.startswith(self.pattern)

    def get_result(self):
        i = 0
        tot_len = len(self.result)
        res = ""
        while i < tot_len:
            if self.result[i:].startswith("rand("):
                start = i+len("rand(")
                end = start
                while end < tot_len:
                    if self.result[end] == ',':
                        break
                    end += 1
                start_val_str = self.result[start:end]
                start_val = float(start_val_str)
                end += 1
                start = end
                while end < tot_len:
                    if self.result[end] == ')':
                        break
                    end += 1
                end_val_str = self.result[start:end]
                end_val = float(end_val_str)
                val = random.uniform(start_val, end_val)
                res += str(val)
                i = end+1
            else:
                res += self.result[i]
                i += 1

        return res

    def __str__(self):
        return self.pattern + "->" + self.result


def exec_rules(input, rules):
    result = ""
    i = 0
    while i < len(input):
        matching_rules = []
        for rule in rules:
            if rule.matches(input[i:]):
                matching_rules.append(rule)
        if len(matching_rules) > 0:
            chosen_rule = random.choice(matching_rules)
            i += chosen_rule.get_consumed()
            result += chosen_rule.get_result()
        else:
            result += input[i]
            i += 1


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


def test_rand():
    random.seed(0)
    axiom = "X"
    rule = ProductionRule("X", "F+(rand(22,44))X")
    result = iterate(axiom, 1, [rule])
    expected = "F+(38.674996864686655)X"
    assert_equals(expected, result)


def test_stochastic():
    axiom = "X"
    rule1 = ProductionRule("X", "FX")
    rule2 = ProductionRule("X", "+X")

    random.seed(0)
    result = iterate(axiom, 1, [rule1, rule2])
    expected = "+X"
    assert_equals(expected, result)

    random.seed(0)
    result = iterate(axiom, 3, [rule1, rule2])
    expected = "++FX"
    assert_equals(expected, result)


def assert_equals(expected, actual):
    if actual != expected:
        raise Exception("Expected '" + expected + "' but got '" + actual + "'")

if __name__ == "__main__":

    test_algae()
    test_para()
    test_rand()
    test_stochastic()
