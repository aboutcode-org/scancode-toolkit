package com.privatecompany.somepackage;

import java.io.File;
import java.io.FilenameFilter;
import javax.swing.filechooser.FileFilter;

/**
 * <p>Title: CustomFileFilter</p>
 *
 * <p>Description: </p>
 *
 * <p>Copyright: Copyright (c) 2006</p>
 *
 * <p>Company: Private Company</p>
 *
 * @author John Doe
 * @version 1.0
 */
public class CustomFileFilter extends FileFilter
{
    // private static final member variable
    private static final int TYPE_LENGTH = 2;

    // some comment
    private final String fileType;

    public CustomFileFilter(final String fileType)
    {
    }

}
