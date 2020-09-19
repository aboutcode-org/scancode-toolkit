package org.jgroups.stack;

import org.jgroups.Address;
import org.jgroups.PhysicalAddress;
import org.jgroups.logging.Log;
import org.jgroups.logging.LogFactory;
import org.jgroups.protocols.PingData;
import org.jgroups.protocols.TUNNEL.StubReceiver;
import org.jgroups.util.Util;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketException;
import java.util.ArrayList;
import java.util.List;

/**
 * Client stub that talks to a remote GossipRouter
 * @author Bela Ban
 * @version $Id: RouterStub.java,v 1.62 2010/06/09 14:22:00 belaban Exp $
 */
public class RouterStub {

    public static enum ConnectionStatus {INITIAL, CONNECTION_BROKEN, CONNECTION_ESTABLISHED, CONNECTED,DISCONNECTED};

    private final String router_host; // name of the router host

    private final int router_port; // port on which router listens on

    private Socket sock=null; // socket connecting to the router

    private DataOutputStream output=null;

    private DataInputStream input=null;

    private volatile ConnectionStatus connectionState=ConnectionStatus.INITIAL;

    private static final Log log=LogFactory.getLog(RouterStub.class);

    private final ConnectionListener conn_listener;

    private final InetAddress bind_addr;

    private int sock_conn_timeout=3000; // max number of ms to wait for socket establishment to
    // GossipRouter

    private int sock_read_timeout=3000; // max number of ms to wait for socket reads (0 means block
    // forever, or until the sock is closed)

    private boolean tcp_nodelay=true;
    
    private StubReceiver receiver;

    public interface ConnectionListener {
        void connectionStatusChange(RouterStub stub, ConnectionStatus state);
    }

    /**
     * Creates a stub for a remote Router object.
     * @param routerHost The name of the router's host
     * @param routerPort The router's port
     * @throws SocketException
     */
    public RouterStub(String routerHost, int routerPort, InetAddress bindAddress, ConnectionListener l) {
        router_host=routerHost != null? routerHost : "localhost";
        router_port=routerPort;
        bind_addr=bindAddress;
        conn_listener=l;        
    }
    
    public synchronized void setReceiver(StubReceiver receiver) {
        this.receiver = receiver;
    }
    
    public synchronized StubReceiver  getReceiver() {
        return receiver;
    }

    public boolean isTcpNoDelay() {
        return tcp_nodelay;
    }

    public void setTcpNoDelay(boolean tcp_nodelay) {
        this.tcp_nodelay=tcp_nodelay;
    }

    public synchronized void interrupt() {
        if(receiver != null) {
            Thread thread = receiver.getThread();
            if(thread != null)
                thread.interrupt();
        }
    }
    
    public synchronized void join(long wait) throws InterruptedException {
        if(receiver != null) {
            Thread thread = receiver.getThread();
            if(thread != null)
                thread.join(wait);
        }
    }


    public int getSocketConnectionTimeout() {
        return sock_conn_timeout;
    }

    public void setSocketConnectionTimeout(int sock_conn_timeout) {
        this.sock_conn_timeout=sock_conn_timeout;
    }

    public int getSocketReadTimeout() {
        return sock_read_timeout;
    }

    public void setSocketReadTimeout(int sock_read_timeout) {
        this.sock_read_timeout=sock_read_timeout;
    }

    public boolean isConnected() {
        return !(connectionState == ConnectionStatus.CONNECTION_BROKEN || connectionState == ConnectionStatus.INITIAL);
    }

    public ConnectionStatus getConnectionStatus() {
        return connectionState;
    }


    /**
     * Register this process with the router under <code>group</code>.
     * @param group The name of the group under which to register
     */
    public synchronized void connect(String group, Address addr, String logical_name, List<PhysicalAddress> phys_addrs) throws Exception {
        doConnect();
        GossipData request=new GossipData(GossipRouter.CONNECT, group, addr, logical_name, phys_addrs);
        request.writeTo(output);
        output.flush();
        byte result = input.readByte();
        if(result == GossipRouter.CONNECT_OK) {
            connectionStateChanged(ConnectionStatus.CONNECTED);   
        } else {
            connectionStateChanged(ConnectionStatus.DISCONNECTED);
            throw new Exception("Connect failed received from GR " + getGossipRouterAddress());
        }
    }

