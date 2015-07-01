package com.somecompany.somepackage;

/**
 * Title:        Some Title
 * Description:
 * Copyright:    Copyright (c) 2001
 * Company:      Private Company
 * @author
 * @version
 */

import com.somecompany.someotherpackage.* ;

public class SomeClass
{
    private static final String SOME_STATIC = "value";
    
    private void usage()
    {
        System.out.print("usage: java " + new SomeClass().getClass().getName());
    }

    static public void main(String[] args) {
    	System.exit(0); 
    }
    

}
