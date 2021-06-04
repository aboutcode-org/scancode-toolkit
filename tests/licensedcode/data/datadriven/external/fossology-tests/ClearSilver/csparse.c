/*
 * Copyright 2001-2004 Brandon Long
 * All Rights Reserved.
 *
 * ClearSilver Templating System
 *
 * This code is made available under the terms of the ClearSilver License.
 * http://www.clearsilver.net/license.hdf
 *
 */

/*
 * TODO: there is some really ugly pseudo reference counting in here
 * for allocation of temporary strings (and passing references).  See the alloc
 * member of various structs for details.  We should move this to an arena
 * allocator so we can just allocate whenever we need to and just clean up
 * all the allocation at the end (may require two arenas: one for parese and
 * one for render)
 */

#include "cs_config.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <limits.h>
#include <stdarg.h>

#ifdef ENABLE_GETTEXT
#include <libintl.h>
#endif

#include "util/neo_misc.h"
#include "util/neo_err.h"
#include "util/neo_files.h"
#include "util/neo_str.h"
#include "util/ulist.h"
#include "cs.h"

/* turn on some debug output for expressions */
#define DEBUG_EXPR_PARSE 0
#define DEBUG_EXPR_EVAL 0

typedef enum
{
  ST_SAME = 0,
  ST_GLOBAL = 1<<0,
  ST_IF = 1<<1,
  ST_ELSE = 1<<2,
  ST_EACH = 1<<3,
  ST_WITH = 1<<4,
  ST_POP = 1<<5,
  ST_DEF = 1<<6,
  ST_LOOP =  1<<7,
  ST_ALT = 1<<8,
  ST_ESCAPE = 1<<9,
} CS_STATE;

#define ST_ANYWHERE (ST_EACH | ST_WITH | ST_ELSE | ST_IF | ST_GLOBAL | ST_DEF | ST_LOOP | ST_ALT | ST_ESCAPE)

typedef struct _stack_entry
{
  CS_STATE state;
  NEOS_ESCAPE escape;
  CSTREE *tree;
  CSTREE *next_tree;
  int num_local;
  int location;
} STACK_ENTRY;

static NEOERR *literal_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *literal_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *name_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *name_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *var_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *var_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *evar_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *lvar_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *lvar_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *if_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *if_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *else_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *elif_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *endif_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *each_with_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *each_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *with_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *end_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *include_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *linclude_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *linclude_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *def_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *skip_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *call_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *call_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *set_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *set_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *loop_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *loop_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *alt_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *alt_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);
static NEOERR *escape_parse (CSPARSE *parse, int cmd, char *arg);
static NEOERR *escape_eval (CSPARSE *parse, CSTREE *node, CSTREE **next);

static NEOERR *render_node (CSPARSE *parse, CSTREE *node);
static NEOERR *cs_init_internal (CSPARSE **parse, HDF *hdf, CSPARSE *parent);
static int rearrange_for_call(CSARG **args);

typedef struct _cmds
{
  char *cmd;
  int cmdlen;
  CS_STATE allowed_state;
  CS_STATE next_state;
  NEOERR* (*parse_handler)(CSPARSE *parse, int cmd, char *arg);
  NEOERR* (*eval_handler)(CSPARSE *parse, CSTREE *node, CSTREE **next);
  int has_arg;
} CS_CMDS;

CS_CMDS Commands[] = {
  {"literal", sizeof("literal")-1, ST_ANYWHERE,     ST_SAME,
    literal_parse, literal_eval, 0},
  {"name",     sizeof("name")-1,     ST_ANYWHERE,     ST_SAME,
    name_parse, name_eval,     1},
  {"var",     sizeof("var")-1,     ST_ANYWHERE,     ST_SAME,
    var_parse, var_eval,     1},
  {"uvar",     sizeof("uvar")-1,     ST_ANYWHERE,     ST_SAME,
    var_parse, var_eval,     1},
  {"evar",    sizeof("evar")-1,    ST_ANYWHERE,     ST_SAME,
    evar_parse, skip_eval,    1},
  {"lvar",    sizeof("lvar")-1,    ST_ANYWHERE,     ST_SAME,
    lvar_parse, lvar_eval,    1},
  {"if",      sizeof("if")-1,      ST_ANYWHERE,     ST_IF,
    if_parse, if_eval,      1},
  {"else",    sizeof("else")-1,    ST_IF,           ST_POP | ST_ELSE,
    else_parse, skip_eval,    0},
  {"elseif",  sizeof("elseif")-1,  ST_IF,           ST_SAME,
    elif_parse, if_eval,   1},
  {"elif",    sizeof("elif")-1,    ST_IF,           ST_SAME,
    elif_parse, if_eval,   1},
  {"/if",     sizeof("/if")-1,     ST_IF | ST_ELSE, ST_POP,
    endif_parse, skip_eval,   0},
  {"each",    sizeof("each")-1,    ST_ANYWHERE,     ST_EACH,
    each_with_parse, each_eval,    1},
  {"/each",   sizeof("/each")-1,   ST_EACH,         ST_POP,
    end_parse, skip_eval, 0},
  {"with",    sizeof("each")-1,    ST_ANYWHERE,     ST_WITH,
    each_with_parse, with_eval,    1},
  {"/with",   sizeof("/with")-1,   ST_WITH,         ST_POP,
    end_parse, skip_eval, 0},
  {"include", sizeof("include")-1, ST_ANYWHERE,     ST_SAME,
    include_parse, skip_eval, 1},
  {"linclude", sizeof("linclude")-1, ST_ANYWHERE,     ST_SAME,
    linclude_parse, linclude_eval, 1},
  {"def",     sizeof("def")-1,     ST_ANYWHERE,     ST_DEF,
    def_parse, skip_eval, 1},
  {"/def",    sizeof("/def")-1,    ST_DEF,          ST_POP,
    end_parse, skip_eval, 0},
  {"call",    sizeof("call")-1,    ST_ANYWHERE,     ST_SAME,
    call_parse, call_eval, 1},
  {"set",    sizeof("set")-1,    ST_ANYWHERE,     ST_SAME,
    set_parse, set_eval, 1},
  {"loop",    sizeof("loop")-1,    ST_ANYWHERE,     ST_LOOP,
    loop_parse, loop_eval, 1},
  {"/loop",    sizeof("/loop")-1,    ST_LOOP,     ST_POP,
    end_parse, skip_eval, 1},
  {"alt",    sizeof("alt")-1,    ST_ANYWHERE,     ST_ALT,
    alt_parse, alt_eval, 1},
  {"/alt",    sizeof("/alt")-1,    ST_ALT,     ST_POP,
    end_parse, skip_eval, 1},
  {"escape",    sizeof("escape")-1,    ST_ANYWHERE,     ST_ESCAPE,
    escape_parse, escape_eval, 1},
  {"/escape",    sizeof("/escape")-1,    ST_ESCAPE,     ST_POP,
    end_parse, skip_eval, 1},
  {NULL},
};

/* Possible Config.VarEscapeMode values */
typedef struct _escape_modes
{
  char *mode; /* Add space for NUL */
  NEOS_ESCAPE context; /* Context of the name */
} CS_ESCAPE_MODES;

CS_ESCAPE_MODES EscapeModes[] = {
  {"none", NEOS_ESCAPE_NONE},
  {"html", NEOS_ESCAPE_HTML},
  {"js",   NEOS_ESCAPE_SCRIPT},
  {"url",  NEOS_ESCAPE_URL},
  {NULL},
};


/* **** CS alloc/dealloc ******************************************** */

static int NodeNumber = 0;

static NEOERR *alloc_node (CSTREE **node)
{
  CSTREE *my_node;

  *node = NULL;
  my_node = (CSTREE *) calloc (1, sizeof (CSTREE));
  if (my_node == NULL)
    return nerr_raise (NERR_NOMEM, "Unable to allocate memory for node");

  my_node->cmd = 0;
  my_node->node_num = NodeNumber++;

  *node = my_node;
  return STATUS_OK;
}

/* TODO: make these deallocations linear and not recursive */
static void dealloc_arg (CSARG **arg)
{
  CSARG *p;

  if (*arg == NULL) return;
  p = *arg;
  if (p->expr1) dealloc_arg (&(p->expr1));
  if (p->expr2) dealloc_arg (&(p->expr2));
  if (p->next) dealloc_arg (&(p->next));
  free(p);
  *arg = NULL;
}

static void dealloc_node (CSTREE **node)
{
  CSTREE *my_node;

  if (*node == NULL) return;
  my_node = *node;
  if (my_node->case_0) dealloc_node (&(my_node->case_0));
  if (my_node->case_1) dealloc_node (&(my_node->case_1));
  if (my_node->next) dealloc_node (&(my_node->next));
  if (my_node->vargs) dealloc_arg (&(my_node->vargs));
  if (my_node->arg1.expr1) dealloc_arg (&(my_node->arg1.expr1));
  if (my_node->arg1.expr2) dealloc_arg (&(my_node->arg1.expr2));
  if (my_node->arg1.next) dealloc_arg (&(my_node->arg1.next));
  if (my_node->arg2.expr1) dealloc_arg (&(my_node->arg2.expr1));
  if (my_node->arg2.expr2) dealloc_arg (&(my_node->arg2.expr2));
  if (my_node->arg2.next) dealloc_arg (&(my_node->arg2.next));

  free(my_node);
  *node = NULL;
}

static void dealloc_macro (CS_MACRO **macro)
{
  CS_MACRO *my_macro;

  if (*macro == NULL) return;
  my_macro = *macro;
  if (my_macro->name) free (my_macro->name);
  if (my_macro->args) dealloc_arg (&(my_macro->args));
  if (my_macro->next) dealloc_macro (&(my_macro->next));
  free (my_macro);
  *macro = NULL;
}

static void dealloc_function (CS_FUNCTION **csf)
{
  CS_FUNCTION *my_csf;

  if (*csf == NULL) return;
  my_csf = *csf;
  if (my_csf->name) free (my_csf->name);
  if (my_csf->next) dealloc_function (&(my_csf->next));
  free (my_csf);
  *csf = NULL;
}

static int find_open_delim (CSPARSE *parse, char *buf, int x, int len)
{
  char *p;
  int ws_index = 2+parse->taglen;

  while (x < len)
  {
    p = strchr (&(buf[x]), '<');
    if (p == NULL) return -1;
    if (p[1] == '?' && !strncasecmp(&p[2], parse->tag, parse->taglen) &&
	(p[ws_index] == ' ' || p[ws_index] == '\n' || p[ws_index] == '\t' || p[ws_index] == '\r'))
      /*
    if (p[1] && p[1] == '?' &&
	p[2] && (p[2] == 'C' || p[2] == 'c') &&
	p[3] && (p[3] == 'S' || p[3] == 's') &&
	p[4] && (p[4] == ' ' || p[4] == '\n' || p[4] == '\t' || p[4] == '\r'))
	*/
    {
      return p - buf;
    }
    x = p - buf + 1;
  }
  return -1;
}

NEOERR *cs_parse_file (CSPARSE *parse, const char *path)
{
  NEOERR *err;
  char *ibuf;
  const char *save_context;
  int save_infile;
  char fpath[_POSIX_PATH_MAX];

  if (path == NULL)
    return nerr_raise (NERR_ASSERT, "path is NULL");

  if (parse->fileload)
  {
    err = parse->fileload(parse->fileload_ctx, parse->hdf, path, &ibuf);
  }
  else
  {
    if (path[0] != '/')
    {
      err = hdf_search_path (parse->hdf, path, fpath);
      if (parse->global_hdf && nerr_handle(&err, NERR_NOT_FOUND))
        err = hdf_search_path(parse->global_hdf, path, fpath);
      if (err != STATUS_OK) return nerr_pass(err);
      path = fpath;
    }

    err = ne_load_file (path, &ibuf);
  }
  if (err) return nerr_pass (err);

  save_context = parse->context;
  parse->context = path;
  save_infile = parse->in_file;
  parse->in_file = 1;
  err = cs_parse_string(parse, ibuf, strlen(ibuf));
  parse->in_file = save_infile;
  parse->context = save_context;

  return nerr_pass(err);
}

static char *find_context (CSPARSE *parse, int offset, char *buf, size_t blen)
{
  FILE *fp;
  int dump_err = 1;
  char line[256];
  int count = 0;
  int lineno = 0;
  char *data;

  if (offset == -1) offset = parse->offset;

  do
  {
    if (parse->in_file && parse->context)
    {
      /* Open the file and find which line we're on */

      fp = fopen(parse->context, "r");
      if (fp == NULL) {
	ne_warn("Unable to open context %s", parse->context);
	break;
      }
      while (fgets(line, sizeof(line), fp) != NULL)
      {
	count += strlen(line);
	if (strchr(line, '\n') != NULL)
	  lineno++;
	if (count > offset) break;
      }
      fclose (fp);
      snprintf (buf, blen, "[%s:%d]", parse->context, lineno);
    }
    else
    {
      data = parse->context_string;
      if (data != NULL)
      {
	lineno = 1;
	while (count < offset)
	{
	  if (data[count++] == '\n') lineno++;
	}
	if (parse->context)
	  snprintf (buf, blen, "[%s:~%d]", parse->context, lineno);
	else
	  snprintf (buf, blen, "[lineno:~%d]", lineno);
      }
      else
      {
	if (parse->context)
	  snprintf (buf, blen, "[%s:%d]", parse->context, offset);
	else
	  snprintf (buf, blen, "[offset:%d]", offset);
      }
    }
    dump_err = 0;
  } while (0);
  if (dump_err)
  {
    if (parse->context)
      snprintf (buf, blen, "[-E- %s:%d]", parse->context, offset);
    else
      snprintf (buf, blen, "[-E- offset:%d]", offset);
  }

  return buf;
}

static char *expand_state (CS_STATE state)
{
  static char buf[256];

  if (state & ST_GLOBAL)
    return "GLOBAL";
  else if (state & ST_IF)
    return "IF";
  else if (state & ST_ELSE)
    return "ELSE";
  else if (state & ST_EACH)
    return "EACH";
  else if (state & ST_WITH)
    return "WITH";
  else if (state & ST_DEF)
    return "DEF";
  else if (state & ST_LOOP)
    return "LOOP";
  else if (state & ST_ALT)
    return "ALT";
  else if (state & ST_ESCAPE)
    return "ESCAPE";

  snprintf(buf, sizeof(buf), "Unknown state %d", state);
  return buf;
}

