C_FOLDERS = bmpGenerator guessingGame mastermind quadratic reflex sortingAlgorithms
C_OBJS = $(join $(addsuffix /,$(C_FOLDERS)),$(C_FOLDERS))

JAVA_FOLDERS = Calculator PhysicsEngine SudokuSolver TriangleFractal
JAVA_OBJS = $(addsuffix .class,$(join $(addsuffix /bin/,$(JAVA_FOLDERS)),$(JAVA_FOLDERS)))

FOLDERS = $(C_FOLDERS) $(JAVA_FOLDERS)
OBJS = $(C_OBJS) $(JAVA_OBJS)

all: $(OBJS)

$(C_OBJS):
	@echo "C: Compiling $(basename $(notdir $@))..."
	-@$(MAKE) -s -C $(basename $(notdir $@))

$(JAVA_OBJS):
	@echo "JAVA: Compiling $(basename $(notdir $@))..."
	-@$(MAKE) -s -C $(basename $(notdir $@))

clean:
	@for folder in $(FOLDERS); do $(MAKE) clean -s -C $$folder; done

.PHONY: all clean
