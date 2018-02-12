package org.jgroups.protocols;

import org.jgroups.Event;
import org.jgroups.Message;
import org.jgroups.annotations.*;
import org.jgroups.stack.Protocol;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Protocol which sends at most max_bytes in time_period milliseconds. Can be used instead of a flow control protocol,
 * e.g. FC or SFC (same position in the stack)
 * @author Bela Ban
 * @version $Id: RATE_LIMITER.java,v 1.3 2009/12/11 13:08:03 belaban Exp $
 */
@Experimental @Unsupported
public class RATE_LIMITER extends Protocol {

    @Property(description="Max number of bytes to be sent in time_period ms. Blocks the sender if exceeded until a new " +
            "time period has started")
    protected long max_bytes=500000;

    @Property(description="Number of milliseconds during which max_bytes bytes can be sent")
    protected long time_period=1000L;


    /** Keeps track of the number of bytes sent in the current time period */
    @GuardedBy("lock")
    @ManagedAttribute
    protected long num_bytes_sent=0L;

    @GuardedBy("lock")
    protected long end_of_current_period=0L;

    protected final Lock lock=new ReentrantLock();
    protected final Condition block=lock.newCondition();

    @ManagedAttribute
    protected int num_blockings=0;

    @ManagedAttribute
    protected long total_block_time=0L;



    public Object down(Event evt) {
        if(evt.getType() == Event.MSG) {
            Message msg=(Message)evt.getArg();
            int len=msg.getLength();

            lock.lock();
            try {
                if(len > max_bytes) {
                    log.error("message length (" + len + " bytes) exceeded max_bytes (" + max_bytes + "); " +
                            "adjusting max_bytes to " + len);
                    max_bytes=len;
                }

                while(true) {
                    boolean size_exceeded=num_bytes_sent + len >= max_bytes,
                            time_exceeded=System.currentTimeMillis() > end_of_current_period;
                    if(!size_exceeded && !time_exceeded)
                        break;

                    if(time_exceeded) {
                        reset();
                    }
                    else { // size exceeded
                        long block_time=end_of_current_period - System.currentTimeMillis();
                        if(block_time > 0) {
                            try {
                                block.await(block_time, TimeUnit.MILLISECONDS);
                                num_blockings++;
                                total_block_time+=block_time;
                            }
                            catch(InterruptedException e) {
                            }
                        }
                    }
                }
            }
            finally {
                num_bytes_sent+=len;
                lock.unlock();
            }

            return down_prot.down(evt);
        }

        return down_prot.down(evt);
    }
    

    public void init() throws Exception {
        super.init();
        if(time_period <= 0)
            throw new IllegalArgumentException("time_period needs to be positive");
    }

    public void stop() {
        super.stop();
        reset();
    }

    protected void reset() {
        lock.lock();
        try {
            // blocking=false;
            num_bytes_sent=0L;
            end_of_current_period=System.currentTimeMillis() + time_period;
            block.signalAll();
        }
        finally {
            lock.unlock();
        }
    }
}
