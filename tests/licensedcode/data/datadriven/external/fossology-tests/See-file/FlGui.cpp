// Gmsh - Copyright (C) 1997-2012 C. Geuzaine, J.-F. Remacle
//
// See the LICENSE.txt file for license information. Please report all
// bugs and problems to <gmsh@geuz.org>.

#include "GmshConfig.h"
#if !defined(HAVE_NO_STDINT_H)
#include <stdint.h>
#elif defined(HAVE_NO_INTPTR_T)
typedef unsigned long intptr_t;
#endif
#include <sstream>
#include <string.h>
#include <FL/Fl.H>
#include <FL/Fl_Tooltip.H>
#include <FL/Fl_Shared_Image.H>
#include <FL/Fl_File_Icon.H>
#include <FL/x.H>
#include <FL/gl.h>
#include "FlGui.h"
#include "graphicWindow.h"
#include "menuWindow.h"
#include "optionWindow.h"
#include "fieldWindow.h"
#include "pluginWindow.h"
#include "statisticsWindow.h"
#include "visibilityWindow.h"
#include "clippingWindow.h"
#include "manipWindow.h"
#include "contextWindow.h"
#include "onelabWindow.h"
#include "aboutWindow.h"
#include "colorbarWindow.h"
#include "fileDialogs.h"
#include "GmshDefines.h"
#include "GmshMessage.h"
#include "GModel.h"
#include "MElement.h"
#include "PView.h"
#include "Field.h"
#include "Plugin.h"
#include "PluginManager.h"
#include "OpenFile.h"
#include "Win32Icon.h"
#include "Options.h"
#include "CommandLine.h"
#include "Context.h"
#include "StringUtils.h"
#include "Generator.h"
#include "gl2ps.h"

// check (now!) if there are any pending events, and process them
void FlGui::check(){ Fl::check(); }

// wait (possibly indefinitely) for any events, then process them
void FlGui::wait(){ Fl::wait(); }

// wait (at most time seconds) for any events, then process them
void FlGui::wait(double time){ Fl::wait(time); }

class drawContextFltk : public drawContextGlobal{
 public:
  void draw()
  {
    if(!FlGui::available()) return;
    for(unsigned int i = 0; i < FlGui::instance()->graph.size(); i++){
      for(unsigned int j = 0; j < FlGui::instance()->graph[i]->gl.size(); j++){
        FlGui::instance()->graph[i]->gl[j]->make_current();
        FlGui::instance()->graph[i]->gl[j]->redraw();
	// to initialize the camera distance from model
	drawContext * ctx = FlGui::instance()->graph[i]->gl[j]->getDrawContext();
	ctx->camera.update();
      }
    }
    FlGui::instance()->check();
  }
  void drawCurrentOpenglWindow(bool make_current)
  {
    if(!FlGui::available()) return;
    openglWindow *gl = FlGui::instance()->getCurrentOpenglWindow();
    if(make_current) gl->make_current();
    gl->redraw();
    glFlush();
    FlGui::instance()->check();
  }
  int getFontIndex(const char *fontname)
  {
    if(fontname){
      for(int i = 0; i < NUM_FONTS; i++)
        if(!strcmp(menu_font_names[i].label(), fontname))
          return i;
    }
    Msg::Error("Unknown font \"%s\" (using \"Helvetica\" instead)", fontname);
    Msg::Info("Available fonts:");
    for(int i = 0; i < NUM_FONTS; i++)
      Msg::Info("  \"%s\"", menu_font_names[i].label());
    return 4;
  }
  int getFontEnum(int index)
  {
    if(index >= 0 && index < NUM_FONTS)
      return (intptr_t)menu_font_names[index].user_data();
    return FL_HELVETICA;
  }
  const char *getFontName(int index)
  {
    if(index >= 0 && index < NUM_FONTS)
      return menu_font_names[index].label();
    return "Helvetica";
  }
  int getFontAlign(const char *alignstr)
  {
    if(alignstr){
      if(!strcmp(alignstr, "BottomLeft") || !strcmp(alignstr, "Left") ||
         !strcmp(alignstr, "left"))
        return 0;
      else if(!strcmp(alignstr, "BottomCenter") || !strcmp(alignstr, "Center") ||
              !strcmp(alignstr, "center"))
        return 1;
      else if(!strcmp(alignstr, "BottomRight") || !strcmp(alignstr, "Right") ||
              !strcmp(alignstr, "right"))
        return 2;
      else if(!strcmp(alignstr, "TopLeft"))
        return 3;
      else if(!strcmp(alignstr, "TopCenter"))
        return 4;
      else if(!strcmp(alignstr, "TopRight"))
        return 5;
      else if(!strcmp(alignstr, "CenterLeft"))
        return 6;
      else if(!strcmp(alignstr, "CenterCenter"))
        return 7;
      else if(!strcmp(alignstr, "CenterRight"))
        return 8;
    }
    Msg::Error("Unknown font alignment \"%s\" (using \"Left\" instead)", alignstr);
    Msg::Info("Available font alignments:");
    Msg::Info("  \"Left\" (or \"BottomLeft\")");
    Msg::Info("  \"Center\" (or \"BottomCenter\")");
    Msg::Info("  \"Right\" (or \"BottomRight\")");
    Msg::Info("  \"TopLeft\"");
    Msg::Info("  \"TopCenter\"");
    Msg::Info("  \"TopRight\"");
    Msg::Info("  \"CenterLeft\"");
    Msg::Info("  \"CenterCenter\"");
    Msg::Info("  \"CenterRight\"");
    return 0;
  }
  int getFontSize()
  {
    if(CTX::instance()->fontSize > 0){
      return CTX::instance()->fontSize;
    }
    else{
      int w = Fl::w();
      if(w <= 1024)      return 11;
      else if(w <= 1280) return 12;
      else if(w <= 1680) return 13;
      else if(w <= 1920) return 14;
      else               return 15;
    }
  }
  void setFont(int fontid, int fontsize)
  {
    gl_font(fontid, fontsize);
  }
  double getStringWidth(const char *str)
  {
    return gl_width(str);
  }
  int getStringHeight()
  {
    return gl_height();
  }
  int getStringDescent()
  {
    return gl_descent();
  }
  void drawString(const char *str)
  {
    gl_draw(str);
  }
  void resetFontTextures()
  {
#if defined(__APPLE__) && (FL_MAJOR_VERSION == 1) && (FL_MINOR_VERSION == 3)
    gl_texture_pile_height(1); // force font texture recomputation
#endif
  }
};

