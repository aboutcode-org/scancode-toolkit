/*
 * Copyright (C) 2008 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 *
 * <p>Throughout the documentation of this class, the phrase "matching
 * character" is used to mean "any character {@code c} for which {@code
 * this.matches(c)} returns {@code true}".
 *
 * <p><b>Note:</b> This class deals only with {@code char} values; it does not
   */
  public static final CharMatcher JAVA_DIGIT = new CharMatcher() {
    @Override public boolean matches(char c) {
      return Character.isDigit(c);
    }
  };
   */
  public static final CharMatcher JAVA_LETTER = new CharMatcher() {
    @Override public boolean matches(char c) {
      return Character.isLetter(c);
    }
  };
   */
  public static final CharMatcher JAVA_LETTER_OR_DIGIT = new CharMatcher() {
    @Override public boolean matches(char c) {
      return Character.isLetterOrDigit(c);
    }
  };
   */
  public static final CharMatcher JAVA_UPPER_CASE = new CharMatcher() {
    @Override public boolean matches(char c) {
      return Character.isUpperCase(c);
    }
  };
   */
  public static final CharMatcher JAVA_LOWER_CASE = new CharMatcher() {
    @Override public boolean matches(char c) {
      return Character.isLowerCase(c);
    }
  };
      }
      @Override protected void setBits(LookupTable table) {
        for (char c : chars) {
          table.set(c);
        }
      }
      @Override protected void setBits(LookupTable table) {
        char c = startInclusive;
        while (true) {
          table.set(c);
          if (c++ == endInclusive) {
            break;
    }
    return new CharMatcher() {
      @Override public boolean matches(char c) {
        return predicate.apply(c);
      }
      @Override public boolean apply(Character character) {
    final CharMatcher original = this;
    return new CharMatcher() {
      @Override public boolean matches(char c) {
        return !original.matches(c);
      }


    @Override public boolean matches(char c) {
      for (CharMatcher matcher : components) {
        if (!matcher.matches(c)) {
          return false;
        }

    @Override public boolean matches(char c) {
      for (CharMatcher matcher : components) {
        if (matcher.matches(c)) {
          return true;
        }

    return new CharMatcher() {
      @Override public boolean matches(char c) {
        return table.get(c);
      }

  protected void setBits(LookupTable table) {
    char c = Character.MIN_VALUE;
    while (true) {
      if (matches(c)) {
        table.set(c);
      }
      if (c++ == Character.MAX_VALUE) {
    boolean in = true;
    for (int i = first + 1; i < sequence.length(); i++) {
      char c = sequence.charAt(i);
      if (apply(c)) {
        if (!in) {
          builder.append(replacement);
          in = true;
        }
      } else {
        builder.append(c);
        in = false;
      }
    boolean inMatchingGroup = false;
    for (int i = first; i < sequence.length(); i++) {
      char c = sequence.charAt(i);
      if (apply(c)) {
        inMatchingGroup = true;
      } else {
          builder.append(replacement);
          inMatchingGroup = false;
        }
        builder.append(c);
      }
    }