#!/usr/bin/env bash

set -ex

pushd appimage
conan create . bincrafters/testing
popd

conan install conanfile_appimage.py -g AppImage -if build
