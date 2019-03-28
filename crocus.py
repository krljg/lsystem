# See figure 3.2 in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf)
# on page [69](http://algorithmicbotany.org/papers/abop/abop.pdf#page=81).

import lsystem.exec

ex = lsystem.exec.Exec()
ex.set_axiom("a(1)")
ex.add_rule("a(t)", "F(1)[\\(30)L(0)]>(137.5)a(add(t,1))", "lt(t,7)")
ex.add_rule("a(t)", "F(20)A", "eq(t,7)")
ex.add_rule("A", "K(0)")
ex.add_rule("L(t)", "L(add(t,1))", "lt(t,9)")  # todo: create Leaf
ex.add_rule("K(t)", "K(add(t,1))", "lt(t,5)")  # todo: create flower
ex.add_rule("F(l)", "F(add(l,0.2))", "lt(l,2)")
ex.exec(min_iterations=7)
