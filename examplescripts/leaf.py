import lsystem.exec


exec = lsystem.exec.Exec()
exec.set_axiom("p(surface)L(0.45)")
exec.add_rule("L(w1)", "A(w1)C(w1)")
exec.add_rule("A(w1)", "A(w1)B(w1)")
exec.replace("A(w1)", "[:F(0.0)F(1.0)+(90)F(w1);]f(1.0)")
exec.replace("B(w1)", "[:F(0.0)F(1.0)+(90)F(w1)+(90)F(1.0);]f(1.0)")
exec.replace("C(w1)", "[:F(0.0)[F(1.0)]+(90)F(w1);]f(1.0)")
exec.exec(min_iterations=4)
