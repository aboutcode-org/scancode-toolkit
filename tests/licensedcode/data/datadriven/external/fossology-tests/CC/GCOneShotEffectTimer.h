///**********************************************************************************************************************************
///  GCOneShotEffectTimer.h
///  GCDrawKit
///
///  Created by graham on 24/04/2007.
///  Released under the Creative Commons license 2007 Apptree.net.
///
/// 
///  This work is licensed under the Creative Commons Attribution-ShareAlike 2.5 License.
///  To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/2.5/ or send a letter to
///  Creative Commons, 543 Howard Street, 5th Floor, San Francisco, California, 94105, USA.
///
///**********************************************************************************************************************************

#import <Cocoa/Cocoa.h>


@interface GCOneShotEffectTimer : NSObject
{
	NSTimer*			_timer;
	NSTimeInterval		_start;
	NSTimeInterval		_total;
	id					_delegate;
}

+ (id)			oneShotWithTime:(NSTimeInterval) t forDelegate:(id) del;

@end



@interface NSObject (OneShotDelegate)

- (void)		oneShotHasReached:(float) relpos;
- (void)		oneShotHasReachedInverse:(float) relpos;
- (void)		oneShotComplete;

@end


/* This class wraps up a very simple piece of timer functionality. It sets up a timer that will call the
	delegate frequently with a value from 0..1. Once 1 is reached, it stops.
	
	This is useful for one-shot type animations such as fading out a window or similar.
	
	The inverse method is called with interval 1..0.
	
	The timer starts as soon as it is created.
	
	The timer attempts to maintain a 30fps rate, and is capped at this value. On slower systems, it will drop
	frames as needed.
	
*/