NEOERR *cs_parse_string (CSPARSE *parse, char *ibuf, size_t ibuf_len)
{
  NEOERR *err = STATUS_OK;
  STACK_ENTRY *entry, *current_entry;
  char *p;
  char *token;
  int done = 0;
  int i, n;
  char *arg;
  int initial_stack_depth;
  int initial_offset;
  char *initial_context;
  char tmp[256];

  err = uListAppend(parse->alloc, ibuf);
  if (err)
  {
    free (ibuf);
    return nerr_pass (err);
  }

  initial_stack_depth = uListLength(parse->stack);
  initial_offset = parse->offset;
  initial_context = parse->context_string;

  parse->offset = 0;
  parse->context_string = ibuf;
  while (!done)
  {
    /* Stage 1: Find <?cs starter */
    i = find_open_delim (parse, ibuf, parse->offset, ibuf_len);
    if (i >= 0)
    {
      ibuf[i] = '\0';
      /* Create literal with data up until start delim */
      /* ne_warn ("literal -> %d-%d", parse->offset, i);  */
      err = (*(Commands[0].parse_handler))(parse, 0, &(ibuf[parse->offset]));
      /* skip delim */
      token = &(ibuf[i+3+parse->taglen]);
      while (*token && isspace(*token)) token++;

      p = strstr (token, "?>");
      if (p == NULL)
      {
	return nerr_raise (NERR_PARSE, "%s Missing end ?> at %s",
	    find_context(parse, i, tmp, sizeof(tmp)), &(ibuf[parse->offset]));
      }
      *p = '\0';
      if (strstr (token, "<?") != NULL)
      {
	return nerr_raise (NERR_PARSE, "%s Missing end ?> at %s",
	    find_context(parse, i, tmp, sizeof(tmp)),
	    token);
      }
      parse->offset = p - ibuf + 2;
      if (token[0] != '#') /* handle comments */
      {
	for (i = 1; Commands[i].cmd; i++)
	{
	  n = Commands[i].cmdlen;
	  if (!strncasecmp(token, Commands[i].cmd, n))
	  {
	    if ((Commands[i].has_arg && ((token[n] == ':') || (token[n] == '!')))
		|| (token[n] == ' ' || token[n] == '\0' || token[n] == '\r' || token[n] == '\n'))
	    {
	      err = uListGet (parse->stack, -1, (void *)&entry);
	      if (err != STATUS_OK) goto cs_parse_done;
	      if (!(Commands[i].allowed_state & entry->state))
	      {
		return nerr_raise (NERR_PARSE,
		    "%s Command %s not allowed in %s", Commands[i].cmd,
		    find_context(parse, -1, tmp, sizeof(tmp)),
		    expand_state(entry->state));
	      }
	      if (Commands[i].has_arg)
	      {
		/* Need to parse out arg */
		arg = &token[n];
		err = (*(Commands[i].parse_handler))(parse, i, arg);
	      }
	      else
	      {
		err = (*(Commands[i].parse_handler))(parse, i, NULL);
	      }
	      if (err != STATUS_OK) goto cs_parse_done;
	      if (Commands[i].next_state & ST_POP)
	      {
                void *ptr;
		err = uListPop(parse->stack, &ptr);
		if (err != STATUS_OK) goto cs_parse_done;
                entry = (STACK_ENTRY *)ptr;
		if (entry->next_tree)
		  parse->current = entry->next_tree;
		else
		  parse->current = entry->tree;
		free(entry);
	      }
	      if ((Commands[i].next_state & ~ST_POP) != ST_SAME)
	      {
		entry = (STACK_ENTRY *) calloc (1, sizeof (STACK_ENTRY));
		if (entry == NULL)
		  return nerr_raise (NERR_NOMEM,
		      "%s Unable to allocate memory for stack entry",
		      find_context(parse, -1, tmp, sizeof(tmp)));
		entry->state = Commands[i].next_state;
		entry->tree = parse->current;
		entry->location = parse->offset;
		/* Set the new stack escape context to the parent one */
		err = uListGet (parse->stack, -1, (void *)&current_entry);
		if (err != STATUS_OK) {
		  free (entry);
		  goto cs_parse_done;
		}
		entry->escape = current_entry->escape;
		/* Get the future escape context from parse because when
		 * we parse "escape", the new stack has not yet been established.
		 */
		entry->escape = parse->escaping.next_stack;
		parse->escaping.next_stack = parse->escaping.global;
		err = uListAppend(parse->stack, entry);
		if (err != STATUS_OK) {
		  free (entry);
		  goto cs_parse_done;
		}
	      }
	      break;
	    }
	  }
	}
	if (Commands[i].cmd == NULL)
	{
	  return nerr_raise (NERR_PARSE, "%s Unknown command %s",
	      find_context(parse, -1, tmp, sizeof(tmp)), token);
	}
      }
    }
    else
    {
      /* Create literal with all remaining data */
      err = (*(Commands[0].parse_handler))(parse, 0, &(ibuf[parse->offset]));
      done = 1;
    }
  }
  /* Should we check the parse stack here? */
  while (uListLength(parse->stack) > initial_stack_depth)
  {
    err = uListPop(parse->stack, (void *)&entry);
    if (err != STATUS_OK) goto cs_parse_done;
    if (entry->state & ~(ST_GLOBAL | ST_POP))
      return nerr_raise (NERR_PARSE, "%s Non-terminted %s clause",
	  find_context(parse, entry->location, tmp, sizeof(tmp)),
          expand_state(entry->state));
  }

cs_parse_done:
  parse->offset = initial_offset;
  parse->context_string = initial_context;
  parse->escaping.current = NEOS_ESCAPE_NONE;
  return nerr_pass(err);
}

static CS_LOCAL_MAP * lookup_map (CSPARSE *parse, char *name, char **rest)
{
  CS_LOCAL_MAP *map;
  char *c;

  /* This shouldn't happen, but it did once... */
  if (name == NULL) return NULL;
  map = parse->locals;
  c = strchr (name, '.');
  if (c != NULL) *c = '\0';
  *rest = c;
  while (map != NULL)
  {
    if (!strcmp (map->name, name))
    {
      if (c != NULL) *c = '.';
      return map;
    }
    map = map->next;
  }
  if (c != NULL) *c = '.';
  return NULL;
}

static HDF *var_lookup_obj (CSPARSE *parse, char *name)
{
  CS_LOCAL_MAP *map;
  char *c;
  HDF *ret_hdf;

  map = lookup_map (parse, name, &c);
  if (map && map->type == CS_TYPE_VAR)
  {
    if (c == NULL)
    {
      return map->h;
    }
    else
    {
      return hdf_get_obj (map->h, c+1);
    }
  }
  /* smarti:  Added support for global hdf under local hdf */
  /* return hdf_get_obj (parse->hdf, name); */
  ret_hdf = hdf_get_obj (parse->hdf, name);
  if (ret_hdf == NULL && parse->global_hdf != NULL) {
    ret_hdf = hdf_get_obj (parse->global_hdf, name);
  }
  return ret_hdf;
}

/* Ugh, I have to write the same walking code because I can't grab the
 * object for writing, as it might not exist... */
static NEOERR *var_set_value (CSPARSE *parse, char *name, char *value)
{
  CS_LOCAL_MAP *map;
  char *c;

  map = parse->locals;
  c = strchr (name, '.');
  if (c != NULL) *c = '\0';
  while (map != NULL)
  {
    if (!strcmp (map->name, name))
    {
      if (map->type == CS_TYPE_VAR)
      {
	if (c == NULL)
	{
          if (map->h == NULL) /* node didn't exist yet */
            return nerr_pass (hdf_set_value (parse->hdf, map->s, value));
          else
            return nerr_pass (hdf_set_value (map->h, NULL, value));
	}
	else
	{
	  *c = '.';
          if (map->h == NULL) /* node didn't exist yet */
          {
            NEOERR *err;
            char *mapped_name = sprintf_alloc("%s%s", map->s, c);
            if (mapped_name == NULL)
              return nerr_raise(NERR_NOMEM, "Unable to allocate memory to create mapped name");
            err = hdf_set_value(parse->hdf, mapped_name, value);
            free(mapped_name);
            return nerr_pass(err);
          }
	  return nerr_pass (hdf_set_value (map->h, c+1, value));
	}
      }
      else
      {
	if (c == NULL)
	{
	  char *tmp = NULL;
	  /* If this is a string, it might be what we're setting,
	   * ie <?cs set:value = value ?>
	   */
	  if (map->type == CS_TYPE_STRING && map->map_alloc)
	    tmp = map->s;
	  map->type = CS_TYPE_STRING;
	  map->map_alloc = 1;
	  map->s = strdup(value);
	  if (tmp != NULL) free(tmp);
	  if (map->s == NULL && value != NULL)
	    return nerr_raise(NERR_NOMEM,
		"Unable to allocate memory to set var");

	  return STATUS_OK;
	}
	else {
	  ne_warn("WARNING!! Trying to set sub element '%s' of local variable '%s' which doesn't map to an HDF variable, ignoring", c+1, map->name);
	  return STATUS_OK;
	}
      }
    }
    map = map->next;
  }
  if (c != NULL) *c = '.';
  return nerr_pass (hdf_set_value (parse->hdf, name, value));
}

static char *var_lookup (CSPARSE *parse, char *name)
{
  CS_LOCAL_MAP *map;
  char *c;
  char* retval;

  map = lookup_map (parse, name, &c);
  if (map)
  {
    if (map->type == CS_TYPE_VAR)
    {
      if (c == NULL)
      {
	return hdf_obj_value (map->h);
      }
      else
      {
	return hdf_get_value (map->h, c+1, NULL);
      }
    }
    /* Hmm, if c != NULL, they are asking for a sub member of something
     * which isn't a var... right now we ignore them, I don't know what
     * the right thing is */
    /* hmm, its possible now that they are getting a reference to a
     * string that will be deleted... where is it used? */
    else if (map->type == CS_TYPE_STRING)
    {
      return map->s;
    }
    else if (map->type == CS_TYPE_NUM)
    {
      char buf[40];
      if (map->s) return map->s;
      snprintf (buf, sizeof(buf), "%ld", map->n);
      map->s = strdup(buf);
      map->map_alloc = 1;
      return map->s;
    }
  }
  /* smarti:  Added support for global hdf under local hdf */
  /* return hdf_get_value (parse->hdf, name, NULL); */
  retval = hdf_get_value (parse->hdf, name, NULL);
  if (retval == NULL && parse->global_hdf != NULL) {
    retval = hdf_get_value (parse->global_hdf, name, NULL);
  }
  return retval;
}

long int var_int_lookup (CSPARSE *parse, char *name)
{
  char *vs;

  vs = var_lookup (parse, name);

  if (vs == NULL)
    return 0;
  else
    return atoi(vs);
}

typedef struct _token
{
  CSTOKEN_TYPE type;
  char *value;
  size_t len;
} CSTOKEN;

struct _simple_tokens
{
  BOOL two_chars;
  char *token;
  CSTOKEN_TYPE type;
} SimpleTokens[] = {
  { TRUE, "<=", CS_OP_LTE },
  { TRUE, ">=", CS_OP_GTE },
  { TRUE, "==", CS_OP_EQUAL },
  { TRUE, "!=", CS_OP_NEQUAL },
  { TRUE, "||", CS_OP_OR },
  { TRUE, "&&", CS_OP_AND },
  { FALSE, "!", CS_OP_NOT },
/* For now, we are still treating this special instead of as an op
 * If we make this an op, then we'd have to determine how to handle
 * NUM types without doing something like #"5" */
/*  { FALSE, "#", CS_OP_NUM }, */
  { FALSE, "?", CS_OP_EXISTS },
  { FALSE, "<", CS_OP_LT },
  { FALSE, ">", CS_OP_GT },
  { FALSE, "+", CS_OP_ADD },
  { FALSE, "-", CS_OP_SUB },
  { FALSE, "*", CS_OP_MULT },
  { FALSE, "/", CS_OP_DIV },
  { FALSE, "%", CS_OP_MOD },
  { FALSE, "(", CS_OP_LPAREN },
  { FALSE, ")", CS_OP_RPAREN },
  { FALSE, "[", CS_OP_LBRACKET },
  { FALSE, "]", CS_OP_RBRACKET },
  { FALSE, ".", CS_OP_DOT },
  { FALSE, ",", CS_OP_COMMA },
  { FALSE, NULL, 0 }
};

#define MAX_TOKENS 256

static NEOERR *parse_tokens (CSPARSE *parse, char *arg, CSTOKEN *tokens,
    int *used_tokens)
{
  char tmp[256];
  int ntokens = 0;
  int x;
  BOOL found;
  BOOL last_is_op = 1;
  char *p, *p2;
  char *expr = arg;

  while (arg && *arg != '\0')
  {
    while (*arg && isspace(*arg)) arg++;
    if (*arg == '\0') break;
    x = 0;
    found = FALSE;

    /* If we already saw an operator, and this is a +/-, assume its
     * a number */
    if (!(last_is_op && (*arg == '+' || *arg == '-')))
    {
      while ((found == FALSE) && SimpleTokens[x].token)
      {
	if (((SimpleTokens[x].two_chars == TRUE) &&
	      (*arg == SimpleTokens[x].token[0]) &&
	      (*(arg + 1) == SimpleTokens[x].token[1])) ||
	    ((SimpleTokens[x].two_chars == FALSE) &&
	     (*arg == SimpleTokens[x].token[0])))
	{
	  tokens[ntokens++].type = SimpleTokens[x].type;
	  found = TRUE;
	  arg++;
	  if (SimpleTokens[x].two_chars) arg++;
	}
	x++;
      }
      /* Another special case: RPAREN and RBRACKET can have another op
       * after it */
      if (found && !(tokens[ntokens-1].type == CS_OP_RPAREN || tokens[ntokens-1].type == CS_OP_RBRACKET))
	last_is_op = 1;
    }

    if (found == FALSE)
    {
      if (*arg == '#')
      {
        /* TODO: make # an operator and not syntax */
	arg++;
	tokens[ntokens].type = CS_TYPE_NUM;
	tokens[ntokens].value = arg;
	strtol(arg, &p, 0);
	if (p == arg)
	{
	  tokens[ntokens].type = CS_TYPE_VAR_NUM;
	  p = strpbrk(arg, "\"?<>=!#-+|&,)*/%[]( \t\r\n");
	  if (p == arg)
	    return nerr_raise (NERR_PARSE, "%s Missing varname/number after #: %s",
		find_context(parse, -1, tmp, sizeof(tmp)), arg);
	}
	if (p == NULL)
	  tokens[ntokens].len = strlen(arg);
	else
	  tokens[ntokens].len = p - arg;
	ntokens++;
	arg = p;
      }
      else if (*arg == '"')
      {
	arg++;
	tokens[ntokens].type = CS_TYPE_STRING;
	tokens[ntokens].value = arg;
	p = strchr (arg, '"');
	if (p == NULL)
	  return nerr_raise (NERR_PARSE, "%s Missing end of string: %s",
	      find_context(parse, -1, tmp, sizeof(tmp)), arg);
	tokens[ntokens].len = p - arg;
	ntokens++;
	arg = p + 1;
      }
      else if (*arg == '\'')
      {
	arg++;
	tokens[ntokens].type = CS_TYPE_STRING;
	tokens[ntokens].value = arg;
	p = strchr (arg, '\'');
	if (p == NULL)
	  return nerr_raise (NERR_PARSE, "%s Missing end of string: %s",
	      find_context(parse, -1, tmp, sizeof(tmp)), arg);
	tokens[ntokens].len = p - arg;
	ntokens++;
	arg = p + 1;
      }
      else if (*arg == '$')
      {
        /* TODO: make $ an operator and not syntax */
	arg++;
	tokens[ntokens].type = CS_TYPE_VAR;
	tokens[ntokens].value = arg;
	p = strpbrk(arg, "\"?<>=!#-+|&,)*/%[]( \t\r\n");
	if (p == arg)
	  return nerr_raise (NERR_PARSE, "%s Missing varname after $: %s",
	      find_context(parse, -1, tmp, sizeof(tmp)), arg);
	if (p == NULL)
	  tokens[ntokens].len = strlen(arg);
	else
	  tokens[ntokens].len = p - arg;
	ntokens++;
	arg = p;
      }
      else
      {
	tokens[ntokens].type = CS_TYPE_VAR;
	tokens[ntokens].value = arg;
	/* Special case for Dave: If this is entirely a number, treat it
	 * as one */
	strtol(arg, &p2, 0);
	p = strpbrk(arg, "\"?<>=!#-+|&,)*/%[]( \t\r\n");
	/* This is complicated because +/- is valid in a number, but not
	 * in a varname */
	if (p2 != arg && (p <= p2 || (p == NULL && *p2 == '\0')))
	{
	  tokens[ntokens].type = CS_TYPE_NUM;
	  tokens[ntokens].len = p2 - arg;
	  arg = p2;
	}
	else
	{
	  if (p == arg)
	    return nerr_raise (NERR_PARSE,
		"%s Var arg specified with no varname: %s",
		find_context(parse, -1, tmp, sizeof(tmp)), arg);
	  if (p == NULL)
	    tokens[ntokens].len = strlen(arg);
	  else
	    tokens[ntokens].len = p - arg;
	  arg = p;
	}
	ntokens++;
      }
      last_is_op = 0;
    }
    if (ntokens >= MAX_TOKENS)
	return nerr_raise (NERR_PARSE,
	    "%s Expression exceeds maximum number of tokens of %d: %s",
	    find_context(parse, -1, tmp, sizeof(tmp)), MAX_TOKENS, expr);
  }
  *used_tokens = ntokens;
  return STATUS_OK;
}

