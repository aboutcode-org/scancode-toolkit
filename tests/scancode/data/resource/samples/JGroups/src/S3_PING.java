package org.jgroups.protocols;

import org.jgroups.Address;
import org.jgroups.annotations.Experimental;
import org.jgroups.annotations.Property;
import org.jgroups.annotations.Unsupported;
import org.jgroups.util.Util;
import org.xml.sax.Attributes;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.DefaultHandler;
import org.xml.sax.helpers.XMLReaderFactory;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLEncoder;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

import static java.lang.String.valueOf;


/**
 * Discovery protocol using Amazon's S3 storage. The S3 access code reuses the example shipped by Amazon.
 * This protocol is unsupported and experimental !
 * @author Bela Ban
 * @version $Id: S3_PING.java,v 1.11 2010/06/18 04:39:08 belaban Exp $
 */
@Experimental
public class S3_PING extends FILE_PING {

    @Property(description="The access key to AWS (S3)")
    protected String access_key=null;

    @Property(description="The secret access key to AWS (S3)")
    protected String secret_access_key=null;

    @Property(description="When non-null, we set location to prefix-UUID")
    protected String prefix=null;

    protected AWSAuthConnection conn=null;


  
    public void init() throws Exception {
        super.init();
        if(access_key == null || secret_access_key == null)
            throw new IllegalArgumentException("access_key and secret_access_key must be non-null");

        conn=new AWSAuthConnection(access_key, secret_access_key);

        if(prefix != null && prefix.length() > 0) {
            ListAllMyBucketsResponse bucket_list=conn.listAllMyBuckets(null);
            List buckets=bucket_list.entries;
            if(buckets != null) {
                boolean found=false;
                for(Object tmp: buckets) {
                    if(tmp instanceof Bucket) {
                        Bucket bucket=(Bucket)tmp;
                        if(bucket.name.startsWith(prefix)) {
                            location=bucket.name;
                            found=true;
                        }
                    }
                }
                if(!found) {
                    location=prefix + "-" + java.util.UUID.randomUUID().toString();
                }
            }
        }


        if(!conn.checkBucketExists(location)) {
            conn.createBucket(location, AWSAuthConnection.LOCATION_DEFAULT, null).connection.getResponseMessage();
        }

        Runtime.getRuntime().addShutdownHook(new Thread() {
            public void run() {
                remove(group_addr, local_addr);
            }
        });
    }

    protected void createRootDir() {
        ; // do *not* create root file system (don't remove !)
    }

    protected List<PingData> readAll(String clustername) {
        if(clustername == null)
            return null;

        List<PingData> retval=new ArrayList<PingData>();
        try {
            ListBucketResponse rsp=conn.listBucket(location, clustername, null, null, null);
            if(rsp.entries != null) {
                for(Iterator<ListEntry> it=rsp.entries.iterator(); it.hasNext();) {
                    ListEntry key=it.next();
                    GetResponse val=conn.get(location, key.key, null);
                    if(val.object != null) {
                        byte[] buf=val.object.data;
                        if(buf != null) {
                            try {
                                PingData data=(PingData)Util.objectFromByteBuffer(buf);
                                retval.add(data);
                            }
                            catch(Exception e) {
                                log.error("failed marshalling buffer to address", e);
                            }
                        }
                    }
                }
            }

            return retval;
        }
        catch(IOException ex) {
            log.error("failed reading addresses", ex);
            return retval;
        }
    }


    protected void writeToFile(PingData data, String clustername) {
        if(clustername == null || data == null)
            return;
        String filename=local_addr instanceof org.jgroups.util.UUID? ((org.jgroups.util.UUID)local_addr).toStringLong() : local_addr.toString();
        String key=clustername + "/" + filename;
        try {
            Map headers=new TreeMap();
            headers.put("Content-Type", Arrays.asList("text/plain"));
            byte[] buf=Util.objectToByteBuffer(data);
            S3Object val=new S3Object(buf, null);
            conn.put(location, key, val, headers).connection.getResponseMessage();
        }
        catch(Exception e) {
            log.error("failed marshalling " + data + " to buffer", e);
        }
    }


    protected void remove(String clustername, Address addr) {
        if(clustername == null || addr == null)
            return;
        String filename=addr instanceof org.jgroups.util.UUID? ((org.jgroups.util.UUID)addr).toStringLong() : addr.toString();
        String key=clustername + "/" + filename;
        try {
            Map headers=new TreeMap();
            headers.put("Content-Type", Arrays.asList("text/plain"));
            conn.delete(location, key, headers).connection.getResponseMessage();
            if(log.isTraceEnabled())
                log.trace("removing " + location + "/" + key);
        }
        catch(Exception e) {
            log.error("failure removing data", e);
        }
    }




    


    /**
     * The following classes have been copied from Amazon's sample code
     */
    static class AWSAuthConnection {
        public static final String LOCATION_DEFAULT=null;
        public static final String LOCATION_EU="EU";

        private String awsAccessKeyId;
        private String awsSecretAccessKey;
        private boolean isSecure;
        private String server;
        private int port;
        private CallingFormat callingFormat;

        public AWSAuthConnection(String awsAccessKeyId, String awsSecretAccessKey) {
            this(awsAccessKeyId, awsSecretAccessKey, true);
        }

        public AWSAuthConnection(String awsAccessKeyId, String awsSecretAccessKey, boolean isSecure) {
            this(awsAccessKeyId, awsSecretAccessKey, isSecure, Utils.DEFAULT_HOST);
        }

        public AWSAuthConnection(String awsAccessKeyId, String awsSecretAccessKey, boolean isSecure,
                                 String server) {
            this(awsAccessKeyId, awsSecretAccessKey, isSecure, server,
                 isSecure? Utils.SECURE_PORT : Utils.INSECURE_PORT);
        }

        public AWSAuthConnection(String awsAccessKeyId, String awsSecretAccessKey, boolean isSecure,
                                 String server, int port) {
            this(awsAccessKeyId, awsSecretAccessKey, isSecure, server, port, CallingFormat.getSubdomainCallingFormat());

        }

        public AWSAuthConnection(String awsAccessKeyId, String awsSecretAccessKey, boolean isSecure,
                                 String server, CallingFormat format) {
            this(awsAccessKeyId, awsSecretAccessKey, isSecure, server,
                 isSecure? Utils.SECURE_PORT : Utils.INSECURE_PORT,
                 format);
        }

        /**
         * Create a new interface to interact with S3 with the given credential and connection
         * parameters
         * @param awsAccessKeyId     Your user key into AWS
         * @param awsSecretAccessKey The secret string used to generate signatures for authentication.
         * @param isSecure           use SSL encryption
         * @param server             Which host to connect to.  Usually, this will be s3.amazonaws.com
         * @param port               Which port to use.
         * @param format             Type of request Regular/Vanity or Pure Vanity domain
         */
        public AWSAuthConnection(String awsAccessKeyId, String awsSecretAccessKey, boolean isSecure,
                                 String server, int port, CallingFormat format) {
            this.awsAccessKeyId=awsAccessKeyId;
            this.awsSecretAccessKey=awsSecretAccessKey;
            this.isSecure=isSecure;
            this.server=server;
            this.port=port;
            this.callingFormat=format;
        }

        /**
         * Creates a new bucket.
         * @param bucket   The name of the bucket to create.
         * @param headers  A Map of String to List of Strings representing the http headers to pass (can be null).
         */
        public Response createBucket(String bucket, Map headers) throws IOException {
            return createBucket(bucket, null, headers);
        }

        /**
         * Creates a new bucket.
         * @param bucket   The name of the bucket to create.
         * @param location Desired location ("EU") (or null for default).
         * @param headers  A Map of String to List of Strings representing the http
         *                 headers to pass (can be null).
         * @throws IllegalArgumentException on invalid location
         */
        public Response createBucket(String bucket, String location, Map headers) throws IOException {
            String body;
            if(location == null) {
                body=null;
            }
            else if(LOCATION_EU.equals(location)) {
                if(!callingFormat.supportsLocatedBuckets())
                    throw new IllegalArgumentException("Creating location-constrained bucket with unsupported calling-format");
                body="<CreateBucketConstraint><LocationConstraint>" + location + "</LocationConstraint></CreateBucketConstraint>";
            }
            else
                throw new IllegalArgumentException("Invalid Location: " + location);

            // validate bucket name
            if(!Utils.validateBucketName(bucket, callingFormat))
                throw new IllegalArgumentException("Invalid Bucket Name: " + bucket);

            HttpURLConnection request=makeRequest("PUT", bucket, "", null, headers);
            if(body != null) {
                request.setDoOutput(true);
                request.getOutputStream().write(body.getBytes("UTF-8"));
            }
            return new Response(request);
        }

        /**
         * Check if the specified bucket exists (via a HEAD request)
         * @param bucket The name of the bucket to check
         * @return true if HEAD access returned success
         */
        public boolean checkBucketExists(String bucket) throws IOException {
            HttpURLConnection response=makeRequest("HEAD", bucket, "", null, null);
            int httpCode=response.getResponseCode();

            if(httpCode >= 200 && httpCode < 300)
                return true;
            if(httpCode == HttpURLConnection.HTTP_NOT_FOUND) // bucket doesn't exist
                return false;
            throw new IOException("bucket '" + bucket + "' could not be accessed (rsp=" +
                    httpCode + " (" + response.getResponseMessage() + "). Maybe the bucket is owned by somebody else or " +
                    "the authentication failed");

        }

        /**
         * Lists the contents of a bucket.
         * @param bucket  The name of the bucket to create.
         * @param prefix  All returned keys will start with this string (can be null).
         * @param marker  All returned keys will be lexographically greater than
         *                this string (can be null).
         * @param maxKeys The maximum number of keys to return (can be null).
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public ListBucketResponse listBucket(String bucket, String prefix, String marker,
                                             Integer maxKeys, Map headers) throws IOException {
            return listBucket(bucket, prefix, marker, maxKeys, null, headers);
        }

        /**
         * Lists the contents of a bucket.
         * @param bucket    The name of the bucket to list.
         * @param prefix    All returned keys will start with this string (can be null).
         * @param marker    All returned keys will be lexographically greater than
         *                  this string (can be null).
         * @param maxKeys   The maximum number of keys to return (can be null).
         * @param delimiter Keys that contain a string between the prefix and the first
         *                  occurrence of the delimiter will be rolled up into a single element.
         * @param headers   A Map of String to List of Strings representing the http
         *                  headers to pass (can be null).
         */
        public ListBucketResponse listBucket(String bucket, String prefix, String marker,
                                             Integer maxKeys, String delimiter, Map headers) throws IOException {

            Map pathArgs=Utils.paramsForListOptions(prefix, marker, maxKeys, delimiter);
            return new ListBucketResponse(makeRequest("GET", bucket, "", pathArgs, headers));
        }

        /**
         * Deletes a bucket.
         * @param bucket  The name of the bucket to delete.
         * @param headers A Map of String to List of Strings representing the http headers to pass (can be null).
         */
        public Response deleteBucket(String bucket, Map headers) throws IOException {
            return new Response(makeRequest("DELETE", bucket, "", null, headers));
        }

        /**
         * Writes an object to S3.
         * @param bucket  The name of the bucket to which the object will be added.
         * @param key     The name of the key to use.
         * @param object  An S3Object containing the data to write.
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public Response put(String bucket, String key, S3Object object, Map headers) throws IOException {
            HttpURLConnection request=
                    makeRequest("PUT", bucket, Utils.urlencode(key), null, headers, object);

            request.setDoOutput(true);
            request.getOutputStream().write(object.data == null? new byte[]{} : object.data);

            return new Response(request);
        }

        /**
         * Creates a copy of an existing S3 Object.  In this signature, we will copy the
         * existing metadata.  The default access control policy is private; if you want
         * to override it, please use x-amz-acl in the headers.
         * @param sourceBucket      The name of the bucket where the source object lives.
         * @param sourceKey         The name of the key to copy.
         * @param destinationBucket The name of the bucket to which the object will be added.
         * @param destinationKey    The name of the key to use.
         * @param headers           A Map of String to List of Strings representing the http
         *                          headers to pass (can be null).  You may wish to set the x-amz-acl header appropriately.
         */
        public Response copy(String sourceBucket, String sourceKey, String destinationBucket, String destinationKey, Map headers)
                throws IOException {
            S3Object object=new S3Object(new byte[]{}, new HashMap());
            headers=headers == null? new HashMap() : new HashMap(headers);
            headers.put("x-amz-copy-source", Arrays.asList(sourceBucket + "/" + sourceKey));
            headers.put("x-amz-metadata-directive", Arrays.asList("COPY"));
            return verifyCopy(put(destinationBucket, destinationKey, object, headers));
        }

