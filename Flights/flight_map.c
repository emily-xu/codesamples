#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "flight_map.h"

// A safe version of malloc, that will exit the program in case your allocation
// fails.
void *checked_malloc(size_t size) {
     void *ptr = malloc(size);
     if (ptr == NULL) {
          fprintf(stderr, "memory allocation failed\n");
          exit(1);
     }
     return ptr;
}

// map_t object
struct map_t {
     struct city** citylist;  // collection of city objects
     int numcities;  // number of cities in the citylist
};

// city object
typedef struct city {
     char* name;  // city name
     struct city* next;  // next city in linked 
     struct flight** flightlist; // pointer to array of pointers to other cities
     int numflights; // number of flights
     char** linkedlist; //pointer to list of city names
     int marked; // 0 = not marked, 1 = marked
     struct city* prev; // previous city in path
     char** path; // path starting at city
} city;

// flight object
typedef struct flight {
     city* city;
     struct flight* next;
} flight;

// returns pointer to new map_t instance
map_t* map_create() {
     map_t* map = NULL;     
     map = (map_t*) malloc(sizeof(struct map_t)); // allocate memory for a map
     if (map == NULL) {
          printf("Memory Error\n");
          exit(1);
     }
     map->citylist = (city**) malloc(sizeof(city*));
     *(map->citylist) = NULL;
     map->numcities = 0;
     return map;
}

void free_flights(flight** flightlist) {
     flight* node = *flightlist;
     while(node) {
          flight* temp = node;
          node = node->next;
          free(temp);
          temp = NULL;
     }
     free(flightlist);
}

// frees all cities on citylist
void free_list(city** citylist) {
     city* node = *citylist;
     while(node) {
          city* temp = node;
          node = node->next;
          free(temp->name);
          temp->name = NULL;
          free_flights(temp->flightlist);
          temp->flightlist = NULL;
          free(temp);
          temp = NULL;
     }
     free(citylist);
}

// frees entire map
void map_free(map_t* map) {
     free_list(map->citylist);
     map->citylist = NULL;
     free(map);
     map = NULL;
}

// find if city is in citylist
int find(city** citylist, const char* name) {
     city* this = *citylist;
     // iterate through list
     while(this) {
          if(strcmp(this->name, name) == 0) {
               return 1;  // found in list
          }
          this = this->next;
     }
     return 0;  // not found
}


// adding cities to citylist
void push(city** citylist, const char* name) {     
     city* new = (city*) malloc(sizeof(city));
     if (new == NULL){
          printf("Memory Error\n");
          exit(1);
     }
     new->name = (char*) malloc(sizeof(name));
     strcpy(new->name, name);
     new->next = *citylist;
     new->numflights = 0;
     new->flightlist = (flight**) malloc(sizeof(flight*));
     *(new->flightlist) = NULL;
     *citylist = new;
}

// calls push
int add_city(map_t* map, const char* name) {
     if(map->numcities != 0) {
          if(find(map->citylist, name)) {
               return 0;  // found duplicate
          }
     }     
     push(map->citylist, name);
     map->numcities += 1;
     return 1;
}


void pop_first(city** citylist, const char* name) {
     city* temp = (*citylist)->next;
     city* curr = *citylist;
     free(curr->name);
     curr->name = NULL;
     free_flights(curr->flightlist);
     free(curr);
     *citylist = temp;
}

// removes cities from citylist
int pop(city** citylist, const char* name) {
     city* this = *citylist;
     if(strcmp(this->name, name) == 0) {
          pop_first(citylist, name);
          return 1;
     }
     city* prev = *citylist;
     this = this->next;
     while(this) {
          if(strcmp(this->name, name) == 0) {
               prev->next = this->next;
               free(this->name);
               this->name = NULL;
               free_flights(this->flightlist);
               free(this);
               this = NULL;
               return 1;
          }
          prev = this;
          this = this->next;
     }
     return 0;
}

// calls pop
int remove_city(map_t* map, const char* name) {
     // looks for city in citylist
     if(find(map->citylist, name)) {
          // city found so remove
          pop(map->citylist, name);
          map->numcities -= 1;
          return 1;
     }
     else {
          // city not found
          return 0;
     }
}

// number of cities on citylist
int num_cities(map_t* map) {
     return map->numcities;
}

// return pointer to a city
city* get_city(city** citylist, const char* name) {
     city* this = *citylist;
     while(this) {
          if(strcmp(this->name, name) == 0) {
               return this;
          }
          this = this->next;
     }
     return NULL;
}

// find if flight is in flightlist
int find_flight(flight** flightlist, const char* name) {
     flight* this = *flightlist;
     // iterate through list
     while(this) {
          if(strcmp((this->city)->name, name) == 0) {
               return 0;  // found in list
          }
          this = this->next;
     }
     return 1;  // not found
}

// adds pointer to some city to flightlist
void add_flight(flight** flightlist, city* c) {
     flight* new = (flight*) malloc(sizeof(flight));
     new->city = c;
     new->next = *flightlist;
     *flightlist = new;
}

