/* This file is part of the YAZ toolkit.
 * Copyright (C) 1995-2012 Index Data
 * See the file LICENSE for details.
 */
/**
 * \file json.c
 * \brief JSON encoding/decoding
 */
#if HAVE_CONFIG_H
#include <config.h>
#endif

#include <yaz/json.h>

#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

#include <yaz/xmalloc.h>

struct json_subst_info {
    int idx;
    struct json_subst_info *next;
    struct json_node *node;
};

struct json_parser_s {
    const char *buf;
    const char *cp;
    const char *err_msg;
    struct json_subst_info *subst;
};

json_parser_t json_parser_create(void)
{
    json_parser_t p = (json_parser_t) xmalloc(sizeof(*p));
    
    p->buf = 0;
    p->cp = 0;
    p->err_msg = 0;
    p->subst = 0;
    return p;
}

void json_parser_subst(json_parser_t p, int idx, struct json_node *n)
{
    struct json_subst_info **sb = &p->subst;
    for (; *sb; sb = &(*sb)->next)
        if ((*sb)->idx == idx)
        {
            (*sb)->node = n;
            return;
        }
    *sb = xmalloc(sizeof(**sb));
    (*sb)->next = 0;
    (*sb)->node = n;
    (*sb)->idx = idx;
}

void json_parser_destroy(json_parser_t p)
{
    struct json_subst_info *sb = p->subst;
    while (sb)
    {
        struct json_subst_info *sb_next = sb->next;
        xfree(sb);
        sb = sb_next;
    }
    xfree(p);
}

static int look_ch(json_parser_t p)
{
    while (*p->cp && strchr(" \t\r\n\f", *p->cp))
        (p->cp)++;
    return *p->cp;
}

static void move_ch(json_parser_t p)
{
    if (*p->cp)
        (p->cp)++;
}

static struct json_node *json_new_node(json_parser_t p, enum json_node_type type)
{
    struct json_node *n = (struct json_node *) xmalloc(sizeof(*n));
    n->type = type;
    n->u.link[0] = n->u.link[1] = 0;
    return n;
}

void json_remove_node(struct json_node *n)
{
    if (!n)
        return;
    switch (n->type)
    {
    case json_node_object:
    case json_node_array:
    case json_node_list:
    case json_node_pair:
        json_remove_node(n->u.link[0]);
        json_remove_node(n->u.link[1]);
        break;
    case json_node_string:
        xfree(n->u.string);
        break;
    case json_node_number:
    case json_node_true:
    case json_node_false:
    case json_node_null:
        break;
    }
    xfree(n);
}

static struct json_node *json_parse_object(json_parser_t p);
static struct json_node *json_parse_array(json_parser_t p);

static int json_one_char(const char **p, char *out)
{
    if (**p == '\\' && p[0][1])
    {
        (*p)++;
        switch(**p)
        {
        case '"':
            *out = '"'; break;
        case '\\':
            *out = '\\'; break;
        case '/':
            *out = '/'; break;
        case 'b':
            *out = '\b'; break;
        case 'f':
            *out = '\f'; break;
        case 'n':
            *out = '\n'; break;
        case 'r':
            *out = '\r'; break;
        case 't':
            *out = '\t'; break;
        case 'u':
            if (p[0][1])
            {
                unsigned code;
                char *outp = out;
                int error;
                size_t outbytesleft = 6;
                sscanf(*p + 1, "%4x", &code);
                if (!yaz_write_UTF8_char(code, &outp, &outbytesleft, &error))
                {
                    *p += 5;
                    return outp - out;
                }
            }
        default:
            *out = '_'; break;
            break;
        }
        (*p)++;
        return 1;
    }
    else
    {
        *out = **p;
        (*p)++;
        return 1;
    }
}

