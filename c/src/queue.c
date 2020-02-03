#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>

#include "queue.h"

struct queue * queue_init(uint32_t size)
{
    struct queue * queue = malloc(sizeof(struct queue));
    queue->size = size;
    queue->head = NULL;
}

void queue_enqueue(struct queue * q, void * val)
{
    if (queue_is_full(q))
    {
        // TODO -> handle full queue
    }
 
    struct queue_node * new_node = malloc(sizeof(struct queue_node));
    new_node->val  = val;
    new_node->next = NULL;

    if (queue_is_empty(q))
    {
        q->head = new_node;
        return;
    }

    struct queue_node * next = q->head;

    while (next->next != NULL)
    {
        next = next->next;
    }

    next->next = new_node;
}

void * queue_dequeue(struct queue * q)
{
    if (queue_is_empty(q))
    {
        return NULL;
    }

    struct queue_node * head_node = q->head;
    q->head = head_node->next;
    void * val = head_node->val;
    free(head_node);
    return val;
}

void * queue_peek(struct queue * q)
{
    struct queue_node * head_node = q->head;
    return head_node->val;
}

bool queue_is_empty(struct queue * q)
{
    return q->head == NULL;
}

bool queue_is_full(struct queue * q)
{
    // TODO 
    printf("unimplemented queue_is_full");
    return true;
}

uint32_t queue_size(struct queue * q)
{
    return q->size;
}

