/**
 * An implementation of <a href="https://tools.ietf.org/html/rfc7253">RFC 7253 on The OCB
 * Authenticated-Encryption Algorithm</a>, licensed per:
 * <p>
 * <blockquote> <a href="https://www.cs.ucdavis.edu/~rogaway/ocb/license1.pdf">License for
 * Open-Source Software Implementations of OCB</a> (Jan 9, 2013) &mdash; &ldquo;License 1&rdquo; <br>
 * Under this license, you are authorized to make, use, and distribute open-source software
 * implementations of OCB. This license terminates for you if you sue someone over their open-source
 * software implementation of OCB claiming that you have a patent covering their implementation.
 * <p>
 * This is a non-binding summary of a legal document (the link above). The parameters of the license
 * are specified in the license document and that document is controlling. </blockquote>
 */
public class OCBBlockCipher
    implements AEADBlockCipher
{
    private static final int BLOCK_SIZE = 16;

    private BlockCipher hashCipher;
    private BlockCipher mainCipher;