    public synchronized void doConnect() throws Exception {
        if(!isConnected()) {
            try {
                sock=new Socket();
                sock.bind(new InetSocketAddress(bind_addr, 0));
                sock.setSoTimeout(sock_read_timeout);
                sock.setSoLinger(true, 2);
                sock.setTcpNoDelay(tcp_nodelay);
                sock.setKeepAlive(true);
                Util.connect(sock, new InetSocketAddress(router_host, router_port), sock_conn_timeout);
                output=new DataOutputStream(sock.getOutputStream());
                input=new DataInputStream(sock.getInputStream());                
                connectionStateChanged(ConnectionStatus.CONNECTION_ESTABLISHED);
            }
            catch(Exception e) {                
                Util.close(sock);
                Util.close(input);
                Util.close(output);
                connectionStateChanged(ConnectionStatus.CONNECTION_BROKEN);
                throw new Exception("Could not connect to " + getGossipRouterAddress() , e);
            }
        }
    }

    /**
     * Checks whether the connection is open
     * @return
     */
    public synchronized void checkConnection() {
        GossipData request=new GossipData(GossipRouter.PING);
        try {
            request.writeTo(output);
            output.flush();
        }
        catch(IOException e) {
            connectionStateChanged(ConnectionStatus.CONNECTION_BROKEN);
        }
    }


    public synchronized void disconnect(String group, Address addr) {
        try {
            GossipData request=new GossipData(GossipRouter.DISCONNECT, group, addr);
            request.writeTo(output);
            output.flush();
        }
        catch(Exception e) {
        } finally {
            connectionStateChanged(ConnectionStatus.DISCONNECTED);
        }
    }

    public synchronized void destroy() {
        try {
            GossipData request = new GossipData(GossipRouter.CLOSE);
            request.writeTo(output);
            output.flush();
        } catch (Exception e) {
        } finally {
            Util.close(output);
            Util.close(input);
            Util.close(sock);
        }
    }
    
    
    /*
     * Used only in testing, never access socket directly
     * 
     */
    public Socket getSocket() {
        return sock;
    }


    public synchronized List<PingData> getMembers(final String group) throws Exception {
        List<PingData> retval=new ArrayList<PingData>();
        try {

            if(!isConnected() || input == null) throw new Exception ("not connected");
            // we might get a spurious SUSPECT message from the router, just ignore it
            if(input.available() > 0) // fixes https://jira.jboss.org/jira/browse/JGRP-1151
                input.skipBytes(input.available());

            GossipData request=new GossipData(GossipRouter.GOSSIP_GET, group, null);
            request.writeTo(output);
            output.flush();

            short num_rsps=input.readShort();
            for(int i=0; i < num_rsps; i++) {
                PingData rsp=new PingData();
                rsp.readFrom(input);
                retval.add(rsp);
            }
        }       
        catch(Exception e) {           
            connectionStateChanged(ConnectionStatus.CONNECTION_BROKEN);
            throw new Exception("Connection to " + getGossipRouterAddress() + " broken. Could not send GOSSIP_GET request", e);
        }
        return retval;
    }

    public InetSocketAddress getGossipRouterAddress() {
        return new InetSocketAddress(router_host, router_port);
    }
    
    public String toString() {
        return "RouterStub[localsocket=" + ((sock != null) ? sock.getLocalSocketAddress().toString()
                        : "null")+ ",router_host=" + router_host + "::" + router_port
                                        + ",connected=" + isConnected() + "]";
    }

    public void sendToAllMembers(String group, byte[] data, int offset, int length) throws Exception {
        sendToMember(group, null, data, offset, length); // null destination represents mcast
    }

    public synchronized void sendToMember(String group, Address dest, byte[] data, int offset, int length) throws Exception {
        try {
            GossipData request = new GossipData(GossipRouter.MESSAGE, group, dest, data, offset, length);
            request.writeTo(output);
            output.flush();
        } catch (Exception e) {
            connectionStateChanged(ConnectionStatus.CONNECTION_BROKEN);
            throw new Exception("Connection to " + getGossipRouterAddress()
                            + " broken. Could not send message to " + dest, e);
        }
    }

    public DataInputStream getInputStream() {
        return input;
    }

    private void connectionStateChanged(ConnectionStatus newState) {
        boolean notify=connectionState != newState;
        connectionState=newState;
        if(notify && conn_listener != null) {
            try {
                conn_listener.connectionStatusChange(this, newState);
            }
            catch(Throwable t) {
                log.error("failed notifying ConnectionListener " + conn_listener, t);
            }
        }
    }
}
