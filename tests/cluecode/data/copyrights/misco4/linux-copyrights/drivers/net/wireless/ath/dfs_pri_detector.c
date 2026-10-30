* Copyright (c) 2012 Neratec Solutions AG
 *
 * Permission to use, copy, modify, and/or distribute this software for any


#define DFS_POOL_STAT_INC(c) (global_dfs_pool_stats.c++)
#define DFS_POOL_STAT_DEC(c) (global_dfs_pool_stats.c--)
#define GET_PRI_TO_USE(MIN, MAX, RUNTIME) \
	(MIN + PRI_TOLERANCE == MAX - PRI_TOLERANCE ? \