        /**
         * Creates a copy of an existing S3 Object.  In this signature, we will replace the
         * existing metadata.  The default access control policy is private; if you want
         * to override it, please use x-amz-acl in the headers.
         * @param sourceBucket      The name of the bucket where the source object lives.
         * @param sourceKey         The name of the key to copy.
         * @param destinationBucket The name of the bucket to which the object will be added.
         * @param destinationKey    The name of the key to use.
         * @param metadata          A Map of String to List of Strings representing the S3 metadata
         *                          for the new object.
         * @param headers           A Map of String to List of Strings representing the http
         *                          headers to pass (can be null).  You may wish to set the x-amz-acl header appropriately.
         */
        public Response copy(String sourceBucket, String sourceKey, String destinationBucket, String destinationKey, Map metadata, Map headers)
                throws IOException {
            S3Object object=new S3Object(new byte[]{}, metadata);
            headers=headers == null? new HashMap() : new HashMap(headers);
            headers.put("x-amz-copy-source", Arrays.asList(sourceBucket + "/" + sourceKey));
            headers.put("x-amz-metadata-directive", Arrays.asList("REPLACE"));
            return verifyCopy(put(destinationBucket, destinationKey, object, headers));
        }

        /**
         * Copy sometimes returns a successful response and starts to send whitespace
         * characters to us.  This method processes those whitespace characters and
         * will throw an exception if the response is either unknown or an error.
         * @param response Response object from the PUT request.
         * @return The response with the input stream drained.
         * @throws IOException If anything goes wrong.
         */
        private static Response verifyCopy(Response response) throws IOException {
            if(response.connection.getResponseCode() < 400) {
                byte[] body=GetResponse.slurpInputStream(response.connection.getInputStream());
                String message=new String(body);
                if(message.contains("<Error")) {
                    throw new IOException(message.substring(message.indexOf("<Error")));
                }
                else if(message.contains("</CopyObjectResult>")) {
                    // It worked!
                }
                else {
                    throw new IOException("Unexpected response: " + message);
                }
            }
            return response;
        }

        /**
         * Reads an object from S3.
         * @param bucket  The name of the bucket where the object lives.
         * @param key     The name of the key to use.
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public GetResponse get(String bucket, String key, Map headers) throws IOException {
            return new GetResponse(makeRequest("GET", bucket, Utils.urlencode(key), null, headers));
        }

        /**
         * Deletes an object from S3.
         * @param bucket  The name of the bucket where the object lives.
         * @param key     The name of the key to use.
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public Response delete(String bucket, String key, Map headers) throws IOException {
            return new Response(makeRequest("DELETE", bucket, Utils.urlencode(key), null, headers));
        }

        /**
         * Get the requestPayment xml document for a given bucket
         * @param bucket  The name of the bucket
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public GetResponse getBucketRequestPayment(String bucket, Map headers) throws IOException {
            Map pathArgs=new HashMap();
            pathArgs.put("requestPayment", null);
            return new GetResponse(makeRequest("GET", bucket, "", pathArgs, headers));
        }

        /**
         * Write a new requestPayment xml document for a given bucket
         * @param bucket        The name of the bucket
         * @param requestPaymentXMLDoc
         * @param headers       A Map of String to List of Strings representing the http
         *                      headers to pass (can be null).
         */
        public Response putBucketRequestPayment(String bucket, String requestPaymentXMLDoc, Map headers)
                throws IOException {
            Map pathArgs=new HashMap();
            pathArgs.put("requestPayment", null);
            S3Object object=new S3Object(requestPaymentXMLDoc.getBytes(), null);
            HttpURLConnection request=makeRequest("PUT", bucket, "", pathArgs, headers, object);

            request.setDoOutput(true);
            request.getOutputStream().write(object.data == null? new byte[]{} : object.data);

            return new Response(request);
        }

        /**
         * Get the logging xml document for a given bucket
         * @param bucket  The name of the bucket
         * @param headers A Map of String to List of Strings representing the http headers to pass (can be null).
         */
        public GetResponse getBucketLogging(String bucket, Map headers) throws IOException {
            Map pathArgs=new HashMap();
            pathArgs.put("logging", null);
            return new GetResponse(makeRequest("GET", bucket, "", pathArgs, headers));
        }

        /**
         * Write a new logging xml document for a given bucket
         * @param loggingXMLDoc The xml representation of the logging configuration as a String
         * @param bucket        The name of the bucket
         * @param headers       A Map of String to List of Strings representing the http
         *                      headers to pass (can be null).
         */
        public Response putBucketLogging(String bucket, String loggingXMLDoc, Map headers) throws IOException {
            Map pathArgs=new HashMap();
            pathArgs.put("logging", null);
            S3Object object=new S3Object(loggingXMLDoc.getBytes(), null);
            HttpURLConnection request=makeRequest("PUT", bucket, "", pathArgs, headers, object);

            request.setDoOutput(true);
            request.getOutputStream().write(object.data == null? new byte[]{} : object.data);

            return new Response(request);
        }

        /**
         * Get the ACL for a given bucket
         * @param bucket  The name of the bucket where the object lives.
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public GetResponse getBucketACL(String bucket, Map headers) throws IOException {
            return getACL(bucket, "", headers);
        }

        /**
         * Get the ACL for a given object (or bucket, if key is null).
         * @param bucket  The name of the bucket where the object lives.
         * @param key     The name of the key to use.
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public GetResponse getACL(String bucket, String key, Map headers) throws IOException {
            if(key == null) key="";

            Map pathArgs=new HashMap();
            pathArgs.put("acl", null);

            return new GetResponse(
                    makeRequest("GET", bucket, Utils.urlencode(key), pathArgs, headers)
            );
        }

        /**
         * Write a new ACL for a given bucket
         * @param aclXMLDoc The xml representation of the ACL as a String
         * @param bucket    The name of the bucket where the object lives.
         * @param headers   A Map of String to List of Strings representing the http headers to pass (can be null).
         */
        public Response putBucketACL(String bucket, String aclXMLDoc, Map headers) throws IOException {
            return putACL(bucket, "", aclXMLDoc, headers);
        }

        /**
         * Write a new ACL for a given object
         * @param aclXMLDoc The xml representation of the ACL as a String
         * @param bucket    The name of the bucket where the object lives.
         * @param key       The name of the key to use.
         * @param headers   A Map of String to List of Strings representing the http
         *                  headers to pass (can be null).
         */
        public Response putACL(String bucket, String key, String aclXMLDoc, Map headers)
                throws IOException {
            S3Object object=new S3Object(aclXMLDoc.getBytes(), null);

            Map pathArgs=new HashMap();
            pathArgs.put("acl", null);

            HttpURLConnection request=
                    makeRequest("PUT", bucket, Utils.urlencode(key), pathArgs, headers, object);

            request.setDoOutput(true);
            request.getOutputStream().write(object.data == null? new byte[]{} : object.data);

            return new Response(request);
        }

        public LocationResponse getBucketLocation(String bucket)
                throws IOException {
            Map pathArgs=new HashMap();
            pathArgs.put("location", null);
            return new LocationResponse(makeRequest("GET", bucket, "", pathArgs, null));
        }


        /**
         * List all the buckets created by this account.
         * @param headers A Map of String to List of Strings representing the http
         *                headers to pass (can be null).
         */
        public ListAllMyBucketsResponse listAllMyBuckets(Map headers)
                throws IOException {
            return new ListAllMyBucketsResponse(makeRequest("GET", "", "", null, headers));
        }


        /**
         * Make a new HttpURLConnection without passing an S3Object parameter.
         * Use this method for key operations that do require arguments
         * @param method     The method to invoke
         * @param bucketName the bucket this request is for
         * @param key        the key this request is for
         * @param pathArgs   the
         * @param headers
         * @return
         * @throws MalformedURLException
         * @throws IOException
         */
        private HttpURLConnection makeRequest(String method, String bucketName, String key, Map pathArgs, Map headers)
                throws IOException {
            return makeRequest(method, bucketName, key, pathArgs, headers, null);
        }


        /**
         * Make a new HttpURLConnection.
         * @param method     The HTTP method to use (GET, PUT, DELETE)
         * @param bucket     The bucket name this request affects
         * @param key        The key this request is for
         * @param pathArgs   parameters if any to be sent along this request
         * @param headers    A Map of String to List of Strings representing the http
         *                   headers to pass (can be null).
         * @param object     The S3Object that is to be written (can be null).
         */
        private HttpURLConnection makeRequest(String method, String bucket, String key, Map pathArgs, Map headers,
                                              S3Object object)
                throws IOException {
            CallingFormat format=Utils.getCallingFormatForBucket(this.callingFormat, bucket);
            if(isSecure && format != CallingFormat.getPathCallingFormat() && bucket.contains(".")) {
                System.err.println("You are making an SSL connection, however, the bucket contains periods and the wildcard certificate will not match by default.  Please consider using HTTP.");
            }

            // build the domain based on the calling format
            URL url=format.getURL(isSecure, server, this.port, bucket, key, pathArgs);

            HttpURLConnection connection=(HttpURLConnection)url.openConnection();
            connection.setRequestMethod(method);

            // subdomain-style urls may encounter http redirects.
            // Ensure that redirects are supported.
            if(!connection.getInstanceFollowRedirects()
                    && format.supportsLocatedBuckets())
                throw new RuntimeException("HTTP redirect support required.");

            addHeaders(connection, headers);
            if(object != null) addMetadataHeaders(connection, object.metadata);
            addAuthHeader(connection, method, bucket, key, pathArgs);

            return connection;
        }

        /**
         * Add the given headers to the HttpURLConnection.
         * @param connection The HttpURLConnection to which the headers will be added.
         * @param headers    A Map of String to List of Strings representing the http
         *                   headers to pass (can be null).
         */
        private static void addHeaders(HttpURLConnection connection, Map headers) {
            addHeaders(connection, headers, "");
        }

        /**
         * Add the given metadata fields to the HttpURLConnection.
         * @param connection The HttpURLConnection to which the headers will be added.
         * @param metadata   A Map of String to List of Strings representing the s3
         *                   metadata for this resource.
         */
        private static void addMetadataHeaders(HttpURLConnection connection, Map metadata) {
            addHeaders(connection, metadata, Utils.METADATA_PREFIX);
        }

        /**
         * Add the given headers to the HttpURLConnection with a prefix before the keys.
         * @param connection The HttpURLConnection to which the headers will be added.
         * @param headers    A Map of String to List of Strings representing the http
         *                   headers to pass (can be null).
         * @param prefix     The string to prepend to each key before adding it to the connection.
         */
        private static void addHeaders(HttpURLConnection connection, Map headers, String prefix) {
            if(headers != null) {
                for(Iterator i=headers.keySet().iterator(); i.hasNext();) {
                    String key=(String)i.next();
                    for(Iterator j=((List)headers.get(key)).iterator(); j.hasNext();) {
                        String value=(String)j.next();
                        connection.addRequestProperty(prefix + key, value);
                    }
                }
            }
        }

