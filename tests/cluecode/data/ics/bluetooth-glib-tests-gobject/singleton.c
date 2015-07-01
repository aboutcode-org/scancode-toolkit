/* GObject - GLib Type, Object, Parameter and Signal Library
 * Copyright (C) 2006 Imendio AB
 *
 * This library is free software; you can redistribute it and/or
#define MY_TYPE_SINGLETON         (my_singleton_get_type ())
#define MY_SINGLETON(o)           (G_TYPE_CHECK_INSTANCE_CAST ((o), MY_TYPE_SINGLETON, MySingleton))
#define MY_IS_SINGLETON(o)        (G_TYPE_CHECK_INSTANCE_TYPE ((o), MY_TYPE_SINGLETON))
#define MY_SINGLETON_CLASS(c)     (G_TYPE_CHECK_CLASS_CAST ((c), MY_TYPE_SINGLETON, MySingletonClass))
#define MY_IS_SINGLETON_CLASS(c)  (G_TYPE_CHECK_CLASS_TYPE ((c), MY_TYPE_SINGLETON))
#define MY_SINGLETON_GET_CLASS(o) (G_TYPE_INSTANCE_GET_CLASS ((o), MY_TYPE_SINGLETON, MySingletonClass))
