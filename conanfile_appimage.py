from conans import ConanFile, CMake
import os

class ConanDemoCamera(ConanFile):
   settings = "os", "compiler", "build_type", "arch"
   requires = "opencv/4.1.0@conan/stable", "AppImageGen/1.0@bincrafters/testing"
   generators = "AppImage"
   default_options = {"opencv:shared": True}
   name = "camera"
   executable = "$APPDIR/bin/camera"
   # FIXME: cpp_info is None
   rootpath = os.path.dirname(__file__)
   bin_paths = [os.path.join(rootpath, "bin")]
   lib_paths = []

   def imports(self):
      self.copy("haarcascade*.xml", dst="share/opencv4/haarcascades", src="bin")