        /**
         * Add the appropriate Authorization header to the HttpURLConnection.
         * @param connection The HttpURLConnection to which the header will be added.
         * @param method     The HTTP method to use (GET, PUT, DELETE)
         * @param bucket     the bucket name this request is for
         * @param key        the key this request is for
         * @param pathArgs   path arguments which are part of this request
         */
        private void addAuthHeader(HttpURLConnection connection, String method, String bucket, String key, Map pathArgs) {
            if(connection.getRequestProperty("Date") == null) {
                connection.setRequestProperty("Date", httpDate());
            }
            if(connection.getRequestProperty("Content-Type") == null) {
                connection.setRequestProperty("Content-Type", "");
            }

            String canonicalString=
                    Utils.makeCanonicalString(method, bucket, key, pathArgs, connection.getRequestProperties());
            String encodedCanonical=Utils.encode(this.awsSecretAccessKey, canonicalString, false);
            connection.setRequestProperty("Authorization",
                                          "AWS " + this.awsAccessKeyId + ":" + encodedCanonical);
        }


        /**
         * Generate an rfc822 date for use in the Date HTTP header.
         */
        public static String httpDate() {
            final String DateFormat="EEE, dd MMM yyyy HH:mm:ss ";
            SimpleDateFormat format=new SimpleDateFormat(DateFormat, Locale.US);
            format.setTimeZone(TimeZone.getTimeZone("GMT"));
            return format.format(new Date()) + "GMT";
        }
    }

    static class ListEntry {
        /**
         * The name of the object
         */
        public String key;

        /**
         * The date at which the object was last modified.
         */
        public Date lastModified;

        /**
         * The object's ETag, which can be used for conditional GETs.
         */
        public String eTag;

        /**
         * The size of the object in bytes.
         */
        public long size;

        /**
         * The object's storage class
         */
        public String storageClass;

        /**
         * The object's owner
         */
        public Owner owner;

        public String toString() {
            return key;
        }
    }

    static class Owner {
        public String id;
        public String displayName;
    }


    static class Response {
        public HttpURLConnection connection;

        public Response(HttpURLConnection connection) throws IOException {
            this.connection=connection;
        }
    }


    static class GetResponse extends Response {
        public S3Object object;

        /**
         * Pulls a representation of an S3Object out of the HttpURLConnection response.
         */
        public GetResponse(HttpURLConnection connection) throws IOException {
            super(connection);
            if(connection.getResponseCode() < 400) {
                Map metadata=extractMetadata(connection);
                byte[] body=slurpInputStream(connection.getInputStream());
                this.object=new S3Object(body, metadata);
            }
        }

        /**
         * Examines the response's header fields and returns a Map from String to List of Strings
         * representing the object's metadata.
         */
        private static Map extractMetadata(HttpURLConnection connection) {
            TreeMap metadata=new TreeMap();
            Map headers=connection.getHeaderFields();
            for(Iterator i=headers.keySet().iterator(); i.hasNext();) {
                String key=(String)i.next();
                if(key == null) continue;
                if(key.startsWith(Utils.METADATA_PREFIX)) {
                    metadata.put(key.substring(Utils.METADATA_PREFIX.length()), headers.get(key));
                }
            }

            return metadata;
        }

        /**
         * Read the input stream and dump it all into a big byte array
         */
        static byte[] slurpInputStream(InputStream stream) throws IOException {
            final int chunkSize=2048;
            byte[] buf=new byte[chunkSize];
            ByteArrayOutputStream byteStream=new ByteArrayOutputStream(chunkSize);
            int count;

            while((count=stream.read(buf)) != -1) byteStream.write(buf, 0, count);

            return byteStream.toByteArray();
        }
    }

    static class LocationResponse extends Response {
        String location;

        /**
         * Parse the response to a ?location query.
         */
        public LocationResponse(HttpURLConnection connection) throws IOException {
            super(connection);
            if(connection.getResponseCode() < 400) {
                try {
                    XMLReader xr=Utils.createXMLReader();
                    ;
                    LocationResponseHandler handler=new LocationResponseHandler();
                    xr.setContentHandler(handler);
                    xr.setErrorHandler(handler);

                    xr.parse(new InputSource(connection.getInputStream()));
                    this.location=handler.loc;
                }
                catch(SAXException e) {
                    throw new RuntimeException("Unexpected error parsing ListAllMyBuckets xml", e);
                }
            }
            else {
                this.location="<error>";
            }
        }

        /**
         * Report the location-constraint for a bucket.
         * A value of null indicates an error;
         * the empty string indicates no constraint;
         * and any other value is an actual location constraint value.
         */
        public String getLocation() {
            return location;
        }

        /**
         * Helper class to parse LocationConstraint response XML
         */
        static class LocationResponseHandler extends DefaultHandler {
            String loc=null;
            private StringBuffer currText=null;

            public void startDocument() {
            }

            public void startElement(String uri, String name, String qName, Attributes attrs) {
                if(name.equals("LocationConstraint")) {
                    this.currText=new StringBuffer();
                }
            }

            public void endElement(String uri, String name, String qName) {
                if(name.equals("LocationConstraint")) {
                    loc=this.currText.toString();
                    this.currText=null;
                }
            }

            public void characters(char ch[], int start, int length) {
                if(currText != null)
                    this.currText.append(ch, start, length);
            }
        }
    }


    static class Bucket {
        /**
         * The name of the bucket.
         */
        public String name;

        /**
         * The bucket's creation date.
         */
        public Date creationDate;

        public Bucket() {
            this.name=null;
            this.creationDate=null;
        }

        public Bucket(String name, Date creationDate) {
            this.name=name;
            this.creationDate=creationDate;
        }

        public String toString() {
            return this.name;
        }
    }

    static class ListBucketResponse extends Response {

        /**
         * The name of the bucket being listed.  Null if request fails.
         */
        public String name=null;

        /**
         * The prefix echoed back from the request.  Null if request fails.
         */
        public String prefix=null;

        /**
         * The marker echoed back from the request.  Null if request fails.
         */
        public String marker=null;

        /**
         * The delimiter echoed back from the request.  Null if not specified in
         * the request, or if it fails.
         */
        public String delimiter=null;

        /**
         * The maxKeys echoed back from the request if specified.  0 if request fails.
         */
        public int maxKeys=0;

        /**
         * Indicates if there are more results to the list.  True if the current
         * list results have been truncated.  false if request fails.
         */
        public boolean isTruncated=false;

        /**
         * Indicates what to use as a marker for subsequent list requests in the event
         * that the results are truncated.  Present only when a delimiter is specified.
         * Null if request fails.
         */
        public String nextMarker=null;

        /**
         * A List of ListEntry objects representing the objects in the given bucket.
         * Null if the request fails.
         */
        public List entries=null;

        /**
         * A List of CommonPrefixEntry objects representing the common prefixes of the
         * keys that matched up to the delimiter.  Null if the request fails.
         */
        public List commonPrefixEntries=null;

        public ListBucketResponse(HttpURLConnection connection) throws IOException {
            super(connection);
            if(connection.getResponseCode() < 400) {
                try {
                    XMLReader xr=Utils.createXMLReader();
                    ListBucketHandler handler=new ListBucketHandler();
                    xr.setContentHandler(handler);
                    xr.setErrorHandler(handler);

                    xr.parse(new InputSource(connection.getInputStream()));

                    this.name=handler.getName();
                    this.prefix=handler.getPrefix();
                    this.marker=handler.getMarker();
                    this.delimiter=handler.getDelimiter();
                    this.maxKeys=handler.getMaxKeys();
                    this.isTruncated=handler.getIsTruncated();
                    this.nextMarker=handler.getNextMarker();
                    this.entries=handler.getKeyEntries();
                    this.commonPrefixEntries=handler.getCommonPrefixEntries();

                }
                catch(SAXException e) {
                    throw new RuntimeException("Unexpected error parsing ListBucket xml", e);
                }
            }
        }

        static class ListBucketHandler extends DefaultHandler {

            private String name=null;
            private String prefix=null;
            private String marker=null;
            private String delimiter=null;
            private int maxKeys=0;
            private boolean isTruncated=false;
            private String nextMarker=null;
            private boolean isEchoedPrefix=false;
            private List keyEntries=null;
            private ListEntry keyEntry=null;
            private List commonPrefixEntries=null;
            private CommonPrefixEntry commonPrefixEntry=null;
            private StringBuffer currText=null;
            private SimpleDateFormat iso8601Parser=null;

            public ListBucketHandler() {
                super();
                keyEntries=new ArrayList();
                commonPrefixEntries=new ArrayList();
                this.iso8601Parser=new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
                this.iso8601Parser.setTimeZone(new SimpleTimeZone(0, "GMT"));
                this.currText=new StringBuffer();
            }

            public void startDocument() {
                this.isEchoedPrefix=true;
            }

            public void endDocument() {
                // ignore
            }

            public void startElement(String uri, String name, String qName, Attributes attrs) {
                if(name.equals("Contents")) {
                    this.keyEntry=new ListEntry();
                }
                else if(name.equals("Owner")) {
                    this.keyEntry.owner=new Owner();
                }
                else if(name.equals("CommonPrefixes")) {
                    this.commonPrefixEntry=new CommonPrefixEntry();
                }
            }

            public void endElement(String uri, String name, String qName) {
                if(name.equals("Name")) {
                    this.name=this.currText.toString();
                }
                // this prefix is the one we echo back from the request
                else if(name.equals("Prefix") && this.isEchoedPrefix) {
                    this.prefix=this.currText.toString();
                    this.isEchoedPrefix=false;
                }
                else if(name.equals("Marker")) {
                    this.marker=this.currText.toString();
                }
                else if(name.equals("MaxKeys")) {
                    this.maxKeys=Integer.parseInt(this.currText.toString());
                }
                else if(name.equals("Delimiter")) {
                    this.delimiter=this.currText.toString();
                }
                else if(name.equals("IsTruncated")) {
                    this.isTruncated=Boolean.valueOf(this.currText.toString());
                }
                else if(name.equals("NextMarker")) {
                    this.nextMarker=this.currText.toString();
                }
                else if(name.equals("Contents")) {
                    this.keyEntries.add(this.keyEntry);
                }
                else if(name.equals("Key")) {
                    this.keyEntry.key=this.currText.toString();
                }
                else if(name.equals("LastModified")) {
                    try {
                        this.keyEntry.lastModified=this.iso8601Parser.parse(this.currText.toString());
                    }
                    catch(ParseException e) {
                        throw new RuntimeException("Unexpected date format in list bucket output", e);
                    }
                }
                else if(name.equals("ETag")) {
                    this.keyEntry.eTag=this.currText.toString();
                }
                else if(name.equals("Size")) {
                    this.keyEntry.size=Long.parseLong(this.currText.toString());
                }
                else if(name.equals("StorageClass")) {
                    this.keyEntry.storageClass=this.currText.toString();
                }
                else if(name.equals("ID")) {
                    this.keyEntry.owner.id=this.currText.toString();
                }
                else if(name.equals("DisplayName")) {
                    this.keyEntry.owner.displayName=this.currText.toString();
                }
                else if(name.equals("CommonPrefixes")) {
                    this.commonPrefixEntries.add(this.commonPrefixEntry);
                }
                // this is the common prefix for keys that match up to the delimiter
                else if(name.equals("Prefix")) {
                    this.commonPrefixEntry.prefix=this.currText.toString();
                }
                if(this.currText.length() != 0)
                    this.currText=new StringBuffer();
            }

            public void characters(char ch[], int start, int length) {
                this.currText.append(ch, start, length);
            }

            public String getName() {
                return this.name;
            }

            public String getPrefix() {
                return this.prefix;
            }

            public String getMarker() {
                return this.marker;
            }

            public String getDelimiter() {
                return this.delimiter;
            }

            public int getMaxKeys() {
                return this.maxKeys;
            }

            public boolean getIsTruncated() {
                return this.isTruncated;
            }

            public String getNextMarker() {
                return this.nextMarker;
            }

            public List getKeyEntries() {
                return this.keyEntries;
            }

            public List getCommonPrefixEntries() {
                return this.commonPrefixEntries;
            }
        }
    }


    static class CommonPrefixEntry {
        /**
         * The prefix common to the delimited keys it represents
         */
        public String prefix;
    }


    static class ListAllMyBucketsResponse extends Response {
        /**
         * A list of Bucket objects, one for each of this account's buckets.  Will be null if
         * the request fails.
         */
        public List entries;

