/*
 * $Id: EndpointMessageProcessorsTestCase.java 22419 2011-07-15 03:41:06Z dirk.olmes $
 * --------------------------------------------------------------------------------------
 * Copyright (c) MuleSoft, Inc.  All rights reserved.  http://www.mulesoft.com
 *
 * The software in this package is published under the terms of the CPAL v1.0
 * license, a copy of which has been included with this distribution in the
 * LICENSE.txt file.
 */

package org.mule.test.integration.endpoints;

import org.mule.api.MuleMessage;
import org.mule.module.client.MuleClient;
import org.mule.tck.junit4.FunctionalTestCase;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

public class EndpointMessageProcessorsTestCase extends FunctionalTestCase
{

    private static final int TIMEOUT = 5000;

    @Override
    protected String getConfigResources()
    {
        return "org/mule/test/integration/endpoints/endpoint-message-processors.xml";
    }

    @Test
    public void testSynchronousOutbound() throws Exception
    {
        MuleClient client = new MuleClient(muleContext);
        
        MuleMessage response = client.send("vm://in1", "input", null);
        assertNotNull(response);
        assertEquals("input:A:B:service1:E:F:service2:G:H:C:D", response.getPayload());
    }

    @Test
    public void testAsynchronousOutbound() throws Exception
    {
        MuleClient client = new MuleClient(muleContext);
        
        MuleMessage response = client.send("vm://in2", "input", null);
        assertNotNull(response);
        assertEquals("input:A:B:service1:C:D", response.getPayload());

        response = client.request("vm://out2", TIMEOUT);
        assertNotNull(response);
        assertEquals("input:A:B:service1:E:F", response.getPayload());
    }

    @Test
    public void testLegacyAttributes() throws Exception
    {
        MuleClient client = new MuleClient(muleContext);
        
        MuleMessage response = client.send("vm://in3", "input", null);
        assertNotNull(response);
        assertEquals("input:A:B:service1:E:F:service2:G:H:C:D", response.getPayload());
    }

    @Test
    public void testRouters() throws Exception
    {
        MuleClient client = new MuleClient(muleContext);
        
        client.dispatch("vm://in4", "input1,input2,input3", null);

        MuleMessage response = client.request("vm://wiretap1", TIMEOUT);
        assertNotNull(response);
        assertEquals("input1,input2,input3 (tapped)", response.getPayload());

        response = client.request("vm://wiretap2", TIMEOUT);
        assertNotNull(response);
        assertTrue(response.getPayloadAsString().startsWith("input"));
        assertTrue(response.getPayloadAsString().endsWith(":A:B:service1 (tapped)"));
        response = client.request("vm://wiretap2", TIMEOUT);
        assertNotNull(response);
        assertTrue(response.getPayloadAsString().startsWith("input"));
        assertTrue(response.getPayloadAsString().endsWith(":A:B:service1 (tapped)"));
        response = client.request("vm://wiretap2", TIMEOUT);
        assertNotNull(response);
        assertTrue(response.getPayloadAsString().startsWith("input"));
        assertTrue(response.getPayloadAsString().endsWith(":A:B:service1 (tapped)"));
        response = client.request("vm://wiretap2", TIMEOUT);
        assertNull(response);

        response = client.request("vm://out4", TIMEOUT);
        assertNotNull(response);
        assertTrue(response.getPayloadAsString().startsWith("input"));
        assertTrue(response.getPayloadAsString().endsWith(":A:B:service1:E:F"));
        response = client.request("vm://out4", TIMEOUT);
        assertNotNull(response);
        assertTrue(response.getPayloadAsString().startsWith("input"));
        assertTrue(response.getPayloadAsString().endsWith(":A:B:service1:E:F"));
        response = client.request("vm://out4", TIMEOUT);
        assertNotNull(response);
        assertTrue(response.getPayloadAsString().startsWith("input"));
        assertTrue(response.getPayloadAsString().endsWith(":A:B:service1:E:F"));
        response = client.request("vm://out4", TIMEOUT);
        assertNull(response);
    }
}
