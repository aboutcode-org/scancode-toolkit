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
  modules = {
    ["vdsl"]                    = "lua/vdsl/init.lua",
    ["vdsl.entity"]             = "lua/vdsl/entity.lua",
    ["vdsl.trait"]              = "lua/vdsl/trait.lua",
    ["vdsl.subject"]            = "lua/vdsl/subject.lua",
    ["vdsl.weight"]             = "lua/vdsl/weight.lua",
    ["vdsl.world"]              = "lua/vdsl/world.lua",
    ["vdsl.cast"]               = "lua/vdsl/cast.lua",
    ["vdsl.stage"]              = "lua/vdsl/stage.lua",
    ["vdsl.post"]               = "lua/vdsl/post.lua",
    ["vdsl.catalog"]            = "lua/vdsl/catalog.lua",
    ["vdsl.theme"]              = "lua/vdsl/theme.lua",
    ["vdsl.compiler"]           = "lua/vdsl/compiler.lua",
    ["vdsl.decode"]             = "lua/vdsl/decode.lua",
    ["vdsl.graph"]              = "lua/vdsl/graph.lua",
    ["vdsl.json"]               = "lua/vdsl/json.lua",
    ["vdsl.matcher"]            = "lua/vdsl/matcher.lua",
    ["vdsl.png"]                = "lua/vdsl/png.lua",
    ["vdsl.recipe"]             = "lua/vdsl/recipe.lua",
    ["vdsl.registry"]           = "lua/vdsl/registry.lua",
    ["vdsl.transport"]          = "lua/vdsl/transport/init.lua",
    ["vdsl.transport.curl"]     = "lua/vdsl/transport/curl.lua",
    ["vdsl.themes.cinema"]      = "lua/vdsl/themes/cinema.lua",
    ["vdsl.themes.anime"]       = "lua/vdsl/themes/anime.lua",
    ["vdsl.themes.architecture"] = "lua/vdsl/themes/architecture.lua",
  },
  copy_directories = { "examples", "tests" },
}