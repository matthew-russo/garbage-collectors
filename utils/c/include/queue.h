#ifndef _UTILS_QUEUE_H
#define _UTILS_QUEUE_H

#include <stdint.h>
#include <stdbool.h>

struct node
{
    void * val;
    struct node * next;
};

struct queue
{
    int size;
    struct node * head; 
};

void queue_enqueue(void * n);
void * queue_dequeue();
void * queue_peek();
bool queue_is_empty();
bool queue_is_full();
uint32_t queue_size();

#endif
