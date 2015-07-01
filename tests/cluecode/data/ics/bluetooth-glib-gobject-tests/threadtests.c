/* GLib testing framework examples and tests
 * Copyright (C) 2008 Imendio AB
 * Authors: Tim Janik
 *
                         G_IMPLEMENT_INTERFACE (my_face1_get_type(), interface_per_class_init);
                         );
static void my_tester0_init (MyTester0*t) {}
static void my_tester0_class_init (MyTester0Class*c) { call_counter_init (c); }
typedef GObject         MyTester1;
typedef GObjectClass    MyTester1Class;
                         G_IMPLEMENT_INTERFACE (my_face1_get_type(), interface_per_class_init);
                         );
static void my_tester1_init (MyTester1*t) {}
static void my_tester1_class_init (MyTester1Class*c) { call_counter_init (c); }
typedef GObject         MyTester2;
typedef GObjectClass    MyTester2Class;
                         G_IMPLEMENT_INTERFACE (my_face1_get_type(), interface_per_class_init);
                         );
static void my_tester2_init (MyTester2*t) {}
static void my_tester2_class_init (MyTester2Class*c) { call_counter_init (c); }

static GCond *sync_cond = NULL;
{
  int i;
  GParamSpec *param;
  GObjectClass *gobject_class = G_OBJECT_CLASS (c);

  gobject_class->set_property = prop_tester_set_property; /* silence GObject checks */
  for (i = 0; i < 100; i++) /* wait a bit. */
    g_thread_yield();

  call_counter_init (c);
  param = g_param_spec_string ("name", "name_i18n",
			       "yet-more-wasteful-i18n",