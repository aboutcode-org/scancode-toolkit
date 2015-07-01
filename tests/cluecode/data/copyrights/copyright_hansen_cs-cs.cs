/*
 * Ra-Brix - A Modular-based Framework for building 
 * Web Applications Copyright 2009 - Thomas Hansen 
 * thomas@ra-ajax.org. Unless permission is 
 * explicitly given this code is licensed under the 
 * GNU Affero GPL version 3 which can be found in the 
 * license.txt file on disc.
 * 
 */

using System;

namespace Ra.Brix.Data
{
    /**
     * Used to mark entity objects as serializable. If a property is
     * marked with this attribute then it will be possible to serialise
     * that property. Notice that you still need to mark you classes with the
     * ActiveRecordAttribute. Also only properties, and not fields and such
     * can be marked as serializable with this attribute.
     */
    [AttributeUsage(AttributeTargets.Property, AllowMultiple=false)]
    public class ActiveFieldAttribute : Attribute
    {
        /**
         * If true then this is a one-to-x relationship which
         * means that the type owns this instance and will also delete
         * the instance if the object itself is deleted. If it is false
         * then this indicate a many-to-x relationship 
         * and means that the object does NOT own this property and the 
         * property will NOT be deleted when the object is deleted.
         * If it is false then the property will also NOT be saved whenever
         * the not owning object is being saved.
         * Default value is true - which means that the object will
         * be saved when parent object is saved, and also deleted when
         * the parent object is being deleted.
         */
        public bool IsOwner = true;
    }
}