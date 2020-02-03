#include <stddef.h>
#include <stdlib.h>

#include "map.h"

struct map * map_init(uint32_t size)
{
    struct map * new_map = malloc(sizeof(struct map));
    new_map->size = size;
    new_map->contents = NULL;
    return new_map;
}

struct map_node * node_init(char * key, void * value)
{
    struct map_node * new_node = malloc(sizeof(struct map_node));
    new_node->key   = key;
    new_node->value = value;
    new_node->next  = NULL;
    return new_node;
}

uint32_t map_hashcode(struct map * map, char * key)
{
    unsigned long hash = 5381;
    uint32_t c;

    while ((c = *key++))
    {
        hash = ((hash << 5) + hash) + c; 
        /* hash * 33 + c */
    }

    return hash % map->size;
}

bool map_contains_key(struct map * map, char * key)
{
    uint32_t pos = map_hashcode(map, key);
    struct map_node * n = map_get(map, key);
    return n != NULL;
}

struct map_node * map_get(struct map * map, char * key)
{
    uint32_t pos = map_hashcode(map, key);
    struct map_node * list = map->contents[pos];
    struct map_node * temp = list;

    while (temp)
    {
        if (temp->key == key)
        {
            return temp->value;
        }

        temp = temp->next;
    }

    return NULL;
}

void map_insert(struct map * map, char * key, void * value)
{
    uint32_t pos = map_hashcode(map, key);
    struct map_node * list = map->contents[pos];
    struct map_node * last = list;

    if (last == NULL)
    {
        map->contents[pos] = node_init(key, value);
        return;
    }

    while (last->next != NULL)
    {
        if (last->key == key)
        {
            last->value = value;
            return;
        }

        last = last->next;
    }

    last->next = node_init(key, value); 
}

struct map_iterator map_iter(struct map * map)
{
    struct map_iterator iter;
    iter.map = map;
    iter.current = map->contents[0];
    iter.curr_index = 0;
    return iter;
}

void map_iter_restart(struct map_iterator * map_iter)
{
    map_iter->current = map_iter->map->contents[0];
}

void map_iter_next(struct map_iterator * map_iter)
{
    if (map_iter->current->next != NULL)
    {
        map_iter->current = map_iter->current->next;
        return;
    }

    map_iter->curr_index += 1;
    map_iter->current = map_iter->map->contents[map_iter->curr_index];
}

bool map_iter_is_done(struct map_iterator * map_iter)
{
    if (map_iter->current->next != NULL)
    {
        return false;
    }

    return map_iter->curr_index == map_iter->map->size;
}

struct map_node * map_iter_current_node(struct map_iterator * map_iter)
{
    return map_iter->current;
}

char * map_iter_current_key(struct map_iterator * map_iter)
{
    return map_iter->current->key;
}

void * map_iter_current_value(struct map_iterator * map_iter)
{
    return map_iter->current->value;
}

