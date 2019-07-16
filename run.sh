#!/usr/bin/env bash

set -ex

conan imports -if build .
source build/activate_run.sh
pushd bin
./camera
popd
