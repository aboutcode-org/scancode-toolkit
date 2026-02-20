rockspec_format = "3.0"
package = "vdsl"
version = "0.1.0-1"

source = {
  url = "git+https://github.com/ynishi/vdsl.git",
  tag = "v0.1.0",
}

description = {
  summary = "Visual DSL for ComfyUI",
  detailed = [[
    vdsl transforms semantic scene composition into ComfyUI node graphs.
    Pure Lua. Zero dependencies.
    Images become portable project files through PNG-embedded recipes.
  ]],
  homepage = "https://github.com/ynishi/vdsl",
  license = "MIT",
  labels = { "comfyui", "dsl", "image-generation", "stable-diffusion" },
}

dependencies = {
  "lua >= 5.1",
}

build = {
  type = "builtin",
  copy_directories = { "examples", "tests" },
}