CSTOKEN_TYPE OperatorOrder[] = {
  CS_OP_COMMA,
  CS_OP_OR,
  CS_OP_AND,
  CS_OP_EQUAL | CS_OP_NEQUAL,
  CS_OP_GT | CS_OP_GTE | CS_OP_LT | CS_OP_LTE,
  CS_OP_ADD | CS_OP_SUB,
  CS_OP_MULT | CS_OP_DIV | CS_OP_MOD,
  CS_OP_NOT | CS_OP_EXISTS,
  CS_OP_LBRACKET | CS_OP_DOT | CS_OP_LPAREN,
  0
};

static char *expand_token_type(CSTOKEN_TYPE t_type, int more)
{
  switch (t_type)
  {
    case CS_OP_EXISTS: return "?";
    case CS_OP_NOT: return "!";
    case CS_OP_NUM: return "#";
    case CS_OP_EQUAL: return "==";
    case CS_OP_NEQUAL: return "!=";
    case CS_OP_LT: return "<";
    case CS_OP_LTE: return "<=";
    case CS_OP_GT: return ">";
    case CS_OP_GTE: return ">=";
    case CS_OP_AND: return "&&";
    case CS_OP_OR: return "||";
    case CS_OP_ADD: return "+";
    case CS_OP_SUB: return "-";
    case CS_OP_MULT: return "*";
    case CS_OP_DIV: return "/";
    case CS_OP_MOD: return "%";
    case CS_OP_LPAREN: return "(";
    case CS_OP_RPAREN: return ")";
    case CS_OP_LBRACKET: return "[";
    case CS_OP_RBRACKET: return "]";
    case CS_OP_DOT : return ".";
    case CS_OP_COMMA : return ",";
    case CS_TYPE_STRING: return more ? "STRING" : "s";
    case CS_TYPE_NUM: return more ? "NUM" : "n";
    case CS_TYPE_VAR: return more ? "VAR" : "v";
    case CS_TYPE_VAR_NUM: return more ? "VARNUM" : "vn";
    case CS_TYPE_MACRO: return more ? "MACRO" : "m";
    case CS_TYPE_FUNCTION: return more ? "FUNC" : "f";
    default: return "u";
  }
  return "u";
}

static char *token_list (CSTOKEN *tokens, int ntokens, char *buf, size_t buflen)
{
  char *p = buf;
  int i, t;
  char save;

  for (i = 0; i < ntokens && buflen > 0; i++)
  {
    if (tokens[i].value)
    {
      save = tokens[i].value[tokens[i].len];
      tokens[i].value[tokens[i].len] = '\0';
      t = snprintf(p, buflen, "%s%d:%s:'%s'", i ? "  ":"", i, expand_token_type(tokens[i].type, 0), tokens[i].value);
      tokens[i].value[tokens[i].len] = save;
    }
    else
    {
      t = snprintf(p, buflen, "%s%d:%s", i ? "  ":"", i, expand_token_type(tokens[i].type, 0));
    }
    if (t == -1 || t >= buflen) return buf;
    buflen -= t;
    p += t;
  }
  return buf;
}

static NEOERR *parse_expr2 (CSPARSE *parse, CSTOKEN *tokens, int ntokens, int lvalue, CSARG *arg)
{
  NEOERR *err = STATUS_OK;
  char tmp[256];
  char tmp2[256];
  int x, op;
  int m;

#if DEBUG_EXPR_PARSE
  fprintf(stderr, "%s\n", token_list(tokens, ntokens, tmp, sizeof(tmp)));
  for (x = 0; x < ntokens; x++)
  {
    fprintf (stderr, "%s ", expand_token_type(tokens[x].type, 0));
  }
  fprintf(stderr, "\n");
#endif

  /* Not quite sure what to do with this case... */
  if (ntokens == 0)
  {
    return nerr_raise (NERR_PARSE, "%s Bad Expression",
	find_context(parse, -1, tmp, sizeof(tmp)));
  }
  if (ntokens == 1)
  {
    x = 0;
    if (tokens[0].type & CS_TYPES)
    {
      arg->s = tokens[0].value;
      if (tokens[0].len >= 0)
	arg->s[tokens[0].len] = '\0';
      arg->op_type = tokens[0].type;

      if (tokens[x].type == CS_TYPE_NUM)
	arg->n = strtol(arg->s, NULL, 0);
      return STATUS_OK;
    }
    else
    {
      return nerr_raise (NERR_PARSE,
	  "%s Terminal token is not an argument, type is %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), expand_token_type(tokens[0].type, 0));
    }
  }

  /*
  if (ntokens == 2 && (tokens[0].type & CS_OPS_UNARY))
  {
    arg->op_type = tokens[0].type;
    arg->expr1 = (CSARG *) calloc (1, sizeof (CSARG));
    if (arg->expr1 == NULL)
      return nerr_raise (NERR_NOMEM,
	  "%s Unable to allocate memory for expression",
	  find_context(parse, -1, tmp, sizeof(tmp)));
    err = parse_expr2(parse, tokens + 1, 1, lvalue, arg->expr1);
    return nerr_pass(err);
  }
  */

  op = 0;
  while (OperatorOrder[op])
  {
    x = ntokens-1;
    while (x >= 0)
    {
      /* handle associative ops by skipping through the entire set here,
       * ie the whole thing is an expression that can't match a binary op */
      if (tokens[x].type & CS_OP_RPAREN)
      {
	m = 1;
	x--;
	while (x >= 0)
	{
	  if (tokens[x].type & CS_OP_RPAREN) m++;
	  if (tokens[x].type & CS_OP_LPAREN) m--;
	  if (m == 0) break;
	  x--;
	}
	if (m)
	  return nerr_raise (NERR_PARSE,
	      "%s Missing left parenthesis in expression",
	      find_context(parse, -1, tmp, sizeof(tmp)));
	/* if (x == 0) break; */
	/* x--; */
	/* we don't do an x-- here, because we are special casing the
	 * left bracket to be both an operator and an associative */
      }
      if (tokens[x].type & CS_OP_RBRACKET)
      {
	m = 1;
	x--;
	while (x >= 0)
	{
	  if (tokens[x].type & CS_OP_RBRACKET) m++;
	  if (tokens[x].type & CS_OP_LBRACKET) m--;
	  if (m == 0) break;
	  x--;
	}
	if (m)
	  return nerr_raise (NERR_PARSE,
	      "%s Missing left bracket in expression",
	      find_context(parse, -1, tmp, sizeof(tmp)));
	if (x == 0) break;
	/* we don't do an x-- here, because we are special casing the
	 * left bracket to be both an operator and an associative */
      }
      if (lvalue && !(tokens[x].type & CS_OPS_LVALUE))
      {
	return nerr_raise (NERR_PARSE,
	    "%s Invalid op '%s' in lvalue",
	    find_context(parse, -1, tmp, sizeof(tmp)),
	    expand_token_type(tokens[x].type, 0));
      }
      if (tokens[x].type & OperatorOrder[op])
      {
	if (tokens[x].type & CS_OPS_UNARY)
	{
	  if (x == 0)
	  {
	    arg->op_type = tokens[x].type;
	    arg->expr1 = (CSARG *) calloc (1, sizeof (CSARG));
	    if (arg->expr1 == NULL)
	      return nerr_raise (NERR_NOMEM,
		  "%s Unable to allocate memory for expression",
		  find_context(parse, -1, tmp, sizeof(tmp)));
            if (tokens[x].type & CS_OP_LPAREN)
            {
              if (!(tokens[ntokens-1].type & CS_OP_RPAREN))
              {
                return nerr_raise (NERR_PARSE,
                                   "%s Missing right parenthesis in expression",
                                   find_context(parse, -1, tmp, sizeof(tmp)));
              }
              /* XXX: we might want to set lvalue to 0 here */
              /* -2 since we strip the RPAREN as well */
              err = parse_expr2(parse, tokens + 1, ntokens-2, lvalue, arg->expr1);
            }
            else
            {
              err = parse_expr2(parse, tokens + 1, ntokens-1, lvalue, arg->expr1);
            }
	    return nerr_pass(err);
	  }
	}
	else if (tokens[x].type == CS_OP_COMMA)
	{
	  /* Technically, comma should be a left to right, not right to
	   * left, so we're going to build up the arguments in reverse
	   * order... */
	  arg->op_type = tokens[x].type;
	  /* The actual argument is expr1 */
	  arg->expr1 = (CSARG *) calloc (1, sizeof (CSARG));
	  /* The previous argument is next */
	  arg->next = (CSARG *) calloc (1, sizeof (CSARG));
	  if (arg->expr1 == NULL || arg->next == NULL)
	    return nerr_raise (NERR_NOMEM,
		"%s Unable to allocate memory for expression",
		find_context(parse, -1, tmp, sizeof(tmp)));
	  err = parse_expr2(parse, tokens + x + 1, ntokens-x-1, lvalue, arg->expr1);
	  if (err) return nerr_pass (err);
	  err = parse_expr2(parse, tokens, x, lvalue, arg->next);
	  if (err) return nerr_pass (err);
	  return STATUS_OK;
	}
	else
	{
	  arg->op_type = tokens[x].type;
	  arg->expr2 = (CSARG *) calloc (1, sizeof (CSARG));
	  arg->expr1 = (CSARG *) calloc (1, sizeof (CSARG));
	  if (arg->expr1 == NULL || arg->expr2 == NULL)
	    return nerr_raise (NERR_NOMEM,
		"%s Unable to allocate memory for expression",
		find_context(parse, -1, tmp, sizeof(tmp)));
	  if (tokens[x].type & CS_OP_LBRACKET)
	  {
            if (!(tokens[ntokens-1].type & CS_OP_RBRACKET))
            {
              return nerr_raise (NERR_PARSE,
                                 "%s Missing right bracket in expression",
                                 find_context(parse, -1, tmp, sizeof(tmp)));
            }
	    /* Inside of brackets, we don't limit to valid lvalue ops */
            /* -2 since we strip the RBRACKET as well */
	    err = parse_expr2(parse, tokens + x + 1, ntokens-x-2, 0, arg->expr2);
	  }
	  else
	  {
	    err = parse_expr2(parse, tokens + x + 1, ntokens-x-1, lvalue, arg->expr2);
	  }
	  if (err) return nerr_pass (err);
	  err = parse_expr2(parse, tokens, x, lvalue, arg->expr1);
	  if (err) return nerr_pass (err);
	  return STATUS_OK;
	}
      }
      x--;
    }
    op++;
  }

  /* Unary op against an entire expression */
  if ((tokens[0].type & CS_OPS_UNARY) && tokens[1].type == CS_OP_LPAREN &&
      tokens[ntokens-1].type == CS_OP_RPAREN)
  {
    arg->op_type = tokens[0].type;
    arg->expr1 = (CSARG *) calloc (1, sizeof (CSARG));
    if (arg->expr1 == NULL)
      return nerr_raise (NERR_NOMEM,
	  "%s Unable to allocate memory for expression",
	  find_context(parse, -1, tmp, sizeof(tmp)));
    err = parse_expr2(parse, tokens + 2, ntokens-3, lvalue, arg->expr1);
    return nerr_pass(err);
  }
  if (tokens[0].type & CS_OPS_UNARY)
  {
    arg->op_type = tokens[0].type;
    arg->expr1 = (CSARG *) calloc (1, sizeof (CSARG));
    if (arg->expr1 == NULL)
      return nerr_raise (NERR_NOMEM,
	  "%s Unable to allocate memory for expression",
	  find_context(parse, -1, tmp, sizeof(tmp)));
    err = parse_expr2(parse, tokens + 1, ntokens-1, lvalue, arg->expr1);
    return nerr_pass(err);
  }

  /* function call */
  if ((tokens[0].type & CS_TYPE_VAR) && tokens[1].type == CS_OP_LPAREN &&
      tokens[ntokens-1].type == CS_OP_RPAREN)
  {
    CS_FUNCTION *csf;
    int nargs;

    if (tokens[0].len >= 0)
      tokens[0].value[tokens[0].len] = '\0';

    arg->op_type = CS_TYPE_FUNCTION;
    csf = parse->functions;
    while (csf != NULL)
    {
      if (!strcmp(tokens[0].value, csf->name))
      {
	arg->function = csf;
	break;
      }
      csf = csf->next;
    }
    if (csf == NULL)
    {
      return nerr_raise (NERR_PARSE, "%s Unknown function %s called",
	  find_context(parse, -1, tmp, sizeof(tmp)), tokens[0].value);
    }
    arg->expr1 = (CSARG *) calloc (1, sizeof (CSARG));
    if (arg->expr1 == NULL)
      return nerr_raise (NERR_NOMEM,
	  "%s Unable to allocate memory for expression",
	  find_context(parse, -1, tmp, sizeof(tmp)));
    if (ntokens-3 > 0) {
      err = parse_expr2(parse, tokens + 2, ntokens-3, lvalue, arg->expr1);
      if (err) return nerr_pass(err);
    } else {
      free(arg->expr1);
      arg->expr1 = NULL;
    }
    nargs = rearrange_for_call(&(arg->expr1));
    if (nargs != arg->function->n_args)
    {
      return nerr_raise (NERR_PARSE,
	  "%s Incorrect number of arguments in call to %s, expected %d, got %d",
	  find_context(parse, -1, tmp, sizeof(tmp)), tokens[0].value,
	  arg->function->n_args, nargs);
    }
    return nerr_pass(err);
  }

  return nerr_raise (NERR_PARSE, "%s Bad Expression:%s",
      find_context(parse, -1, tmp, sizeof(tmp)),
      token_list(tokens, ntokens, tmp2, sizeof(tmp2)));
}

static NEOERR *parse_expr (CSPARSE *parse, char *arg, int lvalue, CSARG *expr)
{
  NEOERR *err;
  CSTOKEN tokens[MAX_TOKENS];
  int ntokens = 0;

  memset(tokens, 0, sizeof(CSTOKEN) * MAX_TOKENS);
  err = parse_tokens (parse, arg, tokens, &ntokens);
  if (err) return nerr_pass(err);
  err = parse_expr2 (parse, tokens, ntokens, lvalue, expr);
  if (err) return nerr_pass(err);
  return STATUS_OK;
}

static NEOERR *literal_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;

  /* ne_warn ("literal: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  node->arg1.op_type = CS_TYPE_STRING;
  node->arg1.s = arg;
  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *literal_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;

  if (node->arg1.s != NULL)
    err = parse->output_cb (parse->output_ctx, node->arg1.s);
  *next = node->next;
  return nerr_pass(err);
}

static NEOERR *name_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  char *a, *s;
  char tmp[256];

  /* ne_warn ("name: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;
  /* Validate arg is a var (regex /^[#" ]$/) */
  a = neos_strip(arg);
  s = strpbrk(a, "#\" <>");
  if (s != NULL)
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE, "%s Invalid character in var name %s: %c",
	find_context(parse, -1, tmp, sizeof(tmp)),
	a, s[0]);
  }

  node->arg1.op_type = CS_TYPE_VAR;
  node->arg1.s = a;
  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *escape_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  char *a = NULL;
  char tmp[256];
  CS_ESCAPE_MODES *esc_cursor;
  CSTREE *node;

  /* ne_warn ("escape: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  /* Since this throws an error always if there's a problem
   * this flag seems pointless, but following convention,
   * here it is. */
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++; /* ignore colon, space, etc */

  /* Parse the arg - we're expecting a string */
  err = parse_expr (parse, arg, 0, &(node->arg1));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }
  if (node->arg1.op_type != CS_TYPE_STRING)
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE, "%s Invalid argument for escape: %s",
      find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }

  a = neos_strip(node->arg1.s); /* Strip spaces for testing */

  /* Ensure the mode specified is allowed */
  for (esc_cursor = &EscapeModes[0];
       esc_cursor->mode != NULL;
       esc_cursor++)
    if (!strncasecmp(a, esc_cursor->mode, strlen(esc_cursor->mode)))
    {
      if (err != STATUS_OK) return nerr_pass(err);
      parse->escaping.next_stack = esc_cursor->context;
      break;
    }
  /* Didn't find an acceptable value we were looking for */
  if (esc_cursor->mode == NULL)
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE, "%s Invalid argument for escape: %s",
      find_context(parse, -1, tmp, sizeof(tmp)), a);
  }

  *(parse->next) = node;
  parse->next = &(node->case_0);
  parse->current = node;
  return STATUS_OK;
}

