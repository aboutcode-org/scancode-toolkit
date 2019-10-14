; Example makefile
; ----------------
; This is an example makefile to introduce new users of drush_make to the
; syntax and options available to drush_make. For a full description of all
; options available, see README.txt.

; This make file is a working makefile - try it! Any line starting with a `;`
; is a comment.

; Core version
; ------------
; Each makefile should begin by declaring the core version of Drupal that all
; projects should be compatible with.

core = 7.x

; API version
; ------------
; Every makefile needs to declare it's Drush Make API version. This version of
; drush make uses API version `2`.

api = 2

; Core project
; ------------
; In order for your makefile to generate a full Drupal site, you must include
; a core project. This is usually Drupal core, but you can also specify
; alternative core projects like Pressflow. Note that makefiles included with
; install profiles *should not* include a core project.

; Use Pressflow instead of Drupal core:
; projects[pressflow][type] = "core"
; projects[pressflow][download][type] = "file"
; projects[pressflow][download][url] = "http://launchpad.net/pressflow/6.x/6.15.73/+download/pressflow-6.15.73.tar.gz"

; Git clone of Drupal 7.x. Requires the `core` property to be set to 7.x.
; projects[drupal][type] = "core"
; projects[drupal][download][type] = git
; projects[drupal][download][url] = https://git.drupalcode.org/project/drupal.git

projects[] = drupal

; Projects
; --------
; Each project that you would like to include in the makefile should be
; declared under the `projects` key. The simplest declaration of a project
; looks like this:

; To include the most recent views module:

projects[] = views

; This will, by default, retrieve the latest recommended version of the project
; using its update XML feed on Drupal.org. If any of those defaults are not
; desirable for a project, you will want to use the keyed syntax combined with
; some options.

; If you want to retrieve a specific version of a project:

; projects[views] = 2.16

; Or an alternative, extended syntax:

projects[ctools][version] = 1.3

; Check out the latest version of a project from Git. Note that when using a
; repository as your project source, you must explicitly declare the project
; type so that drush_make knows where to put your project.

projects[data][type] = module
projects[data][download][type] = git
projects[data][download][url] = https://git.drupalcode.org/project/views.git
projects[data][download][revision] = DRUPAL-6--3

; For projects on drupal.org, some shorthand is available. If any
; download parameters are specified, but not type, the default is git.
projects[cck_signup][download][revision] = "2fe932c"
; It is recommended to also specify the corresponding branch so that
; the .info file rewriting can obtain a version string that works with
; the core update module
projects[cck_signup][download][branch] = "7.x-1.x"

; Clone a project from github.

projects[tao][type] = theme
projects[tao][download][type] = git
projects[tao][download][url] = git://github.com/developmentseed/tao.git

; If you want to install a module into a sub-directory, you can use the
; `subdir` attribute.

projects[admin_menu][subdir] = custom

; To apply a patch to a project, use the `patch` attribute and pass in the URL
; of the patch.

projects[admin_menu][patch][687750] = "http://drupal.org/files/issues/admin_menu.long_.31.patch"

; If all projects or libraries share common attributes, the `defaults`
; array can be used to specify these globally, rather than
; per-project.

defaults[projects][subdir] = "contrib"
