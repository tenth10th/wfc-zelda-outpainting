# Wave Function Collapse Experiments

Using examples from blog posts, and retro gaming graphics, do some experiments with pseudo-random map generation via "wave function collapse" (arguably, more of a superposition collapse?)

Inspired by example code from this blog post:

https://dev.to/kavinbharathi/the-fascinating-wave-function-collapse-algorithm-4nc3

And more convenient Zelda tile and map data from this Git Repo:

https://github.com/asweigart/nes_zelda_map_data/blob/master/overworld_map/labeled_overworldtiles.png

While I found the example to be education, it inspired me to try my own implementation...

## Status

Sort of works? But not all of the tiles are actually used in the Map data, leading to most map generations immediately failing for lack of neighbors...

I would also like to take a shot at re-implementing this algorithm, re-naming some stuff, and possibly improving the performance. (And making the Zelda example more functional...)