static NEOERR *name_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  HDF *obj;
  char *v;

  if (node->arg1.op_type == CS_TYPE_VAR && node->arg1.s != NULL)
  {
    obj = var_lookup_obj (parse, node->arg1.s);
    if (obj != NULL)
    {
      v = hdf_obj_name(obj);
      err = parse->output_cb (parse->output_ctx, v);
    }
  }
  *next = node->next;
  return nerr_pass(err);
}

static NEOERR *var_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  STACK_ENTRY *entry;

  err = uListGet (parse->stack, -1, (void *)&entry);
  if (err != STATUS_OK) return nerr_pass(err);

  /* ne_warn ("var: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;

  /* Default escape the variable based on
   * current stack's escape context except for
   * uvar:
   */
  if (!strcmp(Commands[cmd].cmd, "uvar"))
    node->escape = NEOS_ESCAPE_NONE;
  else
    node->escape = entry->escape;


  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;
  /* Validate arg is a var (regex /^[#" ]$/) */
  err = parse_expr (parse, arg, 0, &(node->arg1));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *lvar_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;

  /* ne_warn ("lvar: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;
  /* Validate arg is a var (regex /^[#" ]$/) */
  err = parse_expr (parse, arg, 0, &(node->arg1));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *linclude_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;

  /* ne_warn ("linclude: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;
  /* Validate arg is a var (regex /^[#" ]$/) */
  err = parse_expr (parse, arg, 0, &(node->arg1));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *alt_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;

  /* ne_warn ("var: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;
  /* Validate arg is a var (regex /^[#" ]$/) */
  err = parse_expr (parse, arg, 0, &(node->arg1));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  *(parse->next) = node;
  parse->next = &(node->case_0);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *evar_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  char *a, *s;
  const char *save_context;
  int save_infile;
  char tmp[256];

  /* ne_warn ("evar: %s", arg); */
  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;
  /* Validate arg is a var (regex /^[#" ]$/) */
  a = neos_strip(arg);
  s = strpbrk(a, "#\" <>");
  if (s != NULL)
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE, "%s Invalid character in var name %s: %c",
	find_context(parse, -1, tmp, sizeof(tmp)),
	a, s[0]);
  }

  err = hdf_get_copy (parse->hdf, a, &s, NULL);
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass (err);
  }
  if (node->flags & CSF_REQUIRED && s == NULL)
  {
    dealloc_node(&node);
    return nerr_raise (NERR_NOT_FOUND, "%s Unable to evar empty variable %s",
	find_context(parse, -1, tmp, sizeof(tmp)), a);
  }

  node->arg1.op_type = CS_TYPE_VAR;
  node->arg1.s = a;
  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  save_context = parse->context;
  save_infile = parse->in_file;
  parse->context = a;
  parse->in_file = 0;
  if (s) err = cs_parse_string (parse, s, strlen(s));
  parse->context = save_context;
  parse->in_file = save_infile;

  return nerr_pass (err);
}

static NEOERR *if_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;

  /* ne_warn ("if: %s", arg); */
  err = alloc_node (&node);
  if (err != STATUS_OK) return nerr_pass(err);
  node->cmd = cmd;
  arg++;

  err = parse_expr (parse, arg, 0, &(node->arg1));
  if (err != STATUS_OK)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  *(parse->next) = node;
  parse->next = &(node->case_0);
  parse->current = node;

  return STATUS_OK;
}

char *arg_eval (CSPARSE *parse, CSARG *arg)
{
  switch ((arg->op_type & CS_TYPES))
  {
    case CS_TYPE_STRING:
      return arg->s;
    case CS_TYPE_VAR:
      return var_lookup (parse, arg->s);
    case CS_TYPE_NUM:
    case CS_TYPE_VAR_NUM:
    default:
      ne_warn ("Unsupported type %s in arg_eval", expand_token_type(arg->op_type, 1));
      return NULL;
  }
}

/* This coerces everything to numbers */
long int arg_eval_num (CSPARSE *parse, CSARG *arg)
{
  long int v = 0;

  switch ((arg->op_type & CS_TYPES))
  {
    case CS_TYPE_STRING:
      v = strtol(arg->s, NULL, 0);
      break;
    case CS_TYPE_NUM:
      v = arg->n;
      break;

    case CS_TYPE_VAR:
    case CS_TYPE_VAR_NUM:
      v = var_int_lookup (parse, arg->s);
      break;
    default:
      ne_warn ("Unsupported type %s in arg_eval_num", expand_token_type(arg->op_type, 1));
      v = 0;
      break;
  }
  return v;
}

/* This is different from arg_eval_num because we don't force strings to
 * numbers, a string is either a number (if it is all numeric) or we're
 * testing existance.  At least, that's what perl does and what dave
 * wants */
long int arg_eval_bool (CSPARSE *parse, CSARG *arg)
{
  long int v = 0;
  char *s, *r;

  switch ((arg->op_type & CS_TYPES))
  {
    case CS_TYPE_STRING:
    case CS_TYPE_VAR:
      if (arg->op_type == CS_TYPE_VAR)
	s = var_lookup(parse, arg->s);
      else
	s = arg->s;
      if (!s || *s == '\0') return 0; /* non existance or empty is false(0) */
      v = strtol(s, &r, 0);
      if (*r == '\0') /* entire string converted, treat as number */
	return v;
      /* if the entire string didn't convert, then its non-numeric and
       * exists, so its true (1) */
      return 1;
    case CS_TYPE_NUM:
      return arg->n;
    case CS_TYPE_VAR_NUM: /* this implies forced numeric evaluation */
      return var_int_lookup (parse, arg->s);
      break;
    default:
      ne_warn ("Unsupported type %s in arg_eval_bool", expand_token_type(arg->op_type, 1));
      v = 0;
      break;
  }
  return v;
}

char *arg_eval_str_alloc (CSPARSE *parse, CSARG *arg)
{
  char *s = NULL;
  char buf[256];
  long int n_val;

  switch ((arg->op_type & CS_TYPES))
  {
    case CS_TYPE_STRING:
      s = arg->s;
      break;
    case CS_TYPE_VAR:
      s = var_lookup (parse, arg->s);
      break;
    case CS_TYPE_NUM:
    case CS_TYPE_VAR_NUM:
      s = buf;
      n_val = arg_eval_num (parse, arg);
      snprintf (buf, sizeof(buf), "%ld", n_val);
      break;
    default:
      ne_warn ("Unsupported type %s in arg_eval_str_alloc",
	  expand_token_type(arg->op_type, 1));
      s = NULL;
      break;
  }
  if (s) return strdup(s);
  return NULL;
}

#if DEBUG_EXPR_EVAL
static void expand_arg (CSPARSE *parse, int depth, char *where, CSARG *arg)
{
  int x;

  for (x=0; x<depth; x++)
    fputc(' ', stderr);

  fprintf(stderr, "%s op: %s alloc: %d value: ", where, expand_token_type(arg->op_type, 0), arg->alloc);
  if (arg->op_type & CS_OP_NOT)
    fprintf(stderr, "!");
  if (arg->op_type & CS_OP_NUM)
    fprintf(stderr, "#");
  if (arg->op_type & CS_OP_EXISTS)
    fprintf(stderr, "?");
  if (arg->op_type & (CS_TYPE_VAR_NUM | CS_TYPE_NUM))
    fprintf(stderr, "#");
  if (arg->op_type & CS_TYPE_NUM)
    fprintf(stderr, "%ld\n", arg->n);
  else if (arg->op_type & CS_TYPE_STRING)
    fprintf(stderr, "'%s'\n", arg->s);
  else if (arg->op_type & CS_TYPE_VAR)
    fprintf(stderr, "%s = %s\n", arg->s, var_lookup(parse, arg->s));
  else if (arg->op_type & CS_TYPE_VAR_NUM)
    fprintf(stderr, "%s = %ld\n", arg->s, var_int_lookup(parse, arg->s));
  else
    fprintf(stderr, "\n");
}
#endif

static NEOERR *eval_expr_string(CSPARSE *parse, CSARG *arg1, CSARG *arg2, CSTOKEN_TYPE op, CSARG *result)
{
  char *s1, *s2;
  int out;

  result->op_type = CS_TYPE_NUM;
  s1 = arg_eval (parse, arg1);
  s2 = arg_eval (parse, arg2);

  if ((s1 == NULL) || (s2 == NULL))
  {
    switch (op)
    {
      case CS_OP_EQUAL:
	result->n = (s1 == s2) ? 1 : 0;
	break;
      case CS_OP_NEQUAL:
	result->n = (s1 != s2) ? 1 : 0;
	break;
      case CS_OP_LT:
	result->n = ((s1 == NULL) && (s2 != NULL)) ? 1 : 0;
	break;
      case CS_OP_LTE:
	result->n = (s1 == NULL) ? 1 : 0;
	break;
      case CS_OP_GT:
	result->n = ((s1 != NULL) && (s2 == NULL)) ? 1 : 0;
	break;
      case CS_OP_GTE:
	result->n = (s2 == NULL) ? 1 : 0;
	break;
      case CS_OP_ADD:
	/* be sure to transfer ownership of the string here */
	result->op_type = CS_TYPE_STRING;
	if (s1 == NULL)
	{
	  result->s = s2;
	  result->alloc = arg2->alloc;
	  arg2->alloc = 0;
	}
	else
	{
	  result->s = s1;
	  result->alloc = arg1->alloc;
	  arg1->alloc = 0;
	}
	break;
      default:
	ne_warn ("Unsupported op %s in eval_expr", expand_token_type(op, 1));
	break;
    }
  }
  else
  {
    out = strcmp (s1, s2);
    switch (op)
    {
      case CS_OP_EQUAL:
	result->n = (!out) ? 1 : 0;
	break;
      case CS_OP_NEQUAL:
	result->n = (out) ? 1 : 0;
	break;
      case CS_OP_LT:
	result->n = (out < 0) ? 1 : 0;
	break;
      case CS_OP_LTE:
	result->n = (out <= 0) ? 1 : 0;
	break;
      case CS_OP_GT:
	result->n = (out > 0) ? 1 : 0;
	break;
      case CS_OP_GTE:
	result->n = (out >= 0) ? 1 : 0;
	break;
      case CS_OP_ADD:
	result->op_type = CS_TYPE_STRING;
	result->alloc = 1;
	result->s = (char *) calloc ((strlen(s1) + strlen(s2) + 1), sizeof(char));
	if (result->s == NULL)
	  return nerr_raise (NERR_NOMEM, "Unable to allocate memory to concatenate strings in expression: %s + %s", s1, s2);
	strcpy(result->s, s1);
	strcat(result->s, s2);
	break;
      default:
	ne_warn ("Unsupported op %s in eval_expr_string", expand_token_type(op, 1));
	break;
    }
  }
  return STATUS_OK;
}

static NEOERR *eval_expr_num(CSPARSE *parse, CSARG *arg1, CSARG *arg2, CSTOKEN_TYPE op, CSARG *result)
{
  long int n1, n2;

  result->op_type = CS_TYPE_NUM;
  n1 = arg_eval_num (parse, arg1);
  n2 = arg_eval_num (parse, arg2);

  switch (op)
  {
    case CS_OP_EQUAL:
      result->n = (n1 == n2) ? 1 : 0;
      break;
    case CS_OP_NEQUAL:
      result->n = (n1 != n2) ? 1 : 0;
      break;
    case CS_OP_LT:
      result->n = (n1 < n2) ? 1 : 0;
      break;
    case CS_OP_LTE:
      result->n = (n1 <= n2) ? 1 : 0;
      break;
    case CS_OP_GT:
      result->n = (n1 > n2) ? 1 : 0;
      break;
    case CS_OP_GTE:
      result->n = (n1 >= n2) ? 1 : 0;
      break;
    case CS_OP_ADD:
      result->n = (n1 + n2);
      break;
    case CS_OP_SUB:
      result->n = (n1 - n2);
      break;
    case CS_OP_MULT:
      result->n = (n1 * n2);
      break;
    case CS_OP_DIV:
      if (n2 == 0) result->n = UINT_MAX;
      else result->n = (n1 / n2);
      break;
    case CS_OP_MOD:
      if (n2 == 0) result->n = 0;
      else result->n = (n1 % n2);
      break;
    default:
      ne_warn ("Unsupported op %s in eval_expr_num", expand_token_type(op, 1));
      break;
  }
  return STATUS_OK;
}

static NEOERR *eval_expr_bool(CSPARSE *parse, CSARG *arg1, CSARG *arg2, CSTOKEN_TYPE op, CSARG *result)
{
  long int n1, n2;

  result->op_type = CS_TYPE_NUM;
  n1 = arg_eval_bool (parse, arg1);
  n2 = arg_eval_bool (parse, arg2);

  switch (op)
  {
    case CS_OP_AND:
      result->n = (n1 && n2) ? 1 : 0;
      break;
    case CS_OP_OR:
      result->n = (n1 || n2) ? 1 : 0;
      break;
    default:
      ne_warn ("Unsupported op %s in eval_expr_bool", expand_token_type(op, 1));
      break;
  }
  return STATUS_OK;
}

