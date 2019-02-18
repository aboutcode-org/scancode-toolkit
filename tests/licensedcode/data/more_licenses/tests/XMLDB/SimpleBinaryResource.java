package org.xmldb.api.sdk.modules;

/*
 *  The XML:DB Initiative Software License, Version 1.0
 *
 *
 * Copyright (c) 2000-2001 The XML:DB Initiative.  All rights
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:
 *       "This product includes software developed by the
 *        XML:DB Initiative (http://www.xmldb.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The name "XML:DB Initiative" must not be used to endorse or
 *    promote products derived from this software without prior written
 *    permission. For written permission, please contact info@xmldb.org.
 *
 * 5. Products derived from this software may not be called "XML:DB",
 *    nor may "XML:DB" appear in their name, without prior written
 *    permission of the XML:DB Initiative.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the XML:DB Initiative. For more information
 * on the XML:DB Initiative, please see <http://www.xmldb.org/>.
 */

import org.xmldb.api.base.*;
import org.xmldb.api.modules.*;

/**
 * Resource for encapsulation of binary data that is stored in the data base.
 * Support for BinaryResources is optional.<p />
 *
 */
public abstract class SimpleBinaryResource extends BaseResource 
      implements BinaryResource {
   protected byte[] content = null;
   
   /**
    * Create a new BinaryResource without any content.
    */
   public SimpleBinaryResource (Collection parent, String id) {
      this(parent, id, null);
   }

   /**
    * Create a fully initialized BinaryResource
    */
   public SimpleBinaryResource (Collection parent, String id, byte[] content) {
      super(parent, id);      
      this.content = content;
   }
   
   /**
    * Returns the resource type for this Resource. 
    * 
    * @return the resource type for the Resource.     
    */
   public String getResourceType() throws XMLDBException {
      return RESOURCE_TYPE;
   }

   /**
    * Retrieves the content from the resource. The type of the content varies
    * depending what type of resource is being used.
    *
    * @return the content of the resource.
    */
   public Object getContent() throws XMLDBException {      
      return content;
   }

   /**
    * Sets the content for this resource. The type of content that can be set
    * depends on the type of resource being used.
    *
    * @param value the content value to set for the resource.
    */
   public void setContent(Object value) throws XMLDBException {
      if ( ! (value instanceof byte[]) ) {
         throw new XMLDBException(ErrorCodes.WRONG_CONTENT_TYPE);
      }
      
      this.content = (byte[]) value;
   }
}

