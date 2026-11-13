-- Source: https://github.com/S1M0N38/claude.nvim/blob/main/claude.nvim-scm-1.rockspec

---@diagnostic disable: lowercase-global

local _MODREV, _SPECREV = "scm", "-1"
rockspec_format = "3.0"
version = _MODREV .. _SPECREV

local user = "S1M0N38"
package = "claude.nvim"

description = {
	summary = "A simple plugin to integrate Claude Code in Neovim",
	detailed = [[
claude.nvim is a simple plugin to integrate Claude Code in Neovim.
  ]],
	labels = { "neovim", "plugin", "lua", "claude", "ai" },
	homepage = "https://github.com/" .. user .. "/" .. package,
	license = "MIT",
}

dependencies = {
	"lua >= 5.1",
}


source = {
	url = "git://github.com/" .. user .. "/" .. package,
}

build = {
	type = "builtin",
	copy_directories = { "plugin", "doc", "scripts" },
}