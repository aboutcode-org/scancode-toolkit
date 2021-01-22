/*
 * JBoss, Home of Professional Open Source
 * Copyright 2005, JBoss Inc., and individual contributors as indicated
 * by the @authors tag. See the copyright.txt in the distribution for a
 * full listing of individual contributors.
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
package org.jgroups.auth;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

import org.jgroups.Event;
import org.jgroups.Message;
import org.jgroups.PhysicalAddress;
import org.jgroups.annotations.Property;
import org.jgroups.util.Util;

/**
 * <p>
 * The FixedMemberShipToken object predefines a list of IP addresses and ports that can join the
 * group.
 * </p>
 * <p>
 * Configuration parameters for this example are shown below:
 * </p>
 * <ul>
 * <li>fixed_members_value (required) = List of IP addresses & ports (optionally) - ports must be
 * seperated by a '/' e.g. 127.0.0.1/1010*127.0.0.1/4567</li>
 * <li>fixed_members_seperator (required) = The seperator used between IP addresses - e.g. *</li>
 * </ul>
 * 
 * @author Chris Mills (millsy@jboss.com)
 */
public class FixedMembershipToken extends AuthToken {
    private List<String> memberList = null;
    private String token = "emptyToken";

    @Property
    private String fixed_members_seperator = ",";
    private static final long serialVersionUID = 4717069536900221681L;

    public FixedMembershipToken() {
    }

    public String getName() {
        return "org.jgroups.auth.FixedMembershipToken";
    }

    @Property
    public void setFixedMembersSeparator(String value) {
        fixed_members_seperator = value;
    }

    public boolean authenticate(AuthToken token, Message msg) {
        if ((token != null) && (token instanceof FixedMembershipToken) && (this.memberList != null)) {
            PhysicalAddress src = (PhysicalAddress) auth.down(new Event(Event.GET_PHYSICAL_ADDRESS,
                            msg.getSrc()));
            if (src == null) {
                if (log.isErrorEnabled())
                    log.error("didn't find physical address for " + msg.getSrc());
                return false;
            }

            String sourceAddressWithPort = src.toString();
            String sourceAddressWithoutPort = sourceAddressWithPort.substring(0,
                            sourceAddressWithPort.indexOf(":"));

            if (log.isDebugEnabled()) {
                log.debug("AUTHToken received from " + sourceAddressWithPort);
            }

            for (String member : memberList) {
                if (hasPort(member)) {
                    if (member.equals(sourceAddressWithPort))
                        return true;
                } else {
                    if (member.equals(sourceAddressWithoutPort))
                        return true;
                }
            }
            return false;
        }

        if (log.isWarnEnabled()) {
            log.warn("Invalid AuthToken instance - wrong type or null");
        }
        return false;
    }

    private static boolean hasPort(String member) {
        return member.contains(":");
    }

    @Property(name = "fixed_members_value")
    public void setMemberList(String list) {
        memberList = new ArrayList<String>();
        StringTokenizer memberListTokenizer = new StringTokenizer(list, fixed_members_seperator);
        while (memberListTokenizer.hasMoreTokens()) {
            memberList.add(memberListTokenizer.nextToken().replace('/', ':'));
        }
    }

    /**
     * Required to serialize the object to pass across the wire
     * 
     * @param out
     * @throws java.io.IOException
     */
    public void writeTo(DataOutputStream out) throws IOException {
        if (log.isDebugEnabled()) {
            log.debug("SimpleToken writeTo()");
        }
        Util.writeString(this.token, out);
    }

    /**
     * Required to deserialize the object when read in from the wire
     * 
     * @param in
     * @throws IOException
     * @throws IllegalAccessException
     * @throws InstantiationException
     */
    public void readFrom(DataInputStream in) throws IOException, IllegalAccessException,
                    InstantiationException {
        if (log.isDebugEnabled()) {
            log.debug("SimpleToken readFrom()");
        }
        this.token = Util.readString(in);
    }
}
