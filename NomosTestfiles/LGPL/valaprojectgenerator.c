/* valaprojectgenerator.vala
 *
 * Copyright (C) 2007-2008  Jürg Billeter
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.

 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.

 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
 *
 * Author:
 * 	Jürg Billeter <j@bitron.ch>
 */

#include <gen-project/valaprojectgenerator.h>
#include <stdlib.h>
#include <string.h>
#include <glib/gstdio.h>
#include <config.h>
#include <string.h>


#define VALA_TYPE_PROJECT_TYPE (vala_project_type_get_type ())

#define VALA_TYPE_PROJECT_LICENSE (vala_project_license_get_type ())

#define VALA_TYPE_PROJECT_GENERATOR (vala_project_generator_get_type ())
#define VALA_PROJECT_GENERATOR(obj) (G_TYPE_CHECK_INSTANCE_CAST ((obj), VALA_TYPE_PROJECT_GENERATOR, ValaProjectGenerator))
#define VALA_PROJECT_GENERATOR_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST ((klass), VALA_TYPE_PROJECT_GENERATOR, ValaProjectGeneratorClass))
#define VALA_IS_PROJECT_GENERATOR(obj) (G_TYPE_CHECK_INSTANCE_TYPE ((obj), VALA_TYPE_PROJECT_GENERATOR))
#define VALA_IS_PROJECT_GENERATOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), VALA_TYPE_PROJECT_GENERATOR))
#define VALA_PROJECT_GENERATOR_GET_CLASS(obj) (G_TYPE_INSTANCE_GET_CLASS ((obj), VALA_TYPE_PROJECT_GENERATOR, ValaProjectGeneratorClass))

typedef struct _ValaProjectGenerator ValaProjectGenerator;
typedef struct _ValaProjectGeneratorClass ValaProjectGeneratorClass;
typedef struct _ValaProjectGeneratorPrivate ValaProjectGeneratorPrivate;

typedef enum  {
	VALA_PROJECT_TYPE_CONSOLE_APPLICATION,
	VALA_PROJECT_TYPE_GTK_APPLICATION
} ValaProjectType;

typedef enum  {
	VALA_PROJECT_LICENSE_GPL2,
	VALA_PROJECT_LICENSE_GPL3,
	VALA_PROJECT_LICENSE_LGPL2,
	VALA_PROJECT_LICENSE_LGPL3
} ValaProjectLicense;

struct _ValaProjectGenerator {
	GtkDialog parent_instance;
	ValaProjectGeneratorPrivate * priv;
};

struct _ValaProjectGeneratorClass {
	GtkDialogClass parent_class;
};



GType vala_project_type_get_type (void);
GType vala_project_license_get_type (void);
struct _ValaProjectGeneratorPrivate {
	GtkFileChooserButton* project_folder_button;
	GtkComboBox* project_type_combobox;
	GtkComboBox* license_combobox;
	GtkEntry* name_entry;
	GtkEntry* email_entry;
	char* project_path;
	char* project_name;
	char* namespace_name;
	char* make_name;
	char* upper_case_make_name;
	char* real_name;
	char* email_address;
	ValaProjectType project_type;
	ValaProjectLicense project_license;
};

#define VALA_PROJECT_GENERATOR_GET_PRIVATE(o) (G_TYPE_INSTANCE_GET_PRIVATE ((o), VALA_TYPE_PROJECT_GENERATOR, ValaProjectGeneratorPrivate))
enum  {
	VALA_PROJECT_GENERATOR_DUMMY_PROPERTY
};
static ValaProjectGenerator* vala_project_generator_construct (GType object_type);
static ValaProjectGenerator* vala_project_generator_new (void);
static GtkHBox* vala_project_generator_create_hbox (ValaProjectGenerator* self, const char* title, GtkSizeGroup* size_group);
static void vala_project_generator_create_project (ValaProjectGenerator* self);
static void vala_project_generator_write_autogen_sh (ValaProjectGenerator* self, GError** error);
static void vala_project_generator_write_configure_ac (ValaProjectGenerator* self, GError** error);
static void vala_project_generator_write_makefile_am (ValaProjectGenerator* self, GError** error);
static char* vala_project_generator_generate_source_file_header (ValaProjectGenerator* self, const char* filename);
static void vala_project_generator_write_main_vala (ValaProjectGenerator* self, GError** error);
static void vala_project_generator_write_mainwindow_vala (ValaProjectGenerator* self, GError** error);
static void vala_project_generator_write_potfiles (ValaProjectGenerator* self, GError** error);
static void vala_project_generator_write_linguas (ValaProjectGenerator* self, GError** error);
static void vala_project_generator_write_authors (ValaProjectGenerator* self, GError** error);
static void vala_project_generator_write_maintainers (ValaProjectGenerator* self, GError** error);
static char* vala_project_generator_get_automake_path (ValaProjectGenerator* self);
static void vala_project_generator_main (char** args, int args_length1);
static GObject * vala_project_generator_constructor (GType type, guint n_construct_properties, GObjectConstructParam * construct_properties);
static gpointer vala_project_generator_parent_class = NULL;
static void vala_project_generator_finalize (GObject* obj);
static GType vala_project_generator_get_type (void);
static void _vala_array_free (gpointer array, gint array_length, GDestroyNotify destroy_func);




GType vala_project_type_get_type (void) {
	static GType vala_project_type_type_id = 0;
	if (G_UNLIKELY (vala_project_type_type_id == 0)) {
		static const GEnumValue values[] = {{VALA_PROJECT_TYPE_CONSOLE_APPLICATION, "VALA_PROJECT_TYPE_CONSOLE_APPLICATION", "console-application"}, {VALA_PROJECT_TYPE_GTK_APPLICATION, "VALA_PROJECT_TYPE_GTK_APPLICATION", "gtk-application"}, {0, NULL, NULL}};
		vala_project_type_type_id = g_enum_register_static ("ValaProjectType", values);
	}
	return vala_project_type_type_id;
}



GType vala_project_license_get_type (void) {
	static GType vala_project_license_type_id = 0;
	if (G_UNLIKELY (vala_project_license_type_id == 0)) {
		static const GEnumValue values[] = {{VALA_PROJECT_LICENSE_GPL2, "VALA_PROJECT_LICENSE_GPL2", "gpl2"}, {VALA_PROJECT_LICENSE_GPL3, "VALA_PROJECT_LICENSE_GPL3", "gpl3"}, {VALA_PROJECT_LICENSE_LGPL2, "VALA_PROJECT_LICENSE_LGPL2", "lgpl2"}, {VALA_PROJECT_LICENSE_LGPL3, "VALA_PROJECT_LICENSE_LGPL3", "lgpl3"}, {0, NULL, NULL}};
		vala_project_license_type_id = g_enum_register_static ("ValaProjectLicense", values);
	}
	return vala_project_license_type_id;
}


static ValaProjectGenerator* vala_project_generator_construct (GType object_type) {
	ValaProjectGenerator * self;
	self = g_object_newv (object_type, 0, NULL);
	gtk_window_set_title (((GtkWindow*) (self)), "Vala Project Generator");
	return self;
}


static ValaProjectGenerator* vala_project_generator_new (void) {
	return vala_project_generator_construct (VALA_TYPE_PROJECT_GENERATOR);
}