#if DEBUG_EXPR_EVAL
static int _depth = 0;
#endif

static NEOERR *eval_expr (CSPARSE *parse, CSARG *expr, CSARG *result)
{
  NEOERR *err;

  if (expr == NULL)
    return nerr_raise (NERR_ASSERT, "expr is NULL");
  if (result == NULL)
    return nerr_raise (NERR_ASSERT, "result is NULL");

#if DEBUG_EXPR_EVAL
  _depth++;
  expand_arg(parse, _depth, "expr", expr);
#endif

  memset(result, 0, sizeof(CSARG));
  if (expr->op_type & CS_TYPES)
  {
    *result = *expr;
    /* we transfer ownership of the string here.. ugh */
    if (expr->alloc) expr->alloc = 0;
#if DEBUG_EXPR_EVAL
    expand_arg(parse, _depth, "result", result);
    _depth--;
#endif
    return STATUS_OK;
  }

  if (expr->op_type & CS_OP_LPAREN)
  {
    /* lparen is a no-op, just skip */
    return nerr_pass(eval_expr(parse, expr->expr1, result));
  }
  if (expr->op_type & CS_TYPE_FUNCTION)
  {
    if (expr->function == NULL || expr->function->function == NULL)
      return nerr_raise(NERR_ASSERT,
          "Function is NULL in attempt to evaluate function call %s",
          (expr->function) ? expr->function->name : "");

    /* The function evaluates all the arguments, so don't pre-evaluate
     * argument1 */
    err = expr->function->function(parse, expr->function, expr->expr1, result);
    if (err) return nerr_pass(err);
    /* Indicate whether or not an explicit escape call was made by
     * setting the mode (usually NONE or FUNCTION). This is ORed to
     * ensure that escaping calls within other functions do not get
     * double-escaped. E.g. slice(html_escape(foo), 10, 20) */
    parse->escaping.current |= expr->function->escape;
  }
  else
  {
    CSARG arg1, arg2;
    arg1.alloc = 0;
    arg2.alloc = 0;

    err = eval_expr (parse, expr->expr1, &arg1);
    if (err) return nerr_pass(err);
#if DEBUG_EXPR_EVAL
    expand_arg(parse, _depth, "arg1", &arg1);
#endif
    if (expr->op_type & CS_OPS_UNARY)
    {
      result->op_type = CS_TYPE_NUM;
      switch (expr->op_type) {
        case CS_OP_NOT:
          result->n = arg_eval_bool(parse, &arg1) ? 0 : 1;
          break;
        case CS_OP_EXISTS:
          if (arg1.op_type & (CS_TYPE_VAR | CS_TYPE_VAR_NUM))
          {
            if (arg_eval(parse, &arg1) == NULL)
              result->n = 0;
            else
              result->n = 1;
          }
          else
          {
            /* All numbers/strings exist */
            result->n = 1;
          }
          break;
        case CS_OP_NUM:
          result->n = arg_eval_num (parse, &arg1);
          break;
        case CS_OP_LPAREN:
          return nerr_raise(NERR_ASSERT, "LPAREN should be handled above");
        default:
          result->n = 0;
          ne_warn ("Unsupported op %s in eval_expr", expand_token_type(expr->op_type, 1));
          break;
      }
    }
    else if (expr->op_type == CS_OP_COMMA)
    {
      /* The comma operator, like in C, we return the value of the right
       * most argument, in this case that's expr1, but we still need to
       * evaluate the other stuff */
      if (expr->next)
      {
        err = eval_expr (parse, expr->next, &arg2);
#if DEBUG_EXPR_EVAL
        expand_arg(parse, _depth, "arg2", &arg2);
#endif
        if (err) return nerr_pass(err);
        if (arg2.alloc) free(arg2.s);
      }
      *result = arg1;
      /* we transfer ownership of the string here.. ugh */
      if (arg1.alloc) arg1.alloc = 0;
#if DEBUG_EXPR_EVAL
      expand_arg(parse, _depth, "result", result);
      _depth--;
#endif
      return STATUS_OK;
    }
    else
    {
      err = eval_expr (parse, expr->expr2, &arg2);
#if DEBUG_EXPR_EVAL
      expand_arg(parse, _depth, "arg2", &arg2);
#endif
      if (err) return nerr_pass(err);

      if (expr->op_type == CS_OP_LBRACKET)
      {
        /* the bracket op is essentially hdf array lookups, which just
         * means appending the value of arg2, .0 */
        result->op_type = CS_TYPE_VAR;
        result->alloc = 1;
        if (arg2.op_type & (CS_TYPE_VAR_NUM | CS_TYPE_NUM))
        {
          long int n2 = arg_eval_num (parse, &arg2);
          result->s = sprintf_alloc("%s.%d", arg1.s, n2);
          if (result->s == NULL)
            return nerr_raise (NERR_NOMEM, "Unable to allocate memory to concatenate varnames in expression: %s + %d", arg1.s, n2);
        }
        else
        {
          char *s2 = arg_eval (parse, &arg2);
          if (s2 && s2[0])
          {
            result->s = sprintf_alloc("%s.%s", arg1.s, s2);
            if (result->s == NULL)
              return nerr_raise (NERR_NOMEM, "Unable to allocate memory to concatenate varnames in expression: %s + %s", arg1.s, s2);
          }
          else
          {
            /* if s2 doesn't match anything, then the whole thing is empty */
            result->s = "";
            result->alloc = 0;
          }
        }
      }
      else if (expr->op_type == CS_OP_DOT)
      {
        /* the dot op is essentially extending the hdf name, which just
         * means appending the string .0 */
        result->op_type = CS_TYPE_VAR;
        result->alloc = 1;
        if (arg2.op_type & CS_TYPES_VAR)
        {
          result->s = sprintf_alloc("%s.%s", arg1.s, arg2.s);
          if (result->s == NULL)
            return nerr_raise (NERR_NOMEM, "Unable to allocate memory to concatenate varnames in expression: %s + %s", arg1.s, arg2.s);
        }
        else
        {
          if (arg2.op_type & CS_TYPE_NUM)
          {
            long int n2 = arg_eval_num (parse, &arg2);
            result->s = sprintf_alloc("%s.%d", arg1.s, n2);
            if (result->s == NULL)
              return nerr_raise (NERR_NOMEM, "Unable to allocate memory to concatenate varnames in expression: %s + %d", arg1.s, n2);
          }
          else
          {
            char *s2 = arg_eval (parse, &arg2);
            if (s2 && s2[0])
            {
              result->s = sprintf_alloc("%s.%s", arg1.s, s2);
              if (result->s == NULL)
                return nerr_raise (NERR_NOMEM, "Unable to allocate memory to concatenate varnames in expression: %s + %s", arg1.s, s2);
            }
            else
            {
              /* if s2 doesn't match anything, then the whole thing is empty */
              result->s = "";
              result->alloc = 0;
            }
          }
        }
      }
      else if (expr->op_type & (CS_OP_AND | CS_OP_OR))
      {
        /* eval as bool */
        err = eval_expr_bool (parse, &arg1, &arg2, expr->op_type, result);
      }
      else if ((arg1.op_type & (CS_TYPE_NUM | CS_TYPE_VAR_NUM)) ||
               (arg2.op_type & (CS_TYPE_NUM | CS_TYPE_VAR_NUM)) ||
               (expr->op_type & (CS_OP_AND | CS_OP_OR | CS_OP_SUB | CS_OP_MULT | CS_OP_DIV | CS_OP_MOD | CS_OP_GT | CS_OP_GTE | CS_OP_LT | CS_OP_LTE)))
      {
        /* eval as num */
        err = eval_expr_num(parse, &arg1, &arg2, expr->op_type, result);
      }
      else /* eval as string */
      {
        err = eval_expr_string(parse, &arg1, &arg2, expr->op_type, result);
      }
    }
    if (arg1.alloc) free(arg1.s);
    if (arg2.alloc) free(arg2.s);
  }

#if DEBUG_EXPR_EVAL
  expand_arg(parse, _depth, "result", result);
  _depth--;
#endif
  return STATUS_OK;
}

static NEOERR *var_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CSARG val;

  parse->escaping.current = NEOS_ESCAPE_NONE;
  err = eval_expr(parse, &(node->arg1), &val);
  if (err) return nerr_pass(err);
  if (val.op_type & (CS_TYPE_NUM | CS_TYPE_VAR_NUM))
  {
    char buf[256];
    long int n_val;

    n_val = arg_eval_num (parse, &val);
    snprintf (buf, sizeof(buf), "%ld", n_val);
    err = parse->output_cb (parse->output_ctx, buf);
  }
  else
  {
    char *s = arg_eval (parse, &val);
    /* Determine if the node has been escaped by an explicit function. If not
     * call to escape. node->escape should contain the default escaping from
     * Config.VarEscapeMode and parse->escaping.current will have a non-zero
     * value if an explicit escape call was made sooooo.
     */
    if (s && parse->escaping.current == NEOS_ESCAPE_NONE) /* no explicit escape */
    {
      char *escaped = NULL;
      /* Use default escape if escape is UNDEF */
      if (node->escape == NEOS_ESCAPE_UNDEF)
        err = neos_var_escape(parse->escaping.when_undef, s, &escaped);
      else
        err = neos_var_escape(node->escape, s, &escaped);

      if (escaped)
      {
        err = parse->output_cb (parse->output_ctx, escaped);
        free(escaped);
      }
    }
    else if (s)
    { /* already explicitly escaped */
      err = parse->output_cb (parse->output_ctx, s);
    }
    /* Do we set it to blank if s == NULL? */
  }
  if (val.alloc) free(val.s);

  *next = node->next;
  return nerr_pass(err);
}

static NEOERR *lvar_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CSARG val;

  err = eval_expr(parse, &(node->arg1), &val);
  if (err) return nerr_pass(err);
  if (val.op_type & (CS_TYPE_NUM | CS_TYPE_VAR_NUM))
  {
    char buf[256];
    long int n_val;

    n_val = arg_eval_num (parse, &val);
    snprintf (buf, sizeof(buf), "%ld", n_val);
    err = parse->output_cb (parse->output_ctx, buf);
  }
  else
  {
    char *s = arg_eval (parse, &val);

    if (s)
    {
      CSPARSE *cs = NULL;

      /* Ok, we need our own copy of the string to pass to
       * cs_parse_string... */
      if (val.alloc && (val.op_type & CS_TYPE_STRING)) {
	val.alloc = 0;
      }
      else
      {
	s = strdup(s);
	if (s == NULL)
	{
	  return nerr_raise(NERR_NOMEM, "Unable to allocate memory for lvar_eval");
	}
      }

      do {
	err = cs_init_internal(&cs, parse->hdf, parse);
	if (err) break;
	err = cs_parse_string(cs, s, strlen(s));
	if (err) break;
	err = cs_render(cs, parse->output_ctx, parse->output_cb);
	if (err) break;
      } while (0);
      cs_destroy(&cs);
    }
  }
  if (val.alloc) free(val.s);

  *next = node->next;
  return nerr_pass(err);
}

static NEOERR *linclude_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CSARG val;

  err = eval_expr(parse, &(node->arg1), &val);
  if (err) return nerr_pass(err);
  if (val.op_type & (CS_TYPE_NUM | CS_TYPE_VAR_NUM))
  {
    char buf[256];
    long int n_val;

    n_val = arg_eval_num (parse, &val);
    snprintf (buf, sizeof(buf), "%ld", n_val);
    err = parse->output_cb (parse->output_ctx, buf);
  }
  else
  {
    char *s = arg_eval (parse, &val);

    if (s)
    {
      CSPARSE *cs = NULL;
      do {
	err = cs_init_internal(&cs, parse->hdf, parse);
	if (err) break;
	err = cs_parse_file(cs, s);
	if (!(node->flags & CSF_REQUIRED))
	{
	  nerr_handle(&err, NERR_NOT_FOUND);
	}
	if (err) break;
	err = cs_render(cs, parse->output_ctx, parse->output_cb);
	if (err) break;
      } while (0);
      cs_destroy(&cs);
    }
  }
  if (val.alloc) free(val.s);

  *next = node->next;
  return nerr_pass(err);
}

/* if the expr evaluates to true, display it, else render the alternate */
static NEOERR *alt_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CSARG val;
  int eval_true = 1;

  err = eval_expr(parse, &(node->arg1), &val);
  if (err) return nerr_pass(err);
  eval_true = arg_eval_bool(parse, &val);
  if (eval_true)
  {
    if (val.op_type & (CS_TYPE_NUM | CS_TYPE_VAR_NUM))
    {
      char buf[256];
      long int n_val;

      n_val = arg_eval_num (parse, &val);
      snprintf (buf, sizeof(buf), "%ld", n_val);
      err = parse->output_cb (parse->output_ctx, buf);
    }
    else
    {
      char *s = arg_eval (parse, &val);
      /* Do we set it to blank if s == NULL? */
      if (s)
      {
	err = parse->output_cb (parse->output_ctx, s);
      }
    }
  }
  if (val.alloc) free(val.s);

  if (eval_true == 0)
  {
    err = render_node (parse, node->case_0);
  }

  *next = node->next;
  return nerr_pass(err);
}

/* just calls through to the child nodes */
static NEOERR *escape_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  /* TODO(wad): Should I set a eval-time value here? */
  err = render_node (parse, node->case_0);
  *next = node->next;
  return nerr_pass(err);
}


static NEOERR *if_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  int eval_true = 0;
  CSARG val;

  err = eval_expr(parse, &(node->arg1), &val);
  if (err) return nerr_pass (err);
  eval_true = arg_eval_bool(parse, &val);
  if (val.alloc) free(val.s);

  if (eval_true)
  {
    err = render_node (parse, node->case_0);
  }
  else if (node->case_1 != NULL)
  {
    err = render_node (parse, node->case_1);
  }
  *next = node->next;
  return nerr_pass (err);
}

static NEOERR *else_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  STACK_ENTRY *entry;

  /* ne_warn ("else"); */
  err = uListGet (parse->stack, -1, (void *)&entry);
  if (err != STATUS_OK) return nerr_pass(err);

  parse->next = &(entry->tree->case_1);
  parse->current = entry->tree;
  return STATUS_OK;
}

static NEOERR *elif_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  STACK_ENTRY *entry;

  /* ne_warn ("elif: %s", arg); */
  err = uListGet (parse->stack, -1, (void *)&entry);
  if (err != STATUS_OK) return nerr_pass(err);

  if (entry->next_tree == NULL)
    entry->next_tree = entry->tree;

  parse->next = &(entry->tree->case_1);

  err = if_parse(parse, cmd, arg);
  entry->tree = parse->current;
  return nerr_pass(err);
}

static NEOERR *endif_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  STACK_ENTRY *entry;

  /* ne_warn ("endif"); */
  err = uListGet (parse->stack, -1, (void *)&entry);
  if (err != STATUS_OK) return nerr_pass(err);

  if (entry->next_tree)
    parse->next = &(entry->next_tree->next);
  else
    parse->next = &(entry->tree->next);
  parse->current = entry->tree;
  return STATUS_OK;
}

