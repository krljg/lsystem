# See figure 3.5 in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf)
# on page [74](http://algorithmicbotany.org/papers/abop/abop.pdf#page=86).

import lsystem.exec

ex = lsystem.exec.Exec()
ex.set_axiom("p(edge)I(9)aa(13)")
ex.add_rule("aa(t)", "[&(70)L]/(137.5)I(10)aa(sub(t,1))", "gt(t,0)")
ex.add_rule("aa(t)", "[&(70)L]/(137.5)I(10)A", "eq(t,0)")
ex.add_rule("A", "[&(18)uu(4)FFI(10)I(5)X(5)KKKK]/(137.5)I(8)A")
ex.add_rule("I(t)", "FI(sub(t,1))", "gt(t,0)")
ex.add_rule("I(t)", "F", "eq(t,0)")
ex.add_rule("ii(t)", "fii(sub(t,1))", "gt(t,0)")
ex.add_rule("ii(t)", "f", "eq(t,0)")
ex.add_rule("uu(t)", "&(9)uu(sub(t,1))", "gt(t,0)")
ex.add_rule("uu(t)", "&(9)", "eq(t,0)")
ex.add_rule("L", ":p(surface)[{F(0)-fI(7)+fI(7)+fI(7)}][{F(0)+fI(7)-fI(7)-fI(7)}];")
ex.add_rule("K", ":p(surface)[&{F(0)+fI(2)--fI(2)}][&{F(0)-fI(2)++fI(2)}]/(90);")
ex.add_rule("X(t)", "X(sub(t,1))", "gt(t,0)")
ex.add_rule("X(t)", "^(50)[[-ffff++[fff[++f{F(0)]F(0)]F(0)]F(0)++ffffF(0)--fffF(0)--fF(0)}]%", "eq(t,0)")

ex.exec(min_iterations=1, max_iterations=16)