static GtkHBox* vala_project_generator_create_hbox (ValaProjectGenerator* self, const char* title, GtkSizeGroup* size_group) {
	GtkHBox* hbox;
	GtkLabel* label;
	GtkLabel* _tmp0;
	GtkHBox* _tmp1;
	g_return_val_if_fail (self != NULL, NULL);
	g_return_val_if_fail (title != NULL, NULL);
	g_return_val_if_fail (size_group != NULL, NULL);
	hbox = g_object_ref_sink (((GtkHBox*) (gtk_hbox_new (FALSE, 6))));
	gtk_box_pack_start (((GtkBox*) ((GTK_VBOX (((GtkDialog*) (self))->vbox)))), ((GtkWidget*) (hbox)), FALSE, FALSE, ((guint) (0)));
	gtk_widget_show (((GtkWidget*) (hbox)));
	label = g_object_ref_sink (((GtkLabel*) (gtk_label_new ("    "))));
	gtk_box_pack_start (((GtkBox*) (hbox)), ((GtkWidget*) (label)), FALSE, FALSE, ((guint) (0)));
	gtk_widget_show (((GtkWidget*) (label)));
	_tmp0 = NULL;
	label = (_tmp0 = g_object_ref_sink (((GtkLabel*) (gtk_label_new (title)))), (label == NULL ? NULL : (label = (g_object_unref (label), NULL))), _tmp0);
	gtk_box_pack_start (((GtkBox*) (hbox)), ((GtkWidget*) (label)), FALSE, FALSE, ((guint) (0)));
	g_object_set (((GtkMisc*) (label)), "xalign", ((float) (0)), NULL);
	gtk_widget_show (((GtkWidget*) (label)));
	gtk_size_group_add_widget (size_group, ((GtkWidget*) (label)));
	_tmp1 = NULL;
	return (_tmp1 = hbox, (label == NULL ? NULL : (label = (g_object_unref (label), NULL))), _tmp1);
}


