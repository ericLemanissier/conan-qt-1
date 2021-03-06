#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            self.build_requires("jom_installer/1.1.2@bincrafters/stable")

    def build(self):
        tools.mkdir("qmake_folder")
        with tools.chdir("qmake_folder"):
            self.output.info("Building with qmake")
            def qmakeBuild(self):
                with tools.environment_append(RunEnvironment(self).vars):
                    self.run("qmake %s" % self.source_folder)
                if tools.os_info.is_windows:
                    if self.settings.compiler == "Visual Studio":
                        self.run("jom")
                    else:
                        self.run("mingw32-make")
                else:
                    self.run("make")

            if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self.settings):
                    qmakeBuild(self)
            else:
                qmakeBuild(self)
                
        if not self.options["Qt"].shared:
            self.output.info("disabled cmake test with static Qt, because of https://bugreports.qt.io/browse/QTBUG-38913")
        else:
            self.output.info("Building with CMake")
            cmake = CMake(self)
            cmake.configure(build_folder="cmake_folder")
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.output.info("Testing qmake")
            if tools.os_info.is_windows:
                bin_path = str(self.settings.build_type).lower()
            elif tools.os_info.is_linux:
                bin_path = "."
            else:
                bin_path = os.path.join("test_package.app", "Contents", "MacOS")
            self.run(os.path.join("qmake_folder", bin_path, "test_package"))

            if not self.options["Qt"].shared:
                self.output.info("disabled cmake test with static Qt, because of https://bugreports.qt.io/browse/QTBUG-38913")
            else:
                self.output.info("Testing CMake")
                self.run(os.path.join("cmake_folder", "bin", "test_package"))
