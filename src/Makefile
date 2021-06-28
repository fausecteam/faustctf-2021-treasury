CFLAGS = -std=c11 -pedantic -Wall -Werror -Wextra -D_FORTIFY_SOURCE=2 -O3 -fPIC -fstack-protector-all -pie -s
CC=gcc

.PHONY: all

all: treasury

util.o: util.c include/util.h include/treasure.h
	$(CC) $(CFLAGS) -c -o $@ $<

treasure.o: treasure.c include/util.h include/treasure.h
	$(CC) $(CFLAGS) -c -o $@ $<

treasury.o: main.c include/util.h include/treasure.h
	$(CC) $(CFLAGS) -c -o $@ $<

treasury: treasury.o util.o treasure.o
	$(CC) $(CFLAGS) -o $@ $^
