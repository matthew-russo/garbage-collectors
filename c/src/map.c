#include <stddef.h>
#include <stdlib.h>

#include "map.h"

struct map * map_init(int size)
{
    struct map * new_map = malloc(sizeof(struct map));
    new_map->size = size;
    new_map->contents = NULL;
    return new_map;
}

struct node * node_init(char * key, void * value)
{
    struct node * new_node = malloc(sizeof(struct node));
    new_node->key   = key;
    new_node->value = value;
    new_node->next  = NULL;
    return new_node;
}

int map_hashcode(struct map * map, char * key)
{
    unsigned long hash = 5381;
    int c;

    while ((c = *key++))
    {
        hash = ((hash << 5) + hash) + c; 
        /* hash * 33 + c */
    }

    return hash % map->size;
}

bool map_contains_key(struct map * map, char * key)
{
    int pos = map_hashcode(map, key);
    struct node * n = map_get(map, key);
    return n != NULL;
}

struct node * map_get(struct map * map, char * key)
{
    int pos = map_hashcode(map, key);
    struct node * list = map->contents[pos];
    struct node * temp = list;

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
    int pos = map_hashcode(map, key);
    struct node * list = map->contents[pos];
    struct node * last = list;

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