static NEOERR *each_with_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  char *lvar;
  char *p;
  char tmp[256];

  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;

  p = lvar = neos_strip(arg);
  while (*p && !isspace(*p) && *p != '=') p++;
  if (*p == '\0')
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Improperly formatted %s directive: %s",
	find_context(parse, -1, tmp, sizeof(tmp)), Commands[cmd].cmd, arg);
  }
  if (*p != '=')
  {
    *p++ = '\0';
    while (*p && *p != '=') p++;
    if (*p == '\0')
    {
      dealloc_node(&node);
      return nerr_raise (NERR_PARSE,
	  "%s Improperly formatted %s directive: %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), Commands[cmd].cmd, arg);
    }
    p++;
  }
  else
  {
    *p++ = '\0';
  }
  while (*p && isspace(*p)) p++;
  if (*p == '\0')
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Improperly formatted %s directive: %s",
	find_context(parse, -1, tmp, sizeof(tmp)), Commands[cmd].cmd, arg);
  }
  node->arg1.op_type = CS_TYPE_VAR;
  node->arg1.s = lvar;

  err = parse_expr(parse, p, 0, &(node->arg2));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }
  /* ne_warn ("each %s %s", lvar, p); */

  *(parse->next) = node;
  parse->next = &(node->case_0);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *each_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CS_LOCAL_MAP each_map;
  CSARG val;
  HDF *var, *child;

  memset(&each_map, 0, sizeof(each_map));

  err = eval_expr(parse, &(node->arg2), &val);
  if (err) return nerr_pass(err);

  if (val.op_type == CS_TYPE_VAR)
  {
    var = var_lookup_obj (parse, val.s);

    if (var != NULL)
    {
      /* Init and install local map */
      each_map.type = CS_TYPE_VAR;
      each_map.name = node->arg1.s;
      each_map.next = parse->locals;
      each_map.first = 1;
      each_map.last = 0;
      parse->locals = &each_map;

      do
      {
	child = hdf_obj_child (var);
	while (child != NULL)
	{
          /* We don't explicitly set each_map.last here since checking
           * requires a function call, so we move the check to _builtin_last
           * so it only makes the call if last() is being used */
	  each_map.h = child;
	  err = render_node (parse, node->case_0);
          if (each_map.map_alloc) {
            free(each_map.s);
            each_map.s = NULL;
          }
          if (each_map.first) each_map.first = 0;
	  if (err != STATUS_OK) break;
	  child = hdf_obj_next (child);
	}

      } while (0);

      /* Remove local map */
      parse->locals = each_map.next;
    }
  } /* else WARNING */
  if (val.alloc) free(val.s);

  *next = node->next;
  return nerr_pass (err);
}

static NEOERR *with_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CS_LOCAL_MAP with_map;
  CSARG val;
  HDF *var;

  memset(&with_map, 0, sizeof(with_map));

  err = eval_expr(parse, &(node->arg2), &val);
  if (err) return nerr_pass(err);

  if (val.op_type == CS_TYPE_VAR)
  {
    var = var_lookup_obj (parse, val.s);

    if (var != NULL)
    {
      /* Init and install local map */
      with_map.type = CS_TYPE_VAR;
      with_map.name = node->arg1.s;
      with_map.next = parse->locals;
      with_map.h = var;
      parse->locals = &with_map;
      err = render_node (parse, node->case_0);
      /* Remove local map */
      if (with_map.map_alloc) free(with_map.s);
      parse->locals = with_map.next;
    }
  }
  else
  {
    /* else WARNING */
    ne_warn("Invalid op_type for with: %s", expand_token_type(val.op_type, 1));
  }
  if (val.alloc) free(val.s);

  *next = node->next;
  return nerr_pass (err);
}
static NEOERR *end_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  STACK_ENTRY *entry;

  err = uListGet (parse->stack, -1, (void *)&entry);
  if (err != STATUS_OK) return nerr_pass(err);

  parse->next = &(entry->tree->next);
  parse->current = entry->tree;
  return STATUS_OK;
}

static NEOERR *include_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  char *s;
  int flags = 0;
  CSARG arg1, val;

  memset(&arg1, 0, sizeof(CSARG));
  if (arg[0] == '!')
    flags |= CSF_REQUIRED;
  arg++;
  /* Validate arg is a var (regex /^[#" ]$/) */
  err = parse_expr (parse, arg, 0, &arg1);
  if (err) return nerr_pass(err);
  /* ne_warn ("include: %s", a); */

  err = eval_expr(parse, &arg1, &val);
  if (err) return nerr_pass(err);

  s = arg_eval (parse, &val);
  if (s == NULL && !(flags & CSF_REQUIRED))
    return STATUS_OK;
  err = cs_parse_file(parse, s);
  if (!(flags & CSF_REQUIRED))
  {
    nerr_handle(&err, NERR_NOT_FOUND);
  }
  if (val.alloc) free(val.s);

  return nerr_pass (err);
}

static NEOERR *def_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  CS_MACRO *macro;
  CSARG *carg, *larg = NULL;
  char *a = NULL, *p = NULL, *s;
  char tmp[256];
  char name[256];
  int x = 0;
  BOOL last = FALSE;

  /* Since def doesn't get a new stack entry until after this is run,
   * setup a dumb var on the parse object to hold the future setting.
   */
  parse->escaping.next_stack = NEOS_ESCAPE_UNDEF;

  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  arg++;
  s = arg;
  while (*s && *s != ' ' && *s != '#' && *s != '(')
  {
    name[x++] = *s;
    s++;
  }
  name[x] = '\0';
  while (*s && isspace(*s)) s++;
  if (*s == '\0' || *s != '(')
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Missing left paren in macro def %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }
  s++;
  /* Check to see if this is a redefinition */
  macro = parse->macros;
  while (macro != NULL)
  {
    if (!strcmp(macro->name, name))
    {
      dealloc_node(&node);
      return nerr_raise (NERR_PARSE,
	  "%s Duplicate macro def for %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), arg);
    }
    macro = macro->next;
  }

  macro = (CS_MACRO *) calloc (1, sizeof (CS_MACRO));
  if (macro) macro->name = strdup(name);
  if (macro == NULL || macro->name == NULL)
  {
    dealloc_node(&node);
    dealloc_macro(&macro);
    return nerr_raise (NERR_NOMEM,
	"%s Unable to allocate memory for CS_MACRO in def %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }

  while (*s)
  {
    while (*s && isspace(*s)) s++;
    a = strpbrk(s, ",)");
    if (a == NULL)
    {
      err = nerr_raise (NERR_PARSE,
	  "%s Missing right paren in def %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), arg);
      break;
    }
    if (*a == ')') last = TRUE;
    *a = '\0';
    /* cut out ending whitespace */
    p = strpbrk(s, " \t\r\n");
    if (p != NULL) *p = '\0';
    p = strpbrk(s, "\"?<>=!#-+|&,)*/%[]( \t\r\n");
    if (p != NULL)
    {
      err = nerr_raise (NERR_PARSE,
	  "%s Invalid character in def %s argument: %c",
	  find_context(parse, -1, tmp, sizeof(tmp)), arg, *p);
      break;
    }
    /* No argument case */
    if (*s == '\0' && macro->n_args == 0) break;
    if (*s == '\0')
    {
      err = nerr_raise (NERR_PARSE,
	  "%s Missing argument name or extra comma in def %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), arg);
      break;
    }
    carg = (CSARG *) calloc (1, sizeof(CSARG));
    if (carg == NULL)
    {
      err = nerr_raise (NERR_NOMEM,
	  "%s Unable to allocate memory for CSARG in def %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), arg);
      break;
    }
    if (larg == NULL)
    {
      macro->args = carg;
      larg = carg;
    }
    else
    {
      larg->next = carg;
      larg = carg;
    }
    macro->n_args++;
    carg->s = s;
    if (last == TRUE) break;
    s = a+1;
  }
  if (err)
  {
    dealloc_node(&node);
    dealloc_macro(&macro);
    return nerr_pass(err);
  }

  macro->tree = node;
  if (parse->macros)
  {
    macro->next = parse->macros;
  }
  parse->macros = macro;

  *(parse->next) = node;
  parse->next = &(node->case_0);
  parse->current = node;

  return STATUS_OK;
}

static int rearrange_for_call(CSARG **args)
{
  CSARG *larg = NULL;
  CSARG *carg = *args;
  CSARG *vargs = NULL;
  int nargs = 0;

  /* multiple argument case, we have to walk the args and reverse
   * them. Also handles single arg case since its the same as the
   * last arg */
  while (carg)
  {
    nargs++;
    if (carg->op_type != CS_OP_COMMA)
    {
      /* last argument */
      if (vargs)
	carg->next = vargs;
      vargs = carg;
      break;
    }
    if (vargs)
      carg->expr1->next = vargs;
    vargs = carg->expr1;
    larg = carg;
    carg = carg->next;
    /* dealloc comma, but not its descendents */
    larg->next = NULL;
    larg->expr1 = NULL;
    dealloc_arg(&larg);
  }
  *args = vargs;

  return nargs;
}

static NEOERR *call_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  CS_MACRO *macro;
  CSARG *carg;
  char *s, *a = NULL;
  char tmp[256];
  char name[256];
  int x = 0;
  int nargs = 0;
  STACK_ENTRY *entry;

  err = uListGet (parse->stack, -1, (void *)&entry);
  if (err != STATUS_OK) return nerr_pass(err);

  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  node->escape = entry->escape;
  arg++;
  s = arg;
  while (x < sizeof(name) && *s && *s != ' ' && *s != '#' && *s != '(')
  {
    name[x++] = *s;
    s++;
  }
  name[x] = '\0';
  while (*s && isspace(*s)) s++;
  if (*s == '\0' || *s != '(')
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Missing left paren in call %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }
  s++;
  /* Check to see if this macro exists */
  macro = parse->macros;
  while (macro != NULL)
  {
    if (!strcmp(macro->name, name)) break;
    macro = macro->next;
  }
  if (macro == NULL)
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Undefined macro called: %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }
  node->arg1.op_type = CS_TYPE_MACRO;
  node->arg1.macro = macro;

  a = strrchr(s, ')');
  if (a == NULL)
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Missing right paren in call %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }
  *a = '\0';

  while (*s && isspace(*s)) s++;
  /* No arguments case */
  if (*s == '\0')
  {
    nargs = 0;
  }
  else
  {
    /* Parse arguments case */
    do
    {
      carg = (CSARG *) calloc (1, sizeof(CSARG));
      if (carg == NULL)
      {
	err = nerr_raise (NERR_NOMEM,
	    "%s Unable to allocate memory for CSARG in call %s",
	    find_context(parse, -1, tmp, sizeof(tmp)), arg);
	break;
      }
      err = parse_expr (parse, s, 0, carg);
      if (err) break;
      nargs = rearrange_for_call(&carg);
      node->vargs = carg;
    } while (0);
  }
  if (!err && nargs != macro->n_args)
  {
    err = nerr_raise (NERR_PARSE,
	"%s Incorrect number of arguments, expected %d, got %d in call to macro %s: %s",
	find_context(parse, -1, tmp, sizeof(tmp)), macro->n_args, nargs,
	macro->name, arg);
  }
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *call_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CS_LOCAL_MAP *call_map, *map;
  CS_MACRO *macro;
  CSARG *carg, *darg;
  HDF *var;
  int x;

  /* Reset the value of when_undef for the coming call evaluation.
   * This is only used here so it there's no need to reset its value after
   * the call. If this call is nested (escape == NEOS_ESCAPE_UNDEF), then
   * leave the when_undef variable alone. The parent call_eval should have
   * already defined it.
   */
  if (node->escape != NEOS_ESCAPE_UNDEF)
    parse->escaping.when_undef = node->escape;

  macro = node->arg1.macro;
  if (macro->n_args)
  {
    call_map = (CS_LOCAL_MAP *) calloc (macro->n_args, sizeof(CS_LOCAL_MAP));
    if (call_map == NULL)
      return nerr_raise (NERR_NOMEM,
                "Unable to allocate memory for call_map in call_eval of %s",
                         macro->name);
  }
  else
  {
    call_map = NULL;
  }

  darg = macro->args;
  carg = node->vargs;

  for (x = 0; x < macro->n_args; x++)
  {
    CSARG val;
    map = &call_map[x];
    if (x) call_map[x-1].next = map;

    map->name = darg->s;
    err = eval_expr(parse, carg, &val);
    if (err) break;
    if (val.op_type & CS_TYPE_STRING)
    {
      map->s = val.s;
      map->type = val.op_type;
      map->map_alloc = val.alloc;
      val.alloc = 0;
    }
    else if (val.op_type & CS_TYPE_NUM)
    {
      map->n = val.n;
      map->type = CS_TYPE_NUM;
    }
    else if (val.op_type & (CS_TYPE_VAR | CS_TYPE_VAR_NUM))
    {
      CS_LOCAL_MAP *lmap;
      char *c;
      lmap = lookup_map (parse, val.s, &c);
      if (lmap != NULL && (lmap->type != CS_TYPE_VAR && lmap->type != CS_TYPE_VAR_NUM))
      {
	/* if we're referencing a local var which maps to a string or
	 * number... then copy  */
	if (lmap->type == CS_TYPE_NUM)
	{
	  map->n = lmap->n;
	  map->type = lmap->type;
	}
	else
	{
	  map->s = lmap->s;
	  map->type = lmap->type;
	}
      }
      else
      {
	var = var_lookup_obj (parse, val.s);
	map->h = var;
        map->type = CS_TYPE_VAR;
        /* Bring across the name we're mapping to, in case h doesn't exist and
         * we need to set it. */
        map->s = val.s;
        map->map_alloc = val.alloc;
        val.alloc = 0;
      }
    }
    else
    {
      ne_warn("Unsupported type %s in call_expr", expand_token_type(val.op_type, 1));
    }
    if (val.alloc) free(val.s);
    map->next = parse->locals;

    darg = darg->next;
    carg = carg->next;
  }

  if (err == STATUS_OK)
  {
    map = parse->locals;
    if (macro->n_args) parse->locals = call_map;
    err = render_node (parse, macro->tree->case_0);
    parse->locals = map;
  }
  for (x = 0; x < macro->n_args; x++)
  {
    if (call_map[x].map_alloc) free(call_map[x].s);
  }
  if (call_map) free (call_map);

  *next = node->next;
  return nerr_pass(err);
}

static NEOERR *set_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  char *s;
  char tmp[256];

  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  arg++;
  s = arg;
  while (*s && *s != '=') s++;
  if (*s == '\0')
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Missing equals in set %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }
  *s = '\0';
  s++;
  err = parse_expr(parse, arg, 1, &(node->arg1));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  err = parse_expr(parse, s, 0, &(node->arg2));
  if (err)
  {
    dealloc_node(&node);
    return nerr_pass(err);
  }

  *(parse->next) = node;
  parse->next = &(node->next);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *set_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CSARG val;
  CSARG set;

  err = eval_expr(parse, &(node->arg1), &set);
  if (err) return nerr_pass (err);
  err = eval_expr(parse, &(node->arg2), &val);
  if (err) {
    if (set.alloc) free(set.s);
    return nerr_pass (err);
  }

  if (set.op_type != CS_TYPE_NUM)
  {
    /* this allow for a weirdness where set:"foo"="bar"
     * actually sets the hdf var foo... */
    if (val.op_type & (CS_TYPE_NUM | CS_TYPE_VAR_NUM))
    {
      char buf[256];
      long int n_val;

      n_val = arg_eval_num (parse, &val);
      snprintf (buf, sizeof(buf), "%ld", n_val);
      if (set.s)
      {
	err = var_set_value (parse, set.s, buf);
      }
      else
      {
	err = nerr_raise(NERR_ASSERT,
	    "lvalue is NULL/empty in attempt to evaluate set to '%s'", buf);
      }
    }
    else
    {
      char *s = arg_eval (parse, &val);
      /* Do we set it to blank if s == NULL? */
      if (set.s)
      {
	err = var_set_value (parse, set.s, s);
      }
      else
      {
	err = nerr_raise(NERR_ASSERT,
	    "lvalue is NULL/empty in attempt to evaluate set to '%s'",
	    (s) ? s : "");
      }
    }
  } /* else WARNING */
  if (set.alloc) free(set.s);
  if (val.alloc) free(val.s);

  *next = node->next;
  return nerr_pass (err);
}

