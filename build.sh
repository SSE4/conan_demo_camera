#!/usr/bin/env bash

set -ex

mkdir -p build

conan remote add bc https://api.bintray.com/conan/bincrafters/public-conan || true

conan install . -if build
pushd build
cmake ..
cmake --build .
popd
