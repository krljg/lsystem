
# Installation #

Copy lsystem directory over to
  _F:\SteamLibrary\steamapps\common\Blender\2.78\scripts\addons_
or wherever your blender installation is.

In blender go to File->User Preferences->Add-ons and enable
 "Add Mesh: LSystem" then press the "Save User Settings" button.

# Usage #

 Add a mesh via Add->Mesh->LSystem. Change the settings in the LSystem panel to get something halway decent.

## Turtle interpretation of symbols ##

| Symbol | Interpretation                           |
|--------|------------------------------------------|
| F      | Move forward and produce an edge ( a branch segment ) |
| +      | Turn left                                |
| -      | Turn right                               |
| /      | Pitch up                                 |
| \      | Pitch down                               |
| <      | Roll left                                |
| >      | Roll right                               |
| [      | Start a branch (push state)              |
| ]      | Complete a branch (pop state)            |
| !      | Expand segment radius                    |
| @      | Diminish segment radius                  |
| #,%    | Fatten or slink the radius of the branch |
| {      | Start a new blender object               |
| }      | End current blender object               |

F,+,-,/,\,<,>,!,@,#,% use the configured default values in settings panel but this
can also be specified directly in the axiom and the production rules. For example
+(90) would indicate a 90 degree turn to the left.

## Production Rules ##

### Random values ###
It's possible to specify random numbers in production rules, for example +(rand(45,90)) would
give a random left turn between 45 and 90 degrees.

### Stochastic rules ###

If there are several rules that match the same input one of the matching rules will be
selected at random.

# Example #

![screenshot](https://github.com/krljg/lsystem/blob/master/examples/sort_of_a_tree_screenshot.png)

# See Also #

https://en.wikipedia.org/wiki/L-system

https://www.reddit.com/r/proceduralgeneration/comments/5771ea/making_fractal_trees_in_blender/

https://16bpp.net/blog/post/making-fractal-trees-in-blender

https://github.com/ento/blender-lsystem-addon

http://michelanders.blogspot.se/p/creating-blender-26-python-add-on.html

http://algorithmicbotany.org/papers/#abop

http://algorithmicbotany.org/papers/abop/abop.pdf