        public ListAllMyBucketsResponse(HttpURLConnection connection) throws IOException {
            super(connection);
            if(connection.getResponseCode() < 400) {
                try {
                    XMLReader xr=Utils.createXMLReader();
                    ;
                    ListAllMyBucketsHandler handler=new ListAllMyBucketsHandler();
                    xr.setContentHandler(handler);
                    xr.setErrorHandler(handler);

                    xr.parse(new InputSource(connection.getInputStream()));
                    this.entries=handler.getEntries();
                }
                catch(SAXException e) {
                    throw new RuntimeException("Unexpected error parsing ListAllMyBuckets xml", e);
                }
            }
        }

        static class ListAllMyBucketsHandler extends DefaultHandler {

            private List entries=null;
            private Bucket currBucket=null;
            private StringBuffer currText=null;
            private SimpleDateFormat iso8601Parser=null;

            public ListAllMyBucketsHandler() {
                super();
                entries=new ArrayList();
                this.iso8601Parser=new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
                this.iso8601Parser.setTimeZone(new SimpleTimeZone(0, "GMT"));
                this.currText=new StringBuffer();
            }

            public void startDocument() {
                // ignore
            }

            public void endDocument() {
                // ignore
            }

            public void startElement(String uri, String name, String qName, Attributes attrs) {
                if(name.equals("Bucket")) {
                    this.currBucket=new Bucket();
                }
            }

            public void endElement(String uri, String name, String qName) {
                if(name.equals("Bucket")) {
                    this.entries.add(this.currBucket);
                }
                else if(name.equals("Name")) {
                    this.currBucket.name=this.currText.toString();
                }
                else if(name.equals("CreationDate")) {
                    try {
                        this.currBucket.creationDate=this.iso8601Parser.parse(this.currText.toString());
                    }
                    catch(ParseException e) {
                        throw new RuntimeException("Unexpected date format in list bucket output", e);
                    }
                }
                this.currText=new StringBuffer();
            }

            public void characters(char ch[], int start, int length) {
                this.currText.append(ch, start, length);
            }

            public List getEntries() {
                return this.entries;
            }
        }
    }


    static class S3Object {

        public byte[] data;

        /**
         * A Map from String to List of Strings representing the object's metadata
         */
        public Map metadata;

        public S3Object(byte[] data, Map metadata) {
            this.data=data;
            this.metadata=metadata;
        }
    }


    abstract static class CallingFormat {

        protected static CallingFormat pathCallingFormat=new PathCallingFormat();
        protected static CallingFormat subdomainCallingFormat=new SubdomainCallingFormat();
        protected static CallingFormat vanityCallingFormat=new VanityCallingFormat();

        public abstract boolean supportsLocatedBuckets();

        public abstract String getEndpoint(String server, int port, String bucket);

        public abstract String getPathBase(String bucket, String key);

        public abstract URL getURL(boolean isSecure, String server, int port, String bucket, String key, Map pathArgs)
                throws MalformedURLException;

        public static CallingFormat getPathCallingFormat() {
            return pathCallingFormat;
        }

        public static CallingFormat getSubdomainCallingFormat() {
            return subdomainCallingFormat;
        }

        public static CallingFormat getVanityCallingFormat() {
            return vanityCallingFormat;
        }

        private static class PathCallingFormat extends CallingFormat {
            public boolean supportsLocatedBuckets() {
                return false;
            }

            public String getPathBase(String bucket, String key) {
                return isBucketSpecified(bucket)? "/" + bucket + "/" + key : "/";
            }

            public String getEndpoint(String server, int port, String bucket) {
                return server + ":" + port;
            }

            public URL getURL(boolean isSecure, String server, int port, String bucket, String key, Map pathArgs)
                    throws MalformedURLException {
                String pathBase=isBucketSpecified(bucket)? "/" + bucket + "/" + key : "/";
                String pathArguments=Utils.convertPathArgsHashToString(pathArgs);
                return new URL(isSecure? "https" : "http", server, port, pathBase + pathArguments);
            }

            private static boolean isBucketSpecified(String bucket) {
                return bucket != null && bucket.length() != 0;
            }
        }

        private static class SubdomainCallingFormat extends CallingFormat {
            public boolean supportsLocatedBuckets() {
                return true;
            }

            public String getServer(String server, String bucket) {
                return bucket + "." + server;
            }

            public String getEndpoint(String server, int port, String bucket) {
                return getServer(server, bucket) + ":" + port;
            }

            public String getPathBase(String bucket, String key) {
                return "/" + key;
            }

            public URL getURL(boolean isSecure, String server, int port, String bucket, String key, Map pathArgs)
                    throws MalformedURLException {
                if(bucket == null || bucket.length() == 0) {
                    //The bucket is null, this is listAllBuckets request
                    String pathArguments=Utils.convertPathArgsHashToString(pathArgs);
                    return new URL(isSecure? "https" : "http", server, port, "/" + pathArguments);
                }
                else {
                    String serverToUse=getServer(server, bucket);
                    String pathBase=getPathBase(bucket, key);
                    String pathArguments=Utils.convertPathArgsHashToString(pathArgs);
                    return new URL(isSecure? "https" : "http", serverToUse, port, pathBase + pathArguments);
                }
            }
        }

        private static class VanityCallingFormat extends SubdomainCallingFormat {
            public String getServer(String server, String bucket) {
                return bucket;
            }
        }
    }

    static class Utils {
        static final String METADATA_PREFIX="x-amz-meta-";
        static final String AMAZON_HEADER_PREFIX="x-amz-";
        static final String ALTERNATIVE_DATE_HEADER="x-amz-date";
        public static final String DEFAULT_HOST="s3.amazonaws.com";

        public static final int SECURE_PORT=443;
        public static final int INSECURE_PORT=80;


        /**
         * HMAC/SHA1 Algorithm per RFC 2104.
         */
        private static final String HMAC_SHA1_ALGORITHM="HmacSHA1";

        static String makeCanonicalString(String method, String bucket, String key, Map pathArgs, Map headers) {
            return makeCanonicalString(method, bucket, key, pathArgs, headers, null);
        }

        /**
         * Calculate the canonical string.  When expires is non-null, it will be
         * used instead of the Date header.
         */
        static String makeCanonicalString(String method, String bucketName, String key, Map pathArgs,
                                          Map headers, String expires) {
            StringBuilder buf=new StringBuilder();
            buf.append(method + "\n");

            // Add all interesting headers to a list, then sort them.  "Interesting"
            // is defined as Content-MD5, Content-Type, Date, and x-amz-
            SortedMap interestingHeaders=new TreeMap();
            if(headers != null) {
                for(Iterator i=headers.keySet().iterator(); i.hasNext();) {
                    String hashKey=(String)i.next();
                    if(hashKey == null) continue;
                    String lk=hashKey.toLowerCase();

                    // Ignore any headers that are not particularly interesting.
                    if(lk.equals("content-type") || lk.equals("content-md5") || lk.equals("date") ||
                            lk.startsWith(AMAZON_HEADER_PREFIX)) {
                        List s=(List)headers.get(hashKey);
                        interestingHeaders.put(lk, concatenateList(s));
                    }
                }
            }

            if(interestingHeaders.containsKey(ALTERNATIVE_DATE_HEADER)) {
                interestingHeaders.put("date", "");
            }

            // if the expires is non-null, use that for the date field.  this
            // trumps the x-amz-date behavior.
            if(expires != null) {
                interestingHeaders.put("date", expires);
            }

            // these headers require that we still put a new line in after them,
            // even if they don't exist.
            if(!interestingHeaders.containsKey("content-type")) {
                interestingHeaders.put("content-type", "");
            }
            if(!interestingHeaders.containsKey("content-md5")) {
                interestingHeaders.put("content-md5", "");
            }

            // Finally, add all the interesting headers (i.e.: all that startwith x-amz- ;-))
            for(Iterator i=interestingHeaders.keySet().iterator(); i.hasNext();) {
                String headerKey=(String)i.next();
                if(headerKey.startsWith(AMAZON_HEADER_PREFIX)) {
                    buf.append(headerKey).append(':').append(interestingHeaders.get(headerKey));
                }
                else {
                    buf.append(interestingHeaders.get(headerKey));
                }
                buf.append("\n");
            }

            // build the path using the bucket and key
            if(bucketName != null && bucketName.length() != 0) {
                buf.append("/" + bucketName);
            }

            // append the key (it might be an empty string)
            // append a slash regardless
            buf.append("/");
            if(key != null) {
                buf.append(key);
            }

            // if there is an acl, logging or torrent parameter
            // add them to the string
            if(pathArgs != null) {
                if(pathArgs.containsKey("acl")) {
                    buf.append("?acl");
                }
                else if(pathArgs.containsKey("torrent")) {
                    buf.append("?torrent");
                }
                else if(pathArgs.containsKey("logging")) {
                    buf.append("?logging");
                }
                else if(pathArgs.containsKey("location")) {
                    buf.append("?location");
                }
            }

            return buf.toString();

        }

        /**
         * Calculate the HMAC/SHA1 on a string.
         * @return Signature
         * @throws java.security.NoSuchAlgorithmException
         *          If the algorithm does not exist.  Unlikely
         * @throws java.security.InvalidKeyException
         *          If the key is invalid.
         */
        static String encode(String awsSecretAccessKey, String canonicalString,
                             boolean urlencode) {
            // The following HMAC/SHA1 code for the signature is taken from the
            // AWS Platform's implementation of RFC2104 (amazon.webservices.common.Signature)
            //
            // Acquire an HMAC/SHA1 from the raw key bytes.
            SecretKeySpec signingKey=
                    new SecretKeySpec(awsSecretAccessKey.getBytes(), HMAC_SHA1_ALGORITHM);

            // Acquire the MAC instance and initialize with the signing key.
            Mac mac=null;
            try {
                mac=Mac.getInstance(HMAC_SHA1_ALGORITHM);
            }
            catch(NoSuchAlgorithmException e) {
                // should not happen
                throw new RuntimeException("Could not find sha1 algorithm", e);
            }
            try {
                mac.init(signingKey);
            }
            catch(InvalidKeyException e) {
                // also should not happen
                throw new RuntimeException("Could not initialize the MAC algorithm", e);
            }

            // Compute the HMAC on the digest, and set it.
            String b64=Base64.encodeBytes(mac.doFinal(canonicalString.getBytes()));

            if(urlencode) {
                return urlencode(b64);
            }
            else {
                return b64;
            }
        }

        static Map paramsForListOptions(String prefix, String marker, Integer maxKeys) {
            return paramsForListOptions(prefix, marker, maxKeys, null);
        }

        static Map paramsForListOptions(String prefix, String marker, Integer maxKeys, String delimiter) {

            Map argParams=new HashMap();
            // these three params must be url encoded
            if(prefix != null)
                argParams.put("prefix", urlencode(prefix));
            if(marker != null)
                argParams.put("marker", urlencode(marker));
            if(delimiter != null)
                argParams.put("delimiter", urlencode(delimiter));

            if(maxKeys != null)
                argParams.put("max-keys", Integer.toString(maxKeys.intValue()));

            return argParams;

        }

        /**
         * Converts the Path Arguments from a map to String which can be used in url construction
         * @param pathArgs a map of arguments
         * @return a string representation of pathArgs
         */
        public static String convertPathArgsHashToString(Map pathArgs) {
            StringBuilder pathArgsString=new StringBuilder();
            String argumentValue;
            boolean firstRun=true;
            if(pathArgs != null) {
                for(Iterator argumentIterator=pathArgs.keySet().iterator(); argumentIterator.hasNext();) {
                    String argument=(String)argumentIterator.next();
                    if(firstRun) {
                        firstRun=false;
                        pathArgsString.append("?");
                    }
                    else {
                        pathArgsString.append("&");
                    }

                    argumentValue=(String)pathArgs.get(argument);
                    pathArgsString.append(argument);
                    if(argumentValue != null) {
                        pathArgsString.append("=");
                        pathArgsString.append(argumentValue);
                    }
                }
            }

            return pathArgsString.toString();
        }


