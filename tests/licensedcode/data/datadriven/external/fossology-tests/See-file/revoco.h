
 /* 
  * Copyright (C) 2007  Olli Salonen <oasalonen@gmail.com>
  * see btnx.c for detailed license information
  * 
  * revoco.c is under a different copyright. See that file for details.
  * 
  */
  
#ifndef REVOCO_H_
#define REVOCO_H_

/* Possible revoco modes */
enum
{
	REVOCO_DISABLED=0,
	REVOCO_FREE_MODE,
	REVOCO_CLICK_MODE,
	REVOCO_MANUAL_MODE,
	REVOCO_AUTO_MODE,
	REVOCO_INVALID_MODE
};

/* Config parser uses these to set up revoco */
void revoco_set_mode(int mode);
void revoco_set_btn(int btn);
void revoco_set_up_scroll(int value);
void revoco_set_down_scroll(int value);

/* Execute revoco functionality */
int revoco_launch(void);

#endif /*REVOCO_H_*/
