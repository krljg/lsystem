# See 4.2.3 Exploration of Parameter Space in "Visual Models of Plant Development" by Prusinkiewicz et al.

import lsystem.exec


def ex(consts, index):
    exec = lsystem.exec.Exec()
    for key in consts.keys():
        exec.define(key, str(consts[key][index]))
    exec.set_axiom("p(edge)¤(w0)f(0)A(10,w0)")
    exec.add_rule("A(s,w)", "¤(w)F(s)[+(a1)>(f1)A(mul(s,r1),mul(w,pow(q0,e0)))][+(a2)>(f2)A(mul(s,r2),mul(w,pow(sub(1,q0),e0)))]", condition="gteq(s,min)")
    exec.exec(min_iterations=consts["n0"][index])
    return exec


consts = dict()
consts["r1"] = ["0.75", "0.65", "0.50", "0.60", "0.58", "0.92", "0.80", "0.95", "0.55"]
consts["r2"] = ["0.77", "0.71", "0.85", "0.85", "0.83", "0.37", "0.80", "0.75", "0.95"]
consts["a1"] = [ "35",    "27",   "25",   "25",   "30",    "0",   "30",    "5",   "-5"]
consts["a2"] = ["-35",   "-68",  "-15",  "-15",   "15",   "60",  "-30",  "-30",   "30"]
consts["f1"] = [  "0",     "0",  "180",  "180",    "0",  "180",  "137",  "-90",  "137"]
consts["f2"] = [  "0",     "0",    "0",  "180",  "180",    "0",  "137",   "90",  "137"]
consts["w0"] = [  "3",     "2",    "2",    "2",    "2",  "0.2",    "3",    "4",  "0.5"]
consts["q0"] = ["0.50", "0.53", "0.45", "0.45", "0.40", "0.50", "0.50", "0.60", "0.40"]
consts["e0"] = ["0.40", "0.50", "0.50", "0.50", "0.50", "0.00", "0.50", "0.45", "0.00"]
consts["min"] =[ "0.0",  "1.7",  "0.5",  "0.0",  "1.0",  "0.5",  "0.0", "25.0",  "5.0"]
consts["n0"] = [    10,     12,      9,     10,     11,     15,     10,     12,     12]

bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
exec = ex(consts, 2)
