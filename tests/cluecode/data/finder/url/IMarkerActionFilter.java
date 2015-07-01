/*******************************************************************************
 * Copyright (c) 2000, 2006 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.ui;


/**
 * Describes the public attributes for a marker and the acceptable values
 * each may have.  
 * <p>
 * A popup menu extension may use these constants to describe its object target.  
 * Each identifies an attribute name or possible value.  
 * <p>
 * Clients are not expected to implement this interface.
 * </p>
 *
 * @see IActionFilter
 */
public interface IMarkerActionFilter extends IActionFilter {
    /**
     * An attribute indicating the marker type (value <code>"type"</code>).  
     * The attribute value in xml should match one of the marker types defined in 
     * the workbench's marker extension point.  Common examples are 
     * <code>IMarker.TASK, IMarker.BOOKMARK, and IMarker.MARKER</code>.
     */
    public static final String TYPE = "type"; //$NON-NLS-1$

    /**
     * An attribute indicating the marker super type (value <code>"superType"</code>).  
     * The attribute value in xml should match one of the marker types defined in 
     * the workbench's marker extension point.  Common examples are 
     * <code>IMarker.TASK, IMarker.BOOKMARK, and IMarker.MARKER</code>.
     */
    public static final String SUPER_TYPE = "superType"; //$NON-NLS-1$

    /**
     * An attribute indicating the marker priority (value <code>"priority"</code>).
     * The attribute value in xml must be one of <code>IMarker.PRIORITY_LOW, 
     * IMarker.PRIORITY_NORMAL, or IMarker.PRIORITY_HIGH</code> 
     */
    public static final String PRIORITY = "priority"; //$NON-NLS-1$

    /**
     * An attribute indicating the marker severity (value <code>"severity"</code>).  
     * The attribute value in xml in xml must be one of <code>IMarker.SEVERITY_ERROR, 
     * IMarker.SEVERITY_WARNING, or IMarker.SEVERITY_INFO</code> 
     */
    public static final String SEVERITY = "severity"; //$NON-NLS-1$

    /**
     * An attribute indicating whether the marker is considered done (value 
     * <code>"done"</code>).
     * The attribute value in xml must be one of <code>"true" or "false"</code>.
     */
    public static final String DONE = "done"; //$NON-NLS-1$

    /**
     * An attribute indicating the marker message (value <code>"message"</code>).
     * The attribute value in xml is unconstrained. "*" may be used at the start or
     * the end to represent "one or more characters".
     */
    public static final String MESSAGE = "message"; //$NON-NLS-1$

    /**
     * An attribute indicating the type of resource associated with the marker
     * (value <code>"resourceType"</code>). The attribute value in xml must be
     * one of <code>IResource.FILE, IResource.PROJECT, IResource.FOLDER,
     * or IResource.ROOT</code>.
     */
    public static final String RESOURCE_TYPE = "resourceType"; //$NON-NLS-1$

}
