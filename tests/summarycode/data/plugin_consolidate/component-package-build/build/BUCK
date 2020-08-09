load('//:subdir_glob.bzl', 'subdir_glob')

cxx_binary(
  name = 'demo',
  header_namespace = 'demo',
  headers = subdir_glob([
    ('demo/include', '**/*.hpp'),
  ]),
  srcs = glob([
    'demo/src/**/*.cpp',
  ]),
  deps = [
    '//mathutils:mathutils',
  ],
)