        static String urlencode(String unencoded) {
            try {
                return URLEncoder.encode(unencoded, "UTF-8");
            }
            catch(UnsupportedEncodingException e) {
                // should never happen
                throw new RuntimeException("Could not url encode to UTF-8", e);
            }
        }

        static XMLReader createXMLReader() {
            try {
                return XMLReaderFactory.createXMLReader();
            }
            catch(SAXException e) {
                // oops, lets try doing this (needed in 1.4)
                System.setProperty("org.xml.sax.driver", "org.apache.crimson.parser.XMLReaderImpl");
            }
            try {
                // try once more
                return XMLReaderFactory.createXMLReader();
            }
            catch(SAXException e) {
                throw new RuntimeException("Couldn't initialize a sax driver for the XMLReader");
            }
        }

        /**
         * Concatenates a bunch of header values, seperating them with a comma.
         * @param values List of header values.
         * @return String of all headers, with commas.
         */
        private static String concatenateList(List values) {
            StringBuilder buf=new StringBuilder();
            for(int i=0, size=values.size(); i < size; ++i) {
                buf.append(((String)values.get(i)).replaceAll("\n", "").trim());
                if(i != (size - 1)) {
                    buf.append(",");
                }
            }
            return buf.toString();
        }

        /**
         * Validate bucket-name
         */
        static boolean validateBucketName(String bucketName, CallingFormat callingFormat) {
            if(callingFormat == CallingFormat.getPathCallingFormat()) {
                final int MIN_BUCKET_LENGTH=3;
                final int MAX_BUCKET_LENGTH=255;
                final String BUCKET_NAME_REGEX="^[0-9A-Za-z\\.\\-_]*$";

                return null != bucketName &&
                        bucketName.length() >= MIN_BUCKET_LENGTH &&
                        bucketName.length() <= MAX_BUCKET_LENGTH &&
                        bucketName.matches(BUCKET_NAME_REGEX);
            }
            else {
                return isValidSubdomainBucketName(bucketName);
            }
        }

        static boolean isValidSubdomainBucketName(String bucketName) {
            final int MIN_BUCKET_LENGTH=3;
            final int MAX_BUCKET_LENGTH=63;
            // don't allow names that look like 127.0.0.1
            final String IPv4_REGEX="^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$";
            // dns sub-name restrictions
            final String BUCKET_NAME_REGEX="^[a-z0-9]([a-z0-9\\-\\_]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9\\-\\_]*[a-z0-9])?)*$";

            // If there wasn't a location-constraint, then the current actual
            // restriction is just that no 'part' of the name (i.e. sequence
            // of characters between any 2 '.'s has to be 63) but the recommendation
            // is to keep the entire bucket name under 63.
            return null != bucketName &&
                    bucketName.length() >= MIN_BUCKET_LENGTH &&
                    bucketName.length() <= MAX_BUCKET_LENGTH &&
                    !bucketName.matches(IPv4_REGEX) &&
                    bucketName.matches(BUCKET_NAME_REGEX);
        }

        static CallingFormat getCallingFormatForBucket(CallingFormat desiredFormat, String bucketName) {
            CallingFormat callingFormat=desiredFormat;
            if(callingFormat == CallingFormat.getSubdomainCallingFormat() && !Utils.isValidSubdomainBucketName(bucketName)) {
                callingFormat=CallingFormat.getPathCallingFormat();
            }
            return callingFormat;
        }
    }


//
//  NOTE: The following source code is the iHarder.net public domain
//  Base64 library and is provided here as a convenience.  For updates,
//  problems, questions, etc. regarding this code, please visit:
//  http://iharder.sourceforge.net/current/java/base64/
//


    /**
     * Encodes and decodes to and from Base64 notation.
     * <p/>
     * <p>
     * Change Log:
     * </p>
     * <ul>
     * <li>v2.1 - Cleaned up javadoc comments and unused variables and methods. Added
     * some convenience methods for reading and writing to and from files.</li>
     * <li>v2.0.2 - Now specifies UTF-8 encoding in places where the code fails on systems
     * with other encodings (like EBCDIC).</li>
     * <li>v2.0.1 - Fixed an error when decoding a single byte, that is, when the
     * encoded data was a single byte.</li>
     * <li>v2.0 - I got rid of methods that used booleans to set options.
     * Now everything is more consolidated and cleaner. The code now detects
     * when data that's being decoded is gzip-compressed and will decompress it
     * automatically. Generally things are cleaner. You'll probably have to
     * change some method calls that you were making to support the new
     * options format (<tt>int</tt>s that you "OR" together).</li>
     * <li>v1.5.1 - Fixed bug when decompressing and decoding to a
     * byte[] using <tt>decode( String s, boolean gzipCompressed )</tt>.
     * Added the ability to "suspend" encoding in the Output Stream so
     * you can turn on and off the encoding if you need to embed base64
     * data in an otherwise "normal" stream (like an XML file).</li>
     * <li>v1.5 - Output stream pases on flush() command but doesn't do anything itself.
     * This helps when using GZIP streams.
     * Added the ability to GZip-compress objects before encoding them.</li>
     * <li>v1.4 - Added helper methods to read/write files.</li>
     * <li>v1.3.6 - Fixed OutputStream.flush() so that 'position' is reset.</li>
     * <li>v1.3.5 - Added flag to turn on and off line breaks. Fixed bug in input stream
     * where last buffer being read, if not completely full, was not returned.</li>
     * <li>v1.3.4 - Fixed when "improperly padded stream" error was thrown at the wrong time.</li>
     * <li>v1.3.3 - Fixed I/O streams which were totally messed up.</li>
     * </ul>
     * <p/>
     * <p>
     * I am placing this code in the Public Domain. Do with it as you will.
     * This software comes with no guarantees or warranties but with
     * plenty of well-wishing instead!
     * Please visit <a href="http://iharder.net/base64">http://iharder.net/base64</a>
     * periodically to check for updates or to contribute improvements.
     * </p>
     * @author Robert Harder
     * @author rob@iharder.net
     * @version 2.1
     */
    static class Base64 {

/* ********  P U B L I C   F I E L D S  ******** */


        /**
         * No options specified. Value is zero.
         */
        public final static int NO_OPTIONS=0;

        /**
         * Specify encoding.
         */
        public final static int ENCODE=1;


        /**
         * Specify decoding.
         */
        public final static int DECODE=0;


        /**
         * Specify that data should be gzip-compressed.
         */
        public final static int GZIP=2;


        /**
         * Don't break lines when encoding (violates strict Base64 specification)
         */
        public final static int DONT_BREAK_LINES=8;


/* ********  P R I V A T E   F I E L D S  ******** */


        /**
         * Maximum line length (76) of Base64 output.
         */
        private final static int MAX_LINE_LENGTH=76;


        /**
         * The equals sign (=) as a byte.
         */
        private final static byte EQUALS_SIGN=(byte)'=';


        /**
         * The new line character (\n) as a byte.
         */
        private final static byte NEW_LINE=(byte)'\n';


        /**
         * Preferred encoding.
         */
        private final static String PREFERRED_ENCODING="UTF-8";


        /**
         * The 64 valid Base64 values.
         */
        private static final byte[] ALPHABET;
        private static final byte[] _NATIVE_ALPHABET= /* May be something funny like EBCDIC */
                {
                        (byte)'A', (byte)'B', (byte)'C', (byte)'D', (byte)'E', (byte)'F', (byte)'G',
                        (byte)'H', (byte)'I', (byte)'J', (byte)'K', (byte)'L', (byte)'M', (byte)'N',
                        (byte)'O', (byte)'P', (byte)'Q', (byte)'R', (byte)'S', (byte)'T', (byte)'U',
                        (byte)'V', (byte)'W', (byte)'X', (byte)'Y', (byte)'Z',
                        (byte)'a', (byte)'b', (byte)'c', (byte)'d', (byte)'e', (byte)'f', (byte)'g',
                        (byte)'h', (byte)'i', (byte)'j', (byte)'k', (byte)'l', (byte)'m', (byte)'n',
                        (byte)'o', (byte)'p', (byte)'q', (byte)'r', (byte)'s', (byte)'t', (byte)'u',
                        (byte)'v', (byte)'w', (byte)'x', (byte)'y', (byte)'z',
                        (byte)'0', (byte)'1', (byte)'2', (byte)'3', (byte)'4', (byte)'5',
                        (byte)'6', (byte)'7', (byte)'8', (byte)'9', (byte)'+', (byte)'/'
                };

        /** Determine which ALPHABET to use. */
        static {
            byte[] __bytes;
            try {
                __bytes="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".getBytes(PREFERRED_ENCODING);
            }   // end try
            catch(java.io.UnsupportedEncodingException use) {
                __bytes=_NATIVE_ALPHABET; // Fall back to native encoding
            }   // end catch
            ALPHABET=__bytes;
        }   // end static


        /**
         * Translates a Base64 value to either its 6-bit reconstruction value
         * or a negative number indicating some other meaning.
         */
        private final static byte[] DECODABET=
                {
                        -9, -9, -9, -9, -9, -9, -9, -9, -9,                 // Decimal  0 -  8
                        -5, -5,                                      // Whitespace: Tab and Linefeed
                        -9, -9,                                      // Decimal 11 - 12
                        -5,                                         // Whitespace: Carriage Return
                        -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9,     // Decimal 14 - 26
                        -9, -9, -9, -9, -9,                             // Decimal 27 - 31
                        -5,                                         // Whitespace: Space
                        -9, -9, -9, -9, -9, -9, -9, -9, -9, -9,              // Decimal 33 - 42
                        62,                                         // Plus sign at decimal 43
                        -9, -9, -9,                                   // Decimal 44 - 46
                        63,                                         // Slash at decimal 47
                        52, 53, 54, 55, 56, 57, 58, 59, 60, 61,              // Numbers zero through nine
                        -9, -9, -9,                                   // Decimal 58 - 60
                        -1,                                         // Equals sign at decimal 61
                        -9, -9, -9,                                      // Decimal 62 - 64
                        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,            // Letters 'A' through 'N'
                        14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,        // Letters 'O' through 'Z'
                        -9, -9, -9, -9, -9, -9,                          // Decimal 91 - 96
                        26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,     // Letters 'a' through 'm'
                        39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,     // Letters 'n' through 'z'
                        -9, -9, -9, -9                                 // Decimal 123 - 126
                        /*,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 127 - 139
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 140 - 152
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 153 - 165
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 166 - 178
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 179 - 191
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 192 - 204
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 205 - 217
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 218 - 230
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,     // Decimal 231 - 243
          -9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9         // Decimal 244 - 255 */
                };

        // I think I end up not using the BAD_ENCODING indicator.
        //private final static byte BAD_ENCODING    = -9; // Indicates error in encoding
        private final static byte WHITE_SPACE_ENC=-5; // Indicates white space in encoding
        private final static byte EQUALS_SIGN_ENC=-1; // Indicates equals sign in encoding


        /**
         * Defeats instantiation.
         */
        private Base64() {
        }


/* ********  E N C O D I N G   M E T H O D S  ******** */


        /**
         * Encodes up to the first three bytes of array <var>threeBytes</var>
         * and returns a four-byte array in Base64 notation.
         * The actual number of significant bytes in your array is
         * given by <var>numSigBytes</var>.
         * The array <var>threeBytes</var> needs only be as big as
         * <var>numSigBytes</var>.
         * Code can reuse a byte array by passing a four-byte array as <var>b4</var>.
         * @param b4          A reusable byte array to reduce array instantiation
         * @param threeBytes  the array to convert
         * @param numSigBytes the number of significant bytes in your array
         * @return four byte array in Base64 notation.
         * @since 1.5.1
         */
        private static byte[] encode3to4(byte[] b4, byte[] threeBytes, int numSigBytes) {
            encode3to4(threeBytes, 0, numSigBytes, b4, 0);
            return b4;
        }   // end encode3to4