static NEOERR *loop_parse (CSPARSE *parse, int cmd, char *arg)
{
  NEOERR *err;
  CSTREE *node;
  CSARG *carg, *larg = NULL;
  BOOL last = FALSE;
  char *lvar;
  char *p, *a;
  char tmp[256];
  int x;

  err = alloc_node (&node);
  if (err) return nerr_pass(err);
  node->cmd = cmd;
  if (arg[0] == '!')
    node->flags |= CSF_REQUIRED;
  arg++;

  p = lvar = neos_strip(arg);
  while (*p && !isspace(*p) && *p != '=') p++;
  if (*p == '\0')
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Improperly formatted loop directive: %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }
  if (*p != '=')
  {
    *p++ = '\0';
    while (*p && *p != '=') p++;
    if (*p == '\0')
    {
      dealloc_node(&node);
      return nerr_raise (NERR_PARSE,
	  "%s Improperly formatted loop directive: %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), arg);
    }
    p++;
  }
  else
  {
    *p++ = '\0';
  }
  while (*p && isspace(*p)) p++;
  if (*p == '\0')
  {
    dealloc_node(&node);
    return nerr_raise (NERR_PARSE,
	"%s Improperly formatted loop directive: %s",
	find_context(parse, -1, tmp, sizeof(tmp)), arg);
  }
  node->arg1.op_type = CS_TYPE_VAR;
  node->arg1.s = lvar;

  x = 0;
  while (*p)
  {
    carg = (CSARG *) calloc (1, sizeof(CSARG));
    if (carg == NULL)
    {
      err = nerr_raise (NERR_NOMEM,
	  "%s Unable to allocate memory for CSARG in loop %s",
	  find_context(parse, -1, tmp, sizeof(tmp)), arg);
      break;
    }
    if (larg == NULL)
    {
      node->vargs = carg;
      larg = carg;
    }
    else
    {
      larg->next = carg;
      larg = carg;
    }
    x++;
    a = strpbrk(p, ",");
    if (a == NULL) last = TRUE;
    else *a = '\0';
    err = parse_expr (parse, p, 0, carg);
    if (err) break;
    if (last == TRUE) break;
    p = a+1;
  }
  if (!err && ((x < 1) || (x > 3)))
  {
    err = nerr_raise (NERR_PARSE,
	"%s Incorrect number of arguments, expected 1, 2, or 3 got %d in loop: %s",
	find_context(parse, -1, tmp, sizeof(tmp)), x, arg);
  }

  /* ne_warn ("loop %s %s", lvar, p); */

  *(parse->next) = node;
  parse->next = &(node->case_0);
  parse->current = node;

  return STATUS_OK;
}

static NEOERR *loop_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  NEOERR *err = STATUS_OK;
  CS_LOCAL_MAP each_map;
  int var;
  int start = 0, end = 0, step = 1;
  int x, iter = 1;
  CSARG *carg;
  CSARG val;

  memset(&each_map, 0, sizeof(each_map));

  carg = node->vargs;
  if (carg == NULL) return nerr_raise (NERR_ASSERT, "No arguments in loop eval?");
  err = eval_expr(parse, carg, &val);
  if (err) return nerr_pass(err);
  end = arg_eval_num(parse, &val);
  if (val.alloc) free(val.s);
  if (carg->next)
  {
    start = end;
    carg = carg->next;
    err = eval_expr(parse, carg, &val);
    if (err) return nerr_pass(err);
    end = arg_eval_num(parse, &val);
    if (val.alloc) free(val.s);
    if (carg->next)
    {
      carg = carg->next;
      err = eval_expr(parse, carg, &val);
      if (err) return nerr_pass(err);
      step = arg_eval_num(parse, &val);
      if (val.alloc) free(val.s);
    }
  }
  if (((step < 0) && (start < end)) ||
      ((step > 0) && (end < start)))
  {
    iter = 0;
  }
  else if (step == 0)
  {
    iter = 0;
  }
  else
  {
    iter = abs((end - start) / step + 1);
  }

  if (iter > 0)
  {
    /* Init and install local map */
    each_map.type = CS_TYPE_NUM;
    each_map.name = node->arg1.s;
    each_map.next = parse->locals;
    each_map.first = 1;
    parse->locals = &each_map;

    var = start;
    for (x = 0, var = start; x < iter; x++, var += step)
    {
      if (x == iter - 1) each_map.last = 1;
      each_map.n = var;
      err = render_node (parse, node->case_0);
      if (each_map.map_alloc) {
        free(each_map.s);
        each_map.s = NULL;
      }
      if (each_map.first) each_map.first = 0;
      if (err != STATUS_OK) break;
    }

    /* Remove local map */
    parse->locals = each_map.next;
  }

  *next = node->next;
  return nerr_pass (err);
}

static NEOERR *skip_eval (CSPARSE *parse, CSTREE *node, CSTREE **next)
{
  *next = node->next;
  return STATUS_OK;
}
static NEOERR *render_node (CSPARSE *parse, CSTREE *node)
{
  NEOERR *err = STATUS_OK;

  while (node != NULL)
  {
    /* ne_warn ("%s %08x", Commands[node->cmd].cmd, node); */
    err = (*(Commands[node->cmd].eval_handler))(parse, node, &node);
    if (err) break;
  }
  return nerr_pass(err);
}

NEOERR *cs_render (CSPARSE *parse, void *ctx, CSOUTFUNC cb)
{
  CSTREE *node;

  if (parse->tree == NULL)
    return nerr_raise (NERR_ASSERT, "No parse tree exists");

  parse->output_ctx = ctx;
  parse->output_cb = cb;

  node = parse->tree;
  return nerr_pass (render_node(parse, node));
}

/* **** Functions ******************************************** */

NEOERR *cs_register_function(CSPARSE *parse, const char *funcname,
                                  int n_args, CSFUNCTION function)
{
  CS_FUNCTION *csf;

  /* Should we validate the parseability of the name? */

  csf = parse->functions;
  while (csf != NULL)
  {
    if (!strcmp(csf->name, funcname) && csf->function != function)
    {
      return nerr_raise(NERR_DUPLICATE,
	  "Attempt to register duplicate function %s", funcname);
    }
    csf = csf->next;
  }
  csf = (CS_FUNCTION *) calloc (1, sizeof(CS_FUNCTION));
  if (csf == NULL)
    return nerr_raise(NERR_NOMEM,
	"Unable to allocate memory to register function %s", funcname);
  csf->name = strdup(funcname);
  if (csf->name == NULL)
  {
    free(csf);
    return nerr_raise(NERR_NOMEM,
	"Unable to allocate memory to register function %s", funcname);
  }
  csf->function = function;
  csf->n_args = n_args;
  csf->escape = NEOS_ESCAPE_NONE;
  csf->next = parse->functions;
  parse->functions = csf;

  return STATUS_OK;
}

/* This is similar to python's PyArg_ParseTuple, :
 *   s - string (allocated)
 *   i - int
 *   A - arg ptr (maybe later)
 */
NEOERR * cs_arg_parsev(CSPARSE *parse, CSARG *args, const char *fmt,
                       va_list ap)
{
  NEOERR *err = STATUS_OK;
  char **s;
  long int *i;
  CSARG val;

  while (*fmt)
  {
    memset(&val, 0, sizeof(val));
    err = eval_expr(parse, args, &val);
    if (err) return nerr_pass(err);

    switch (*fmt)
    {
      case 's':
	s = va_arg(ap, char **);
	if (s == NULL)
	{
	  err = nerr_raise(NERR_ASSERT,
	      "Invalid number of arguments in call to cs_arg_parse");
	  break;
	}
	*s = arg_eval_str_alloc(parse, &val);
	break;
      case 'i':
	i = va_arg(ap, long int *);
	if (i == NULL)
	{
	  err = nerr_raise(NERR_ASSERT,
	      "Invalid number of arguments in call to cs_arg_parse");
	  break;
	}
	*i = arg_eval_num(parse, &val);
	break;
      default:
	break;
    }
    if (err) return nerr_pass(err);
    fmt++;
    args = args->next;
    if (val.alloc) free(val.s);
  }
  if (err) return nerr_pass(err);
  return STATUS_OK;
}

NEOERR * cs_arg_parse(CSPARSE *parse, CSARG *args, const char *fmt, ...)
{
  NEOERR *err;
  va_list ap;

  va_start(ap, fmt);
  err = cs_arg_parsev(parse, args, fmt, ap);
  va_end(ap);
  return nerr_pass(err);
}

static NEOERR * _builtin_subcount(CSPARSE *parse, CS_FUNCTION *csf, CSARG *args, CSARG *result)
{
  NEOERR *err;
  HDF *obj;
  int count = 0;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  /* default for non-vars is 0 children */
  result->op_type = CS_TYPE_NUM;
  result->n = 0;

  if (val.op_type & CS_TYPE_VAR)
  {
    obj = var_lookup_obj (parse, val.s);
    if (obj != NULL)
    {
      obj = hdf_obj_child(obj);
      while (obj != NULL)
      {
	count++;
	obj = hdf_obj_next(obj);
      }
    }
    result->n = count;
  }
  if (val.alloc) free(val.s);

  return STATUS_OK;
}

static NEOERR * _builtin_str_length(CSPARSE *parse, CS_FUNCTION *csf, CSARG *args, CSARG *result)
{
  NEOERR *err;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  /* non var/string objects have 0 length */
  result->op_type = CS_TYPE_NUM;
  result->n = 0;

  if (val.op_type & (CS_TYPE_VAR | CS_TYPE_STRING))
  {
    char *s = arg_eval(parse, &val);
    if (s) result->n = strlen(s);
  }
  if (val.alloc) free(val.s);
  return STATUS_OK;
}


static NEOERR * _builtin_str_find(CSPARSE *parse, CS_FUNCTION *csf, CSARG *args, CSARG *result)
{
  NEOERR *err;
  char *s = NULL;
  char *substr = NULL;
  char *pstr = NULL;

  result->op_type = CS_TYPE_NUM;
  result->n = -1;

  err = cs_arg_parse(parse, args, "ss", &s, &substr);
  if (err) return nerr_pass(err);
  /* If null arguments, return -1 index */
  if (s == NULL || substr == NULL) {
    if (s) free(s);
    if (substr) free(substr);
    return STATUS_OK;
  }
  pstr = strstr(s, substr);
  if (pstr != NULL) {
    result->n = (pstr - s) / sizeof(char);
  }
  free(s);
  free(substr);
  return STATUS_OK;
}


static NEOERR * _builtin_name(CSPARSE *parse, CS_FUNCTION *csf, CSARG *args, CSARG *result)
{
  NEOERR *err;
  HDF *obj;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  result->op_type = CS_TYPE_STRING;
  result->s = "";

  if (val.op_type & CS_TYPE_VAR)
  {
    obj = var_lookup_obj (parse, val.s);
    if (obj != NULL)
      result->s = hdf_obj_name(obj);
  }
  else if (val.op_type & CS_TYPE_STRING)
  {
    result->s = val.s;
    result->alloc = val.alloc;
    val.alloc = 0;
  }
  if (val.alloc) free(val.s);
  return STATUS_OK;
}

/* Check to see if a local variable is the first in an each/loop sequence */
static NEOERR * _builtin_first(CSPARSE *parse, CS_FUNCTION *csf, CSARG *args,
                               CSARG *result)
{
  NEOERR *err;
  CS_LOCAL_MAP *map;
  char *c;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  /* default is "not first" */
  result->op_type = CS_TYPE_NUM;
  result->n = 0;

  /* Only applies to possible local vars */
  if ((val.op_type & CS_TYPE_VAR) && !strchr(val.s, '.'))
  {
    map = lookup_map (parse, val.s, &c);
    if (map && map->first)
      result->n = 1;
  }
  if (val.alloc) free(val.s);
  return STATUS_OK;
}

/* Check to see if a local variable is the last in an each/loop sequence */
/* TODO: consider making this work on regular HDF vars */
static NEOERR * _builtin_last(CSPARSE *parse, CS_FUNCTION *csf, CSARG *args,
                               CSARG *result)
{
  NEOERR *err;
  CS_LOCAL_MAP *map;
  char *c;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  /* default is "not last" */
  result->op_type = CS_TYPE_NUM;
  result->n = 0;

  /* Only applies to possible local vars */
  if ((val.op_type & CS_TYPE_VAR) && !strchr(val.s, '.'))
  {
    map = lookup_map (parse, val.s, &c);
    if (map) {
      if (map->last) {
        result->n = 1;
      } else if (map->type == CS_TYPE_VAR) {
        if (hdf_obj_next(map->h) == NULL) {
          result->n = 1;
        }
      }
    }
  }
  if (val.alloc) free(val.s);
  return STATUS_OK;
}

/* returns the absolute value (ie, positive) of a number */
static NEOERR * _builtin_abs (CSPARSE *parse, CS_FUNCTION *csf, CSARG *args,
                              CSARG *result)
{
  NEOERR *err;
  int n1 = 0;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  result->op_type = CS_TYPE_NUM;
  n1 = arg_eval_num(parse, &val);
  result->n = abs(n1);

  if (val.alloc) free(val.s);
  return STATUS_OK;
}

/* returns the larger or two integers */
static NEOERR * _builtin_max (CSPARSE *parse, CS_FUNCTION *csf, CSARG *args,
                              CSARG *result)
{
  NEOERR *err;
  long int n1 = 0;
  long int n2 = 0;

  result->op_type = CS_TYPE_NUM;
  result->n = 0;

  err = cs_arg_parse(parse, args, "ii", &n1, &n2);
  if (err) return nerr_pass(err);
  result->n = (n1 > n2) ? n1 : n2;

  return STATUS_OK;
}

/* returns the smaller or two integers */
static NEOERR * _builtin_min (CSPARSE *parse, CS_FUNCTION *csf, CSARG *args,
                              CSARG *result)
{
  NEOERR *err;
  long int n1 = 0;
  long int n2 = 0;

  result->op_type = CS_TYPE_NUM;
  result->n = 0;

  err = cs_arg_parse(parse, args, "ii", &n1, &n2);
  if (err) return nerr_pass(err);
  result->n = (n1 < n2) ? n1 : n2;

  return STATUS_OK;
}

