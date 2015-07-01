/*
 * Javassist, a Java-bytecode translator toolkit.
 * Copyright (C) 1999-2007 Shigeru Chiba. All Rights Reserved.
 *
 * The contents of this file are subject to the Mozilla Public License Version
    public static final String version = "3.14.0.GA";

    /**
     * Prints the version number and the copyright notice.
     *
     * <p>The following command invokes this method:
     */
    public static void main(String[] args) {
        System.out.println("Javassist version " + CtClass.version);
        System.out.println("Copyright (C) 1999-2010 Shigeru Chiba."
                           + " All Rights Reserved.");
    }