static int globalShortcut(int event)
{
  if(!FlGui::available()) return 0;
  return FlGui::instance()->testGlobalShortcuts(event);
}

FlGui::FlGui(int argc, char **argv) : _openedThroughMacFinder(false)
{
  // set X display
  if(CTX::instance()->display.size())
    Fl::display(CTX::instance()->display.c_str());

#if 0 // dark scheme... not bad, but needs work
  Fl::background(60, 60, 60);
  Fl::background2(120, 120, 120);
  Fl::foreground(200, 200, 200);
#endif

  // add global shortcuts
  Fl::add_handler(globalShortcut);

  // set global fltk-dependent drawing functions
  drawContext::setGlobal(new drawContextFltk);

  // set default font size
  FL_NORMAL_SIZE = drawContext::global()->getFontSize();

  // handle themes and tooltip font size
  if(CTX::instance()->guiTheme.size())
    Fl::scheme(CTX::instance()->guiTheme.c_str());
  Fl_Tooltip::size(FL_NORMAL_SIZE);

  // register image formats not in core fltk library (jpeg/png)
  fl_register_images();

  // load default system icons (for file browser)
  Fl_File_Icon::load_system_icons();

  // add callback to respond to Mac Finder
#if defined(__APPLE__)
  fl_open_callback(OpenProjectMacFinder);
#if (FL_MAJOR_VERSION == 1) && (FL_MINOR_VERSION == 3)
  fl_mac_set_about(help_about_cb, 0);
#endif
#endif

  // all the windows are contructed (even if some are not displayed)
  // since the shortcuts should be valid even for hidden windows, and
  // we don't want to test for widget existence every time
  menu = new menuWindow();
  graph.push_back(new graphicWindow(true, CTX::instance()->numTiles));

#if defined(WIN32)
  graph[0]->win->icon
    ((const char*)LoadImage(fl_display, MAKEINTRESOURCE(IDI_ICON),
                            IMAGE_ICON, 16, 16, LR_DEFAULTCOLOR));
#elif defined(__APPLE__)
  // nothing to do here
#else
  fl_open_display();
  static char gmsh32x32[] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x01, 0x00, 0x00, 0x40, 0x03, 0x00,
    0x00, 0x40, 0x03, 0x00, 0x00, 0x20, 0x07, 0x00, 0x00, 0x20, 0x07, 0x00,
    0x00, 0x10, 0x0f, 0x00, 0x00, 0x10, 0x0f, 0x00, 0x00, 0x08, 0x1f, 0x00,
    0x00, 0x08, 0x1f, 0x00, 0x00, 0x04, 0x3f, 0x00, 0x00, 0x04, 0x3f, 0x00,
    0x00, 0x02, 0x7f, 0x00, 0x00, 0x02, 0x7f, 0x00, 0x00, 0x01, 0xff, 0x00,
    0x00, 0x01, 0xff, 0x00, 0x80, 0x00, 0xff, 0x01, 0x80, 0x00, 0xff, 0x01,
    0x40, 0x00, 0xff, 0x03, 0x40, 0x00, 0xff, 0x03, 0x20, 0x00, 0xff, 0x07,
    0x20, 0x00, 0xff, 0x07, 0x10, 0x00, 0xff, 0x0f, 0x10, 0x00, 0xff, 0x0f,
    0x08, 0x00, 0xff, 0x1f, 0x08, 0x00, 0xff, 0x1f, 0x04, 0x40, 0xfd, 0x3f,
    0x04, 0xa8, 0xea, 0x3f, 0x02, 0x55, 0x55, 0x7f, 0xa2, 0xaa, 0xaa, 0x7a,
    0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00};
  graph[0]->win->icon
    ((const char*)XCreateBitmapFromData(fl_display, DefaultRootWindow(fl_display),
                                        gmsh32x32, 32, 32));
  menu->win->icon
    ((const char*)XCreateBitmapFromData(fl_display, DefaultRootWindow(fl_display),
                                        gmsh32x32, 32, 32));
