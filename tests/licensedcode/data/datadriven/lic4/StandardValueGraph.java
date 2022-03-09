/*
 * Copyright (C) 2016 The Guava Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.common.graph;

import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.graph.GraphConstants.DEFAULT_NODE_COUNT;
import static com.google.common.graph.Graphs.checkNonNegative;

import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import javax.annotation.CheckForNull;

/**
 * Standard implementation of {@link ValueGraph} that supports the options supplied by {@link
 * AbstractGraphBuilder}.
 *
 * <p>This class maintains a map of nodes to {@link GraphConnections}.
 *
 * <p>Collection-returning accessors return unmodifiable views: the view returned will reflect
 * changes to the graph (if the graph is mutable) but may not be modified by the user.
 *
 * <p>The time complexity of all collection-returning accessors is O(1), since views are returned.
 *
 */