static NEOERR * _builtin_str_slice (CSPARSE *parse, CS_FUNCTION *csf, CSARG *args, CSARG *result)
{
  NEOERR *err;
  char *s = NULL;
  char *slice;
  long int b = 0;
  long int e = 0;
  size_t len;

  result->op_type = CS_TYPE_STRING;
  result->s = "";

  err = cs_arg_parse(parse, args, "sii", &s, &b, &e);
  if (err) return nerr_pass(err);
  /* If null, return empty string */
  if (s == NULL) return STATUS_OK;
  len = strlen(s);
  if (b < 0 && e == 0) e = len;
  if (b < 0) b += len;
  if (e < 0) e += len;
  if (e > len) e = len;
  /* Its the whole string */
  if (b == 0 && e == len)
  {
    result->s = s;
    result->alloc = 1;
    return STATUS_OK;
  }
  if (e < b) b = e;
  if (b == e)
  {
    /* If null, return empty string */
    free(s);
    return STATUS_OK;
  }
  slice = (char *) malloc (sizeof(char) * (e-b+1));
  if (slice == NULL)
    return nerr_raise(NERR_NOMEM, "Unable to allocate memory for string slice");
  strncpy(slice, s + b, e-b);
  free(s);
  slice[e-b] = '\0';

  result->s = slice;
  result->alloc = 1;

  return STATUS_OK;
}

#ifdef ENABLE_GETTEXT
static NEOERR * _builtin_gettext(CSPARSE *parse, CS_FUNCTION *csf, CSARG *args, CSARG *result)
{
  NEOERR *err;
  char *s;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  result->op_type = CS_TYPE_STRING;
  result->s = "";

  if (val.op_type & (CS_TYPE_VAR | CS_TYPE_STRING))
  {
    s = arg_eval(parse, &val);
    if (s)
    {
      result->s = gettext(s);
    }
  }
  if (val.alloc) free(val.s);
  return STATUS_OK;
}
#endif

static NEOERR * _str_func_wrapper (CSPARSE *parse, CS_FUNCTION *csf, CSARG *args, CSARG *result)
{
  NEOERR *err;
  char *s;
  CSARG val;

  memset(&val, 0, sizeof(val));
  err = eval_expr(parse, args, &val);
  if (err) return nerr_pass(err);

  if (val.op_type & (CS_TYPE_VAR | CS_TYPE_STRING))
  {
    result->op_type = CS_TYPE_STRING;
    result->n = 0;

    s = arg_eval(parse, &val);
    if (s)
    {
      err = csf->str_func(s, &(result->s));
      if (err) return nerr_pass(err);
      result->alloc = 1;
    }
  }
  else
  {
    result->op_type = val.op_type;
    result->n = val.n;
    result->s = val.s;
    result->alloc = val.alloc;
    val.alloc = 0;
  }
  if (val.alloc) free(val.s);
  return STATUS_OK;
}

NEOERR *cs_register_strfunc(CSPARSE *parse, char *funcname, CSSTRFUNC str_func)
{
  NEOERR *err;

  err = cs_register_function(parse, funcname, 1, _str_func_wrapper);
  if (err) return nerr_pass(err);
  parse->functions->str_func = str_func;

  return STATUS_OK;
}

NEOERR *cs_register_esc_strfunc(CSPARSE *parse, char *funcname,
                                CSSTRFUNC str_func)
{
  NEOERR *err;

  err = cs_register_strfunc(parse, funcname, str_func);
  if (err) return nerr_pass(err);
  parse->functions->escape = NEOS_ESCAPE_FUNCTION;

  return STATUS_OK;
}

/* **** CS Initialize/Destroy ************************************ */
NEOERR *cs_init (CSPARSE **parse, HDF *hdf) {
  return nerr_pass(cs_init_internal(parse, hdf, NULL));
}

static NEOERR *cs_init_internal (CSPARSE **parse, HDF *hdf, CSPARSE *parent)
{
  NEOERR *err = STATUS_OK;
  CSPARSE *my_parse;
  STACK_ENTRY *entry;
  char *esc_value;
  CS_ESCAPE_MODES *esc_cursor;

  err = nerr_init();
  if (err != STATUS_OK) return nerr_pass (err);

  my_parse = (CSPARSE *) calloc (1, sizeof (CSPARSE));
  if (my_parse == NULL)
    return nerr_raise (NERR_NOMEM, "Unable to allocate memory for CSPARSE");

  err = uListInit (&(my_parse->stack), 10, 0);
  if (err != STATUS_OK)
  {
    free(my_parse);
    return nerr_pass(err);
  }
  err = uListInit (&(my_parse->alloc), 10, 0);
  if (err != STATUS_OK)
  {
    free(my_parse);
    return nerr_pass(err);
  }
  err = alloc_node (&(my_parse->tree));
  if (err != STATUS_OK)
  {
    cs_destroy (&my_parse);
    return nerr_pass(err);
  }
  my_parse->current = my_parse->tree;
  my_parse->next = &(my_parse->current->next);

  entry = (STACK_ENTRY *) calloc (1, sizeof (STACK_ENTRY));
  if (entry == NULL)
  {
    cs_destroy (&my_parse);
    return nerr_raise (NERR_NOMEM,
	"Unable to allocate memory for stack entry");
  }
  entry->state = ST_GLOBAL;
  entry->tree = my_parse->current;
  entry->location = 0;
  entry->escape = NEOS_ESCAPE_NONE;
  err = uListAppend(my_parse->stack, entry);
  if (err != STATUS_OK) {
    free (entry);
    cs_destroy(&my_parse);
    return nerr_pass(err);
  }
  my_parse->tag = hdf_get_value(hdf, "Config.TagStart", "cs");
  my_parse->taglen = strlen(my_parse->tag);
  my_parse->hdf = hdf;

  /* Let's set the default escape data */
  my_parse->escaping.global = NEOS_ESCAPE_NONE;
  my_parse->escaping.next_stack = NEOS_ESCAPE_NONE;
  my_parse->escaping.when_undef = NEOS_ESCAPE_NONE;

  /* See CS_ESCAPE_MODES. 0 is "none" */
  esc_value = hdf_get_value(hdf, "Config.VarEscapeMode", EscapeModes[0].mode);
  /* Let's ensure the specified escape mode is valid and proceed */
  for (esc_cursor = &EscapeModes[0];
       esc_cursor->mode != NULL;
       esc_cursor++)
    if (!strcmp(esc_value, esc_cursor->mode))
    {
      my_parse->escaping.global = esc_cursor->context;
      my_parse->escaping.next_stack = esc_cursor->context;
      entry->escape = esc_cursor->context;
      break;
    }
  /* Didn't find an acceptable value we were looking for */
  if (esc_cursor->mode == NULL) {
    cs_destroy (&my_parse);
    return nerr_raise (NERR_OUTOFRANGE,
      "Invalid HDF value for Config.VarEscapeMode (none,html,js,url): %s",
      esc_value);
  }

  if (parent == NULL)
  {
    static struct _builtin_functions {
      const char *name;
      int nargs;
      CSFUNCTION function;
    } Builtins[] = {
      { "len", 1, _builtin_subcount },
      { "subcount", 1, _builtin_subcount },
      { "name", 1, _builtin_name },
      { "first", 1, _builtin_first },
      { "last", 1, _builtin_last },
      { "abs", 1, _builtin_abs },
      { "max", 2, _builtin_max },
      { "min", 2, _builtin_min },
      { "string.find", 2, _builtin_str_find },
      { "string.slice", 3, _builtin_str_slice },
      { "string.length", 1, _builtin_str_length },
#ifdef ENABLE_GETTEXT
      { "_", 1, _builtin_gettext },
#endif
      { NULL, 0, NULL },
    };
    int x = 0;
    while (Builtins[x].name != NULL) {
      err = cs_register_function(my_parse, Builtins[x].name, Builtins[x].nargs,
                               Builtins[x].function);
      if (err)
      {
        cs_destroy(&my_parse);
        return nerr_pass(err);
      }
      x++;
    }
    /* Set global_hdf to be null */
    my_parse->global_hdf = NULL;
    my_parse->parent = NULL;
  }
  else
  {
    /* TODO: macros and functions should actually not be duplicated, they
     * should just be modified in lookup to walk the CS struct hierarchy we're
     * creating here */
    /* BUG: We currently can't copy the macros because they reference the parse
     * tree, so if this sub-parse tree adds a macro, the macro reference will
     * persist, but the parse tree it points to will be gone when the sub-parse
     * is gone. */
    my_parse->functions = parent->functions;
    my_parse->global_hdf = parent->global_hdf;
    my_parse->fileload = parent->fileload;
    my_parse->fileload_ctx = parent->fileload_ctx;
    my_parse->parent = parent;
  }

  *parse = my_parse;
  return STATUS_OK;
}

void cs_register_fileload(CSPARSE *parse, void *ctx, CSFILELOAD fileload) {
  if (parse != NULL) {
    parse->fileload_ctx = ctx;
    parse->fileload = fileload;
  }
}

void cs_destroy (CSPARSE **parse)
{
  CSPARSE *my_parse = *parse;

  if (my_parse == NULL)
    return;

  uListDestroy (&(my_parse->stack), ULIST_FREE);
  uListDestroy (&(my_parse->alloc), ULIST_FREE);

  dealloc_macro(&my_parse->macros);
  dealloc_node(&(my_parse->tree));
  if (my_parse->parent == NULL) {
    dealloc_function(&(my_parse->functions));
  }

  free(my_parse);
  *parse = NULL;
}

/* **** CS Debug Dumps ******************************************** */

static NEOERR *dump_node (CSPARSE *parse, CSTREE *node, int depth, void *ctx,
    CSOUTFUNC cb, char *buf, int blen)
{
  NEOERR *err;

  while (node != NULL)
  {
    snprintf (buf, blen, "%*s %s ", depth, "", Commands[node->cmd].cmd);
    err = cb (ctx, buf);
    if (err) return nerr_pass (err);
    if (node->cmd)
    {
      if (node->arg1.op_type)
      {
	if (node->arg1.op_type == CS_TYPE_NUM)
	{
	  snprintf (buf, blen, "%ld ", node->arg1.n);
	}
	else if (node->arg1.op_type == CS_TYPE_MACRO)
	{
	  snprintf (buf, blen, "%s ", node->arg1.macro->name);
	}
	else
	{
	  snprintf (buf, blen, "%s ", node->arg1.s);
	}
	err = cb (ctx, buf);
	if (err) return nerr_pass (err);
      }
      if (node->arg2.op_type)
      {
	if (node->arg2.op_type == CS_TYPE_NUM)
	{
	  snprintf (buf, blen, "%ld", node->arg2.n);
	}
	else
	{
	  snprintf (buf, blen, "%s", node->arg2.s);
	}
	err = cb (ctx, buf);
	if (err) return nerr_pass (err);
      }
      if (node->vargs)
      {
	CSARG *arg;
	arg = node->vargs;
	while (arg)
	{
	  if (arg->op_type == CS_TYPE_NUM)
	  {
	    snprintf (buf, blen, "%ld ", arg->n);
	  }
	  else
	  {
	    snprintf (buf, blen, "%s ", arg->s);
	  }
	  err = cb (ctx, buf);
	  if (err) return nerr_pass (err);
	  arg = arg->next;
	}
      }
    }
    err = cb (ctx, "\n");
    if (err) return nerr_pass (err);
    if (node->case_0)
    {
      snprintf (buf, blen, "%*s %s\n", depth, "", "Case 0");
      err = cb (ctx, buf);
      if (err) return nerr_pass (err);
      err = dump_node (parse, node->case_0, depth+1, ctx, cb, buf, blen);
      if (err) return nerr_pass (err);
    }
    if (node->case_1)
    {
      snprintf (buf, blen, "%*s %s\n", depth, "", "Case 1");
      err = cb (ctx, buf);
      if (err) return nerr_pass (err);
      err = dump_node (parse, node->case_1, depth+1, ctx, cb, buf, blen);
      if (err) return nerr_pass (err);
    }
    node = node->next;
  }
  return STATUS_OK;
}

NEOERR *cs_dump (CSPARSE *parse, void *ctx, CSOUTFUNC cb)
{
  CSTREE *node;
  char buf[4096];

  if (parse->tree == NULL)
    return nerr_raise (NERR_ASSERT, "No parse tree exists");

  node = parse->tree;
  return nerr_pass (dump_node (parse, node, 0, ctx, cb, buf, sizeof(buf)));
}

#if 0
static char *node_name (CSTREE *node)
{
  static char buf[256];

  if (node == NULL)
    snprintf (buf, sizeof(buf), "NULL");
  else
    snprintf (buf, sizeof(buf), "%s_%08x", Commands[node->cmd].cmd,
	node->node_num);

  return buf;
}

static NEOERR *dump_node_pre_c (CSPARSE *parse, CSTREE *node, FILE *fp)
{
  NEOERR *err;

  while (node != NULL)
  {
    fprintf (fp, "CSTREE %s;\n", node_name(node));
    if (node->case_0)
    {
      err = dump_node_pre_c (parse, node->case_0, fp);
      if (err != STATUS_OK) nerr_pass (err);
    }
    if (node->case_1)
    {
      err = dump_node_pre_c (parse, node->case_1, fp);
      if (err != STATUS_OK) nerr_pass (err);
    }
    node = node->next;
  }
  return STATUS_OK;
}

static NEOERR *dump_node_c (CSPARSE *parse, CSTREE *node, FILE *fp)
{
  NEOERR *err;
  char *s;

  while (node != NULL)
  {
    fprintf (fp, "CSTREE %s =\n\t{%d, %d, %d, ", node_name(node), node->node_num,
	node->cmd, node->flags);
    s = repr_string_alloc (node->arg1.s);
    if (s == NULL)
      return nerr_raise(NERR_NOMEM, "Unable to allocate space for repr");
    fprintf (fp, "\n\t  { %d, %s, %ld }, ", node->arg1.op_type, s, node->arg1.n);
    free(s);
    s = repr_string_alloc (node->arg2.s);
    if (s == NULL)
      return nerr_raise(NERR_NOMEM, "Unable to allocate space for repr");
    fprintf (fp, "\n\t  { %d, %s, %ld }, ", node->arg2.op_type, s, node->arg2.n);
    free(s);
    if (node->case_0)
      fprintf (fp, "\n\t%d, &%s, ", node->op, node_name(node->case_0));
    else
      fprintf (fp, "\n\t%d, NULL, ", node->op);
    if (node->case_1)
      fprintf (fp, "&%s, ", node_name(node->case_1));
    else
      fprintf (fp, "NULL, ");
    if (node->next)
      fprintf (fp, "&%s};\n\n", node_name(node->next));
    else
      fprintf (fp, "NULL};\n\n");
    if (node->case_0)
    {
      err = dump_node_c (parse, node->case_0, fp);
      if (err != STATUS_OK) nerr_pass (err);
    }
    if (node->case_1)
    {
      err = dump_node_c (parse, node->case_1, fp);
      if (err != STATUS_OK) nerr_pass (err);
    }
    node = node->next;
  }
  return STATUS_OK;
}

NEOERR *cs_dump_c (CSPARSE *parse, char *path)
{
  CSTREE *node;
  FILE *fp;
  NEOERR *err;

  if (parse->tree == NULL)
    return nerr_raise (NERR_ASSERT, "No parse tree exists");

  fp = fopen(path, "w");
  if (fp == NULL)
  {
    return nerr_raise (NERR_SYSTEM,
	"Unable to open file %s for writing: [%d] %s", path, errno,
	strerror(errno));
  }

  fprintf(fp, "/* Auto-generated file: DO NOT EDIT */\n");
  fprintf(fp, "#include <stdlib.h>\n\n");
  fprintf(fp, "#include \"cs.h\"\n");
  node = parse->tree;
  err = dump_node_pre_c (parse, node, fp);
  fprintf(fp, "\n");
  err = dump_node_c (parse, node, fp);
  fclose(fp);
  return nerr_pass (err);
}
#endif
