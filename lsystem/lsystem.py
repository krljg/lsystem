import random


class ProductionRule():
    def __init__(self, pattern, result):
        self.pattern = pattern
        self.parameters = self.get_parameters(pattern)
        if len(self.parameters) == 0:
            self.module = pattern
            self.parameters = None
            self.consumed = len(self.module)
        else:
            pind = pattern.find("(")
            self.module = pattern[:pind]
        self.param_subs = None
        self.result = result

    def get_pattern(self):
        return self.pattern

    def get_consumed(self):
        return self.consumed

    def get_parameters(self, str):
        if "(" in str:
            sind = str.find("(")+1
            if ")" in str:
                eind = str.find(")")
            else:
                eind = len(str)
            parameters = str[sind:eind].split(",")
            for i in range(0, len(parameters)):
                parameters[i] = parameters[i].strip()
            return parameters
        return []

    def matches(self, input):
        # print("self.module: "+self.module)

        if not input.startswith(self.module):
            # print("input doesn't start with module")
            return False

        if self.parameters is None:
            # print("no parameters")
            return True

        parameters = self.get_parameters(input)
        if len(parameters) != len(self.parameters):
            # print(str(len(parameters)) + " != " + str(len(self.parameters)))
            return False

        self.param_subs = dict()
        for i in range(0, len(self.parameters)):
            self.param_subs[self.parameters[i]] = parameters[i]
        self.consumed = input.find(")")+1
        return True

    def parse_expression(self, string):
        # print("parse_expression('"+string+"')")
        try:
            if string.startswith("rand("):
                op_len = len("rand(")
                c, val1 = self.parse_expression(string[op_len:])
                c += op_len+1
                # print(str(c)+" "+string[c:])
                c2, val2 = self.parse_expression(string[c:])
                c += c2
                # print(str(c)+" "+string[c:])
                c = string.find(")", c)+1
                return c, random.uniform(val1, val2)
            elif string.startswith("add("):
                op_len = len("add(")
                c, val1 = self.parse_expression(string[op_len:])
                c += op_len+1
                c2, val2 = self.parse_expression(string[c:])
                c = string.find(")", c)+1
                return c, val1+val2
            elif string.startswith("mul("):
                op_len = len("mul(")
                c, val1 = self.parse_expression(string[op_len:])
                c += op_len+1
                c2, val2 = self.parse_expression(string[c:])
                c = string.find(")", c)+1
                return c, val1*val2
            elif string.startswith("div("):
                op_len = len("div(")
                c, val1 = self.parse_expression(string[op_len:])
                c += op_len+1
                c2, val2 = self.parse_expression(string[c:])
                c = string.find(")", c)+1
                return c, val1/val2
            elif string.startswith("pow("):
                op_len = len("pow(")
                c, val1 = self.parse_expression(string[op_len:])
                c += op_len+1
                c2, val2 = self.parse_expression(string[c:])
                c = string.find(")", c)+1
                return c, pow(val1,val2)
            else:
                c = 0
                while string[c] != ',' and string[c] != ')':
                    c += 1
                val = string[:c]
                try:
                    val = float(string[:c])
                except:
                    pass
                return c, val

        except Exception as e:
            print(string)
            raise e

    def get_result(self):
        # print(self.result)
        # print(self.param_subs)
        tmp_result = self.result
        if self.param_subs is not None:
            for p in self.param_subs:
                tmp_result = tmp_result.replace(p, self.param_subs[p])

        i = 0
        tot_len = len(tmp_result)
        res = ""
        # assume result of a rule is "module(expression)module(expression)"
        # where (expression) is optional
        while i < tot_len:
            c = tmp_result[i]
            if c == "(" or c == ",":
                i += 1
                consumed, value = self.parse_expression(tmp_result[i:])
                i += consumed
                res += c+str(value)
            else:
                res += c
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
    print("test_algae")
    print("==========")
    axiom = "A"
    rule1 = ProductionRule("A", "AB")
    rule2 = ProductionRule("B", "A")
    result = iterate(axiom, 5, [rule1, rule2])
    expected = "ABAABABAABAAB"
    if result != expected:
        raise Exception("Expected '"+expected+"' but got '"+result+"'")


def test_para():
    print("test_para")
    print("=========")
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
    print("test_rand")
    print("=========")
    random.seed(0)
    axiom = "X"
    rule = ProductionRule("X", "F+(rand(22,44))X")
    result = iterate(axiom, 1, [rule])
    expected = "F+(38.674996864686655)X"
    assert_equals(expected, result)


def test_stochastic():
    print("test_stochastic")
    print("===============")
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


def test_parametric_simple():
    print("test_parametric_simple")
    print("======================")
    axiom = "A(1.0,2.0)B(3.0)"
    rule1 = ProductionRule("A(x,y)", "A(y,x)")
    result = iterate(axiom, 1, [rule1])
    expected = "A(2.0,1.0)B(3.0)"
    assert_equals(expected, result)


def test_parametric():
    print("test_parametric")
    print("===============")
    axiom = "A(2.0, 3.0)B(1.0)"
    rule1 = ProductionRule("A(x,y)", "A(div(x,2),add(x,y))B(x)")

    result = iterate(axiom, 1, [rule1])
    expected = "A(1.0,5.0)B(2.0)B(1.0)"
    assert_equals(expected, result)


def test_set_pen():
    print("test_set_pen")
    print("============")
    axiom = "X"
    rule1 = ProductionRule("X", "p(line)")
    result = iterate(axiom, 1, [rule1])
    expected = "p(line)"
    assert_equals(expected, result)

def assert_equals(expected, actual):
    if actual != expected:
        raise Exception("Expected '" + expected + "' but got '" + actual + "'")

if __name__ == "__main__":

    test_algae()
    # todo test_para()
    test_rand()
    test_stochastic()
    test_parametric_simple()
    test_parametric()
    test_set_pen()
