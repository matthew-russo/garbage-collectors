#ifndef _UTILS_MAP_H
#define _UTILS_MAP_H

#include <stdint.h>
#include <stdbool.h>

struct map_node
{
    char * key;
    void * value;
    struct map_node * next;
};

struct map
{
    uint32_t size;
    struct map_node ** contents;
};

struct map * map_init(uint32_t);
uint32_t map_hashcode(struct map *, char *);
bool map_contains_key(struct map *, char *);
struct map_node * map_get(struct map *, char *);
void map_insert(struct map *, char *, void *);

struct map_iterator
{
    struct map * map;
    struct map_node * current;
    uint32_t curr_index;
};

struct map_iterator map_iter(struct map *);
void map_iter_restart(struct map_iterator *);
void map_iter_next(struct map_iterator *);
bool map_iter_is_done(struct map_iterator *);
struct map_node * map_iter_current_node(struct map_iterator *);
char * map_iter_current_key(struct map_iterator *);
void * map_iter_current_value(struct map_iterator *);

#endif
