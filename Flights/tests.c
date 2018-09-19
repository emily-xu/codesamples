#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "flight_map.h"

int cities_match(const char** actual, const char** expected) {
     for (; *actual != NULL && *expected != NULL; ++actual, ++expected) {
          if (strcmp(*actual, *expected) != 0) {
               return 0;
          }
     }
     return (*actual == NULL && *expected == NULL);
}

int main() {
     // empty_map
     {
          // create a map
          map_t *map = map_create();
          // check that the number of cities in the map is 0
          assert(num_cities(map) == 0); 
          // free the map
          map_free(map);
     }

     // add and link cities
     {
          const char** result;
          map_t *map = map_create();
          // add a city named "abc" to the map
          assert(add_city(map, "abc") == 1);
          assert(add_city(map, "def") == 1);
          assert(num_cities(map) == 2);
          // assert(add_city(map, "def") == 0);
          // assert(remove_city(map, "abc"));
          // assert(num_cities(map) == 1);
          // assert(remove_city(map, "hey") == 0);
          // assert(remove_city(map, "def"));
          // assert(num_cities(map) == 0);
          // printf("passed for now\n");

          //link the cities named "abc" and "def"
          assert(link_cities(map, "abc", "def"));
          assert(unlink_cities(map, "abc", "def"));

          // get a list of the cities linked to "abc"
          result = linked_cities(map, "abc");
          assert(cities_match(result, (const char*[]){NULL}));
          // check that the list returned matches {"def", NULL}
          //assert(cities_match(
          //            result,
          //            (const char*[]){"def", NULL}));
          // free the returned list
          free(result);
          map_free(map);
     }

     // find path
     {
          const char** result;
          map_t* map = map_create();
          add_city(map, "abc");
          add_city(map, "def");
          add_city(map, "ghi");

          // result = find_path(map, "abc", "abc");
          // assert(cities_match(result, (const char*[]){"abc", NULL}));

          link_cities(map, "abc", "def");
          // link_cities(map, "def", "ghi");

          // get a list of cities forming a path between "abc" and "ghi"
          result = find_path(map, "abc", "ghi");
          assert(result == NULL);
          // assert(cities_match(
          //             result,
          //             (const char*[]){"abc", "def", "ghi", NULL}));
          free(result);
          map_free(map);
     }

     printf("ALL TESTS PASS!\n");
}
