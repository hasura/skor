project      := skor
current_dir  := $(shell pwd)
registry     := hasura
CPPFLAGS     += $(shell pkg-config --cflags libpq)
version      := 0.2
build_dir    := $(current_dir)/build

skor: src/skor.c src/req.c
	mkdir -p build
	c99 $(CPPFLAGS) -O3 -Wall -Wextra -o build/skor src/skor.c src/log.c -lpq -lcurl

clean:
	rm -rf build

image:
	docker build -t $(registry)/$(project):$(version) .
