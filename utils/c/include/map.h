#ifndef _UTILS_MAP_H
#define _UTILS_MAP_H

#include <stdbool.h>

struct node
{
    char * key;
    void * value;
    struct node * next;
};

struct map
{
    int size;
    struct node **contents;
};

struct map * map_init(int size);
int map_hashcode(struct map * map, char * key);
bool map_contains_key(struct map * map, char * key);
struct node * map_get(struct map * map, char * key);
void map_insert(struct map * map, char * key, void * value);

#endif