#endif

  // open graphic window first for correct non-modal behaviour on
  // Win32
  graph[0]->win->show(1, argv);
  menu->win->show();

  // graphic window should have the initial focus (so we can
  // e.g. directly loop through time steps with the keyboard)
  //graph[0]->gl[0]->take_focus();
  Fl::focus(graph[0]->gl[0]);

  // create additional graphic windows
  for(int i = 1; i < CTX::instance()->numWindows; i++){
    graphicWindow *g = new graphicWindow(false, CTX::instance()->numTiles);
    g->win->resize(graph.back()->win->x() + 10, graph.back()->win->y() + 10,
                   graph.back()->win->w(), graph.back()->win->h());
    g->win->show();
    graph.push_back(g);
  }

  options = new optionWindow(CTX::instance()->deltaFontSize);
  fields = new fieldWindow(CTX::instance()->deltaFontSize);
  plugins = new pluginWindow(CTX::instance()->deltaFontSize);
  stats = new statisticsWindow(CTX::instance()->deltaFontSize);
  visibility = new visibilityWindow(CTX::instance()->deltaFontSize);
  clipping = new clippingWindow(CTX::instance()->deltaFontSize);
  manip = new manipWindow(CTX::instance()->deltaFontSize);
  geoContext = new geometryContextWindow(CTX::instance()->deltaFontSize);
  meshContext = new meshContextWindow(CTX::instance()->deltaFontSize);
  about = new aboutWindow();
#if defined(HAVE_ONELAB) && (FL_MAJOR_VERSION == 1) && (FL_MINOR_VERSION == 3)
  onelab = new onelabWindow(CTX::instance()->deltaFontSize);
#endif

  // init solver plugin stuff
  callForSolverPlugin(-1);

  // draw
  for(unsigned int i = 0; i < graph.size(); i++)
    for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
      graph[i]->gl[j]->redraw();

  menu->setContext(menu_geometry, 0);
}

FlGui *FlGui::_instance = 0;

FlGui *FlGui::instance(int argc, char **argv)
{
  if(!_instance){
    _instance = new FlGui(argc, argv);
    // set all options in the new GUI
    InitOptionsGUI(0);
    // say welcome!
    Msg::StatusBar(1, false, "Geometry");
    Msg::StatusBar(2, false, "Gmsh %s", GetGmshVersion());
    // log the following for bug reports
    Msg::Info("-------------------------------------------------------");
    Msg::Info("Gmsh version   : %s", GetGmshVersion());
    Msg::Info("Build OS       : %s", GetGmshBuildOS());
    Msg::Info("Build options  :%s", GetGmshBuildOptions());
    Msg::Info("Build date     : %s", GetGmshBuildDate());
    Msg::Info("Build host     : %s", GetGmshBuildHost());
    Msg::Info("Packager       : %s", GetGmshPackager());
    Msg::Info("Home directory : %s", CTX::instance()->homeDir.c_str());
    Msg::Info("Launch date    : %s", Msg::GetLaunchDate().c_str());
    Msg::Info("Command line   : %s", Msg::GetCommandLineArgs().c_str());
    Msg::Info("-------------------------------------------------------");
  }
  return _instance;
}