// add link between two cities
int link_cities(map_t* map, const char* city1_name, const char* city2_name) {
     if(find(map->citylist, city1_name) & find(map->citylist, city2_name)) {
          // if both cities exist
          city* city1 = get_city(map->citylist, city1_name);  // pointer to city1
          city* city2 = get_city(map->citylist, city2_name);  // pointer to city2
          if(find_flight(city1->flightlist, city2_name) & strcmp(city1_name, city2_name)) {
               // not already in either flightlist
               add_flight(city1->flightlist, city2);
               city1->numflights += 1;
               add_flight(city2->flightlist, city1);
               city2->numflights += 1;
               return 1;
          }
     }
     return 0;
}

void remove_flight(flight** flightlist, const char* name) {
     flight* this = *flightlist;
     if(strcmp((this->city)->name, name) == 0) {
          // if flight is first in the list
          flight* temp = (*flightlist)->next;
          flight* curr = *flightlist;
          curr->city = NULL; // is this necessary?
          free(curr);
          curr = NULL;
          *flightlist = temp;
          return;
     }
     flight* prev = *flightlist;
     this = this->next;
     while(this) {
          if(strcmp((this->city)->name, name) == 0) {
               prev->next = this->next;
               this->city = NULL;
               free(this);
               this = NULL;
               return;
          }
          prev = this;
          this = this->next;
     }
}

int unlink_cities(map_t* map, const char* city1_name, const char* city2_name) {
     if(find(map->citylist, city1_name) & find(map->citylist, city2_name)) {
          // if both cities exist
          city* city1 = get_city(map->citylist, city1_name);  // pointer to city1
          city* city2 = get_city(map->citylist, city2_name);  // pointer to city2
          if(find_flight(city1->flightlist, city2_name) == 0) {
               // found in flightlist
               remove_flight(city1->flightlist, city2_name);
               city1->numflights -= 1;
               remove_flight(city2->flightlist, city1_name);
               city2->numflights -= 1;
               return 1;
          }
     }
     return 0;
}

char** get_flights(city* city) {
     flight* this = *(city->flightlist); // pointer to flightlist
     int f = (city->numflights) + 1; // number of flights + 1 = size of array
     char** array = (char**) malloc(f * (sizeof(char*))); // allocate array
     int i = 0;
     while(this) {
          array[i] = (this->city)->name;
          i += 1;
          this = this->next;
     }
     array[f - 1] = NULL;
     return array;
}

// return array of cities directly linked to a given city
const char** linked_cities(map_t* map, const char* city_name) {
     if(find(map->citylist, city_name) == 0) {
          // city doesn't exist
          return NULL;
     }
     city* this = get_city(map->citylist, city_name); // get pointer to the city
     if(this->numflights == 0) {
          // city has no links
          this->linkedlist = (char**) calloc( 1, sizeof(char*));
          return (const char**) this->linkedlist;
     }
     else {
          this->linkedlist = get_flights(this);
          return (const char**) this->linkedlist;
     }
}

void clear(city** citylist) {
     city* this = *citylist;
     while(this) {
          this->marked = 0;
          this->prev = NULL;
          this = this->next;
     }
}

// recursive function Depth First Search
city* path(city* source, city* end) {
     flight** flightlist = source->flightlist; // search flights from source
     flight* flight = *flightlist; // first flight in flightlist
     while(flight) {
          // while flight is not NULL
          if ((flight->city)->marked == 0) {
               // flight is not visited yet
               (flight->city)->prev = source; // record previous 
               (flight->city)->marked = 1;  // mark visit
               if(flight->city == end) {
                    return end; // found destination
               }
               return path(flight->city, end); // recursively call path
          }
          flight = flight->next; 
     }
     return NULL;
}

int countpath(city* source, city* dest) {
     city* this = dest;
     int x = 1;
     while(this != source) {
          x += 1;
          this = this->prev;
     }
     return x;
}


// traces path from dest
char** print(city* source, city* dest) {
     city* this = dest;
     int c = countpath(source, dest) + 1;  // size of array
     char** array = (char**) malloc(c * (sizeof(char*))); // allocate array
     array[c - 1] = NULL;
     int i = c - 2; // index
     while(this != source) {
          array[i] = this->name; 
          i -= 1;  
          this = this->prev;
     }
     array[i] = source->name;
     return array;
}

// path from source to destination
const char** find_path(map_t* map, const char* src_name, const char* dst_name) {
     clear(map->citylist);  // clear all markers
     if(find(map->citylist, src_name) & find(map->citylist, dst_name)) {
          // if both cities exist
          city* source = get_city(map->citylist, src_name);
          source->path = NULL;
          city* dest = get_city(map->citylist, dst_name);
          if(strcmp(src_name, dst_name) == 0) {
               // if source = dest
               source->path = (char**) malloc(2*sizeof(char*));
               (source->path)[0] = source->name;
               (source->path)[1] = NULL;
               return (const char**) source->path;
          }
          city* result = path(source, dest);
          if(result == NULL) {
               return NULL; // no path exists
          }
          // else found path
          return (const char**) print(source, dest); 
     }
     return NULL;
}

void map_export(map_t* map, FILE* f) {
     // YOUR CODE HERE
}

map_t* map_import(FILE* f) {
     // YOUR CODE HERE
     return NULL;
}