        /**
         * Encodes up to three bytes of the array <var>source</var>
         * and writes the resulting four Base64 bytes to <var>destination</var>.
         * The source and destination arrays can be manipulated
         * anywhere along their length by specifying
         * <var>srcOffset</var> and <var>destOffset</var>.
         * This method does not check to make sure your arrays
         * are large enough to accomodate <var>srcOffset</var> + 3 for
         * the <var>source</var> array or <var>destOffset</var> + 4 for
         * the <var>destination</var> array.
         * The actual number of significant bytes in your array is
         * given by <var>numSigBytes</var>.
         * @param source      the array to convert
         * @param srcOffset   the index where conversion begins
         * @param numSigBytes the number of significant bytes in your array
         * @param destination the array to hold the conversion
         * @param destOffset  the index where output will be put
         * @return the <var>destination</var> array
         * @since 1.3
         */
        private static byte[] encode3to4(
                byte[] source, int srcOffset, int numSigBytes,
                byte[] destination, int destOffset) {
            //           1         2         3
            // 01234567890123456789012345678901 Bit position
            // --------000000001111111122222222 Array position from threeBytes
            // --------|    ||    ||    ||    | Six bit groups to index ALPHABET
            //          >>18  >>12  >> 6  >> 0  Right shift necessary
            //                0x3f  0x3f  0x3f  Additional AND

            // Create buffer with zero-padding if there are only one or two
            // significant bytes passed in the array.
            // We have to shift left 24 in order to flush out the 1's that appear
            // when Java treats a value as negative that is cast from a byte to an int.
            int inBuff=(numSigBytes > 0? ((source[srcOffset] << 24) >>> 8) : 0)
                    | (numSigBytes > 1? ((source[srcOffset + 1] << 24) >>> 16) : 0)
                    | (numSigBytes > 2? ((source[srcOffset + 2] << 24) >>> 24) : 0);

            switch(numSigBytes) {
                case 3:
                    destination[destOffset]=ALPHABET[(inBuff >>> 18)];
                    destination[destOffset + 1]=ALPHABET[(inBuff >>> 12) & 0x3f];
                    destination[destOffset + 2]=ALPHABET[(inBuff >>> 6) & 0x3f];
                    destination[destOffset + 3]=ALPHABET[(inBuff) & 0x3f];
                    return destination;

                case 2:
                    destination[destOffset]=ALPHABET[(inBuff >>> 18)];
                    destination[destOffset + 1]=ALPHABET[(inBuff >>> 12) & 0x3f];
                    destination[destOffset + 2]=ALPHABET[(inBuff >>> 6) & 0x3f];
                    destination[destOffset + 3]=EQUALS_SIGN;
                    return destination;

                case 1:
                    destination[destOffset]=ALPHABET[(inBuff >>> 18)];
                    destination[destOffset + 1]=ALPHABET[(inBuff >>> 12) & 0x3f];
                    destination[destOffset + 2]=EQUALS_SIGN;
                    destination[destOffset + 3]=EQUALS_SIGN;
                    return destination;

                default:
                    return destination;
            }   // end switch
        }   // end encode3to4


        /**
         * Serializes an object and returns the Base64-encoded
         * version of that serialized object. If the object
         * cannot be serialized or there is another error,
         * the method will return <tt>null</tt>.
         * The object is not GZip-compressed before being encoded.
         * @param serializableObject The object to encode
         * @return The Base64-encoded object
         * @since 1.4
         */
        public static String encodeObject(java.io.Serializable serializableObject) {
            return encodeObject(serializableObject, NO_OPTIONS);
        }   // end encodeObject


        /**
         * Serializes an object and returns the Base64-encoded
         * version of that serialized object. If the object
         * cannot be serialized or there is another error,
         * the method will return <tt>null</tt>.
         * <p/>
         * Valid options:<pre>
         *   GZIP: gzip-compresses object before encoding it.
         *   DONT_BREAK_LINES: don't break lines at 76 characters
         *     <i>Note: Technically, this makes your encoding non-compliant.</i>
         * </pre>
         * <p/>
         * Example: <code>encodeObject( myObj, Base64.GZIP )</code> or
         * <p/>
         * Example: <code>encodeObject( myObj, Base64.GZIP | Base64.DONT_BREAK_LINES )</code>
         * @param serializableObject The object to encode
         * @param options            Specified options
         * @return The Base64-encoded object
         * @see Base64#GZIP
         * @see Base64#DONT_BREAK_LINES
         * @since 2.0
         */
        public static String encodeObject(java.io.Serializable serializableObject, int options) {
            // Streams
            java.io.ByteArrayOutputStream baos=null;
            java.io.OutputStream b64os=null;
            java.io.ObjectOutputStream oos=null;
            java.util.zip.GZIPOutputStream gzos=null;

            // Isolate options
            int gzip=(options & GZIP);
            int dontBreakLines=(options & DONT_BREAK_LINES);

            try {
                // ObjectOutputStream -> (GZIP) -> Base64 -> ByteArrayOutputStream
                baos=new java.io.ByteArrayOutputStream();
                b64os=new Base64.OutputStream(baos, ENCODE | dontBreakLines);

                // GZip?
                if(gzip == GZIP) {
                    gzos=new java.util.zip.GZIPOutputStream(b64os);
                    oos=new java.io.ObjectOutputStream(gzos);
                }   // end if: gzip
                else
                    oos=new java.io.ObjectOutputStream(b64os);

                oos.writeObject(serializableObject);
            }   // end try
            catch(java.io.IOException e) {
                e.printStackTrace();
                return null;
            }   // end catch
            finally {
                try {
                    oos.close();
                }
                catch(Exception e) {
                }
                try {
                    gzos.close();
                }
                catch(Exception e) {
                }
                try {
                    b64os.close();
                }
                catch(Exception e) {
                }
                try {
                    baos.close();
                }
                catch(Exception e) {
                }
            }   // end finally

            // Return value according to relevant encoding.
            try {
                return new String(baos.toByteArray(), PREFERRED_ENCODING);
            }   // end try
            catch(java.io.UnsupportedEncodingException uue) {
                return new String(baos.toByteArray());
            }   // end catch

        }   // end encode


        /**
         * Encodes a byte array into Base64 notation.
         * Does not GZip-compress data.
         * @param source The data to convert
         * @since 1.4
         */
        public static String encodeBytes(byte[] source) {
            return encodeBytes(source, 0, source.length, NO_OPTIONS);
        }   // end encodeBytes


        /**
         * Encodes a byte array into Base64 notation.
         * <p/>
         * Valid options:<pre>
         *   GZIP: gzip-compresses object before encoding it.
         *   DONT_BREAK_LINES: don't break lines at 76 characters
         *     <i>Note: Technically, this makes your encoding non-compliant.</i>
         * </pre>
         * <p/>
         * Example: <code>encodeBytes( myData, Base64.GZIP )</code> or
         * <p/>
         * Example: <code>encodeBytes( myData, Base64.GZIP | Base64.DONT_BREAK_LINES )</code>
         * @param source  The data to convert
         * @param options Specified options
         * @see Base64#GZIP
         * @see Base64#DONT_BREAK_LINES
         * @since 2.0
         */
        public static String encodeBytes(byte[] source, int options) {
            return encodeBytes(source, 0, source.length, options);
        }   // end encodeBytes


        /**
         * Encodes a byte array into Base64 notation.
         * Does not GZip-compress data.
         * @param source The data to convert
         * @param off    Offset in array where conversion should begin
         * @param len    Length of data to convert
         * @since 1.4
         */
        public static String encodeBytes(byte[] source, int off, int len) {
            return encodeBytes(source, off, len, NO_OPTIONS);
        }   // end encodeBytes


        /**
         * Encodes a byte array into Base64 notation.
         * <p/>
         * Valid options:<pre>
         *   GZIP: gzip-compresses object before encoding it.
         *   DONT_BREAK_LINES: don't break lines at 76 characters
         *     <i>Note: Technically, this makes your encoding non-compliant.</i>
         * </pre>
         * <p/>
         * Example: <code>encodeBytes( myData, Base64.GZIP )</code> or
         * <p/>
         * Example: <code>encodeBytes( myData, Base64.GZIP | Base64.DONT_BREAK_LINES )</code>
         * @param source  The data to convert
         * @param off     Offset in array where conversion should begin
         * @param len     Length of data to convert
         * @param options Specified options
         * @see Base64#GZIP
         * @see Base64#DONT_BREAK_LINES
         * @since 2.0
         */
        public static String encodeBytes(byte[] source, int off, int len, int options) {
            // Isolate options
            int dontBreakLines=(options & DONT_BREAK_LINES);
            int gzip=(options & GZIP);

            // Compress?
            if(gzip == GZIP) {
                java.io.ByteArrayOutputStream baos=null;
                java.util.zip.GZIPOutputStream gzos=null;
                Base64.OutputStream b64os=null;


                try {
                    // GZip -> Base64 -> ByteArray
                    baos=new java.io.ByteArrayOutputStream();
                    b64os=new Base64.OutputStream(baos, ENCODE | dontBreakLines);
                    gzos=new java.util.zip.GZIPOutputStream(b64os);

                    gzos.write(source, off, len);
                    gzos.close();
                }   // end try
                catch(java.io.IOException e) {
                    e.printStackTrace();
                    return null;
                }   // end catch
                finally {
                    try {
                        gzos.close();
                    }
                    catch(Exception e) {
                    }
                    try {
                        b64os.close();
                    }
                    catch(Exception e) {
                    }
                    try {
                        baos.close();
                    }
                    catch(Exception e) {
                    }
                }   // end finally

                // Return value according to relevant encoding.
                try {
                    return new String(baos.toByteArray(), PREFERRED_ENCODING);
                }   // end try
                catch(java.io.UnsupportedEncodingException uue) {
                    return new String(baos.toByteArray());
                }   // end catch
            }   // end if: compress

            // Else, don't compress. Better not to use streams at all then.
            else {
                // Convert option to boolean in way that code likes it.
                boolean breakLines=dontBreakLines == 0;

                int len43=len * 4 / 3;
                byte[] outBuff=new byte[(len43)                      // Main 4:3
                        + ((len % 3) > 0? 4 : 0)      // Account for padding
                        + (breakLines? (len43 / MAX_LINE_LENGTH) : 0)]; // New lines
                int d=0;
                int e=0;
                int len2=len - 2;
                int lineLength=0;
                for(; d < len2; d+=3, e+=4) {
                    encode3to4(source, d + off, 3, outBuff, e);

                    lineLength+=4;
                    if(breakLines && lineLength == MAX_LINE_LENGTH) {
                        outBuff[e + 4]=NEW_LINE;
                        e++;
                        lineLength=0;
                    }   // end if: end of line
                }   // en dfor: each piece of array

                if(d < len) {
                    encode3to4(source, d + off, len - d, outBuff, e);
                    e+=4;
                }   // end if: some padding needed


                // Return value according to relevant encoding.
                try {
                    return new String(outBuff, 0, e, PREFERRED_ENCODING);
                }   // end try
                catch(java.io.UnsupportedEncodingException uue) {
                    return new String(outBuff, 0, e);
                }   // end catch

            }   // end else: don't compress

        }   // end encodeBytes


/* ********  D E C O D I N G   M E T H O D S  ******** */


