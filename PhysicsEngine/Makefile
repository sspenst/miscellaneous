FILE = PhysicsEngine

all: bin/$(FILE).class

bin/$(FILE).class: src/$(FILE).java
	mkdir -p bin
	javac -d bin -sourcepath src $<

run:
	java -cp bin $(FILE)

clean:
	rm -rf bin

.PHONY: all run clean
