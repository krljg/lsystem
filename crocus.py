# See figure 3.2 in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf)
# on page [69](http://algorithmicbotany.org/papers/abop/abop.pdf#page=81).

import lsystem.lsystem
import lsystem.exec
import math
exec = lsystem.exec.Exec()
exec.set_axiom("a(1)")
exec.add_rule("a(t)", "F(1)[\\(30)L(0)]>(137.5)a(add(t,1))", "lt(t,7)")
exec.add_rule("a(t)", "F(20)A", "eq(t,7)")
exec.add_rule("A", "K(0)")
exec.add_rule("L(t)", "L(add(t,1))", "lt(t,9)")  # todo: create Leaf
exec.add_rule("K(t)", "K(add(t,1))", "lt(t,5)")  # todo: create flower
exec.add_rule("F(l)", "F(add(l,0.2))", "lt(l,2)")
exec.exec(min_iterations=7)
