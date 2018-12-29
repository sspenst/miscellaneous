FILE = bmpGenerator

all: $(FILE)

$(FILE): $(FILE).c
	gcc -g -Wall -o $@ $^

clean:
	rm -f $(FILE) *.bmp

.PHONY: all clean