        /**
         * Decodes four bytes from array <var>source</var>
         * and writes the resulting bytes (up to three of them)
         * to <var>destination</var>.
         * The source and destination arrays can be manipulated
         * anywhere along their length by specifying
         * <var>srcOffset</var> and <var>destOffset</var>.
         * This method does not check to make sure your arrays
         * are large enough to accomodate <var>srcOffset</var> + 4 for
         * the <var>source</var> array or <var>destOffset</var> + 3 for
         * the <var>destination</var> array.
         * This method returns the actual number of bytes that
         * were converted from the Base64 encoding.
         * @param source      the array to convert
         * @param srcOffset   the index where conversion begins
         * @param destination the array to hold the conversion
         * @param destOffset  the index where output will be put
         * @return the number of decoded bytes converted
         * @since 1.3
         */
        private static int decode4to3(byte[] source, int srcOffset, byte[] destination, int destOffset) {
            // Example: Dk==
            if(source[srcOffset + 2] == EQUALS_SIGN) {
                // Two ways to do the same thing. Don't know which way I like best.
                //int outBuff =   ( ( DECODABET[ source[ srcOffset    ] ] << 24 ) >>>  6 )
                //              | ( ( DECODABET[ source[ srcOffset + 1] ] << 24 ) >>> 12 );
                int outBuff=((DECODABET[source[srcOffset]] & 0xFF) << 18)
                        | ((DECODABET[source[srcOffset + 1]] & 0xFF) << 12);

                destination[destOffset]=(byte)(outBuff >>> 16);
                return 1;
            }

            // Example: DkL=
            else if(source[srcOffset + 3] == EQUALS_SIGN) {
                // Two ways to do the same thing. Don't know which way I like best.
                //int outBuff =   ( ( DECODABET[ source[ srcOffset     ] ] << 24 ) >>>  6 )
                //              | ( ( DECODABET[ source[ srcOffset + 1 ] ] << 24 ) >>> 12 )
                //              | ( ( DECODABET[ source[ srcOffset + 2 ] ] << 24 ) >>> 18 );
                int outBuff=((DECODABET[source[srcOffset]] & 0xFF) << 18)
                        | ((DECODABET[source[srcOffset + 1]] & 0xFF) << 12)
                        | ((DECODABET[source[srcOffset + 2]] & 0xFF) << 6);

                destination[destOffset]=(byte)(outBuff >>> 16);
                destination[destOffset + 1]=(byte)(outBuff >>> 8);
                return 2;
            }

            // Example: DkLE
            else {
                try {
                    // Two ways to do the same thing. Don't know which way I like best.
                    //int outBuff =   ( ( DECODABET[ source[ srcOffset     ] ] << 24 ) >>>  6 )
                    //              | ( ( DECODABET[ source[ srcOffset + 1 ] ] << 24 ) >>> 12 )
                    //              | ( ( DECODABET[ source[ srcOffset + 2 ] ] << 24 ) >>> 18 )
                    //              | ( ( DECODABET[ source[ srcOffset + 3 ] ] << 24 ) >>> 24 );
                    int outBuff=((DECODABET[source[srcOffset]] & 0xFF) << 18)
                            | ((DECODABET[source[srcOffset + 1]] & 0xFF) << 12)
                            | ((DECODABET[source[srcOffset + 2]] & 0xFF) << 6)
                            | ((DECODABET[source[srcOffset + 3]] & 0xFF));


                    destination[destOffset]=(byte)(outBuff >> 16);
                    destination[destOffset + 1]=(byte)(outBuff >> 8);
                    destination[destOffset + 2]=(byte)(outBuff);

                    return 3;
                }
                catch(Exception e) {
                    System.out.println(valueOf(source[srcOffset]) + ": " + (DECODABET[source[srcOffset]]));
                    System.out.println(valueOf(source[srcOffset + 1]) + ": " + (DECODABET[source[srcOffset + 1]]));
                    System.out.println(valueOf(source[srcOffset + 2]) + ": " + (DECODABET[source[srcOffset + 2]]));
                    System.out.println(String.valueOf(source[srcOffset + 3]) + ": " + (DECODABET[source[srcOffset + 3]]));
                    return -1;
                }   //e nd catch
            }
        }   // end decodeToBytes


        /**
         * Very low-level access to decoding ASCII characters in
         * the form of a byte array. Does not support automatically
         * gunzipping or any other "fancy" features.
         * @param source The Base64 encoded data
         * @param off    The offset of where to begin decoding
         * @param len    The length of characters to decode
         * @return decoded data
         * @since 1.3
         */
        public static byte[] decode(byte[] source, int off, int len) {
            int len34=len * 3 / 4;
            byte[] outBuff=new byte[len34]; // Upper limit on size of output
            int outBuffPosn=0;

            byte[] b4=new byte[4];
            int b4Posn=0;
            int i=0;
            byte sbiCrop=0;
            byte sbiDecode=0;
            for(i=off; i < off + len; i++) {
                sbiCrop=(byte)(source[i] & 0x7f); // Only the low seven bits
                sbiDecode=DECODABET[sbiCrop];

                if(sbiDecode >= WHITE_SPACE_ENC) // White space, Equals sign or better
                {
                    if(sbiDecode >= EQUALS_SIGN_ENC) {
                        b4[b4Posn++]=sbiCrop;
                        if(b4Posn > 3) {
                            outBuffPosn+=decode4to3(b4, 0, outBuff, outBuffPosn);
                            b4Posn=0;

                            // If that was the equals sign, break out of 'for' loop
                            if(sbiCrop == EQUALS_SIGN)
                                break;
                        }   // end if: quartet built

                    }   // end if: equals sign or better

                }   // end if: white space, equals sign or better
                else {
                    System.err.println("Bad Base64 input character at " + i + ": " + source[i] + "(decimal)");
                    return null;
                }   // end else:
            }   // each input character

            byte[] out=new byte[outBuffPosn];
            System.arraycopy(outBuff, 0, out, 0, outBuffPosn);
            return out;
        }   // end decode


        /**
         * Decodes data from Base64 notation, automatically
         * detecting gzip-compressed data and decompressing it.
         * @param s the string to decode
         * @return the decoded data
         * @since 1.4
         */
        public static byte[] decode(String s) {
            byte[] bytes;
            try {
                bytes=s.getBytes(PREFERRED_ENCODING);
            }   // end try
            catch(java.io.UnsupportedEncodingException uee) {
                bytes=s.getBytes();
            }   // end catch
            //</change>

            // Decode
            bytes=decode(bytes, 0, bytes.length);


            // Check to see if it's gzip-compressed
            // GZIP Magic Two-Byte Number: 0x8b1f (35615)
            if(bytes != null && bytes.length >= 4) {

                int head=((int)bytes[0] & 0xff) | ((bytes[1] << 8) & 0xff00);
                if(java.util.zip.GZIPInputStream.GZIP_MAGIC == head) {
                    java.io.ByteArrayInputStream bais=null;
                    java.util.zip.GZIPInputStream gzis=null;
                    java.io.ByteArrayOutputStream baos=null;
                    byte[] buffer=new byte[2048];
                    int length=0;

                    try {
                        baos=new java.io.ByteArrayOutputStream();
                        bais=new java.io.ByteArrayInputStream(bytes);
                        gzis=new java.util.zip.GZIPInputStream(bais);

                        while((length=gzis.read(buffer)) >= 0) {
                            baos.write(buffer, 0, length);
                        }   // end while: reading input

                        // No error? Get new bytes.
                        bytes=baos.toByteArray();

                    }   // end try
                    catch(java.io.IOException e) {
                        // Just return originally-decoded bytes
                    }   // end catch
                    finally {
                        try {
                            baos.close();
                        }
                        catch(Exception e) {
                        }
                        try {
                            gzis.close();
                        }
                        catch(Exception e) {
                        }
                        try {
                            bais.close();
                        }
                        catch(Exception e) {
                        }
                    }   // end finally

                }   // end if: gzipped
            }   // end if: bytes.length >= 2

            return bytes;
        }   // end decode


        /**
         * Attempts to decode Base64 data and deserialize a Java
         * Object within. Returns <tt>null</tt> if there was an error.
         * @param encodedObject The Base64 data to decode
         * @return The decoded and deserialized object
         * @since 1.5
         */
        public static Object decodeToObject(String encodedObject) {
            // Decode and gunzip if necessary
            byte[] objBytes=decode(encodedObject);

            java.io.ByteArrayInputStream bais=null;
            java.io.ObjectInputStream ois=null;
            Object obj=null;

            try {
                bais=new java.io.ByteArrayInputStream(objBytes);
                ois=new java.io.ObjectInputStream(bais);

                obj=ois.readObject();
            }   // end try
            catch(java.io.IOException e) {
                e.printStackTrace();
                obj=null;
            }   // end catch
            catch(java.lang.ClassNotFoundException e) {
                e.printStackTrace();
                obj=null;
            }   // end catch
            finally {
                try {
                    if(bais != null)
                        bais.close();
                }
                catch(Exception e) {
                }
                try {
                    if(ois != null)
                        ois.close();
                }
                catch(Exception e) {
                }
            }   // end finally

            return obj;
        }   // end decodeObject


        /**
         * Convenience method for encoding data to a file.
         * @param dataToEncode byte array of data to encode in base64 form
         * @param filename     Filename for saving encoded data
         * @return <tt>true</tt> if successful, <tt>false</tt> otherwise
         * @since 2.1
         */
        public static boolean encodeToFile(byte[] dataToEncode, String filename) {
            boolean success=false;
            Base64.OutputStream bos=null;
            try {
                bos=new Base64.OutputStream(
                        new java.io.FileOutputStream(filename), Base64.ENCODE);
                bos.write(dataToEncode);
                success=true;
            }   // end try
            catch(java.io.IOException e) {

                success=false;
            }   // end catch: IOException
            finally {
                try {
                    if(bos != null)
                        bos.close();
                }
                catch(Exception e) {
                }
            }   // end finally

            return success;
        }   // end encodeToFile


        /**
         * Convenience method for decoding data to a file.
         * @param dataToDecode Base64-encoded data as a string
         * @param filename     Filename for saving decoded data
         * @return <tt>true</tt> if successful, <tt>false</tt> otherwise
         * @since 2.1
         */
        public static boolean decodeToFile(String dataToDecode, String filename) {
            boolean success=false;
            Base64.OutputStream bos=null;
            try {
                bos=new Base64.OutputStream(
                        new java.io.FileOutputStream(filename), Base64.DECODE);
                bos.write(dataToDecode.getBytes(PREFERRED_ENCODING));
                success=true;
            }   // end try
            catch(java.io.IOException e) {
                success=false;
            }   // end catch: IOException
            finally {
                try {
                    if(bos != null)
                        bos.close();
                }
                catch(Exception e) {
                }
            }   // end finally

            return success;
        }   // end decodeToFile


        /**
         * Convenience method for reading a base64-encoded
         * file and decoding it.
         * @param filename Filename for reading encoded data
         * @return decoded byte array or null if unsuccessful
         * @since 2.1
         */
        public static byte[] decodeFromFile(String filename) {
            byte[] decodedData=null;
            Base64.InputStream bis=null;
            try {
                // Set up some useful variables
                java.io.File file=new java.io.File(filename);
                byte[] buffer=null;
                int length=0;
                int numBytes=0;

                // Check for size of file
                if(file.length() > Integer.MAX_VALUE) {
                    System.err.println("File is too big for this convenience method (" + file.length() + " bytes).");
                    return null;
                }   // end if: file too big for int index
                buffer=new byte[(int)file.length()];

                // Open a stream
                bis=new Base64.InputStream(
                        new java.io.BufferedInputStream(
                                new java.io.FileInputStream(file)), Base64.DECODE);

                // Read until done
                while((numBytes=bis.read(buffer, length, 4096)) >= 0)
                    length+=numBytes;

                // Save in a variable to return
                decodedData=new byte[length];
                System.arraycopy(buffer, 0, decodedData, 0, length);

            }   // end try
            catch(java.io.IOException e) {
                System.err.println("Error decoding from file " + filename);
            }   // end catch: IOException
            finally {
                try {
                    if(bis != null)
                        bis.close();
                }
                catch(Exception e) {
                }
            }   // end finally

            return decodedData;
        }   // end decodeFromFile


        /**
         * Convenience method for reading a binary file
         * and base64-encoding it.
         * @param filename Filename for reading binary data
         * @return base64-encoded string or null if unsuccessful
         * @since 2.1
         */
        public static String encodeFromFile(String filename) {
            String encodedData=null;
            Base64.InputStream bis=null;
            try {
                // Set up some useful variables
                java.io.File file=new java.io.File(filename);
                byte[] buffer=new byte[(int)(file.length() * 1.4)];
                int length=0;
                int numBytes=0;

                // Open a stream
                bis=new Base64.InputStream(
                        new java.io.BufferedInputStream(
                                new java.io.FileInputStream(file)), Base64.ENCODE);

                // Read until done
                while((numBytes=bis.read(buffer, length, 4096)) >= 0)
                    length+=numBytes;

                // Save in a variable to return
                encodedData=new String(buffer, 0, length, Base64.PREFERRED_ENCODING);

            }   // end try
            catch(java.io.IOException e) {
                System.err.println("Error encoding from file " + filename);
            }   // end catch: IOException
            finally {
                try {
                    if(bis != null)
                        bis.close();
                }
                catch(Exception e) {
                }
            }   // end finally

            return encodedData;
        }   // end encodeFromFile