int FlGui::run()
{
  // bounding box computation necessary if we run the gui without
  // merging any files (e.g. if we build the geometry with python and
  // create the gui from the python script)
  SetBoundingBox();

  // draw the scene
  drawContext::global()->draw();

  return Fl::run();
}

int FlGui::testGlobalShortcuts(int event)
{
  // we only handle shortcuts here
  if(event != FL_SHORTCUT) return 0;

  int status = 0;

  if(Fl::test_shortcut('0')) {
    // FIXME: here we should also reset all onelab variables that depend on Gmsh
    geometry_reload_cb(0, 0);
    mod_geometry_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut('1') || Fl::test_shortcut(FL_F + 1)) {
    mesh_1d_cb(0, 0);
    mod_mesh_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut('2') || Fl::test_shortcut(FL_F + 2)) {
    mesh_2d_cb(0, 0);
    mod_mesh_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut('3') || Fl::test_shortcut(FL_F + 3)) {
    mesh_3d_cb(0, 0);
    mod_mesh_cb(0, 0);
    status = 1;
  }
  // FIXME TEST
  else if(Fl::test_shortcut('4') || Fl::test_shortcut(FL_F + 4)) {
    RecombineMesh(GModel::current());
    status = 2;
  }
  else if(Fl::test_shortcut(FL_CTRL + 'q') || Fl::test_shortcut(FL_META + 'q')){
    // only necessary when using the system menu bar, but hey, it
    // cannot hurt...
    file_quit_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut('g')) {
    mod_geometry_cb(0, 0);
    Fl::focus(menu->scroll);
    status = 1;
  }
  else if(Fl::test_shortcut('m')) {
    mod_mesh_cb(0, 0);
    Fl::focus(menu->scroll);
    status = 1;
  }
  else if(Fl::test_shortcut('s')) {
    mod_solver_cb(0, 0);
    Fl::focus(menu->scroll);
    status = 1;
  }
  else if(Fl::test_shortcut('p')) {
    mod_post_cb(0, 0);
    Fl::focus(menu->scroll);
    status = 1;
  }
  else if(Fl::test_shortcut('<')) {
    mod_back_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut('>')) {
    mod_forward_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut('w')) {
    file_watch_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut('e')) {
    for(unsigned int i = 0; i < graph.size(); i++)
      for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
        graph[i]->gl[j]->endSelection = 1;
    status = 0; // trick: do as if we didn't use it
  }
  else if(Fl::test_shortcut('u')) {
    for(unsigned int i = 0; i < graph.size(); i++)
      for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
        graph[i]->gl[j]->undoSelection = 1;
    status = 0; // trick: do as if we didn't use it
  }
  else if(Fl::test_shortcut('i')) {
    for(unsigned int i = 0; i < graph.size(); i++)
      for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
        graph[i]->gl[j]->invertSelection = 1;
    status = 0; // trick: do as if we didn't use it
  }
  else if(Fl::test_shortcut('q')) {
    for(unsigned int i = 0; i < graph.size(); i++)
      for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
        graph[i]->gl[j]->quitSelection = 1;
    status = 0; // trick: do as if we didn't use it
  }
  else if(Fl::test_shortcut('-')) {
    for(unsigned int i = 0; i < graph.size(); i++)
      for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
        graph[i]->gl[j]->invertSelection = 1;
    status = 0; // trick: do as if we didn't use it
  }
  else if(Fl::test_shortcut(FL_Escape) ||
          Fl::test_shortcut(FL_META + FL_Escape) ||
          Fl::test_shortcut(FL_SHIFT + FL_Escape) ||
          Fl::test_shortcut(FL_CTRL + FL_Escape) ||
          Fl::test_shortcut(FL_ALT + FL_Escape)) {
    bool lasso = false;
    for(unsigned int i = 0; i < graph.size(); i++)
      for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
        if(graph[i]->gl[j]->lassoMode) lasso = true;
    if(lasso){
      for(unsigned int i = 0; i < graph.size(); i++)
        for(unsigned int j = 0; j < graph[i]->gl.size(); j++)
          graph[i]->gl[j]->lassoMode = false;
      status = 2;
    }
    else{
      status_options_cb(0, (void *)"S");
      status = 1;
    }
  }
  else if(Fl::test_shortcut(FL_SHIFT + 'a')) {
    window_cb(0, (void*)"front");
    status = 1;
  }
  else if(Fl::test_shortcut(FL_SHIFT + 'o')) {
    general_options_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut(FL_SHIFT + 'g')) {
    geometry_options_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut(FL_SHIFT + 'm')) {
    mesh_options_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut(FL_SHIFT + 's')) {
    solver_options_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut(FL_SHIFT + 'p')) {
    post_options_cb(0, 0);
    status = 1;
  }
  else if(Fl::test_shortcut(FL_SHIFT + 'w')) {
    if(PView::list.size()){
      if(options->view.index >= 0 && options->view.index < (int)PView::list.size())
        options->showGroup(options->view.index + 6);
      else
        options->showGroup(6);
    }
    status = 1;
  }
  else if(Fl::test_shortcut(FL_SHIFT + 'u')) {
    if(PView::list.size()){
      if(options->view.index >= 0 && options->view.index < (int)PView::list.size())
        plugins->show(options->view.index);
      else
        plugins->show(0);
    }
    status = 1;
  }
  else if(Fl::test_shortcut(FL_ALT + 'f')) {
    opt_general_fast_redraw
      (0, GMSH_SET | GMSH_GUI, !opt_general_fast_redraw(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'b')) {
    opt_general_draw_bounding_box
      (0, GMSH_SET | GMSH_GUI, !opt_general_draw_bounding_box(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'i')) {
    for(unsigned int i = 0; i < PView::list.size(); i++)
      if(opt_view_visible(i, GMSH_GET, 0))
        opt_view_show_scale
          (i, GMSH_SET | GMSH_GUI, !opt_view_show_scale(i, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'c')) {
    opt_general_color_scheme
      (0, GMSH_SET | GMSH_GUI, opt_general_color_scheme(0, GMSH_GET, 0) + 1);
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'w')) {
    opt_geometry_light
      (0, GMSH_SET | GMSH_GUI, !opt_geometry_light(0, GMSH_GET, 0));
    opt_mesh_light
      (0, GMSH_SET | GMSH_GUI, !opt_mesh_light(0, GMSH_GET, 0));
    for(unsigned int i = 0; i < PView::list.size(); i++)
      if(opt_view_visible(i, GMSH_GET, 0))
        opt_view_light
          (i, GMSH_SET | GMSH_GUI, !opt_view_light(i, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 'w')) {
    opt_mesh_reverse_all_normals
      (0, GMSH_SET | GMSH_GUI, !opt_mesh_reverse_all_normals(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'x') ||
          Fl::test_shortcut(FL_ALT + FL_SHIFT + 'x')) {
    status_xyz1p_cb(0, (void *)"x");
    status = 1;
  }
  else if(Fl::test_shortcut(FL_ALT + 'y') ||
          Fl::test_shortcut(FL_ALT + FL_SHIFT + 'y')) {
    status_xyz1p_cb(0, (void *)"y");
    status = 1;
  }
  else if(Fl::test_shortcut(FL_ALT + 'z') ||
          Fl::test_shortcut(FL_ALT + FL_SHIFT + 'z')) {
    status_xyz1p_cb(0, (void *)"z");
    status = 1;
  }
  else if(Fl::test_shortcut(FL_ALT + 'o') ||
          Fl::test_shortcut(FL_ALT + FL_SHIFT + 'o')) {
    status_options_cb(0, (void *)"p");
    status = 1;
  }
  else if(Fl::test_shortcut(FL_ALT + 'a')) {
    opt_general_axes
      (0, GMSH_SET | GMSH_GUI, opt_general_axes(0, GMSH_GET, 0) + 1);
    for(unsigned int i = 0; i < PView::list.size(); i++)
      if(opt_view_visible(i, GMSH_GET, 0))
        opt_view_axes(i, GMSH_SET | GMSH_GUI, opt_view_axes(i, GMSH_GET, 0) + 1);
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 'a')) {
    opt_general_small_axes
      (0, GMSH_SET | GMSH_GUI, !opt_general_small_axes(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'p')) {
    opt_geometry_points
      (0, GMSH_SET | GMSH_GUI, !opt_geometry_points(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'l')) {
    opt_geometry_lines
      (0, GMSH_SET | GMSH_GUI, !opt_geometry_lines(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 's')) {
    opt_geometry_surfaces
      (0, GMSH_SET | GMSH_GUI, !opt_geometry_surfaces(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'v')) {
    opt_geometry_volumes
      (0, GMSH_SET | GMSH_GUI, !opt_geometry_volumes(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 'p')) {
    opt_mesh_points(0, GMSH_SET | GMSH_GUI, !opt_mesh_points(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 'l')) {
    opt_mesh_lines
      (0, GMSH_SET | GMSH_GUI, !opt_mesh_lines(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 's')) {
    opt_mesh_surfaces_edges
      (0, GMSH_SET | GMSH_GUI, !opt_mesh_surfaces_edges(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 'v')) {
    opt_mesh_volumes_edges
      (0, GMSH_SET | GMSH_GUI, !opt_mesh_volumes_edges(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'd')){
    opt_geometry_surface_type
      (0, GMSH_SET | GMSH_GUI, opt_geometry_surface_type(0, GMSH_GET, 0) + 1);
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 'd')) {
    opt_mesh_surfaces_faces
      (0, GMSH_SET | GMSH_GUI, !opt_mesh_surfaces_faces(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + FL_SHIFT + 'b')) {
    opt_mesh_volumes_faces
      (0, GMSH_SET | GMSH_GUI, !opt_mesh_volumes_faces(0, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'm')) {
    status_options_cb(0, (void *)"M");
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 't')) {
    for(unsigned int i = 0; i < PView::list.size(); i++)
      if(opt_view_visible(i, GMSH_GET, 0))
        opt_view_intervals_type
          (i, GMSH_SET | GMSH_GUI, opt_view_intervals_type(i, GMSH_GET, 0) + 1);
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'r')) {
    for(unsigned int i = 0; i < PView::list.size(); i++)
      if(opt_view_visible(i, GMSH_GET, 0))
        opt_view_range_type
          (i, GMSH_SET | GMSH_GUI, opt_view_range_type(i, GMSH_GET, 0) + 1);
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'n')) {
    for(unsigned int i = 0; i < PView::list.size(); i++)
      if(opt_view_visible(i, GMSH_GET, 0))
        opt_view_draw_strings
          (i, GMSH_SET | GMSH_GUI, !opt_view_draw_strings(i, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'e') ||
          Fl::test_shortcut(FL_ALT + FL_SHIFT + 'e')) {
    for(unsigned int i = 0; i < PView::list.size(); i++)
      if(opt_view_visible(i, GMSH_GET, 0))
        opt_view_show_element
          (i, GMSH_SET | GMSH_GUI, !opt_view_show_element(i, GMSH_GET, 0));
    status = 2;
  }
  else if(Fl::test_shortcut(FL_ALT + 'h')) {
    static int show = 0;
    for(unsigned int i = 0; i < PView::list.size(); i++)
      opt_view_visible(i, GMSH_SET | GMSH_GUI, show);
    show = !show;
    status = 2;
  }
  else if(testArrowShortcuts()) {
    status = 1;
  }

  if(status == 2){
    drawContext::global()->draw();
    return 1;
  }
  else if(status == 1)
    return 1;
  else
    return 0;
}

int FlGui::testArrowShortcuts()
{
  if(Fl::test_shortcut(FL_Left)) {
    status_play_manual(1, -CTX::instance()->post.animStep);
    return 1;
  }
  else if(Fl::test_shortcut(FL_Right)) {
    status_play_manual(1, CTX::instance()->post.animStep);
    return 1;
  }
  else if(Fl::test_shortcut(FL_Up)) {
    status_play_manual(0, -CTX::instance()->post.animStep);
    return 1;
  }
  else if(Fl::test_shortcut(FL_Down)) {
    status_play_manual(0, CTX::instance()->post.animStep);
    return 1;
  }
  return 0;
}

void FlGui::setGraphicTitle(std::string title)
{
  for(unsigned int i = 0; i < graph.size(); i++){
    if(!i){
      graph[i]->setTitle(title);
    }
    else{
      std::ostringstream sstream;
      sstream << title << " [" << i << "]";
      graph[i]->setTitle(sstream.str());
    }
  }
}

void FlGui::updateViews(bool numberOfViewsHasChanged)
{
  for(unsigned int i = 0; i < graph.size(); i++)
    graph[i]->checkAnimButtons();
  if(numberOfViewsHasChanged){
    if(menu->module->value() == 3)
      menu->setContext(menu_post, 0);
    options->resetBrowser();
    options->resetExternalViewList();
    fields->loadFieldViewList();
    plugins->resetViewBrowser();
    clipping->resetBrowser();
  }
}

void FlGui::updateFields()
{
  fields->editField(GModel::current()->getFields()->get(fields->selected_id));
}

void FlGui::resetVisibility()
{
  if(visibility->win->shown())
    visibility_cb(NULL, NULL);
}

openglWindow *FlGui::getCurrentOpenglWindow()
{
  if(openglWindow::getLastHandled())
    return openglWindow::getLastHandled();
  else
    return graph[0]->gl[0];
}

void FlGui::splitCurrentOpenglWindow(char how)
{
  openglWindow *g = getCurrentOpenglWindow();
  for(unsigned int i = 0; i < graph.size(); i++){
    if(graph[i]->tile->find(g) != graph[i]->tile->children()){
      graph[i]->split(g, how);
      break;
    }
  }
}

char FlGui::selectEntity(int type)
{
  return getCurrentOpenglWindow()->selectEntity
    (type, selectedVertices, selectedEdges, selectedFaces, selectedRegions,
     selectedElements);
}

void FlGui::setStatus(const char *msg, int num)
{
  if(num == 0 || num == 1){
    static char buff[2][1024];
    strncpy(buff[num], msg, sizeof(buff[num]) - 1);
    buff[num][sizeof(buff[num]) - 1] = '\0';
    for(unsigned int i = 0; i < graph.size(); i++){
      graph[i]->label[num]->label(buff[num]);
      graph[i]->label[num]->redraw();
    }
  }
  else if(num == 2){
    openglWindow *gl = getCurrentOpenglWindow();
    int n = strlen(msg);
    int i = 0;
    while(i < n) if(msg[i++] == '\n') break;
    gl->screenMessage[0] = std::string(msg);
    if(i)
      gl->screenMessage[0].resize(i - 1);
    if(i < n)
      gl->screenMessage[1] = std::string(&msg[i]);
    else
      gl->screenMessage[1].clear();
    drawContext::global()->draw();
  }
}

void FlGui::storeCurrentWindowsInfo()
{
  CTX::instance()->menuPosition[0] = menu->win->x();
  CTX::instance()->menuPosition[1] = menu->win->y();
  CTX::instance()->glPosition[0] = graph[0]->win->x();
  CTX::instance()->glPosition[1] = graph[0]->win->y();
  CTX::instance()->glSize[0] = graph[0]->win->w();
  CTX::instance()->glSize[1] = (graph[0]->win->h() - graph[0]->bottom->h());
  CTX::instance()->msgSize = graph[0]->getMessageHeight();
  CTX::instance()->optPosition[0] = options->win->x();
  CTX::instance()->optPosition[1] = options->win->y();
  CTX::instance()->pluginPosition[0] = plugins->win->x();
  CTX::instance()->pluginPosition[1] = plugins->win->y();
  CTX::instance()->pluginSize[0] = plugins->win->w();
  CTX::instance()->pluginSize[1] = plugins->win->h();
  CTX::instance()->fieldPosition[0] = fields->win->x();
  CTX::instance()->fieldPosition[1] = fields->win->y();
  CTX::instance()->fieldSize[0] = fields->win->w();
  CTX::instance()->fieldSize[1] = fields->win->h();
  CTX::instance()->statPosition[0] = stats->win->x();
  CTX::instance()->statPosition[1] = stats->win->y();
  CTX::instance()->visPosition[0] = visibility->win->x();
  CTX::instance()->visPosition[1] = visibility->win->y();
  CTX::instance()->clipPosition[0] = clipping->win->x();
  CTX::instance()->clipPosition[1] = clipping->win->y();
  CTX::instance()->manipPosition[0] = manip->win->x();
  CTX::instance()->manipPosition[1] = manip->win->y();
  CTX::instance()->ctxPosition[0] = geoContext->win->x();
  CTX::instance()->ctxPosition[1] = meshContext->win->y();
#if defined(HAVE_ONELAB) && (FL_MAJOR_VERSION == 1) && (FL_MINOR_VERSION == 3)
  CTX::instance()->solverPosition[0] = onelab->x();
  CTX::instance()->solverPosition[1] = onelab->y();
  CTX::instance()->solverSize[0] = onelab->w();
  CTX::instance()->solverSize[1] = onelab->h();
#endif
  fileChooserGetPosition(&CTX::instance()->fileChooserPosition[0],
                         &CTX::instance()->fileChooserPosition[1]);
}

void FlGui::callForSolverPlugin(int dim)
{
  GMSH_SolverPlugin *sp = PluginManager::instance()->findSolverPlugin();
  if(sp) sp->popupPropertiesForPhysicalEntity(dim);
}

// Callbacks

void redraw_cb(Fl_Widget *w, void *data)
{
  drawContext::global()->draw();
}

void window_cb(Fl_Widget *w, void *data)
{
  static int oldx = 0, oldy = 0, oldw = 0, oldh = 0, zoom = 1;
  std::string str((const char*)data);

  if(str == "minimize"){
    for(unsigned int i = 0; i < FlGui::instance()->graph.size(); i++)
      if(FlGui::instance()->graph[i]->win->shown())
        FlGui::instance()->graph[i]->win->iconize();
    if(FlGui::instance()->options->win->shown())
      FlGui::instance()->options->win->iconize();
    if(FlGui::instance()->plugins->win->shown())
      FlGui::instance()->plugins->win->iconize();
    if(FlGui::instance()->fields->win->shown())
      FlGui::instance()->fields->win->iconize();
    if(FlGui::instance()->visibility->win->shown())
      FlGui::instance()->visibility->win->iconize();
    if(FlGui::instance()->clipping->win->shown())
      FlGui::instance()->clipping->win->iconize();
    if(FlGui::instance()->manip->win->shown())
      FlGui::instance()->manip->win->iconize();
    if(FlGui::instance()->stats->win->shown())
      FlGui::instance()->stats->win->iconize();
    if(FlGui::instance()->menu->win->shown())
      FlGui::instance()->menu->win->iconize();
  }
  else if(str == "zoom"){
    if(zoom){
      oldx = FlGui::instance()->graph[0]->win->x();
      oldy = FlGui::instance()->graph[0]->win->y();
      oldw = FlGui::instance()->graph[0]->win->w();
      oldh = FlGui::instance()->graph[0]->win->h();
//#define FS
#ifndef FS
      FlGui::instance()->graph[0]->win->resize(Fl::x(), Fl::y(), Fl::w(), Fl::h());
      FlGui::instance()->graph[0]->hideMessages();
      FlGui::check();
#else
      FlGui::instance()->graph[0]->win->fullscreen();
#endif
      zoom = 0;
    }
    else{
#ifndef FS
      FlGui::instance()->graph[0]->win->resize(oldx, oldy, oldw, oldh);
#else
      FlGui::instance()->graph[0]->win->fullscreen_off();
#endif
      zoom = 1;
    }
    FlGui::instance()->menu->win->show();
  }
  else if(str == "front"){
    // the order is important!
    for(unsigned int i = 0; i < FlGui::instance()->graph.size(); i++)
      FlGui::instance()->graph[i]->win->show();
    if(FlGui::instance()->options->win->shown())
      FlGui::instance()->options->win->show();
    if(FlGui::instance()->plugins->win->shown())
      FlGui::instance()->plugins->win->show();
    if(FlGui::instance()->fields->win->shown())
      FlGui::instance()->fields->win->show();
    if(FlGui::instance()->geoContext->win->shown())
      FlGui::instance()->geoContext->win->show();
    if(FlGui::instance()->meshContext->win->shown())
      FlGui::instance()->meshContext->win->show();
#if defined(HAVE_ONELAB) && (FL_MAJOR_VERSION == 1) && (FL_MINOR_VERSION == 3)
    if(FlGui::instance()->onelab->shown())
      FlGui::instance()->onelab->show();
#endif
    if(FlGui::instance()->visibility->win->shown())
      FlGui::instance()->visibility->win->show();
    if(FlGui::instance()->clipping->win->shown())
      FlGui::instance()->clipping->win->show();
    if(FlGui::instance()->manip->win->shown())
      FlGui::instance()->manip->win->show();
    if(FlGui::instance()->stats->win->shown())
      FlGui::instance()->stats->win->show();
    FlGui::instance()->menu->win->show();
  }
}

void FlGui::addMessage(const char *msg)
{
  for(unsigned int i = 0; i < FlGui::instance()->graph.size(); i++)
    FlGui::instance()->graph[i]->addMessage(msg);
}

void FlGui::showMessages()
{
  for(unsigned int i = 0; i < FlGui::instance()->graph.size(); i++)
    FlGui::instance()->graph[i]->showMessages();
}

void FlGui::saveMessages(const char *fileName)
{
  FlGui::instance()->graph[0]->saveMessages(fileName);
}