static struct json_node *json_parse_string(json_parser_t p)
{
    struct json_node *n;
    const char *cp;
    char *dst;
    int l = 0;
    if (look_ch(p) != '\"')
    {
        p->err_msg = "string expected";
        return 0;
    }
    move_ch(p);

    cp = p->cp;
    while (*cp && *cp != '"')
    {
        char out[6];
        l += json_one_char(&cp, out);
    }
    if (!*cp)
    {
        p->err_msg = "missing \"";
        return 0;
    }
    n = json_new_node(p, json_node_string);
    dst = n->u.string = (char *) xmalloc(l + 1);
    
    cp = p->cp;
    while (*cp && *cp != '"')
    {
        char out[6];

        l = json_one_char(&cp, out);
        memcpy(dst, out, l);
        dst += l;
    }
    *dst = '\0';
    p->cp = cp+1;
    return n;
}

static struct json_node *json_parse_number(json_parser_t p)
{
    struct json_node *n;
    char *endptr;
    double v;

    look_ch(p); // skip spaces
    v = strtod(p->cp, &endptr);

    if (endptr == p->cp)
    {
        p->err_msg = "bad number";
        return 0;
    }
    p->cp = endptr;
    n = json_new_node(p, json_node_number);
    n->u.number = v;
    return n;
}

static struct json_node *json_parse_value(json_parser_t p)
{
    int c = look_ch(p);
    if (c == '\"')
        return json_parse_string(p);
    else if (strchr("0123456789-+", c))
        return json_parse_number(p);
    else if (c == '{')
        return json_parse_object(p);
    else if (c == '[')
        return json_parse_array(p);
    else if (c == '%')
    {
        struct json_subst_info *sb;
        int idx = 0;
        p->cp++;
        c = *p->cp;
        while (c >= '0' && c <= '9')
        {
            idx = idx*10 + (c - '0');
            p->cp++;
            c = *p->cp;
        }
        for (sb = p->subst; sb; sb = sb->next)
            if (sb->idx == idx)
                return sb->node;
    }
    else
    {
        char tok[8];
        int i = 0;
        while (c >= 'a' && c <= 'z' && i < 7)
        {
            tok[i++] = c;
            p->cp++;
            c = *p->cp;
        }
        tok[i] = 0;
        if (!strcmp(tok, "true"))
            return json_new_node(p, json_node_true);
        else if (!strcmp(tok, "false"))
            return json_new_node(p, json_node_false);
        else if (!strcmp(tok, "null"))
            return json_new_node(p, json_node_null);
    }
    p->err_msg = "bad token";
    return 0;
}

static struct json_node *json_parse_elements(json_parser_t p)
{
    struct json_node *n1 = json_parse_value(p);
    struct json_node *m0, *m1;
    if (!n1)
        return 0;
    m0 = m1 = json_new_node(p, json_node_list);
    m1->u.link[0] = n1;
    while (look_ch(p) == ',')
    {
        struct json_node *n2, *m2;
        move_ch(p);
        n2 = json_parse_value(p);
        if (!n2)
        {
            json_remove_node(m0);
            return 0;
        }
        m2 = json_new_node(p, json_node_list);
        m2->u.link[0] = n2;
        
        m1->u.link[1] = m2;
        m1 = m2;
    }
    return m0;
}

static struct json_node *json_parse_array(json_parser_t p)
{
    struct json_node *n;
    if (look_ch(p) != '[')
    {
        p->err_msg = "expecting [";
        return 0;
    }
    move_ch(p);
    n = json_new_node(p, json_node_array);
    if (look_ch(p) != ']')
        n->u.link[0] = json_parse_elements(p);

    if (look_ch(p) != ']')
    {
        p->err_msg = "expecting ]";
        json_remove_node(n);
        return 0;
    }
    move_ch(p);
    return n;
}

static struct json_node *json_parse_pair(json_parser_t p)
{
    struct json_node *s = json_parse_string(p);
    struct json_node *v, *n;
    if (!s)
        return 0;
    if (look_ch(p) != ':')
    {
        p->err_msg = "missing :";
        json_remove_node(s);
        return 0;
    }
    move_ch(p);
    v = json_parse_value(p);
    if (!v)
    {
        json_remove_node(s);
        return 0;
    }
    n = json_new_node(p, json_node_pair);
    n->u.link[0] = s;
    n->u.link[1] = v;
    return n;
}

static struct json_node *json_parse_members(json_parser_t p)
{
    struct json_node *n1 = json_parse_pair(p);
    struct json_node *m0, *m1;
    if (!n1)
        return 0;
    m0 = m1 = json_new_node(p, json_node_list);
    m1->u.link[0] = n1;
    while (look_ch(p) == ',')
    {
        struct json_node *n2, *m2;
        move_ch(p);
        n2 = json_parse_pair(p);
        if (!n2)
        {
            json_remove_node(m0);
            return 0;
        }
        m2 = json_new_node(p, json_node_list);
        m2->u.link[0] = n2;
        
        m1->u.link[1] = m2;
        m1 = m2;
    }
    return m0;
}

static struct json_node *json_parse_object(json_parser_t p)
{
    struct json_node *n;
    if (look_ch(p) != '{')
    {
        p->err_msg = "{ expected";
        return 0;
    }
    move_ch(p);

    n = json_new_node(p, json_node_object);
    if (look_ch(p) != '}')
    {
        struct json_node *m = json_parse_members(p);
        if (!m)
        {
            json_remove_node(n);
            return 0;
        }
        n->u.link[0] = m;
    }
    if (look_ch(p) != '}')
    {
        p->err_msg = "Missing }";
        json_remove_node(n);
        return 0;
    }
    move_ch(p);
    return n;
}

struct json_node *json_parser_parse(json_parser_t p, const char *json_str)
{
    int c;
    struct json_node *n;
    p->buf = json_str;
    p->cp = p->buf;

    n = json_parse_value(p);
    if (!n)
        return 0;
    c = look_ch(p);
    if (c != 0)
    {
        p->err_msg = "extra characters";
        json_remove_node(n);
        return 0;
    }
    return n;
}

struct json_node *json_parse2(const char *json_str, const char **errmsg,
                              size_t *pos)
{
    json_parser_t p = json_parser_create();
    struct json_node *n = 0;
    if (!p)
    {
        if (errmsg)
            *errmsg = "could not create parser";
    }
    else
    {
        n = json_parser_parse(p, json_str);
        if (!n && errmsg)
            *errmsg = json_parser_get_errmsg(p);
        if (pos)
            *pos = json_parser_get_position(p);
        json_parser_destroy(p);
    }
    return n;
}

struct json_node *json_parse(const char *json_str, const char **errmsg)
{
    return json_parse2(json_str, errmsg, 0);
}

static void wrbuf_json_write(WRBUF b, const char *cp, size_t sz)
{
    size_t i;
    for (i = 0; i < sz; i++)
    {
        if (cp[i] > 0 && cp[i] < 32)
        {
            wrbuf_putc(b, '\\');
            switch (cp[i])
            {
            case '\b': wrbuf_putc(b, 'b'); break;
            case '\f': wrbuf_putc(b, 'f'); break;
            case '\n': wrbuf_putc(b, 'n'); break;
            case '\r': wrbuf_putc(b, 'r'); break;
            case '\t': wrbuf_putc(b, 't'); break;
            default:
                wrbuf_printf(b, "u%04x", cp[i]);
            }
        }
        else if (cp[i] == '"')
        {
            wrbuf_putc(b, '\\'); wrbuf_putc(b, '"');
        }
        else if (cp[i] == '\\')
        {
            wrbuf_putc(b, '\\'); wrbuf_putc(b, '\\');
        }
        else
        {   /* leave encoding as raw UTF-8 */
            wrbuf_putc(b, cp[i]);
        }
    }       
        
}

void wrbuf_json_puts(WRBUF b, const char *str)
{
    wrbuf_json_write(b, str, strlen(str));
}

void json_write_wrbuf(struct json_node *node, WRBUF result)
{
    switch (node->type)
    {
    case json_node_object:
        wrbuf_puts(result, "{");
        if (node->u.link[0])
            json_write_wrbuf(node->u.link[0], result);
        wrbuf_puts(result, "}");
        break;
    case json_node_array:
        wrbuf_puts(result, "[");
        if (node->u.link[0])
            json_write_wrbuf(node->u.link[0], result);
        wrbuf_puts(result, "]");
        break;
    case json_node_list:
        json_write_wrbuf(node->u.link[0], result);
        if (node->u.link[1])
        {
            wrbuf_puts(result, ",");
            json_write_wrbuf(node->u.link[1], result);
        }
        break;
    case json_node_pair:
        json_write_wrbuf(node->u.link[0], result);
        wrbuf_puts(result, ":");
        json_write_wrbuf(node->u.link[1], result);
        break;
    case json_node_string:
        wrbuf_puts(result, "\"");
        wrbuf_json_puts(result, node->u.string);
        wrbuf_puts(result, "\"");
        break;
    case json_node_number:
        wrbuf_printf(result, "%lg", node->u.number);
        break;
    case json_node_true:
        wrbuf_puts(result, "true");
        break;
    case json_node_false:
        wrbuf_puts(result, "false");
        break;
    case json_node_null:
        wrbuf_puts(result, "null");
        break;
    }
}

static struct json_node **json_get_objectp(struct json_node *n,
                                           const char *name)
{
    if (n && n->type == json_node_object)
    {
        for (n = n->u.link[0]; n; n = n->u.link[1])
        {
            struct json_node *c = n->u.link[0];
            if (c && c->type == json_node_pair &&
                c->u.link[0] && c->u.link[0]->type == json_node_string)
                if (!strcmp(name, c->u.link[0]->u.string))
                    return &c->u.link[1];
        }
    }
    return 0;
}

struct json_node *json_get_object(struct json_node *n, const char *name)
{
    struct json_node **np = json_get_objectp(n, name);
    
    if (np)
        return *np;
    return 0;
}

struct json_node *json_detach_object(struct json_node *n, const char *name)
{
    struct json_node **np = json_get_objectp(n, name);
    
    if (np)
    {
        struct json_node *n = *np;
        *np = 0;
        return n;
    }
    return 0;
}

struct json_node *json_get_elem(struct json_node *n, int idx)
{
    if (n && n->type == json_node_array)
    {
        for (n = n->u.link[0]; n; n = n->u.link[1])
        {
            if (--idx < 0)
                return n->u.link[0];
        }
    }
    return 0;
}

int json_count_children(struct json_node *n)
{
    int i = 0;

    if (n && (n->type == json_node_array || n->type == json_node_object))
    {
        for (n = n->u.link[0]; n; n = n->u.link[1])
            i++;
    }
    return i;
}

int json_append_array(struct json_node *dst, struct json_node *src)
{
    if (dst && src &&
        dst->type == json_node_array && src->type == json_node_array)
    {
        struct json_node **np = &dst->u.link[0];
        while (*np)
            np = &(*np)->u.link[1];
        *np = src->u.link[0];
        src->u.link[0] = 0;
        json_remove_node(src);
        return 0;
    }
    return -1;
}

const char *json_parser_get_errmsg(json_parser_t p)
{
    return p->err_msg;
}

size_t json_parser_get_position(json_parser_t p)
{
    return p->cp - p->buf;
}

/*
 * Local variables:
 * c-basic-offset: 4
 * c-file-style: "Stroustrup"
 * indent-tabs-mode: nil
 * End:
 * vim: shiftwidth=4 tabstop=8 expandtab
 */
