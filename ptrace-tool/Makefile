CC = gcc
LD = ld
RM = rm
CP = cp
STRIP = strip
LDCONF = ldconfig
CFLAGS = -Wall -fPIC -DPIC
PLATFORM = $(shell uname -s)

.SUFFIXES: .c
.PHONY: clean install

%.o : %.c
	$(CC) $(CFLAGS) -c $<

all: libpthread-trace.so

libpthread-trace.so: pthread-trace.o tracetime.o log.o
    ifeq ($(PLATFORM),Darwin)
	    $(LD) -dylib -o $@ $^ -ldl 
    else
	    $(LD) -shared -o $@ $^ -ldl -lrt
	    $(STRIP) --strip-unneeded libpthread-trace.so
    endif

pthread-trace.o: pthread-trace.c

tracetime.o: tracetime.c

log.o: log.c

clean:
	-$(RM) libpthread-trace.so
	-$(RM) *.o *~

install:
	$(CP) pthread-trace /usr/local/bin/pthread-trace
	$(CP) libpthread-trace.so /usr/local/lib/libpthread-trace.so
	$(LDCONF)

uninstall:
	-$(RM) /usr/local/bin/pthread-trace
	-$(RM) /usr/local/lib/libpthread-trace.so
	$(LDCONF)
