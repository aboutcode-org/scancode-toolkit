 * and a POLICY for built-ins.
 */

/* (C) 1999 Paul ``Rusty'' Russell - Placed under the GNU GPL (See
 * COPYING for details).
 * (C) 2000-2004 by the Netfilter Core Team <coreteam@netfilter.org>
 *
 * 2003-Jun-20: Harald Welte <laforge@netfilter.org>:

		/* Issue: The index array needs to start after the
		 * builtin chains, as they are not sorted */
		if (!iptcc_is_builtin(c)) {
			cindex=chains / list_length;

	/* First look at builtin chains */
	list_for_each(pos, &handle->chains) {
		struct chain_head *c = list_entry(pos, struct chain_head, list);
		if (!iptcc_is_builtin(c))
			break;
		if (!strcmp(c->name, name))
			return c;

		/* We can stop earlier as we know list is sorted */
		if (res>0 && !iptcc_is_builtin(c)) { /* Walked too far*/
			debug(" Not in list, walked too far, sorted list\n");
			return NULL;
	 * from an older version, as old versions allow last created
	 * chain to be unsorted.
	 */
	if (iptcc_is_builtin(c)) /* Only user defined chains are sorted*/
		list_add_tail(&c->list, &h->chains);
	else {
	struct iptcb_chain_foot *foot;

	/* only user-defined chains have heaer */
	if (!iptcc_is_builtin(c)) {
		/* put chain header in place */
		head = (void *)repl->entries + c->head_offset;
	foot->target.target.u.target_size =
				ALIGN(sizeof(STRUCT_STANDARD_TARGET));
	/* builtin targets have verdict, others return */
	if (iptcc_is_builtin(c))
		foot->target.verdict = c->verdict;
	else
	c->head_offset = *offset;
	DEBUGP("%s: chain_head %u, offset=%u\n", c->name, *num, *offset);

	if (!iptcc_is_builtin(c))  {
		/* Chain has header */
		*offset += sizeof(STRUCT_ENTRY)
			free(r);
		}

		free(c);
	}

		return 0;
	}

	return iptcc_is_builtin(c);
}

		return NULL;
	}

	if (!iptcc_is_builtin(c))
		return NULL;

		DEBUGP("trying to find chain `%s': ", t->u.user.name);

		c = iptcc_find_label(t->u.user.name, handle);
		if (c) {
			DEBUGP_C("found!\n");
			r->type = IPTCC_R_JUMP;

	//list_del(&c->list); /* Done in iptcc_chain_index_delete_chain() */
	iptcc_chain_index_delete_chain(c, handle);
	free(c);

	DEBUGP("chain `%s' deleted\n", chain);
		return 0;
	}

	/* This only unlinks "c" from the list, thus no free(c) */
	iptcc_chain_index_delete_chain(c, handle);

		return 0;
	}

	if (!iptcc_is_builtin(c)) {
		DEBUGP("cannot set policy of userdefinedchain `%s'\n", chain);
		errno = ENOENT;
		struct rule_head *r;

		/* Builtin chains have their own counters */
		if (iptcc_is_builtin(c)) {
			DEBUGP("counter for chain-index %u: ", c->foot_index);
			switch(c->counter_map.maptype) {