static void vala_project_generator_create_project (ValaProjectGenerator* self) {
	GError * inner_error;
	char* _tmp1;
	const char* _tmp0;
	char* _tmp2;
	GString* project_name_str;
	GString* make_name_str;
	GString* namespace_name_str;
	char* _tmp4;
	const char* _tmp3;
	char* _tmp10;
	char* _tmp9;
	char* _tmp8;
	char* _tmp7;
	char* _tmp6;
	char* _tmp5;
	char* _tmp12;
	const char* _tmp11;
	char* _tmp13;
	char* _tmp15;
	const char* _tmp14;
	char* _tmp17;
	const char* _tmp16;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	_tmp1 = NULL;
	_tmp0 = NULL;
	self->priv->project_path = (_tmp1 = (_tmp0 = gtk_file_chooser_get_current_folder (((GtkFileChooser*) (self->priv->project_folder_button))), (_tmp0 == NULL ? NULL : g_strdup (_tmp0))), (self->priv->project_path = (g_free (self->priv->project_path), NULL)), _tmp1);
	_tmp2 = NULL;
	self->priv->project_name = (_tmp2 = g_path_get_basename (self->priv->project_path), (self->priv->project_name = (g_free (self->priv->project_name), NULL)), _tmp2);
	/* only use [a-zA-Z0-9-]* as projectname*/
	project_name_str = g_string_new ("");
	make_name_str = g_string_new ("");
	namespace_name_str = g_string_new ("");
	{
		gint i;
		i = 0;
		for (; i < g_utf8_strlen (self->priv->project_name, -1); i++) {
			gunichar c;
			c = g_utf8_get_char (g_utf8_offset_to_pointer (self->priv->project_name, i));
			if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9')) {
				g_string_append_unichar (project_name_str, c);
				g_string_append_unichar (make_name_str, c);
				g_string_append_unichar (namespace_name_str, c);
			} else {
				if (c == '-' || c == ' ') {
					g_string_append_unichar (project_name_str, ((gunichar) ('-')));
					g_string_append_unichar (make_name_str, ((gunichar) ('_')));
				}
			}
		}
	}
	_tmp4 = NULL;
	_tmp3 = NULL;
	self->priv->project_name = (_tmp4 = (_tmp3 = project_name_str->str, (_tmp3 == NULL ? NULL : g_strdup (_tmp3))), (self->priv->project_name = (g_free (self->priv->project_name), NULL)), _tmp4);
	_tmp10 = NULL;
	_tmp9 = NULL;
	_tmp8 = NULL;
	_tmp7 = NULL;
	_tmp6 = NULL;
	_tmp5 = NULL;
	self->priv->namespace_name = (_tmp10 = g_strconcat ((_tmp7 = g_utf8_strup ((_tmp6 = (_tmp5 = g_utf8_offset_to_pointer (namespace_name_str->str, ((glong) (0))), g_strndup (_tmp5, g_utf8_offset_to_pointer (_tmp5, ((glong) (1))) - _tmp5))), -1)), (_tmp9 = (_tmp8 = g_utf8_offset_to_pointer (namespace_name_str->str, ((glong) (1))), g_strndup (_tmp8, g_utf8_offset_to_pointer (_tmp8, g_utf8_strlen (namespace_name_str->str, -1) - 1) - _tmp8))), NULL), (self->priv->namespace_name = (g_free (self->priv->namespace_name), NULL)), _tmp10);
	_tmp9 = (g_free (_tmp9), NULL);
	_tmp7 = (g_free (_tmp7), NULL);
	_tmp6 = (g_free (_tmp6), NULL);
	_tmp12 = NULL;
	_tmp11 = NULL;
	self->priv->make_name = (_tmp12 = (_tmp11 = make_name_str->str, (_tmp11 == NULL ? NULL : g_strdup (_tmp11))), (self->priv->make_name = (g_free (self->priv->make_name), NULL)), _tmp12);
	_tmp13 = NULL;
	self->priv->upper_case_make_name = (_tmp13 = g_utf8_strup (self->priv->make_name, -1), (self->priv->upper_case_make_name = (g_free (self->priv->upper_case_make_name), NULL)), _tmp13);
	self->priv->project_type = ((ValaProjectType) (gtk_combo_box_get_active (self->priv->project_type_combobox)));
	self->priv->project_license = ((ValaProjectLicense) (gtk_combo_box_get_active (self->priv->license_combobox)));
	_tmp15 = NULL;
	_tmp14 = NULL;
	self->priv->real_name = (_tmp15 = (_tmp14 = gtk_entry_get_text (self->priv->name_entry), (_tmp14 == NULL ? NULL : g_strdup (_tmp14))), (self->priv->real_name = (g_free (self->priv->real_name), NULL)), _tmp15);
	_tmp17 = NULL;
	_tmp16 = NULL;
	self->priv->email_address = (_tmp17 = (_tmp16 = gtk_entry_get_text (self->priv->email_entry), (_tmp16 == NULL ? NULL : g_strdup (_tmp16))), (self->priv->email_address = (g_free (self->priv->email_address), NULL)), _tmp17);
	{
		char* _tmp18;
		char* _tmp19;
		char* _tmp20;
		char* _tmp21;
		char* _tmp22;
		char* _tmp23;
		char* s;
		char* automake_path;
		char* license_filename;
		vala_project_generator_write_autogen_sh (self, &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		vala_project_generator_write_configure_ac (self, &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		vala_project_generator_write_makefile_am (self, &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		_tmp18 = NULL;
		g_mkdir ((_tmp18 = g_strconcat (self->priv->project_path, "/src", NULL)), 0777);
		_tmp18 = (g_free (_tmp18), NULL);
		_tmp19 = NULL;
		g_mkdir ((_tmp19 = g_strconcat (self->priv->project_path, "/po", NULL)), 0777);
		_tmp19 = (g_free (_tmp19), NULL);
		if (self->priv->project_type == VALA_PROJECT_TYPE_CONSOLE_APPLICATION) {
			vala_project_generator_write_main_vala (self, &inner_error);
			if (inner_error != NULL) {
				if (inner_error->domain == G_FILE_ERROR) {
					goto __catch0_g_file_error;
				}
				g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
				g_clear_error (&inner_error);
			}
		} else {
			if (self->priv->project_type == VALA_PROJECT_TYPE_GTK_APPLICATION) {
				vala_project_generator_write_mainwindow_vala (self, &inner_error);
				if (inner_error != NULL) {
					if (inner_error->domain == G_FILE_ERROR) {
						goto __catch0_g_file_error;
					}
					g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
					g_clear_error (&inner_error);
				}
			}
		}
		vala_project_generator_write_authors (self, &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		vala_project_generator_write_maintainers (self, &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		vala_project_generator_write_linguas (self, &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		vala_project_generator_write_potfiles (self, &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		_tmp20 = NULL;
		g_file_set_contents ((_tmp20 = g_strconcat (self->priv->project_path, "/NEWS", NULL)), "", ((glong) (-1)), &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		_tmp20 = (g_free (_tmp20), NULL);
		_tmp21 = NULL;
		g_file_set_contents ((_tmp21 = g_strconcat (self->priv->project_path, "/README", NULL)), "", ((glong) (-1)), &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		_tmp21 = (g_free (_tmp21), NULL);
		_tmp22 = NULL;
		g_file_set_contents ((_tmp22 = g_strconcat (self->priv->project_path, "/ChangeLog", NULL)), "", ((glong) (-1)), &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		_tmp22 = (g_free (_tmp22), NULL);
		_tmp23 = NULL;
		g_file_set_contents ((_tmp23 = g_strconcat (self->priv->project_path, "/po/ChangeLog", NULL)), "", ((glong) (-1)), &inner_error);
		if (inner_error != NULL) {
			if (inner_error->domain == G_FILE_ERROR) {
				goto __catch0_g_file_error;
			}
			g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
			g_clear_error (&inner_error);
		}
		_tmp23 = (g_free (_tmp23), NULL);
		s = NULL;
		automake_path = vala_project_generator_get_automake_path (self);
		if (automake_path != NULL) {
			char* install_filename;
			install_filename = g_strconcat (automake_path, "/INSTALL", NULL);
			if (g_file_test (install_filename, G_FILE_TEST_EXISTS)) {
				char* _tmp26;
				gboolean _tmp25;
				char* _tmp24;
				char* _tmp27;
				_tmp26 = NULL;
				_tmp24 = NULL;
				_tmp25 = g_file_get_contents (install_filename, &_tmp24, NULL, &inner_error);
				s = (_tmp26 = _tmp24, (s = (g_free (s), NULL)), _tmp26);
				_tmp25;
				if (inner_error != NULL) {
					if (inner_error->domain == G_FILE_ERROR) {
						goto __catch0_g_file_error;
					}
					g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
					g_clear_error (&inner_error);
				}
				_tmp27 = NULL;
				g_file_set_contents ((_tmp27 = g_strconcat (self->priv->project_path, "/INSTALL", NULL)), s, ((glong) (-1)), &inner_error);
				if (inner_error != NULL) {
					if (inner_error->domain == G_FILE_ERROR) {
						goto __catch0_g_file_error;
					}
					g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
					g_clear_error (&inner_error);
				}
				_tmp27 = (g_free (_tmp27), NULL);
			}
			install_filename = (g_free (install_filename), NULL);
		}
		license_filename = NULL;
		if (self->priv->project_license == VALA_PROJECT_LICENSE_GPL2) {
			char* _tmp28;
			_tmp28 = NULL;
			license_filename = (_tmp28 = g_strdup (PACKAGE_DATADIR "/licenses/gpl-2.0.txt"), (license_filename = (g_free (license_filename), NULL)), _tmp28);
			if (!g_file_test (license_filename, G_FILE_TEST_EXISTS)) {
				char* _tmp29;
				_tmp29 = NULL;
				license_filename = (_tmp29 = g_strdup ("/usr/share/common-licenses/GPL-2"), (license_filename = (g_free (license_filename), NULL)), _tmp29);
			}
		} else {
			if (self->priv->project_license == VALA_PROJECT_LICENSE_LGPL2) {
				char* _tmp30;
				_tmp30 = NULL;
				license_filename = (_tmp30 = g_strdup (PACKAGE_DATADIR "/licenses/lgpl-2.1.txt"), (license_filename = (g_free (license_filename), NULL)), _tmp30);
				if (!g_file_test (license_filename, G_FILE_TEST_EXISTS)) {
					char* _tmp31;
					_tmp31 = NULL;
					license_filename = (_tmp31 = g_strdup ("/usr/share/common-licenses/LGPL-2.1"), (license_filename = (g_free (license_filename), NULL)), _tmp31);
				}
			} else {
				if (self->priv->project_license == VALA_PROJECT_LICENSE_GPL3) {
					char* _tmp32;
					_tmp32 = NULL;
					license_filename = (_tmp32 = g_strdup (PACKAGE_DATADIR "/licenses/gpl-3.0.txt"), (license_filename = (g_free (license_filename), NULL)), _tmp32);
					if (!g_file_test (license_filename, G_FILE_TEST_EXISTS)) {
						char* _tmp33;
						_tmp33 = NULL;
						license_filename = (_tmp33 = g_strdup ("/usr/share/common-licenses/GPL-3"), (license_filename = (g_free (license_filename), NULL)), _tmp33);
					}
				} else {
					if (self->priv->project_license == VALA_PROJECT_LICENSE_LGPL3) {
						char* _tmp34;
						_tmp34 = NULL;
						license_filename = (_tmp34 = g_strdup (PACKAGE_DATADIR "/licenses/lgpl-3.0.txt"), (license_filename = (g_free (license_filename), NULL)), _tmp34);
						if (!g_file_test (license_filename, G_FILE_TEST_EXISTS)) {
							char* _tmp35;
							_tmp35 = NULL;
							license_filename = (_tmp35 = g_strdup ("/usr/share/common-licenses/LGPL-3"), (license_filename = (g_free (license_filename), NULL)), _tmp35);
						}
					}
				}
			}
		}
		if (license_filename != NULL && g_file_test (license_filename, G_FILE_TEST_EXISTS)) {
			char* _tmp38;
			gboolean _tmp37;
			char* _tmp36;
			char* _tmp39;
			_tmp38 = NULL;
			_tmp36 = NULL;
			_tmp37 = g_file_get_contents (license_filename, &_tmp36, NULL, &inner_error);
			s = (_tmp38 = _tmp36, (s = (g_free (s), NULL)), _tmp38);
			_tmp37;
			if (inner_error != NULL) {
				if (inner_error->domain == G_FILE_ERROR) {
					goto __catch0_g_file_error;
				}
				g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
				g_clear_error (&inner_error);
			}
			_tmp39 = NULL;
			g_file_set_contents ((_tmp39 = g_strconcat (self->priv->project_path, "/COPYING", NULL)), s, ((glong) (-1)), &inner_error);
			if (inner_error != NULL) {
				if (inner_error->domain == G_FILE_ERROR) {
					goto __catch0_g_file_error;
				}
				g_critical ("file %s: line %d: uncaught error: %s", __FILE__, __LINE__, inner_error->message);
				g_clear_error (&inner_error);
			}
			_tmp39 = (g_free (_tmp39), NULL);
		}
		s = (g_free (s), NULL);
		automake_path = (g_free (automake_path), NULL);
		license_filename = (g_free (license_filename), NULL);
	}
	goto __finally0;
	__catch0_g_file_error:
	{
		GError * e;
		e = inner_error;
		inner_error = NULL;
		{
			g_critical ("valaprojectgenerator.vala:236: Error while creating project: %s", e->message);
			(e == NULL ? NULL : (e = (g_error_free (e), NULL)));
		}
	}
	__finally0:
	;
	(project_name_str == NULL ? NULL : (project_name_str = (g_string_free (project_name_str, TRUE), NULL)));
	(make_name_str == NULL ? NULL : (make_name_str = (g_string_free (make_name_str, TRUE), NULL)));
	(namespace_name_str == NULL ? NULL : (namespace_name_str = (g_string_free (namespace_name_str, TRUE), NULL)));
}


static void vala_project_generator_write_autogen_sh (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	GString* s;
	char* _tmp0;
	char* _tmp1;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	s = g_string_new ("");
	g_string_append (s, "#!/bin/sh\n");
	g_string_append (s, "# Run this to generate all the initial makefiles, etc.\n\n");
	g_string_append (s, "srcdir=`dirname $0`\n");
	g_string_append (s, "test -z \"$srcdir\" && srcdir=.\n\n");
	g_string_append_printf (s, "PKG_NAME=\"%s\"\n\n", self->priv->project_name);
	g_string_append (s, ". gnome-autogen.sh\n");
	_tmp0 = NULL;
	g_file_set_contents ((_tmp0 = g_strconcat (self->priv->project_path, "/autogen.sh", NULL)), s->str, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
		return;
	}
	_tmp0 = (g_free (_tmp0), NULL);
	_tmp1 = NULL;
	g_chmod ((_tmp1 = g_strconcat (self->priv->project_path, "/autogen.sh", NULL)), 0755);
	_tmp1 = (g_free (_tmp1), NULL);
	(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
}


static void vala_project_generator_write_configure_ac (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	gboolean use_gtk;
	GString* s;
	char* _tmp0;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	use_gtk = (self->priv->project_type == VALA_PROJECT_TYPE_GTK_APPLICATION);
	s = g_string_new ("");
	g_string_append_printf (s, "AC_INIT([%s], [0.1.0], [%s], [%s])\n", self->priv->project_name, self->priv->email_address, self->priv->project_name);
	g_string_append (s, "AC_CONFIG_SRCDIR([Makefile.am])\n");
	g_string_append (s, "AC_CONFIG_HEADERS(config.h)\n");
	g_string_append (s, "AM_INIT_AUTOMAKE([dist-bzip2])\n");
	g_string_append (s, "AM_MAINTAINER_MODE\n\n");
	g_string_append (s, "AC_PROG_CC\n");
	g_string_append (s, "AM_PROG_CC_C_O\n");
	g_string_append (s, "AC_DISABLE_STATIC\n");
	g_string_append (s, "AC_PROG_LIBTOOL\n\n");
	g_string_append (s, "AC_PATH_PROG(VALAC, valac, valac)\n");
	g_string_append (s, "AC_SUBST(VALAC)\n\n");
	g_string_append (s, "AH_TEMPLATE([GETTEXT_PACKAGE], [Package name for gettext])\n");
	g_string_append_printf (s, "GETTEXT_PACKAGE=%s\n", self->priv->project_name);
	g_string_append (s, "AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, \"$GETTEXT_PACKAGE\")\n");
	g_string_append (s, "AC_SUBST(GETTEXT_PACKAGE)\n");
	g_string_append (s, "AM_GLIB_GNU_GETTEXT\n");
	g_string_append (s, "IT_PROG_INTLTOOL([0.35.0])\n\n");
	g_string_append (s, "AC_SUBST(CFLAGS)\n");
	g_string_append (s, "AC_SUBST(CPPFLAGS)\n");
	g_string_append (s, "AC_SUBST(LDFLAGS)\n\n");
	g_string_append (s, "GLIB_REQUIRED=2.12.0\n");
	if (use_gtk) {
		g_string_append (s, "GTK_REQUIRED=2.10.0\n");
	}
	g_string_append (s, "\n");
	g_string_append_printf (s, "PKG_CHECK_MODULES(%s, glib-2.0 >= $GLIB_REQUIRED gobject-2.0 >= $GLIB_REQUIRED", self->priv->upper_case_make_name);
	if (use_gtk) {
		g_string_append (s, " gtk+-2.0 >= $GTK_REQUIRED");
	}
	g_string_append (s, ")\n");
	g_string_append_printf (s, "AC_SUBST(%s_CFLAGS)\n", self->priv->upper_case_make_name);
	g_string_append_printf (s, "AC_SUBST(%s_LIBS)\n\n", self->priv->upper_case_make_name);
	g_string_append (s, "AC_CONFIG_FILES([Makefile\n");
	g_string_append (s, "\tpo/Makefile.in])\n\n");
	g_string_append (s, "AC_OUTPUT\n");
	_tmp0 = NULL;
	g_file_set_contents ((_tmp0 = g_strconcat (self->priv->project_path, "/configure.ac", NULL)), s->str, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
		return;
	}
	_tmp0 = (g_free (_tmp0), NULL);
	(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
}


static void vala_project_generator_write_makefile_am (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	gboolean use_gtk;
	GString* s;
	char* _tmp0;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	use_gtk = (self->priv->project_type == VALA_PROJECT_TYPE_GTK_APPLICATION);
	s = g_string_new ("");
	g_string_append (s, "NULL = \n\n");
	g_string_append (s, "AUTOMAKE_OPTIONS = subdir-objects\n\n");
	g_string_append (s, "SUBDIRS = \\\n");
	g_string_append (s, "\tpo \\\n");
	g_string_append (s, "\t$(NULL)\n\n");
	g_string_append (s, "AM_CPPFLAGS = \\\n");
	g_string_append_printf (s, "\t$(%s_CFLAGS) \\\n", self->priv->upper_case_make_name);
	g_string_append (s, "\t-include $(CONFIG_HEADER) \\\n");
	g_string_append (s, "\t$(NULL)\n\n");
	g_string_append_printf (s, "BUILT_SOURCES = src/%s.vala.stamp\n\n", self->priv->project_name);
	g_string_append_printf (s, "bin_PROGRAMS = %s\n\n", self->priv->project_name);
	g_string_append_printf (s, "%s_VALASOURCES = \\\n", self->priv->make_name);
	if (use_gtk) {
		g_string_append (s, "\tsrc/mainwindow.vala \\\n");
	} else {
		g_string_append (s, "\tsrc/main.vala \\\n");
	}
	g_string_append (s, "\t$(NULL)\n\n");
	g_string_append_printf (s, "%s_SOURCES = \\\n", self->priv->make_name);
	g_string_append_printf (s, "\t$(%s_VALASOURCES:.vala=.c) \\\n", self->priv->make_name);
	g_string_append_printf (s, "\t$(%s_VALASOURCES:.vala=.h) \\\n", self->priv->make_name);
	g_string_append (s, "\t$(NULL)\n\n");
	g_string_append_printf (s, "src/%s.vala.stamp: $(%s_VALASOURCES)\n", self->priv->project_name, self->priv->make_name);
	g_string_append (s, "\t$(VALAC) -C ");
	if (use_gtk) {
		g_string_append (s, "--pkg gtk+-2.0 ");
	}
	g_string_append (s, "--basedir $(top_srcdir) $^\n");
	g_string_append (s, "\ttouch $@\n\n");
	g_string_append_printf (s, "%s_LDADD = \\\n", self->priv->make_name);
	g_string_append_printf (s, "\t$(%s_LIBS) \\\n", self->priv->upper_case_make_name);
	g_string_append (s, "\t$(NULL)\n\n");
	g_string_append (s, "EXTRA_DIST = \\\n");
	g_string_append (s, "\tintltool-extract.in \\\n");
	g_string_append (s, "\tintltool-update.in \\\n");
	g_string_append (s, "\tintltool-merge.in \\\n");
	g_string_append_printf (s, "\t$(%s_VALASOURCES) \\\n", self->priv->make_name);
	g_string_append_printf (s, "\tsrc/%s.vala.stamp \\\n", self->priv->project_name);
	g_string_append (s, "\t$(NULL)\n\n");
	g_string_append (s, "DISTCLEANFILES = \\\n");
	g_string_append (s, "\tintltool-extract \\\n");
	g_string_append (s, "\tintltool-update \\\n");
	g_string_append (s, "\tintltool-merge \\\n");
	g_string_append (s, "\tpo/.intltool-merge-cache \\\n");
	g_string_append (s, "\t$(NULL)\n\n");
	_tmp0 = NULL;
	g_file_set_contents ((_tmp0 = g_strconcat (self->priv->project_path, "/Makefile.am", NULL)), s->str, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
		return;
	}
	_tmp0 = (g_free (_tmp0), NULL);
	(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
}


static char* vala_project_generator_generate_source_file_header (ValaProjectGenerator* self, const char* filename) {
	GString* s;
	GTimeVal tv = {0};
	GDate _tmp0 = {0};
	GDate d;
	char* license_name;
	char* license_version;
	char* program_type;
	const char* _tmp13;
	char* _tmp14;
	g_return_val_if_fail (self != NULL, NULL);
	g_return_val_if_fail (filename != NULL, NULL);
	s = g_string_new ("");
	g_get_current_time (&tv);
	d = (memset (&_tmp0, 0, sizeof (GDate)), _tmp0);
	g_date_set_time_val (&d, &tv);
	g_string_append_printf (s, "/* %s\n", filename);
	g_string_append (s, " *\n");
	g_string_append_printf (s, " * Copyright (C) %d  %s\n", ((gint) (g_date_get_year (&d))), self->priv->real_name);
	g_string_append (s, " *\n");
	license_name = g_strdup ("");
	license_version = NULL;
	program_type = NULL;
	switch (self->priv->project_license) {
		case VALA_PROJECT_LICENSE_GPL2:
		{
			char* _tmp1;
			char* _tmp2;
			char* _tmp3;
			_tmp1 = NULL;
			license_name = (_tmp1 = g_strdup ("GNU General Public License"), (license_name = (g_free (license_name), NULL)), _tmp1);
			_tmp2 = NULL;
			license_version = (_tmp2 = g_strdup ("2"), (license_version = (g_free (license_version), NULL)), _tmp2);
			_tmp3 = NULL;
			program_type = (_tmp3 = g_strdup ("program"), (program_type = (g_free (program_type), NULL)), _tmp3);
			break;
		}
		case VALA_PROJECT_LICENSE_GPL3:
		{
			char* _tmp4;
			char* _tmp5;
			char* _tmp6;
			_tmp4 = NULL;
			license_name = (_tmp4 = g_strdup ("GNU General Public License"), (license_name = (g_free (license_name), NULL)), _tmp4);
			_tmp5 = NULL;
			license_version = (_tmp5 = g_strdup ("3"), (license_version = (g_free (license_version), NULL)), _tmp5);
			_tmp6 = NULL;
			program_type = (_tmp6 = g_strdup ("program"), (program_type = (g_free (program_type), NULL)), _tmp6);
			break;
		}
		case VALA_PROJECT_LICENSE_LGPL2:
		{
			char* _tmp7;
			char* _tmp8;
			char* _tmp9;
			_tmp7 = NULL;
			license_name = (_tmp7 = g_strdup ("GNU Lesser General Public License"), (license_name = (g_free (license_name), NULL)), _tmp7);
			_tmp8 = NULL;
			license_version = (_tmp8 = g_strdup ("2.1"), (license_version = (g_free (license_version), NULL)), _tmp8);
			_tmp9 = NULL;
			program_type = (_tmp9 = g_strdup ("library"), (program_type = (g_free (program_type), NULL)), _tmp9);
			break;
		}
		case VALA_PROJECT_LICENSE_LGPL3:
		{
			char* _tmp10;
			char* _tmp11;
			char* _tmp12;
			_tmp10 = NULL;
			license_name = (_tmp10 = g_strdup ("GNU Lesser General Public License"), (license_name = (g_free (license_name), NULL)), _tmp10);
			_tmp11 = NULL;
			license_version = (_tmp11 = g_strdup ("3"), (license_version = (g_free (license_version), NULL)), _tmp11);
			_tmp12 = NULL;
			program_type = (_tmp12 = g_strdup ("library"), (program_type = (g_free (program_type), NULL)), _tmp12);
			break;
		}
	}
	g_string_append_printf (s, " * This %s is free software: you can redistribute it and/or modify\n", program_type);
	g_string_append_printf (s, " * it under the terms of the %s as published by\n", license_name);
	g_string_append_printf (s, " * the Free Software Foundation, either version %s of the License, or\n", license_version);
	g_string_append (s, " * (at your option) any later version.\n");
	g_string_append (s, " *\n");
	g_string_append_printf (s, " * This %s is distributed in the hope that it will be useful,\n", program_type);
	g_string_append (s, " * but WITHOUT ANY WARRANTY; without even the implied warranty of\n");
	g_string_append (s, " * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n");
	g_string_append_printf (s, " * %s for more details.\n", license_name);
	g_string_append (s, " *\n");
	g_string_append_printf (s, " * You should have received a copy of the %s\n", license_name);
	g_string_append_printf (s, " * along with this %s.  If not, see <http://www.gnu.org/licenses/>.\n", program_type);
	g_string_append (s, " *\n");
	g_string_append (s, " * Author:\n");
	g_string_append_printf (s, " * \t%s <%s>\n", self->priv->real_name, self->priv->email_address);
	g_string_append (s, " */\n\n");
	_tmp13 = NULL;
	_tmp14 = NULL;
	return (_tmp14 = (_tmp13 = s->str, (_tmp13 == NULL ? NULL : g_strdup (_tmp13))), (s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL))), (license_name = (g_free (license_name), NULL)), (license_version = (g_free (license_version), NULL)), (program_type = (g_free (program_type), NULL)), _tmp14);
}


static void vala_project_generator_write_main_vala (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	GString* s;
	char* _tmp0;
	char* _tmp1;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	s = g_string_new ("");
	_tmp0 = NULL;
	g_string_append (s, (_tmp0 = vala_project_generator_generate_source_file_header (self, "main.vala")));
	_tmp0 = (g_free (_tmp0), NULL);
	g_string_append (s, "using GLib;\n");
	g_string_append (s, "\n");
	g_string_append_printf (s, "public class %s.Main : Object {\n", self->priv->namespace_name);
	g_string_append (s, "\tpublic Main () {\n");
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\tpublic void run () {\n");
	g_string_append (s, "\t\tstdout.printf (\"Hello, world!\\n\");\n");
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\tstatic int main (string[] args) {\n");
	g_string_append (s, "\t\tvar main = new Main ();\n");
	g_string_append (s, "\t\tmain.run ();\n");
	g_string_append (s, "\t\treturn 0;\n");
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "}\n");
	_tmp1 = NULL;
	g_file_set_contents ((_tmp1 = g_strconcat (self->priv->project_path, "/src/main.vala", NULL)), s->str, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
		return;
	}
	_tmp1 = (g_free (_tmp1), NULL);
	(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
}


static void vala_project_generator_write_mainwindow_vala (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	GString* s;
	char* _tmp0;
	char* _tmp1;
	char* _tmp2;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	s = g_string_new ("");
	_tmp0 = NULL;
	g_string_append (s, (_tmp0 = vala_project_generator_generate_source_file_header (self, "mainwindow.vala")));
	_tmp0 = (g_free (_tmp0), NULL);
	g_string_append (s, "using GLib;\n");
	g_string_append (s, "using Gtk;\n");
	g_string_append (s, "\n");
	g_string_append_printf (s, "public class %s.MainWindow : Window {\n", self->priv->namespace_name);
	g_string_append (s, "\tprivate TextBuffer text_buffer;\n");
	g_string_append (s, "\tprivate string filename;\n");
	g_string_append (s, "\n");
	g_string_append (s, "\tpublic MainWindow () {\n");
	_tmp1 = NULL;
	g_string_append_printf (s, "\t\ttitle = \"%s\";\n", (_tmp1 = g_strescape (self->priv->project_name, "")));
	_tmp1 = (g_free (_tmp1), NULL);
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\tconstruct {\n");
	g_string_append (s, "\t\tset_default_size (600, 400);\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tdestroy += Gtk.main_quit;\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tvar vbox = new VBox (false, 0);\n");
	g_string_append (s, "\t\tadd (vbox);\n");
	g_string_append (s, "\t\tvbox.show ();\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tvar toolbar = new Toolbar ();\n");
	g_string_append (s, "\t\tvbox.pack_start (toolbar, false, false, 0);\n");
	g_string_append (s, "\t\ttoolbar.show ();\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tvar button = new ToolButton.from_stock (Gtk.STOCK_SAVE);\n");
	g_string_append (s, "\t\ttoolbar.insert (button, -1);\n");
	g_string_append (s, "\t\tbutton.is_important = true;\n");
	g_string_append (s, "\t\tbutton.clicked += on_save_clicked;\n");
	g_string_append (s, "\t\tbutton.show ();\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tvar scrolled_window = new ScrolledWindow (null, null);\n");
	g_string_append (s, "\t\tvbox.pack_start (scrolled_window, true, true, 0);\n");
	g_string_append (s, "\t\tscrolled_window.hscrollbar_policy = PolicyType.AUTOMATIC;\n");
	g_string_append (s, "\t\tscrolled_window.vscrollbar_policy = PolicyType.AUTOMATIC;\n");
	g_string_append (s, "\t\tscrolled_window.show ();\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\ttext_buffer = new TextBuffer (null);\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tvar text_view = new TextView.with_buffer (text_buffer);\n");
	g_string_append (s, "\t\tscrolled_window.add (text_view);\n");
	g_string_append (s, "\t\ttext_view.show ();\n");
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\tpublic void run () {\n");
	g_string_append (s, "\t\tshow ();\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tGtk.main ();\n");
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\tprivate void on_save_clicked (ToolButton button) {\n");
	g_string_append (s, "\t\tif (filename == null) {\n");
	g_string_append (s, "\t\t\tvar dialog = new FileChooserDialog (_(\"Save File\"), this, FileChooserAction.SAVE,\n");
	g_string_append (s, "\t\t\t\tGtk.STOCK_CANCEL, ResponseType.CANCEL,\n");
	g_string_append (s, "\t\t\t\tGtk.STOCK_SAVE, ResponseType.ACCEPT);\n");
	g_string_append (s, "\t\t\tdialog.set_do_overwrite_confirmation (true);\n");
	g_string_append (s, "\t\t\tif (dialog.run () == ResponseType.ACCEPT) {\n");
	g_string_append (s, "\t\t\t\tfilename = dialog.get_filename ();\n");
	g_string_append (s, "\t\t\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\t\tdialog.destroy ();\n");
	g_string_append (s, "\t\t\tif (filename == null) {\n");
	g_string_append (s, "\t\t\t\treturn;\n");
	g_string_append (s, "\t\t\t}\n");
	g_string_append (s, "\t\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\ttry {\n");
	g_string_append (s, "\t\t\tTextIter start_iter, end_iter;\n");
	g_string_append (s, "\t\t\ttext_buffer.get_bounds (out start_iter, out end_iter);\n");
	g_string_append (s, "\t\t\tstring text = text_buffer.get_text (start_iter, end_iter, true);\n");
	g_string_append (s, "\t\t\tFileUtils.set_contents (filename, text, -1);\n");
	g_string_append (s, "\t\t} catch (FileError e) {\n");
	g_string_append (s, "\t\t\tcritical (\"Error while trying to save file: %s\", e.message);\n");
	g_string_append (s, "\t\t\tfilename = null;\n");
	g_string_append (s, "\t\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "\tstatic int main (string[] args) {\n");
	g_string_append (s, "\t\tGtk.init (ref args);\n");
	g_string_append (s, "\n");
	g_string_append (s, "\t\tvar window = new MainWindow ();\n");
	g_string_append (s, "\t\twindow.run ();\n");
	g_string_append (s, "\t\treturn 0;\n");
	g_string_append (s, "\t}\n");
	g_string_append (s, "\n");
	g_string_append (s, "}\n");
	_tmp2 = NULL;
	g_file_set_contents ((_tmp2 = g_strconcat (self->priv->project_path, "/src/mainwindow.vala", NULL)), s->str, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
		return;
	}
	_tmp2 = (g_free (_tmp2), NULL);
	(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
}


static void vala_project_generator_write_potfiles (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	gboolean use_gtk;
	GString* s;
	char* _tmp0;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	use_gtk = (self->priv->project_type == VALA_PROJECT_TYPE_GTK_APPLICATION);
	s = g_string_new ("");
	g_string_append (s, "[encoding: UTF-8]\n");
	g_string_append (s, "# List of source files which contain translatable strings.\n");
	if (use_gtk) {
		g_string_append (s, "src/mainwindow.vala\n");
	} else {
		g_string_append (s, "src/main.vala\n");
	}
	_tmp0 = NULL;
	g_file_set_contents ((_tmp0 = g_strconcat (self->priv->project_path, "/po/POTFILES.in", NULL)), s->str, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
		return;
	}
	_tmp0 = (g_free (_tmp0), NULL);
	if (use_gtk) {
		char* _tmp1;
		_tmp1 = NULL;
		g_file_set_contents ((_tmp1 = g_strconcat (self->priv->project_path, "/po/POTFILES.skip", NULL)), "src/mainwindow.c\n", ((glong) (-1)), &inner_error);
		if (inner_error != NULL) {
			g_propagate_error (error, inner_error);
			(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
			return;
		}
		_tmp1 = (g_free (_tmp1), NULL);
	} else {
		char* _tmp2;
		_tmp2 = NULL;
		g_file_set_contents ((_tmp2 = g_strconcat (self->priv->project_path, "/po/POTFILES.skip", NULL)), "src/main.c\n", ((glong) (-1)), &inner_error);
		if (inner_error != NULL) {
			g_propagate_error (error, inner_error);
			(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
			return;
		}
		_tmp2 = (g_free (_tmp2), NULL);
	}
	(s == NULL ? NULL : (s = (g_string_free (s, TRUE), NULL)));
}


static void vala_project_generator_write_linguas (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	char* s;
	char* _tmp0;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	s = g_strdup ("# please keep this list sorted alphabetically\n#\n");
	_tmp0 = NULL;
	g_file_set_contents ((_tmp0 = g_strconcat (self->priv->project_path, "/po/LINGUAS", NULL)), s, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		s = (g_free (s), NULL);
		return;
	}
	_tmp0 = (g_free (_tmp0), NULL);
	s = (g_free (s), NULL);
}


static void vala_project_generator_write_authors (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	char* s;
	char* _tmp0;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	s = g_strdup_printf ("%s <%s>\n", self->priv->real_name, self->priv->email_address);
	_tmp0 = NULL;
	g_file_set_contents ((_tmp0 = g_strconcat (self->priv->project_path, "/AUTHORS", NULL)), s, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		s = (g_free (s), NULL);
		return;
	}
	_tmp0 = (g_free (_tmp0), NULL);
	s = (g_free (s), NULL);
}


static void vala_project_generator_write_maintainers (ValaProjectGenerator* self, GError** error) {
	GError * inner_error;
	char* s;
	char* _tmp0;
	g_return_if_fail (self != NULL);
	inner_error = NULL;
	s = g_strdup_printf ("%s\nE-mail: %s\n", self->priv->real_name, self->priv->email_address);
	_tmp0 = NULL;
	g_file_set_contents ((_tmp0 = g_strconcat (self->priv->project_path, "/MAINTAINERS", NULL)), s, ((glong) (-1)), &inner_error);
	if (inner_error != NULL) {
		g_propagate_error (error, inner_error);
		s = (g_free (s), NULL);
		return;
	}
	_tmp0 = (g_free (_tmp0), NULL);
	s = (g_free (s), NULL);
}


static char* vala_project_generator_get_automake_path (ValaProjectGenerator* self) {
	char** _tmp1;
	gint automake_paths_length1;
	char** _tmp0;
	char** automake_paths;
	char* _tmp4;
	g_return_val_if_fail (self != NULL, NULL);
	_tmp1 = NULL;
	_tmp0 = NULL;
	automake_paths = (_tmp1 = (_tmp0 = g_new0 (char*, 3 + 1), _tmp0[0] = g_strdup ("/usr/share/automake"), _tmp0[1] = g_strdup ("/usr/share/automake-1.10"), _tmp0[2] = g_strdup ("/usr/share/automake-1.9"), _tmp0), automake_paths_length1 = 3, _tmp1);
	{
		char** automake_path_collection;
		int automake_path_collection_length1;
		int automake_path_it;
		automake_path_collection = automake_paths;
		automake_path_collection_length1 = automake_paths_length1;
		for (automake_path_it = 0; (automake_paths_length1 != -1 && automake_path_it < automake_paths_length1) || (automake_paths_length1 == -1 && automake_path_collection[automake_path_it] != NULL); automake_path_it = automake_path_it + 1) {
			const char* _tmp3;
			char* automake_path;
			_tmp3 = NULL;
			automake_path = (_tmp3 = automake_path_collection[automake_path_it], (_tmp3 == NULL ? NULL : g_strdup (_tmp3)));
			{
				if (g_file_test (automake_path, G_FILE_TEST_IS_DIR)) {
					char* _tmp2;
					_tmp2 = NULL;
					return (_tmp2 = automake_path, (automake_paths = (_vala_array_free (automake_paths, automake_paths_length1, ((GDestroyNotify) (g_free))), NULL)), _tmp2);
				}
				automake_path = (g_free (automake_path), NULL);
			}
		}
	}
	_tmp4 = NULL;
	return (_tmp4 = NULL, (automake_paths = (_vala_array_free (automake_paths, automake_paths_length1, ((GDestroyNotify) (g_free))), NULL)), _tmp4);
}


static void vala_project_generator_main (char** args, int args_length1) {
	ValaProjectGenerator* generator;
	gtk_init (&args_length1, &args);
	generator = g_object_ref_sink (vala_project_generator_new ());
	if (gtk_dialog_run (((GtkDialog*) (generator))) == GTK_RESPONSE_OK) {
		vala_project_generator_create_project (generator);
	}
	(generator == NULL ? NULL : (generator = (g_object_unref (generator), NULL)));
}


int main (int argc, char ** argv) {
	g_type_init ();
	vala_project_generator_main (argv, argc);
	return 0;
}


static GObject * vala_project_generator_constructor (GType type, guint n_construct_properties, GObjectConstructParam * construct_properties) {
	GObject * obj;
	ValaProjectGeneratorClass * klass;
	GObjectClass * parent_class;
	ValaProjectGenerator * self;
	klass = VALA_PROJECT_GENERATOR_CLASS (g_type_class_peek (VALA_TYPE_PROJECT_GENERATOR));
	parent_class = G_OBJECT_CLASS (g_type_class_peek_parent (klass));
	obj = parent_class->constructor (type, n_construct_properties, construct_properties);
	self = VALA_PROJECT_GENERATOR (obj);
	{
		GtkVBox* _tmp0;
		GtkVBox* vbox;
		GtkSizeGroup* size_group;
		GtkLabel* label;
		GtkHBox* hbox;
		GtkLabel* _tmp1;
		GtkHBox* _tmp2;
		GtkFileChooserButton* _tmp3;
		GtkHBox* _tmp4;
		GtkComboBox* _tmp5;
		GtkHBox* _tmp6;
		GtkComboBox* _tmp7;
		GtkLabel* _tmp8;
		GtkHBox* _tmp9;
		GtkEntry* _tmp10;
		char* _tmp12;
		const char* _tmp11;
		GtkHBox* _tmp13;
		GtkEntry* _tmp14;
		char* _tmp16;
		const char* _tmp15;
		GtkWidget* _tmp17;
		GtkWidget* ok_button;
		gtk_container_set_border_width (((GtkContainer*) (self)), ((guint) (12)));
		gtk_dialog_set_has_separator (((GtkDialog*) (self)), FALSE);
		_tmp0 = NULL;
		vbox = (_tmp0 = GTK_VBOX (((GtkDialog*) (self))->vbox), (_tmp0 == NULL ? NULL : g_object_ref (_tmp0)));
		size_group = gtk_size_group_new (GTK_SIZE_GROUP_HORIZONTAL);
		label = NULL;
		hbox = NULL;
		gtk_box_set_spacing (((GtkBox*) (vbox)), 6);
		_tmp1 = NULL;
		label = (_tmp1 = g_object_ref_sink (((GtkLabel*) (gtk_label_new ("<b>Project</b>")))), (label == NULL ? NULL : (label = (g_object_unref (label), NULL))), _tmp1);
		gtk_box_pack_start (((GtkBox*) (vbox)), ((GtkWidget*) (label)), FALSE, FALSE, ((guint) (0)));
		gtk_label_set_use_markup (label, TRUE);
		g_object_set (((GtkMisc*) (label)), "xalign", ((float) (0)), NULL);
		gtk_widget_show (((GtkWidget*) (label)));
		_tmp2 = NULL;
		hbox = (_tmp2 = vala_project_generator_create_hbox (self, "Project folder:", size_group), (hbox == NULL ? NULL : (hbox = (g_object_unref (hbox), NULL))), _tmp2);
		_tmp3 = NULL;
		self->priv->project_folder_button = (_tmp3 = g_object_ref_sink (((GtkFileChooserButton*) (gtk_file_chooser_button_new ("Select a project folder", GTK_FILE_CHOOSER_ACTION_SELECT_FOLDER)))), (self->priv->project_folder_button == NULL ? NULL : (self->priv->project_folder_button = (g_object_unref (self->priv->project_folder_button), NULL))), _tmp3);
		gtk_box_pack_start (((GtkBox*) (hbox)), ((GtkWidget*) (self->priv->project_folder_button)), TRUE, TRUE, ((guint) (0)));
		gtk_widget_show (((GtkWidget*) (self->priv->project_folder_button)));
		_tmp4 = NULL;
		hbox = (_tmp4 = vala_project_generator_create_hbox (self, "Project type:", size_group), (hbox == NULL ? NULL : (hbox = (g_object_unref (hbox), NULL))), _tmp4);
		_tmp5 = NULL;
		self->priv->project_type_combobox = (_tmp5 = g_object_ref_sink (((GtkComboBox*) (gtk_combo_box_new_text ()))), (self->priv->project_type_combobox == NULL ? NULL : (self->priv->project_type_combobox = (g_object_unref (self->priv->project_type_combobox), NULL))), _tmp5);
		gtk_box_pack_start (((GtkBox*) (hbox)), ((GtkWidget*) (self->priv->project_type_combobox)), TRUE, TRUE, ((guint) (0)));
		gtk_combo_box_append_text (self->priv->project_type_combobox, "Console Application");
		gtk_combo_box_append_text (self->priv->project_type_combobox, "GTK+ Application");
		gtk_combo_box_set_active (self->priv->project_type_combobox, ((gint) (VALA_PROJECT_TYPE_GTK_APPLICATION)));
		gtk_widget_show (((GtkWidget*) (self->priv->project_type_combobox)));
		_tmp6 = NULL;
		hbox = (_tmp6 = vala_project_generator_create_hbox (self, "License:", size_group), (hbox == NULL ? NULL : (hbox = (g_object_unref (hbox), NULL))), _tmp6);
		_tmp7 = NULL;
		self->priv->license_combobox = (_tmp7 = g_object_ref_sink (((GtkComboBox*) (gtk_combo_box_new_text ()))), (self->priv->license_combobox == NULL ? NULL : (self->priv->license_combobox = (g_object_unref (self->priv->license_combobox), NULL))), _tmp7);
		gtk_box_pack_start (((GtkBox*) (hbox)), ((GtkWidget*) (self->priv->license_combobox)), TRUE, TRUE, ((guint) (0)));
		gtk_combo_box_append_text (self->priv->license_combobox, "GNU General Public License, version 2 or later");
		gtk_combo_box_append_text (self->priv->license_combobox, "GNU General Public License, version 3 or later");
		gtk_combo_box_append_text (self->priv->license_combobox, "GNU Lesser General Public License, version 2.1 or later");
		gtk_combo_box_append_text (self->priv->license_combobox, "GNU Lesser General Public License, version 3 or later");
		gtk_combo_box_set_active (self->priv->license_combobox, ((gint) (VALA_PROJECT_LICENSE_LGPL2)));
		gtk_widget_show (((GtkWidget*) (self->priv->license_combobox)));
		_tmp8 = NULL;
		label = (_tmp8 = g_object_ref_sink (((GtkLabel*) (gtk_label_new ("<b>Author</b>")))), (label == NULL ? NULL : (label = (g_object_unref (label), NULL))), _tmp8);
		gtk_box_pack_start (((GtkBox*) (vbox)), ((GtkWidget*) (label)), FALSE, FALSE, ((guint) (0)));
		gtk_label_set_use_markup (label, TRUE);
		g_object_set (((GtkMisc*) (label)), "xalign", ((float) (0)), NULL);
		gtk_widget_show (((GtkWidget*) (label)));
		_tmp9 = NULL;
		hbox = (_tmp9 = vala_project_generator_create_hbox (self, "Name:", size_group), (hbox == NULL ? NULL : (hbox = (g_object_unref (hbox), NULL))), _tmp9);
		_tmp10 = NULL;
		self->priv->name_entry = (_tmp10 = g_object_ref_sink (((GtkEntry*) (gtk_entry_new ()))), (self->priv->name_entry == NULL ? NULL : (self->priv->name_entry = (g_object_unref (self->priv->name_entry), NULL))), _tmp10);
		gtk_box_pack_start (((GtkBox*) (hbox)), ((GtkWidget*) (self->priv->name_entry)), TRUE, TRUE, ((guint) (0)));
		_tmp12 = NULL;
		_tmp11 = NULL;
		self->priv->real_name = (_tmp12 = (_tmp11 = g_getenv ("REAL_NAME"), (_tmp11 == NULL ? NULL : g_strdup (_tmp11))), (self->priv->real_name = (g_free (self->priv->real_name), NULL)), _tmp12);
		if (self->priv->real_name != NULL) {
			gtk_entry_set_text (self->priv->name_entry, self->priv->real_name);
		}
		gtk_widget_show (((GtkWidget*) (self->priv->name_entry)));
		_tmp13 = NULL;
		hbox = (_tmp13 = vala_project_generator_create_hbox (self, "E-mail address:", size_group), (hbox == NULL ? NULL : (hbox = (g_object_unref (hbox), NULL))), _tmp13);
		_tmp14 = NULL;
		self->priv->email_entry = (_tmp14 = g_object_ref_sink (((GtkEntry*) (gtk_entry_new ()))), (self->priv->email_entry == NULL ? NULL : (self->priv->email_entry = (g_object_unref (self->priv->email_entry), NULL))), _tmp14);
		gtk_box_pack_start (((GtkBox*) (hbox)), ((GtkWidget*) (self->priv->email_entry)), TRUE, TRUE, ((guint) (0)));
		_tmp16 = NULL;
		_tmp15 = NULL;
		self->priv->email_address = (_tmp16 = (_tmp15 = g_getenv ("EMAIL_ADDRESS"), (_tmp15 == NULL ? NULL : g_strdup (_tmp15))), (self->priv->email_address = (g_free (self->priv->email_address), NULL)), _tmp16);
		if (self->priv->email_address != NULL) {
			gtk_entry_set_text (self->priv->email_entry, self->priv->email_address);
		}
		gtk_widget_show (((GtkWidget*) (self->priv->email_entry)));
		gtk_dialog_add_button (((GtkDialog*) (self)), GTK_STOCK_CANCEL, ((gint) (GTK_RESPONSE_CANCEL)));
		_tmp17 = NULL;
		ok_button = (_tmp17 = gtk_dialog_add_button (((GtkDialog*) (self)), "Create Project", ((gint) (GTK_RESPONSE_OK))), (_tmp17 == NULL ? NULL : g_object_ref (_tmp17)));
		gtk_widget_grab_default (ok_button);
		(vbox == NULL ? NULL : (vbox = (g_object_unref (vbox), NULL)));
		(size_group == NULL ? NULL : (size_group = (g_object_unref (size_group), NULL)));
		(label == NULL ? NULL : (label = (g_object_unref (label), NULL)));
		(hbox == NULL ? NULL : (hbox = (g_object_unref (hbox), NULL)));
		(ok_button == NULL ? NULL : (ok_button = (g_object_unref (ok_button), NULL)));
	}
	return obj;
}


static void vala_project_generator_class_init (ValaProjectGeneratorClass * klass) {
	vala_project_generator_parent_class = g_type_class_peek_parent (klass);
	g_type_class_add_private (klass, sizeof (ValaProjectGeneratorPrivate));
	G_OBJECT_CLASS (klass)->constructor = vala_project_generator_constructor;
	G_OBJECT_CLASS (klass)->finalize = vala_project_generator_finalize;
}


static void vala_project_generator_instance_init (ValaProjectGenerator * self) {
	self->priv = VALA_PROJECT_GENERATOR_GET_PRIVATE (self);
}


static void vala_project_generator_finalize (GObject* obj) {
	ValaProjectGenerator * self;
	self = VALA_PROJECT_GENERATOR (obj);
	(self->priv->project_folder_button == NULL ? NULL : (self->priv->project_folder_button = (g_object_unref (self->priv->project_folder_button), NULL)));
	(self->priv->project_type_combobox == NULL ? NULL : (self->priv->project_type_combobox = (g_object_unref (self->priv->project_type_combobox), NULL)));
	(self->priv->license_combobox == NULL ? NULL : (self->priv->license_combobox = (g_object_unref (self->priv->license_combobox), NULL)));
	(self->priv->name_entry == NULL ? NULL : (self->priv->name_entry = (g_object_unref (self->priv->name_entry), NULL)));
	(self->priv->email_entry == NULL ? NULL : (self->priv->email_entry = (g_object_unref (self->priv->email_entry), NULL)));
	self->priv->project_path = (g_free (self->priv->project_path), NULL);
	self->priv->project_name = (g_free (self->priv->project_name), NULL);
	self->priv->namespace_name = (g_free (self->priv->namespace_name), NULL);
	self->priv->make_name = (g_free (self->priv->make_name), NULL);
	self->priv->upper_case_make_name = (g_free (self->priv->upper_case_make_name), NULL);
	self->priv->real_name = (g_free (self->priv->real_name), NULL);
	self->priv->email_address = (g_free (self->priv->email_address), NULL);
	G_OBJECT_CLASS (vala_project_generator_parent_class)->finalize (obj);
}


static GType vala_project_generator_get_type (void) {
	static GType vala_project_generator_type_id = 0;
	if (vala_project_generator_type_id == 0) {
		static const GTypeInfo g_define_type_info = { sizeof (ValaProjectGeneratorClass), (GBaseInitFunc) NULL, (GBaseFinalizeFunc) NULL, (GClassInitFunc) vala_project_generator_class_init, (GClassFinalizeFunc) NULL, NULL, sizeof (ValaProjectGenerator), 0, (GInstanceInitFunc) vala_project_generator_instance_init, NULL };
		vala_project_generator_type_id = g_type_register_static (GTK_TYPE_DIALOG, "ValaProjectGenerator", &g_define_type_info, 0);
	}
	return vala_project_generator_type_id;
}


static void _vala_array_free (gpointer array, gint array_length, GDestroyNotify destroy_func) {
	if (array != NULL && destroy_func != NULL) {
		int i;
		if (array_length >= 0)
		for (i = 0; i < array_length; i = i + 1) {
			if (((gpointer*) (array))[i] != NULL)
			destroy_func (((gpointer*) (array))[i]);
		}
		else
		for (i = 0; ((gpointer*) (array))[i] != NULL; i = i + 1) {
			destroy_func (((gpointer*) (array))[i]);
		}
	}
	g_free (array);
}




