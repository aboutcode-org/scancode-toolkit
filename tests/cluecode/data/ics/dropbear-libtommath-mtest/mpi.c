    mpi.c

    by Michael J. Fromberger <sting@linguist.dartmouth.edu>
    Copyright (C) 1998 Michael J. Fromberger, All Rights Reserved

    Arbitrary precision integer arithmetic library
  if((res = mp_copy(a, c)) != MP_OKAY)
    return res;

  return s_mp_mul_2(c);

} /* end mp_mul_2() */
  if((res = mp_copy(a, c)) != MP_OKAY)
    return res;

  s_mp_div_2(c);

  return MP_OKAY;

  } else if(cmp == 0) {             /* different sign, a == b   */

    mp_zero(c);
    return MP_OKAY;

    }
  }

  if(USED(c) == 1 && DIGIT(c, 0) == 0)
    SIGN(c) = MP_ZPOS;

  return MP_OKAY;
	return res;
      if((res = s_mp_add(c, a)) != MP_OKAY)
	return res;
      SIGN(c) = SIGN(a);
    }

    }

  } else if(cmp == 0) {  /* Same sign, equal magnitude */
    mp_zero(c);
    return MP_OKAY;

	return res;
    }

    SIGN(c) = !SIGN(b);
  }

  if(USED(c) == 1 && DIGIT(c, 0) == 0)
    SIGN(c) = MP_ZPOS;

  return MP_OKAY;
  }
  
  if(sgn == MP_ZPOS || s_mp_cmp_d(c, 0) == MP_EQ)
    SIGN(c) = MP_ZPOS;
  else
    SIGN(c) = sgn;
  
  return MP_OKAY;
    if((res = mp_div(a, m, NULL, c)) != MP_OKAY)
      return res;
    
    if(SIGN(c) == MP_NEG) {
      if((res = mp_add(c, m, c)) != MP_OKAY)
	return res;
    }
    
  } else {
    mp_zero(c);

  }
      rem = DIGIT(a, 0);
  }

  if(c)
    *c = rem;

  }

  res = mp_mod(&x, m, c);
  SIGN(c) = SIGN(a);

CLEANUP: