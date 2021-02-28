/*
 * ion/mod_query/main.c
 *
 * Copyright (c) Tuomo Valkonen 1999-2008. 
 *
 * See the included file LICENSE for details.
 */

#include <libextl/readconfig.h>
#include <libextl/extl.h>
#include <libtu/minmax.h>
#include <ioncore/binding.h>
#include <ioncore/conf-bindings.h>
#include <ioncore/frame.h>
#include <ioncore/saveload.h>
#include <ioncore/bindmaps.h>
#include <ioncore/ioncore.h>

#include "query.h"
#include "edln.h"
#include "wedln.h"
#include "input.h"
#include "complete.h"
#include "history.h"
#include "exports.h"
#include "main.h"


/*{{{ Module information */


#include "../version.h"

char mod_query_ion_api_version[]=ION_API_VERSION;


/*}}}*/


/*{{{ Bindmaps */


WBindmap *mod_query_input_bindmap=NULL;
WBindmap *mod_query_wedln_bindmap=NULL;


/*}}}*/


/*{{{ Set & get */


ModQueryConfig mod_query_config={
    250,
    TRUE,
    FALSE,
    TRUE
};


/*EXTL_DOC
 * Set module configuration. The following are supported:
 *
 * \begin{tabularx}{\linewidth}{lX}
 *  \tabhead{Field & Description}
 *  \var{autoshowcompl} & (boolean) Is auto-show-completions enabled?
 *      (default: true). \\
 *  \var{autoshowcompl_delay} & (integer) auto-show-completions delay
 *      in milliseconds (default: 250). \\
 *  \var{caseicompl} & (boolean) Turn some completions case-insensitive
 *      (default: false). \\
 *  \var{substrcompl} & (boolean) Complete on sub-strings in some cases
 *      (default: ftrue). \\
 * \end{tabularx}
 */
EXTL_EXPORT
void mod_query_set(ExtlTab tab)
{
    ModQueryConfig *c=&mod_query_config;

    extl_table_gets_b(tab, "autoshowcompl", &c->autoshowcompl);
    extl_table_gets_b(tab, "caseicompl", &c->caseicompl);
    extl_table_gets_b(tab, "substrcompl", &c->substrcompl);
    
    if(extl_table_gets_i(tab, "autoshowcompl_delay",
                         &c->autoshowcompl_delay)){
        c->autoshowcompl_delay=maxof(c->autoshowcompl_delay, 0);
    }
}

/*EXTL_DOC
 * Get module configuration. For more information see
 * \fnref{mod_query.set}.
 */
EXTL_SAFE
EXTL_EXPORT
ExtlTab mod_query_get()
{
    ModQueryConfig *c=&mod_query_config;
    ExtlTab tab=extl_create_table();
    
    extl_table_sets_b(tab, "autoshowcompl", c->autoshowcompl);
    extl_table_sets_i(tab, "autoshowcompl_delay", c->autoshowcompl_delay);
    extl_table_sets_b(tab, "caseicompl", c->caseicompl);
    extl_table_sets_b(tab, "substrcompl", c->substrcompl);
    
    return tab;
}


/*}}}*/


/*{{{ Init & deinit */


static void load_history()
{
    ExtlTab tab;
    int i, n;

    if(!extl_read_savefile("saved_queryhist", &tab))
        return;
    
    n=extl_table_get_n(tab);
    
    for(i=n; i>=1; i--){
        char *s=NULL;
        if(extl_table_geti_s(tab, i, &s)){
            mod_query_history_push(s);
            free(s);
        }
    }
    
    extl_unref_table(tab);
}


static void save_history()
{
    ExtlTab tab=mod_query_history_table();
    
    extl_write_savefile("saved_queryhist", tab);
    
    extl_unref_table(tab);
}


static bool loaded_ok=FALSE;

void mod_query_deinit()
{
    mod_query_unregister_exports();

    if(mod_query_input_bindmap!=NULL){
        ioncore_free_bindmap("WInput", mod_query_input_bindmap);
        mod_query_input_bindmap=NULL;
    }
    
    if(mod_query_wedln_bindmap!=NULL){
        ioncore_free_bindmap("WEdln", mod_query_wedln_bindmap);
        mod_query_wedln_bindmap=NULL;
    }
    
    hook_remove(ioncore_snapshot_hook, save_history);
}


bool mod_query_init()
{
    if(!mod_query_register_exports())
        goto err;
    
    mod_query_input_bindmap=ioncore_alloc_bindmap("WInput", NULL);
    mod_query_wedln_bindmap=ioncore_alloc_bindmap("WEdln", NULL);
    
    if(mod_query_wedln_bindmap==NULL ||
       mod_query_input_bindmap==NULL){
        goto err;
    }

    /*ioncore_read_config("cfg_query", NULL, TRUE);*/

    load_history();
    
    loaded_ok=TRUE;

    hook_add(ioncore_snapshot_hook, save_history);
    
    return TRUE;
    
err:
    mod_query_deinit();
    return FALSE;
}


/*}}}*/