        /* ********  I N N E R   C L A S S   I N P U T S T R E A M  ******** */


        /**
         * A {@link Base64.InputStream} will read data from another
         * <tt>java.io.InputStream</tt>, given in the constructor,
         * and encode/decode to/from Base64 notation on the fly.
         * @see Base64
         * @since 1.3
         */
        public static class InputStream extends java.io.FilterInputStream {
            private boolean encode;         // Encoding or decoding
            private int position;       // Current position in the buffer
            private byte[] buffer;         // Small buffer holding converted data
            private int bufferLength;   // Length of buffer (3 or 4)
            private int numSigBytes;    // Number of meaningful bytes in the buffer
            private int lineLength;
            private boolean breakLines;     // Break lines at less than 80 characters


            /**
             * Constructs a {@link Base64.InputStream} in DECODE mode.
             * @param in the <tt>java.io.InputStream</tt> from which to read data.
             * @since 1.3
             */
            public InputStream(java.io.InputStream in) {
                this(in, DECODE);
            }   // end constructor


            /**
             * Constructs a {@link Base64.InputStream} in
             * either ENCODE or DECODE mode.
             * <p/>
             * Valid options:<pre>
             *   ENCODE or DECODE: Encode or Decode as data is read.
             *   DONT_BREAK_LINES: don't break lines at 76 characters
             *     (only meaningful when encoding)
             *     <i>Note: Technically, this makes your encoding non-compliant.</i>
             * </pre>
             * <p/>
             * Example: <code>new Base64.InputStream( in, Base64.DECODE )</code>
             * @param in      the <tt>java.io.InputStream</tt> from which to read data.
             * @param options Specified options
             * @see Base64#ENCODE
             * @see Base64#DECODE
             * @see Base64#DONT_BREAK_LINES
             * @since 2.0
             */
            public InputStream(java.io.InputStream in, int options) {
                super(in);
                this.breakLines=(options & DONT_BREAK_LINES) != DONT_BREAK_LINES;
                this.encode=(options & ENCODE) == ENCODE;
                this.bufferLength=encode? 4 : 3;
                this.buffer=new byte[bufferLength];
                this.position=-1;
                this.lineLength=0;
            }   // end constructor

            /**
             * Reads enough of the input stream to convert
             * to/from Base64 and returns the next byte.
             * @return next byte
             * @since 1.3
             */
            public int read() throws java.io.IOException {
                // Do we need to get data?
                if(position < 0) {
                    if(encode) {
                        byte[] b3=new byte[3];
                        int numBinaryBytes=0;
                        for(int i=0; i < 3; i++) {
                            try {
                                int b=in.read();

                                // If end of stream, b is -1.
                                if(b >= 0) {
                                    b3[i]=(byte)b;
                                    numBinaryBytes++;
                                }   // end if: not end of stream

                            }   // end try: read
                            catch(java.io.IOException e) {
                                // Only a problem if we got no data at all.
                                if(i == 0)
                                    throw e;

                            }   // end catch
                        }   // end for: each needed input byte

                        if(numBinaryBytes > 0) {
                            encode3to4(b3, 0, numBinaryBytes, buffer, 0);
                            position=0;
                            numSigBytes=4;
                        }   // end if: got data
                        else {
                            return -1;
                        }   // end else
                    }   // end if: encoding

                    // Else decoding
                    else {
                        byte[] b4=new byte[4];
                        int i=0;
                        for(i=0; i < 4; i++) {
                            // Read four "meaningful" bytes:
                            int b=0;
                            do {
                                b=in.read();
                            }
                            while(b >= 0 && DECODABET[b & 0x7f] <= WHITE_SPACE_ENC);

                            if(b < 0)
                                break; // Reads a -1 if end of stream

                            b4[i]=(byte)b;
                        }   // end for: each needed input byte

                        if(i == 4) {
                            numSigBytes=decode4to3(b4, 0, buffer, 0);
                            position=0;
                        }   // end if: got four characters
                        else if(i == 0) {
                            return -1;
                        }   // end else if: also padded correctly
                        else {
                            // Must have broken out from above.
                            throw new java.io.IOException("Improperly padded Base64 input.");
                        }   // end

                    }   // end else: decode
                }   // end else: get data

                // Got data?
                if(position >= 0) {
                    // End of relevant data?
                    if( /*!encode &&*/ position >= numSigBytes)
                        return -1;

                    if(encode && breakLines && lineLength >= MAX_LINE_LENGTH) {
                        lineLength=0;
                        return '\n';
                    }   // end if
                    else {
                        lineLength++;   // This isn't important when decoding
                        // but throwing an extra "if" seems
                        // just as wasteful.

                        int b=buffer[position++];

                        if(position >= bufferLength)
                            position=-1;

                        return b & 0xFF; // This is how you "cast" a byte that's
                        // intended to be unsigned.
                    }   // end else
                }   // end if: position >= 0

                // Else error
                else {
                    // When JDK1.4 is more accepted, use an assertion here.
                    throw new java.io.IOException("Error in Base64 code reading stream.");
                }   // end else
            }   // end read


            /**
             * Calls {@link #read()} repeatedly until the end of stream
             * is reached or <var>len</var> bytes are read.
             * Returns number of bytes read into array or -1 if
             * end of stream is encountered.
             * @param dest array to hold values
             * @param off  offset for array
             * @param len  max number of bytes to read into array
             * @return bytes read into array or -1 if end of stream is encountered.
             * @since 1.3
             */
            public int read(byte[] dest, int off, int len) throws java.io.IOException {
                int i;
                int b;
                for(i=0; i < len; i++) {
                    b=read();

                    //if( b < 0 && i == 0 )
                    //    return -1;

                    if(b >= 0)
                        dest[off + i]=(byte)b;
                    else if(i == 0)
                        return -1;
                    else
                        break; // Out of 'for' loop
                }   // end for: each byte read
                return i;
            }   // end read

        }   // end inner class InputStream


        /* ********  I N N E R   C L A S S   O U T P U T S T R E A M  ******** */


        /**
         * A {@link Base64.OutputStream} will write data to another
         * <tt>java.io.OutputStream</tt>, given in the constructor,
         * and encode/decode to/from Base64 notation on the fly.
         * @see Base64
         * @since 1.3
         */
        public static class OutputStream extends java.io.FilterOutputStream {
            private boolean encode;
            private int position;
            private byte[] buffer;
            private int bufferLength;
            private int lineLength;
            private boolean breakLines;
            private byte[] b4; // Scratch used in a few places
            private boolean suspendEncoding;

            /**
             * Constructs a {@link Base64.OutputStream} in ENCODE mode.
             * @param out the <tt>java.io.OutputStream</tt> to which data will be written.
             * @since 1.3
             */
            public OutputStream(java.io.OutputStream out) {
                this(out, ENCODE);
            }   // end constructor


            /**
             * Constructs a {@link Base64.OutputStream} in
             * either ENCODE or DECODE mode.
             * <p/>
             * Valid options:<pre>
             *   ENCODE or DECODE: Encode or Decode as data is read.
             *   DONT_BREAK_LINES: don't break lines at 76 characters
             *     (only meaningful when encoding)
             *     <i>Note: Technically, this makes your encoding non-compliant.</i>
             * </pre>
             * <p/>
             * Example: <code>new Base64.OutputStream( out, Base64.ENCODE )</code>
             * @param out     the <tt>java.io.OutputStream</tt> to which data will be written.
             * @param options Specified options.
             * @see Base64#ENCODE
             * @see Base64#DECODE
             * @see Base64#DONT_BREAK_LINES
             * @since 1.3
             */
            public OutputStream(java.io.OutputStream out, int options) {
                super(out);
                this.breakLines=(options & DONT_BREAK_LINES) != DONT_BREAK_LINES;
                this.encode=(options & ENCODE) == ENCODE;
                this.bufferLength=encode? 3 : 4;
                this.buffer=new byte[bufferLength];
                this.position=0;
                this.lineLength=0;
                this.suspendEncoding=false;
                this.b4=new byte[4];
            }   // end constructor


            /**
             * Writes the byte to the output stream after
             * converting to/from Base64 notation.
             * When encoding, bytes are buffered three
             * at a time before the output stream actually
             * gets a write() call.
             * When decoding, bytes are buffered four
             * at a time.
             * @param theByte the byte to write
             * @since 1.3
             */
            public void write(int theByte) throws java.io.IOException {
                // Encoding suspended?
                if(suspendEncoding) {
                    super.out.write(theByte);
                    return;
                }   // end if: supsended

                // Encode?
                if(encode) {
                    buffer[position++]=(byte)theByte;
                    if(position >= bufferLength)  // Enough to encode.
                    {
                        out.write(encode3to4(b4, buffer, bufferLength));

                        lineLength+=4;
                        if(breakLines && lineLength >= MAX_LINE_LENGTH) {
                            out.write(NEW_LINE);
                            lineLength=0;
                        }   // end if: end of line

                        position=0;
                    }   // end if: enough to output
                }   // end if: encoding

                // Else, Decoding
                else {
                    // Meaningful Base64 character?
                    if(DECODABET[theByte & 0x7f] > WHITE_SPACE_ENC) {
                        buffer[position++]=(byte)theByte;
                        if(position >= bufferLength)  // Enough to output.
                        {
                            int len=Base64.decode4to3(buffer, 0, b4, 0);
                            out.write(b4, 0, len);
                            //out.write( Base64.decode4to3( buffer ) );
                            position=0;
                        }   // end if: enough to output
                    }   // end if: meaningful base64 character
                    else if(DECODABET[theByte & 0x7f] != WHITE_SPACE_ENC) {
                        throw new java.io.IOException("Invalid character in Base64 data.");
                    }   // end else: not white space either
                }   // end else: decoding
            }   // end write


            /**
             * Calls {@link #write(int)} repeatedly until <var>len</var>
             * bytes are written.
             * @param theBytes array from which to read bytes
             * @param off      offset for array
             * @param len      max number of bytes to read into array
             * @since 1.3
             */
            public void write(byte[] theBytes, int off, int len) throws java.io.IOException {
                // Encoding suspended?
                if(suspendEncoding) {
                    super.out.write(theBytes, off, len);
                    return;
                }   // end if: supsended

                for(int i=0; i < len; i++) {
                    write(theBytes[off + i]);
                }   // end for: each byte written

            }   // end write


            /**
             * Method added by PHIL. [Thanks, PHIL. -Rob]
             * This pads the buffer without closing the stream.
             */
            public void flushBase64() throws java.io.IOException {
                if(position > 0) {
                    if(encode) {
                        out.write(encode3to4(b4, buffer, position));
                        position=0;
                    }   // end if: encoding
                    else {
                        throw new java.io.IOException("Base64 input not properly padded.");
                    }   // end else: decoding
                }   // end if: buffer partially full

            }   // end flush


            /**
             * Flushes and closes (I think, in the superclass) the stream.
             * @since 1.3
             */
            public void close() throws java.io.IOException {
                // 1. Ensure that pending characters are written
                flushBase64();

                // 2. Actually close the stream
                // Base class both flushes and closes.
                super.close();

                buffer=null;
                out=null;
            }   // end close


            /**
             * Suspends encoding of the stream.
             * May be helpful if you need to embed a piece of
             * base640-encoded data in a stream.
             * @since 1.5.1
             */
            public void suspendEncoding() throws java.io.IOException {
                flushBase64();
                this.suspendEncoding=true;
            }   // end suspendEncoding


            /**
             * Resumes encoding of the stream.
             * May be helpful if you need to embed a piece of
             * base640-encoded data in a stream.
             * @since 1.5.1
             */
            public void resumeEncoding() {
                this.suspendEncoding=false;
            }   // end resumeEncoding


        }   // end inner class OutputStream


    }   // end class Base64

}





