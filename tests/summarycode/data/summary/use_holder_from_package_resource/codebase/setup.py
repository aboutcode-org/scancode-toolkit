# Copyright 2020 Google LLC
# Copyright 2021 Fraunhofer FKIE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

setup(
    name="atheris",
    version=__version__,
    author="Bitshift",
    author_email="atheris@google.com",
    url="https://github.com/google/atheris/",
    description="A coverage-guided fuzzer for Python and Python extensions.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    packages=["atheris"],
    package_dir={"atheris": "src"},
    py_modules=["atheris_no_libfuzzer"],
    ext_modules=ext_modules,
    setup_requires=["pybind11>=2.5.0"],
    cmdclass={"build_ext": BuildExt},
    zip_safe=False,
)
