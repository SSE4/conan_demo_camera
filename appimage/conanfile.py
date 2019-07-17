from conans.model import Generator
from conans import ConanFile, tools
import os
import textwrap
import tempfile
import shutil
from distutils.dir_util import copy_tree


class AppImage(Generator):
    def __init__(self, conanfile):
        super(AppImage, self).__init__(conanfile)
        self._settings = self.conanfile.settings
        self._output = self.conanfile.output
        self._name = self.conanfile.name or "MyApp"
        self._exe = self.conanfile.executable or "dummy"
        self._lname = self._name.lower()
        self._dir = "%s.AppDir" % self._name
        self._appimagekit_version = "12"

    @property
    def filename(self):
        return os.path.join(self._dir, "%s.desktop" % self._lname)

    @property
    def _arch(self):
        return self._settings.get_safe("arch_build") or self._settings.get_safe("arch")

    def _get_apprun(self):
        name = {"x86_64": "AppRun-x86_64",
                "x86": "AppRun-i686",
                "armv8": "AppRun-aarch64",
                "armv7": "AppRun-armhf"}.get(self._arch)
        path = os.path.join(tempfile.gettempdir(), name)
        if not os.path.isfile(path):
            url = "https://github.com/AppImage/AppImageKit/releases/download/{version}/{name}".format(version=self._appimagekit_version, name=name)
            self._output.info("downloading %s" % url)
            tools.download(url, path)
        shutil.copy(path, "AppRun")

    def _get_appimagetool(self):
        name = {"x86_64": "appimagetool-x86_64.AppImage",
                "x86": "appimagetool-i686.AppImage",
                "armv8": "appimagetool-aarch64.AppImage",
                "armv7": "appimagetool-armhf.AppImage"}.get(self._arch)
        path = os.path.join(tempfile.gettempdir(), "appimagetool")
        if not os.path.isfile(path):
            url = "https://github.com/AppImage/AppImageKit/releases/download/{version}/{name}".format(version=self._appimagekit_version, name=name)
            self._output.info("downloading %s" % url)
            tools.download(url, path)
            self._chmod_plus_x(path)
        return path

    @staticmethod
    def _chmod_plus_x(name):
        if os.name == 'posix':
            os.chmod(name, os.stat(name).st_mode | 0o111)

    @property
    def content(self):
        with tools.chdir(self.output_path):
            tools.rmdir(self._dir)
            os.makedirs(self._dir)
            with tools.chdir(self._dir):
                self._get_apprun()

                bindirs = set()
                libdirs = set()
                for depname, cpp_info in self.deps_build_info.dependencies:
                    self._output.info("processing dependency %s" % depname)
                    for p in cpp_info.lib_paths:
                        if self.conanfile.options[depname].shared == True:
                            if os.listdir(p):
                                reldir = os.path.relpath(p, cpp_info.rootpath)
                                self._output.info("lib dir %s" % p)
                                copy_tree(p, reldir)
                                libdirs.add(reldir)
                    for p in cpp_info.bin_paths:
                        if os.listdir(p):
                            reldir = os.path.relpath(p, cpp_info.rootpath)
                            self._output.info("bin dir %s" % p)
                            copy_tree(p, reldir)
                            bindirs.add(reldir)
                for p in self.conanfile.bin_paths:
                    if os.listdir(p):
                        reldir = os.path.relpath(p, self.conanfile.rootpath)
                        self._output.info("bin dir %s" % p)
                        copy_tree(p, reldir)
                        bindirs.add(reldir)
                for p in self.conanfile.lib_paths:
                    if self.conanfile.options.shared == True:
                        if os.listdir(p):
                            reldir = os.path.relpath(p, self.conanfile.rootpath)
                            self._output.info("lib dir %s" % p)
                            copy_tree(p, reldir)
                            libdirs.add(reldir)

                path = ":".join(["$APPDIR/%s" % bindir for bindir in bindirs])
                ld_library_path = ":".join(["$APPDIR/%s" % libdir for libdir in libdirs])

                if not os.path.isdir(os.path.join("usr", "bin")):
                    os.makedirs(os.path.join("usr", "bin"))

                env = []
                for depname, env_info in self.deps_env_info.dependencies:
                    for name, value in env_info.vars.items():
                        if isinstance(value, list):
                            value = ":".join(value)
                            export = "export {name}=${name}:".format(name=name)
                        else:
                            export = "export {name}=".format(name=name)
                        rootpath = self.deps_build_info[depname].rootpath
                        value = str(value)
                        value = value.replace(rootpath, "$APPDIR")
                        env.append("{export}{value}".format(export=export, value=value))
                env = "\n".join(env)

                contents = """#!/usr/bin/env bash
set -ex

export PATH=$PATH:{path}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{ld_library_path}
{env}
pushd $(dirname {exe})
{exe}
popd
""".format(path=path,
           ld_library_path=ld_library_path,
           env=env,
           exe=self._exe)

                tools.save(os.path.join("usr", "bin", self._lname), contents)
                icon = os.path.join(os.path.dirname(__file__), "conan.png")
                shutil.copy(icon, "%s.png" % self._lname)

                self._chmod_plus_x("AppRun")
                self._chmod_plus_x(os.path.join("usr", "bin", self._lname))

                content = """[Desktop Entry]
Name={name}
Exec={lname}
Icon={lname}
Type=Application
Categories=Utility;""".format(name=self._name, lname=self._lname)
            tools.save(self.filename, content)

            appimagetool = self._get_appimagetool()
            self.conanfile.run("%s %s" % (appimagetool, self._dir))
            return content

class AppImageConanFile(ConanFile):
    name = "AppImageGen"
    version = "1.0"
    license = "MIT"
    description = "AppImage generator"
    url = "appimage.org"
    exports = "conan.png"
