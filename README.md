# NoodleMapFixer
A simple tool aim to fix old Beat Saber maps that use both MappingExtensions and NoodleExtensions and convert them to using NoodleExtensions only

## Limitations
Currently there are many assumption made for the map.
 - Only support V2 mapping
 - Only look at walls
 - Will only attempt to convert MappingExtensions objects positioning and wall scaling!
 - Negative wall duration is not really supported by the game, will use noodle to simulate a similar behaviour (there are a few parameters tweakable)

## TODO
May be implemented when I try to fix a map that needs it
 - Convert notes
 - Convert some walls to Chroma lights?
