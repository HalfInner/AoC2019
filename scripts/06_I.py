'''
--- Day 6: Universal Orbit Map ---
You've landed at the Universal Orbit Map facility on Mercury. Because navigation in space often involves transferring between orbits, the orbit maps here are useful for finding efficient routes between, for example, you and Santa. You download a map of the local orbits (your puzzle input).

Except for the universal Center of Mass (COM), every object in space is in orbit around exactly one other object. An orbit looks roughly like this:

                  \
                   \
                    |
                    |
AAA--> o            o <--BBB
                    |
                    |
                   /
                  /
In this diagram, the object BBB is in orbit around AAA. The path that BBB takes around AAA (drawn with lines) is only partly shown. In the map data, this orbital relationship is written AAA)BBB, which means "BBB is in orbit around AAA".

Before you use your map data to plot a course, you need to make sure it wasn't corrupted during the download. To verify maps, the Universal Orbit Map facility uses orbit count checksums - the total number of direct orbits (like the one shown above) and indirect orbits.

Whenever A orbits B and B orbits C, then A indirectly orbits C. This chain can be any number of objects long: if A orbits B, B orbits C, and C orbits D, then A indirectly orbits D.

For example, suppose you have the following map:

COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
Visually, the above map of orbits looks like this:

        G - H       J - K - L
       /           /
COM - B - C - D - E - F
               \
                I
In this visual representation, when two objects are connected by a line, the one on the right directly orbits the one on the left.

Here, we can count the total number of orbits as follows:

D directly orbits C and indirectly orbits B and COM, a total of 3 orbits.
L directly orbits K and indirectly orbits J, E, D, C, B, and COM, a total of 7 orbits.
COM orbits nothing.
The total number of direct and indirect orbits in this example is 42.

What is the total number of direct and indirect orbits in your map data?
'''

import sys
import anytree

def calculate_depth(universe, planet='COM', depth=0):
    # print('{}>{}({})'.format('--' * depth, planet, depth), end='\n')

    if planet not in universe:
        return 0, depth

    cur_indirect_orbits = depth
    cur_direct_orbits = len(universe[planet])
    for planet in universe[planet]:
        planet_direct_orbits, planet_indirect_orbits = calculate_depth(universe, planet, depth + 1)
        cur_direct_orbits += planet_direct_orbits
        cur_indirect_orbits += planet_indirect_orbits
    
    # print('Steps', cur_direct_orbits, cur_indirect_orbits)
    return cur_direct_orbits, cur_indirect_orbits

def assembly_universe(orbits):
    universe = {}
    for source, ring in orbits:
        if source not in universe.keys():
            universe[source] = []
        universe[source].append(ring)
    print('Universe', universe)
    return universe
    

def parse_file(file_path : str):
    orbits = []
    with open(file_path, 'r') as f:
        for line in f:
            orbit = line.replace('\n','').replace('\r', '').split(')')
            orbits.append((orbit[0], orbit[1]))
    return orbits

def main(argv):
    center_of_mass = 'COM'
    print(calculate_depth(assembly_universe(parse_file(argv[1])), center_of_mass))
    

    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
