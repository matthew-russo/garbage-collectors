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

void queue_enqueue(struct queue *, void *);
void * queue_dequeue(struct queue *);
void * queue_peek(struct queue *);
bool queue_is_empty(struct queue *);
bool queue_is_full(struct queue *);
uint32_t queue_size(struct queue *);

#endif
