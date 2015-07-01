/* GLib testing utilities
 * Copyright (C) 2007 Imendio AB
 * Authors: Tim Janik, Sven Herzberg
 *
  g_return_if_fail (test_uri_base != NULL);
  g_return_if_fail (bug_uri_snippet != NULL);
  c = strstr (test_uri_base, "%s");
  if (c)
    {
      char *b = g_strndup (test_uri_base, c - test_uri_base);