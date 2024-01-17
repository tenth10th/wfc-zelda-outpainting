# Wave Function Collapse Experiments

Using examples from blog posts, and retro gaming graphics, do some experiments with pseudo-random map generation via "wave function collapse" (arguably, more of a superposition collapse?)

Inspired by example code from this blog post:

https://dev.to/kavinbharathi/the-fascinating-wave-function-collapse-algorithm-4nc3

And using the more convenient Zelda tile and map data from the "Zelda Walking Tour" Git Repo:

https://github.com/asweigart/nes_zelda_map_data/blob/master/overworld_map/labeled_overworldtiles.png

Given that Wave Function Collapse can be implemented to "learn" rules from existing data, it seemed as though it should be able to read classic video game maps (for example, [the overworld map](/data/zelda_worldmap_single_image.png) from the NES Legend of Zelda), and generate similar maps - Or perform "outpainting", rendering an additional world beyond the original...

### wfc-example.py

_(initial rough prototype)_

While I found the original blog post to be educational and illustrative of WFC as a concept, it is (admittedly) missing some features, including "retries" (when the function is unable to collapse), as well as any concept of "weight" or probabilities in the function, even if they're available in the training data.

I also ran into some issues with the Walking Tour tileset data, which includes many "blank" tiles that don't appear in the actual map, and have no neighbors, which drastically increases the chance that the algorithm will get stuck in a non-collapsible state...

(And without weights, the resulting maps are _very_ random, and the performance is not great, though arguably it will only create combinations of tiles that appear in the original game...)

### wfc_model.py

Our first attempt at re-implementing the Waveform Collapse Function in more modern Python, with type annotations, dataclasses, a tileset that can record and use proportional "weights" (based on the number of times tiles appear adjacent to one another), and a generally leaner, cleaner, more functional, and hopefully more performance-optimizable structure...

As of 1/16/2024, we have a good start on a "collapse" function, but need to integrate it with the map and renderer.

### wfc_render.py

The start of a cleaner rendering engine - Currently, if run, it can display the tileset (as per the original walking tour layout), separate the tiles by blocking/passable status, or render the original overworld map and scroll around using the arrow keys. (Still needs to be integrated with the actual WFC code!)
