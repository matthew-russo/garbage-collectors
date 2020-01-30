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
    struct node ** contents;
};

struct map * map_init(int);
int map_hashcode(struct map *, char *);
bool map_contains_key(struct map *, char *);
struct node * map_get(struct map *, char *);
void map_insert(struct map *, char *, void *);

#endif
