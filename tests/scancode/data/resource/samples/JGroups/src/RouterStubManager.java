/*
 * JBoss, Home of Professional Open Source.
 * Copyright 2009, Red Hat Middleware LLC, and individual contributors
 * as indicated by the @author tags. See the copyright.txt file in the
 * distribution for a full listing of individual contributors.
 *
 * This is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation; either version 2.1 of
 * the License, or (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this software; if not, write to the Free
 * Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
 * 02110-1301 USA, or see the FSF site: http://www.fsf.org.
 */
package org.jgroups.stack;

import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import org.jgroups.Address;
import org.jgroups.Event;
import org.jgroups.PhysicalAddress;
import org.jgroups.annotations.GuardedBy;
import org.jgroups.logging.Log;
import org.jgroups.logging.LogFactory;
import org.jgroups.util.TimeScheduler;

public class RouterStubManager implements RouterStub.ConnectionListener {

    @GuardedBy("reconnectorLock")
    private final Map<InetSocketAddress, Future<?>> futures = new HashMap<InetSocketAddress, Future<?>>();
    private final Lock reconnectorLock = new ReentrantLock();    
    private final List<RouterStub> stubs;
    
    private final Protocol owner;
    private final TimeScheduler timer;
    private final String channelName;
    private final Address logicalAddress;
    private final long interval;

    protected final Log log;

    public RouterStubManager(Protocol owner, String channelName, Address logicalAddress, long interval) {
        this.owner = owner;
        this.stubs = new CopyOnWriteArrayList<RouterStub>();             
        this.log = LogFactory.getLog(owner.getClass());     
        this.timer = owner.getTransport().getTimer();
        this.channelName = channelName;
        this.logicalAddress = logicalAddress;
        this.interval = interval;
    }
    
    private RouterStubManager(Protocol p) {
       this(p,null,null,0L);
    }
    
    public List<RouterStub> getStubs(){
        return stubs;
    }
    
    public RouterStub createAndRegisterStub(String routerHost, int routerPort, InetAddress bindAddress) {
        RouterStub s = new RouterStub(routerHost,routerPort,bindAddress,this);
        unregisterAndDestroyStub(s.getGossipRouterAddress());       
        stubs.add(s);   
        return s;
    }
    
    public void registerStub(RouterStub s) {        
        unregisterAndDestroyStub(s.getGossipRouterAddress());        
        stubs.add(s);           
    }
    
    public boolean unregisterStub(final RouterStub s) {
        return stubs.remove(s);
    }
    
    public RouterStub unregisterStub(final InetSocketAddress address) {
        if(address == null) 
            throw new IllegalArgumentException("Cannot remove null address");
        for (RouterStub s : stubs) {
            if (s.getGossipRouterAddress().equals(address)) {
                stubs.remove(address);
                return s;
            }
        }
        return null;
    }
    
    public boolean unregisterAndDestroyStub(final InetSocketAddress address) {
        RouterStub unregisteredStub = unregisterStub(address);
        if(unregisteredStub !=null) {
            unregisteredStub.destroy();
            return true;
        }
        return false;
    }
    
    public void disconnectStubs() {
        for (RouterStub stub : stubs) {
            try {
                stub.disconnect(channelName, logicalAddress);                
            } catch (Exception e) {
            }
        }       
    }
    
    public void destroyStubs() {
        for (RouterStub s : stubs) {
            stopReconnecting(s);
            s.destroy();            
        }
        stubs.clear();
    }

    public void startReconnecting(final RouterStub stub) {
        reconnectorLock.lock();
        try {
            InetSocketAddress routerAddress = stub.getGossipRouterAddress();
            Future<?> f = futures.get(routerAddress);
            if (f != null) {
                f.cancel(true);
                futures.remove(routerAddress);
            }

            final Runnable reconnector = new Runnable() {
                public void run() {
                    try {
                        if (log.isTraceEnabled()) log.trace("Reconnecting " + stub);                        
                        String logical_name = org.jgroups.util.UUID.get(logicalAddress);
                        PhysicalAddress physical_addr = (PhysicalAddress) owner.down(new Event(
                                        Event.GET_PHYSICAL_ADDRESS, logicalAddress));
                        List<PhysicalAddress> physical_addrs = Arrays.asList(physical_addr);
                        stub.connect(channelName, logicalAddress, logical_name, physical_addrs);
                        if (log.isTraceEnabled()) log.trace("Reconnected " + stub);                        
                    } catch (Throwable ex) {
                        if (log.isWarnEnabled())
                            log.warn("failed reconnecting stub to GR at "+ stub.getGossipRouterAddress() + ": " + ex);
                    }
                }
            };
            f = timer.scheduleWithFixedDelay(reconnector, 0, interval, TimeUnit.MILLISECONDS);
            futures.put(stub.getGossipRouterAddress(), f);
        } finally {
            reconnectorLock.unlock();
        }
    }

    public void stopReconnecting(final RouterStub stub) {
        reconnectorLock.lock();
        try {
            InetSocketAddress routerAddress = stub.getGossipRouterAddress();
            Future<?> f = futures.get(stub.getGossipRouterAddress());
            if (f != null) {
                f.cancel(true);
                futures.remove(routerAddress);
            }

            final Runnable pinger = new Runnable() {
                public void run() {
                    try {
                        if(log.isTraceEnabled()) log.trace("Pinging " + stub);                        
                        stub.checkConnection();
                        if(log.isTraceEnabled()) log.trace("Pinged " + stub);                        
                    } catch (Throwable ex) {
                        if (log.isWarnEnabled())
                            log.warn("failed pinging stub, GR at " + stub.getGossipRouterAddress()+ ": " + ex);
                    }
                }
            };
            f = timer.scheduleWithFixedDelay(pinger, 0, interval, TimeUnit.MILLISECONDS);
            futures.put(stub.getGossipRouterAddress(), f);
        } finally {
            reconnectorLock.unlock();
        }
    }
   

    public void connectionStatusChange(RouterStub stub, RouterStub.ConnectionStatus newState) {
        if (newState == RouterStub.ConnectionStatus.CONNECTION_BROKEN) {
            stub.interrupt();
            stub.destroy();
            startReconnecting(stub);
        } else if (newState == RouterStub.ConnectionStatus.CONNECTED) {
            stopReconnecting(stub);
        } else if (newState == RouterStub.ConnectionStatus.DISCONNECTED) {
            // wait for disconnect ack;
            try {
                stub.join(interval);
            } catch (InterruptedException e) {
            }
        }
    }
    
    public static RouterStubManager emptyGossipClientStubManager(Protocol p) {
        return new RouterStubManager(p);
    }
}
