import random
import math
import unittest


class ProductionRule:
    def __init__(self, pattern, result, condition=None):
        self.instance = 0
        self.iteration = 0
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
        self.condition = condition
        self.result = result

    def copy_replace(self, constants):
        new_pattern = self.replace(self.pattern, constants)
        new_result = self.replace(self.result, constants)
        new_condition = self.replace(self.condition, constants)
        return ProductionRule(new_pattern, new_result, new_condition)

    def replace(self, str, constants):
        if str is None:
            return None
        r = str
        for key,value in constants.items():
            r = r.replace(key, value)
        return r

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

    def eval_condition(self, string):
        # print("eval_condition("+string+")")
        i, val = self.parse_expression(string)
        # print("val = "+str(val))
        return val != 0

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

        if self.condition is not None and len(self.condition) > 0:
            if self.eval_condition(self.condition) == 0:
                return False

        self.consumed = input.find(")")+1
        return True

    def parse_parameters(self, string):
        # print("parse_parameters: "+string)
        parameters = list()
        end_ind = 0
        while end_ind < len(string):
            c, val = self.parse_expression(string[end_ind:])
            parameters.append(val)
            end_ind += c
            if string[end_ind] == ')':
                end_ind += 1
                break
            end_ind += 1
        # print("return "+str(end_ind)+", "+str(parameters))
        return end_ind, parameters

    def parse_expression(self, string):
        # print("parse_expression('"+string+"')")
        try:
            if string.startswith("rand("):
                op_len = len("rand(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, random.uniform(values[0], values[1])
            elif string.startswith("add("):
                op_len = len("add(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, values[0]+values[1]
            elif string.startswith("sub("):
                op_len = len("sub(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, values[0] - values[1]
            elif string.startswith("mul("):
                op_len = len("mul(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, values[0] * values[1]
            elif string.startswith("div("):
                op_len = len("div(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, values[0] / values[1]
            elif string.startswith("pow("):
                op_len = len("pow(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, pow(values[0], values[1])
            elif string.startswith("log("):
                op_len = len("log(")
                count, values = self.parse_parameters(string[op_len:])
                if len(values) == 1:
                    return count+op_len, math.log(values[0])
                else:
                    return count+op_len, math.log(values[0], values[1])
            elif string.startswith("sqrt("):
                op_len = len("sqrt(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, math.sqrt(values[0])
            elif string.startswith("sin("):
                op_len = len("sin(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, math.sin(values[0])
            elif string.startswith("cos("):
                op_len = len("cos(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, math.cos(values[0])
            elif string.startswith("tan("):
                op_len = len("tan(")
                count, values = self.parse_parameters(string[op_len:])
                return count+op_len, math.tan(values[0])
            elif string.startswith("eq("):
                op_len = len("eq(")
                count, values = self.parse_parameters(string[op_len:])
                c = count + op_len
                if values[0] == values[1]:
                    return c, 1
                else:
                    return c, 0
            elif string.startswith("lt("):
                op_len = len("lt(")
                count, values = self.parse_parameters(string[op_len:])
                c = count + op_len
                if values[0] < values[1]:
                    return c, 1
                else:
                    return c, 0
            elif string.startswith("gt("):
                op_len = len("gt(")
                count, values = self.parse_parameters(string[op_len:])
                c = count + op_len
                if values[0] > values[1]:
                    return c, 1
                else:
                    return c, 0
            elif string.startswith("gteq("):
                op_len = len("gteq(")
                count, values = self.parse_parameters(string[op_len:])
                c = count + op_len
                if values[0] >= values[1]:
                    return c, 1
                else:
                    return c, 0
            elif string.startswith("get("):
                op_len = len("get(")
                count,values = self.parse_parameters(string[op_len:])
                c = count + op_len
                if values[0] == "i":
                    return c, self.instance
                if values[0] == "iter":
                    return c, self.iteration
            else:
                c = 0
                while c <= len(string) and string[c] != ',' and string[c] != ')':
                    c += 1
                val_str = string[:c]
                if self.param_subs is not None and val_str in self.param_subs:
                    val_str = self.param_subs[val_str]
                try:
                    val = float(val_str)
                    return c,val
                except ValueError:
                    pass
                return c, val_str

        except Exception as e:
            print("string: {}".format(string))
            print(self.param_subs)
            raise e

    def get_result(self, instance, iteration, current_input):
        # print(self.result)
        # print(self.param_subs)
        self.instance = instance
        self.iteration = iteration

        i = 0
        tot_len = len(self.result)
        res = ""
        # assume result of a rule is "module(expression)module(expression)"
        # where (expression) is optional
        while i < tot_len:
            c = self.result[i]
            if c == "(" or c == ",":
                i += 1
                consumed, value = self.parse_expression(self.result[i:])
                i += consumed
                res += c+str(value)
            elif c == "%":
                # find end of branch/object
                consumed = self.scan_end_branch(i+1, current_input)
                self.consumed += consumed
                i += consumed
            else:
                res += c
                i += 1

        return res

    def scan_end_branch(self, start_index, current_input):
        i = start_index
        while i < len(current_input):
            c = current_input[i]
            i += 1
            if c == ']':
                return i

        return i-start_index

    def __str__(self):
        if self.condition is not None and len(self.condition) > 0:
            return "'{}':'{}' -> '{}'".format(self.pattern, self.condition, self.result)
        else:
            return "'{}' -> '{}'".format(self.pattern, self.result)


class LSystem:
    def __init__(self, axiom, rules, replacements):
        self.axiom = axiom
        self.rules = rules
        self.replacements = replacements

    def exec_rules(self, instance, iteration, input, rules):
        result = ""
        i = 0
        while i < len(input):
            current_input = input[i:]
            matching_rules = self.get_matching_rules(current_input)
            if len(matching_rules) > 0:
                chosen_rule = random.choice(matching_rules)
                result += chosen_rule.get_result(instance, iteration, current_input)
                i += chosen_rule.get_consumed()
            else:
                result += input[i]
                i += 1
        return result

    def get_matching_rules(self, string):
        matching_rules = []
        for rule in self.rules:
            if rule.matches(string):
                matching_rules.append(rule)
        return matching_rules

    def iterate(self, instance, iterations):
        result = self.axiom.get_result(instance, 0, "")
        print(result)
        for i in range(0, iterations):
            result = self.exec_rules(instance, i, result, self.rules)
            print(result)
        if self.replacements is not None:
            result = self.exec_rules(instance, 0, result, self.replacements)
            print(result)
        return result


# def exec_rules(instance, iteration, input, rules):
#     result = ""
#     i = 0
#     while i < len(input):
#         current_input = input[i:]
#         matching_rules = get_matching_rules(rules, current_input)
#         if len(matching_rules) > 0:
#             chosen_rule = random.choice(matching_rules)
#             result += chosen_rule.get_result(instance, iteration, current_input)
#             i += chosen_rule.get_consumed()
#         else:
#             result += input[i]
#             i += 1
#     return result
#
#
# def get_matching_rules(rules, string):
#     matching_rules = []
#     for rule in rules:
#         if rule.matches(string):
#             matching_rules.append(rule)
#     return matching_rules
#
#
# def iterate(instance, axiom, iterations, rules):
#     axiomRule = ProductionRule("", axiom)
#     result = axiomRule.get_result(instance, 0, "")
#     # result = axiom
#     for i in range(0, iterations):
#         result = exec_rules(instance, i, result, rules)
#     return result

def run_test(axiom, rules, iterations):
    axiomRule = ProductionRule("", axiom)
    lsystem = LSystem(axiomRule, rules, None)
    return lsystem.iterate(0, iterations)

# Can't use unittests in separate module because of mathutils dependency in __init__.py
class TestLSystem(unittest.TestCase):

    def test_algae(self):
        rule1 = ProductionRule("A", "AB")
        rule2 = ProductionRule("B", "A")
        result = run_test("A", [rule1, rule2], 5)
        expected = "ABAABABAABAAB"
        self.assertEqual(expected, result)

    def test_para(self):
        axiom = "X"
        rule1 = ProductionRule("X", "F+(45)X")
        rule2 = ProductionRule("+(45)", "-(30)")
        result = run_test(axiom, [rule1, rule2], 1)
        expected = "F+(45.0)X"
        self.assertEqual(expected, result)
        result = run_test(axiom, [rule1, rule2], 2)
        expected = "F-(30.0)F+(45.0)X"
        self.assertEqual(expected, result)
        result = run_test(axiom, [rule1, rule2], 3)
        expected = "F-(30.0)F-(30.0)F+(45.0)X"
        self.assertEqual(expected, result)

    def test_rand(self):
        random.seed(0)
        axiom = "X"
        rule = ProductionRule("X", "F+(rand(22,44))X")
        result = run_test(axiom, [rule], 1)
        expected = "F+(38.674996864686655)X"
        self.assertEqual(expected, result)

    def test_stochastic(self):
        axiom = "X"
        rule1 = ProductionRule("X", "FX")
        rule2 = ProductionRule("X", "+X")

        random.seed(0)
        result = run_test(axiom, [rule1, rule2], 1)
        expected = "+X"
        self.assertEqual(expected, result)

        random.seed(0)
        result = run_test(axiom, [rule1, rule2], 3)
        expected = "++FX"
        self.assertEqual(expected, result)

    def test_parametric_simple(self):
        axiom = "A(1.0,2.0)B(3.0)"
        rule1 = ProductionRule("A(x,y)", "A(y,x)")
        result = run_test(axiom, [rule1], 1)
        expected = "A(2.0,1.0)B(3.0)"
        self.assertEqual(expected, result)

    def test_parametric(self):
        axiom = "A(2.0, 3.0)B(1.0)"
        rule1 = ProductionRule("A(x,y)", "A(div(x,2),add(x,y))B(x)")

        result = run_test(axiom, [rule1], 1)
        expected = "A(1.0,5.0)B(2.0)B(1.0)"
        self.assertEqual(expected, result)

    def test_parametric_2(self):
        axiom = "A(1,10)"
        rule1 = ProductionRule("A(l,w)", "¤(w)F(l)[\(45)B(mul(l,0.6),mul(w,0.707))]>(137.5)A(mul(l,0.9),mul(w,0.707))")

        result = run_test(axiom, [rule1], 1)
        expected = "¤(10.0)F(1.0)[\(45.0)B(0.6,7.069999999999999)]>(137.5)A(0.9,7.069999999999999)"
        self.assertEqual(expected, result)

    def test_parametric_with_condition(self):
        axiom = "A(3.0)"
        rule1 = ProductionRule("A(x)", "B(2.0)", "lt(x,2.0)")
        rule2 = ProductionRule("A(x)", "C(4.0)", "gt(x,2.0)")

        result = run_test(axiom, [rule1, rule2], 1)
        expected = "C(4.0)"
        self.assertEqual(expected, result)

    def test_set_pen(self):
        axiom = "X"
        rule1 = ProductionRule("X", "p(line)")
        result = run_test(axiom, [rule1], 1)
        expected = "p(line)"
        self.assertEqual(expected, result)

    def test_math(self):
        axiom = "X(1,0.1)"
        rule1 = ProductionRule("X(x,l)", "¤(sub(1,div(pow(x,2),16)))F(l)X(add(x,l),l)")
        result = run_test(axiom, [rule1], 1)
        expected = "¤(0.9375)F(0.1)X(1.1,0.1)"
        self.assertEqual(expected, result)

    def test_row_of_trees(self):
        axiom = "A(1)"
        rule = ProductionRule("A(s)", "F(s)[+A(div(s,1.456))][-A(div(s,1.456))]")
        result = run_test(axiom, [rule], 2)
        expected = "F(1.0)[+F(0.6868131868131868)[+A(0.47171235358048547)][-A(0.47171235358048547)]][-F(0.6868131868131868)[+A(0.47171235358048547)][-A(0.47171235358048547)]]"
        self.assertEqual(expected, result)

    def test_abscission(self):
        axiom = "AXA"
        rule = ProductionRule("X", "%")
        result = run_test(axiom, [rule], 1)
        expected = "A"
        self.assertEqual(expected, result)

    def test_get_instance(self):
        axiom = "X"
        rule = ProductionRule("X", "F(get(i))")
        result = run_test(axiom, [rule], 1)
        expected = "F(0)"
        self.assertEqual(expected, result)

    def test_get_iterations(self):
        axiom = "X"
        rule = ProductionRule("X", "-(get(iter))F")
        result = run_test(axiom, [rule], 4)
        expected = "-(0)F"
        self.assertEqual(expected, result)

    def test_get_iterations2(self):
        axiom = "X"
        rule = ProductionRule("X", "AX")
        rule2 = ProductionRule("A", "F[-(get(iter))F]")
        result = run_test(axiom, [rule, rule2], 4)
        expected = "F[-(1)F]F[-(2)F]F[-(3)F]AX"
        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
