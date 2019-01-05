
# Installation #

Copy lsystem directory over to
  _F:\SteamLibrary\steamapps\common\Blender\2.79\scripts\addons_
or wherever your blender installation is.

In blender go to File->User Preferences->Add-ons and enable
 "Add Mesh: LSystem" then press the "Save User Settings" button.

# Usage #

 Add a mesh via Add->Mesh->LSystem. Change the settings in the LSystem panel to get something halway decent.

## Turtle interpretation of symbols ##

| Symbol | Interpretation                           | Example |
|--------|------------------------------------------|---------|
| F      | Move forward and produce an edge ( a branch segment ) |
| f      | Move forward without producing an edge   |
| +      | Turn left                                |
| -      | Turn right                               |
| /      | Pitch up                                 |
| \      | Pitch down                               |
| <      | Roll left                                |
| >      | Roll right                               |
| $      | Rotate upright                           |
| [      | Start a branch (push state)              |
| ]      | Complete a branch (pop state)            |
| #,%    | Fatten or slink the radius of the branch |
| ¤      | Set radius                               |
| {      | Start a new blender object               |
| }      | End current blender object               |
| ~      | Copy an existing blender object (requires the name of the object to be copied as a parameter) |
| p      | Change pens, requires a value (see table below). | p(subsurf) |
| m      | Set material, requires the name of the material. Note that the material applies to an entire blender object. If you set the material multiple times for the same object the material value will simply be overwritten. | m(Green)
| s      | scale                                    |
| :      | Start a polygon/face from vertices (only applicable to the "surface" pen |
| ;      | End a polygon/face from vertices (only applicable to the "surface" pen |

F,+,-,/,\,<,>,!,@,#,% use the configured default values in settings panel but this
can also be specified directly in the axiom and the production rules. For example
+(90) would indicate a 90 degree turn to the left.

### Pens ###

| Name   |             |
|--------|-------------|
| surface| Produces a surface of one or more faces from a set of vertices |
| pol    | Produces a single polygon |
| edge   | Produces a single edge between two vertices | 
| skin   | Same as edge but applies a skin modifier automatically. This allows the l-system to set the skin radius. |
| subsurf| Same as skin but with a surface subdivision modifier also. |
| curve  | A bezier curve. |
| line   | Produces a quad |
| cylXXX | Produces a cylinder with XXX number of vertices (must be 3 or higher). For example _cyl4_ produces a cylinder with 4 vertices |
 
## Production Rules ##

Production rules consist of three fields: 

  1. A module either a single character 
     module or a single character followed by parenthesis and parameters names (ie A(x,y)).
     The second field is the condition that has to be true if rule is applicable.
  2. This field is only relevant if the module has parameters. Conditions are 
     expressed as boolean expressions (ie eq(x,0) which would mean the rule applies when x is 0)
  3. The third field is the result. This what the module in the first field will 
     be replaced with if the condition is true. Mathematical expressions can be used
     here with parameters if they occur in the module field (see below for supported functions). 

Example:
```
  A(x,y): gt(x,1) -> A(mul(x,y),div(x,y))F(x)+(rand(0,y))
```

### Mathematical functions ###
| Name      |      | Example |
|-----------|------|---------|
| rand(x,y) | random number between x,y | rand(0,90) |
| add(x,y)  | addition | add(1,4) = 1+4 |
| sub(x,y)  | substraction | sub(2,3) = 2-3 |
| mul(x,y)  | multiply | mul(2,3) = 2*3 |
| div(x,y)  | divide   | div(4,6) = 4/6 |
| pow(x,y)  | x to the power of y | pow(2,3) = 2^3 |
| log(x)    | natural logarithm of x | log(12) |
| log(x,y)  | logarithm of x to the base of y | log(4,2) |
| sqrt(x)   | square root of x | |
| sin(x)    | sine of x | |
| cos(x)    | cosine of x | |
| tan(x)    | tangent of x | |
| eq(x,y)   | is equal | eq(1,0) (false) |
| gt(x,y)   | is x greater than y | gt(1,2) (false) |
| lt(x,y)   | is x less than y | lt(1,2) (true) |
| get(x)    | get property x, currently only the current number of iterations is available represented by _i_ | get(i)

### Stochastic rules ###

If there are several rules that match the same input one of the matching rules will be
selected at random.

### Running from a Script ###

```
import lsystem.lsystem
import lsystem.exec
exec = lsystem.exec.Exec()
exec.set_axiom("p(subsurf)X")
exec.add_rule("X", "F[+X][-X]")
exec.add_rule("X", "<X")
exec.exec()
```

#### Animation ####
When running from a script the growth of the lsystem can be animated.
```
exec.exec(min_iterations=1, max_iterations=5, animate=True)
bpy.context.scene.frame_start=0
bpy.context.scene.frame_end=25
bpy.ops.screen.animation_play()
```
Animation is achieved by generating the blender objects for all iterations between min_iterations 
and max_iterations and then setting the hide property to true or false depending on the frame.

# Examples #

## Sierpinski Gasket ##

See figure 1.10 b in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [11](http://algorithmicbotany.org/papers/abop/abop.pdf#page=23).

Script:
```
import lsystem.lsystem
import lsystem.exec
import math
exec = lsystem.exec.Exec()
exec.set_axiom("p(curve)Fr")
exec.add_rule("Fa", "Fr+Fa+Fr")
exec.add_rule("Fr", "Fa-Fr-Fa")
exec.exec(min_iterations=6, angle=math.radians(60))
```

GUI:

![screenshot](https://github.com/krljg/lsystem/blob/master/examples/sierpinski_gasket.png)

## Fractal Plant ##

See figure 1.24 f in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [25](http://algorithmicbotany.org/papers/abop/abop.pdf#page=37).

Script:
```
import lsystem.lsystem
import lsystem.exec
import math
exec = lsystem.exec.Exec()
exec.set_axiom("X")
exec.add_rule("X", "F-[[X]+X]+F[+FX]-X")
exec.add_rule("F", "FF")
exec.exec(min_iterations=4, angle=25)
```

GUI:

![screenshot](https://github.com/krljg/lsystem/blob/master/examples/fractal_plant.png)

## A Three-Dimensional Bush-Like Structure ##

See figure 1.25 f in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [26](http://algorithmicbotany.org/papers/abop/abop.pdf#page=38).

Script (colour omitted):
```
import lsystem.lsystem
import lsystem.exec
import math
exec = lsystem.exec.Exec()
exec.set_axiom("p(skin)A")
exec.add_rule("A", "[\FaL%A]>>>>>[\FaL%A]>>>>>>>[\FaL%A]")
exec.add_rule("Fa", "S>>>>>Fa")
exec.add_rule("S", "FaL")
exec.add_rule("L", "[//{p(surface)-F+F+F-+(180)-F+F+F}]") 
exec.exec(min_iterations=7, angle=22.5) 
```

## Plant ##

See figure 1.26 in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [27](http://algorithmicbotany.org/papers/abop/abop.pdf#page=39).

Script:
```
import lsystem.lsystem
import lsystem.exec
import math
exec = lsystem.exec.Exec()
exec.set_axiom("P")
exec.add_rule("P", "I+[P+R]-->>[--L]I[++L]-[PR]++PR")
exec.add_rule("I", "FS[>>\\\\L][>>//L]FS")
exec.add_rule("S", "SFS")
exec.add_rule("L", "[{p(surface)+F-FF-F++(180)+F-FF-F}]")
exec.add_rule("R", "[\\\\\\C>W>>>>W>>>>W>>>>W>>>>W]")
exec.add_rule("C", "FF")
exec.add_rule("W", "[/F][{p(surface)\\\\\\\\-F+F+(180)-F+F}]")
exec.exec(min_iterations=5, angle=18) 
```

## Monopodial Tree-like Structure ##

See figure 2.6 a in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [56](http://algorithmicbotany.org/papers/abop/abop.pdf#page=68).

As the rules aren't visible in the picture, here they are:

```
A(l,w) -> ¤(w)F(l)[\(45)B(mul(l,0.6),mul(w,0.707))]>(137.5)A(mul(l,0.9),mul(w,0.707))
B(l,w) -> ¤(w)F(l)[-(45)C(mul(l,0.6),mul(w,0.707))]C(mul(l,0.9),mul(w,0.707))
C(l,w) -> ¤(w)F(l)[+(45)B(mul(l,0.6),mul(w,0.707))]B(mul(l,0.9),mul(w,0.707))
```

Script:
```
import lsystem.lsystem
import lsystem.exec
exec = lsystem.exec.Exec()
exec.set_axiom("p(skin)A(1,0.1)")
exec.add_rule("A(l,w)", "¤(w)F(l)[\(45)B(mul(l,0.6),mul(w,0.707))]>(137.5)A(mul(l,0.9),mul(w,0.707))")
exec.add_rule("B(l,w)", "¤(w)F(l)[-(45)C(mul(l,0.6),mul(w,0.707))]C(mul(l,0.9),mul(w,0.707))")
exec.add_rule("C(l,w)", "¤(w)F(l)[+(45)B(mul(l,0.6),mul(w,0.707))]B(mul(l,0.9),mul(w,0.707))")
exec.exec(min_iterations=10)
```

GUI:

![screenshot](https://github.com/krljg/lsystem/blob/master/examples/monopodial_treelike_structure.png)

## Surface ##

Surface specification using a tree structure as a framework (Figure 5.4 in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [122](http://algorithmicbotany.org/papers/abop/abop.pdf#page=134).)
```
import lsystem.lsystem
import lsystem.exec
exec = lsystem.exec.Exec()
exec.set_axiom("p(surface)[++++F(1.0)] [++F(2.0)] [+F(3.0)] [F(5.0)] [-F(3.0)] [--F(2.0)] [----F(1.0)]")
exec.exec(min_iterations=1, angle=30)
```

Cordate leaf (Figure 5.5 in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [123](http://algorithmicbotany.org/papers/abop/abop.pdf#page=135).)
```
import lsystem.lsystem
import lsystem.exec
exec = lsystem.exec.Exec()
exec.set_axiom("p(surface)[A][B]")
exec.add_rule("A", "[+A:F(0)]F(0)CF(0);")
exec.add_rule("B", "[-B:F(0)]F(0)CF(0);")
exec.add_rule("C", "f(1.0)C")
```

Simple leaf (Figure 5.6 b in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [124](http://algorithmicbotany.org/papers/abop/abop.pdf#page=136))
```
import lsystem.lsystem
import lsystem.exec
exec = lsystem.exec.Exec()
exec.set_axiom("p(surface)F(0)A(0)")
exec.add_rule("A(t)", "f(5,1)[-B(t)F(0)][A(add(t,1))][+B(t)F(0)]")
exec.add_rule("B(t)", "f(1,1)B(sub(t,1))", condition="gt(t,0)")
exec.add_rule("f(s,r)", "f(mul(s,r),r)")
exec.exec(min_iterations=20, angle=60)
```

Rose leaf (Figure 5.8 in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [126](http://algorithmicbotany.org/papers/abop/abop.pdf#page=138))
```
import lsystem.lsystem
import lsystem.exec
exec = lsystem.exec.Exec()
exec.set_axiom("p(surface)[:A(0,0)F(0);][:A(0,1)F(0);]")
exec.add_rule("A(t,d)", "F(0)f(5,1.15)F(0)[+B(t)f(3,1.19,t)F(0);][+B(t):F(0)]A(add(t,1),d)", condition="eq(d,0)")
exec.add_rule("A(t,d)", "F(0)f(5,1.15)F(0)[-B(t)f(3,1.19,t)F(0);][-B(t):F(0)]A(add(t,1),d)", condition="eq(d,1)")
exec.add_rule("B(t)", "f(1.3,1.25)B(sub(t,1))", condition="gt(t,0)")
exec.add_rule("f(s,r)", "f(mul(s,r),r)")
exec.add_rule("f(s,r,t)", "f(mul(s,r),r,sub(t,1))", condition="gt(t,1)")
exec.exec(min_iterations=25, angle=60)
```

Compound leaves (Figure 5.11 b in [Algorithmic Beauty of Plants](http://algorithmicbotany.org/papers/abop/abop.pdf) on page [129](http://algorithmicbotany.org/papers/abop/abop.pdf#page=141))
```
import lsystem.lsystem
import lsystem.exec
exec = lsystem.exec.Exec()
exec.set_axiom("p(edge)A(0)")
exec.add_rule("A(d)", "A(sub(d,1))", condition="gt(d,0)")
exec.add_rule("A(d)", "F(1)[+A(1)][-A(1)]F(1)A(0)", condition="eq(d,0)")
exec.add_rule("F(a)", "F(mul(a,1.5))")
exec.exec(min_iterations=12)
```

# See Also #

https://en.wikipedia.org/wiki/L-system

https://www.reddit.com/r/proceduralgeneration/comments/5771ea/making_fractal_trees_in_blender/

https://16bpp.net/blog/post/making-fractal-trees-in-blender

https://github.com/ento/blender-lsystem-addon

http://michelanders.blogspot.se/p/creating-blender-26-python-add-on.html

http://algorithmicbotany.org/papers/#abop

http://algorithmicbotany.org/papers/abop/abop.pdf

http://archive.org/stream/BrainfillingCurves-AFractalBestiary/BrainFilling#page/n0/mode/2up