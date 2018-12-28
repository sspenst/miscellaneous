FILE = TriangleFractal

all: bin/$(FILE).class

bin/$(FILE).class: $(FILE).java
	mkdir -p bin
	javac -d bin $<

run:
	java -cp bin $(FILE)

clean:
	rm -rf bin

.PHONY: all run clean
