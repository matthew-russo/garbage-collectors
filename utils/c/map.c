#include <map.h>

struct map * map_init(int size)
{
    struct map * new_map = malloc(sizeof(struct map));
    new_map->size = size;
    new_map->node = NULL;
    return new_map;
}

int map_hashcode(struct map * map, char * key)
{
    unsigned long hash = 5381;
    int c;

    while (c = *key++)
    {
        hash = ((hash << 5) + hash) + c; 
        /* hash * 33 + c */
    }

    return hash % map->size;
}

bool map_contains_key(struct map * map, char * key)
{
    int pos = hashcode(map, key);
    struct node * get(map, key);
    return node != NULL;
}

struct node * map_get(struct map * map, char * key)
{
    int pos = hashcode(map, key);
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
    int pos = hashcode(map, key);
    struct node * list = map->contents[pos];
    struct node * last = list;

    if (last == NULL)
    {
        map->contents[pos] = new_node;
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

    struct node * new_node = malloc(sizeof(struct node));
    new_node->key   = key;
    new_node->value = value;
    new_node->next  = NULL;

    last->next = new_node; 
}

