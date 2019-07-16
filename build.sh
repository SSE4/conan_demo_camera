#!/usr/bin/env bash

set -ex

mkdir -p build

conan install . -if build
cmake -Bbuild -S.
cmake --build build
