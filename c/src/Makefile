IDIR =../include
CC=gcc
CFLAGS=-I$(IDIR)

ODIR=obj
LDIR =../lib

LIBS=-lm

_DEPS = map.h queue.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = map.o queue.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

$(ODIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

mark-sweep: $(ODIR)/mark-sweep.o $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

mark-compact: $(ODIR)/mark-compact.o $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

copying: $(ODIR)/copying.o $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

reference-counting: $(ODIR)/reference-counting.o $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~
