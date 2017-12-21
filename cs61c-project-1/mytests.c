#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "flight_map.h"

int main() {
     // empty_map
     {
          // create a map
          map_t *map = map_create();
          // free the map
          map_free(map);
     }
}