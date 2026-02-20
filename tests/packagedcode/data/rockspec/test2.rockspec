package = "LuaSocket"
version = "scm-3"
source = {
  url = "git+https://github.com/lunarmodules/luasocket.git",
  branch = "master"
}
description = {
  summary = "Network support for the Lua language",
  detailed = [[
      LuaSocket is a Lua extension library composed of two parts: a set of C
      modules that provide support for the TCP and UDP transport layers, and a
      set of Lua modules that provide functions commonly needed by applications
      that deal with the Internet.
   ]],
  homepage = "https://github.com/lunarmodules/luasocket",
  license = "MIT"
}
dependencies = {
  "lua >= 5.1"
}

build = {
  type = "builtin",
  copy_directories = {
    "docs",
    "samples",
    "test"
     }
}