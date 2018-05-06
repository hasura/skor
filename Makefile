project      := skor
current_dir  := $(shell pwd)
registry     := hasura
CPPFLAGS     += $(shell pkg-config --cflags libpq)
packager_ver := 1.2
version      := 1.3
build_dir    := $(current_dir)/build

skor: src/skor.c src/req.c
	mkdir -p build
	c99 $(CPPFLAGS) -O3 -Wall -Wextra -o build/skor src/skor.c src/log.c -lpq -lcurl

clean:
	rm -rf build

image:
	docker run --rm -v $(current_dir):/root/skor-src $(registry)/$(project)-packager:$(packager_ver) sh -c "make -C /root/skor-src/ skor > /dev/null && cp /root/skor-src/build/skor /root/skor && /build.sh skor" | docker import - $(registry)/$(project):$(version)

packager: skor-packager.df
	docker build -t "$(registry)/$(project)-packager:$(packager_ver)" -f skor-packager.df .
