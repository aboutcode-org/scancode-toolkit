<?php
/**
 * Bitcoin classes
 *
 * By Mike Gogulski - All rights reversed http://www.unlicense.org/ (public domain)
 *
 * If you find this library useful, your donation of Bitcoins to address
 * 1E3d6EWLgwisXY2CWXDcdQQP2ivRN7e9r9 would be greatly appreciated. Thanks!
 *
 * PHPDoc is available at http://code.gogulski.com/
 *
 * @author Mike Gogulski - http://www.nostate.com/ http://www.gogulski.com/
 * @author theymos - theymos @ http://bitcoin.org/smf
 */

define("BITCOIN_ADDRESS_VERSION", "00");// this is a hex byte
/**
 * Bitcoin utility functions class
 *
 * @author theymos (functionality)
 * @author Mike Gogulski
 * http://www.gogulski.com/ http://www.nostate.com/
 * (encapsulation, string abstraction, PHPDoc)
 */
class Bitcoin {

  /*
   * Bitcoin utility functions by theymos
   * Via http://www.bitcoin.org/smf/index.php?topic=1844.0
   * hex input must be in uppercase, with no leading 0x
   */
  private static $hexchars = "0123456789ABCDEF";
  private static $base58chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

  /**
   * Convert a hex string into a (big) integer
   *
   * @param string $hex
   * @return int
   * @access private
   */
  private function decodeHex($hex) {
    $hex = strtoupper($hex);
    $return = "0";
    for ($i = 0; $i < strlen($hex); $i++) {
      $current = (string) strpos(self::$hexchars, $hex[$i]);
      $return = (string) bcmul($return, "16", 0);
      $return = (string) bcadd($return, $current, 0);
    }
    return $return;
  }

  /**
   * Convert an integer into a hex string
   *
   * @param int $dec
   * @return string
   * @access private
   */
  private function encodeHex($dec) {
    $return = "";
    while (bccomp($dec, 0) == 1) {
      $dv = (string) bcdiv($dec, "16", 0);
      $rem = (integer) bcmod($dec, "16");
      $dec = $dv;
      $return = $return . self::$hexchars[$rem];
    }
    return strrev($return);
  }

  /**
   * Convert a Base58-encoded integer into the equivalent hex string representation
   *
   * @param string $base58
   * @return string
   * @access private
   */
  private function decodeBase58($base58) {
    $origbase58 = $base58;

    $return = "0";
    for ($i = 0; $i < strlen($base58); $i++) {
      $current = (string) strpos(Bitcoin::$base58chars, $base58[$i]);
      $return = (string) bcmul($return, "58", 0);
      $return = (string) bcadd($return, $current, 0);
    }

    $return = self::encodeHex($return);

    //leading zeros
    for ($i = 0; $i < strlen($origbase58) && $origbase58[$i] == "1"; $i++) {
      $return = "00" . $return;
    }

    if (strlen($return) % 2 != 0) {
      $return = "0" . $return;
    }

    return $return;
  }

  /**
   * Convert a hex string representation of an integer into the equivalent Base58 representation
   *
   * @param string $hex
   * @return string
   * @access private
   */
  private function encodeBase58($hex) {
    if (strlen($hex) % 2 != 0) {
      die("encodeBase58: uneven number of hex characters");
    }
    $orighex = $hex;

    $hex = self::decodeHex($hex);
    $return = "";
    while (bccomp($hex, 0) == 1) {
      $dv = (string) bcdiv($hex, "58", 0);
      $rem = (integer) bcmod($hex, "58");
      $hex = $dv;
      $return = $return . self::$base58chars[$rem];
    }
    $return = strrev($return);

    //leading zeros
    for ($i = 0; $i < strlen($orighex) && substr($orighex, $i, 2) == "00"; $i += 2) {
      $return = "1" . $return;
    }

    return $return;
  }

  /**
   * Convert a 160-bit Bitcoin hash to a Bitcoin address
   *
   * @author theymos
   * @param string $hash160
   * @param string $addressversion
   * @return string Bitcoin address
   * @access public
   */
  public static function hash160ToAddress($hash160, $addressversion = BITCOIN_ADDRESS_VERSION) {
    $hash160 = $addressversion . $hash160;
    $check = pack("H*", $hash160);
    $check = hash("sha256", hash("sha256", $check, true));
    $check = substr($check, 0, 8);
    $hash160 = strtoupper($hash160 . $check);
    return self::encodeBase58($hash160);
  }

  /**
   * Convert a Bitcoin address to a 160-bit Bitcoin hash
   *
   * @author theymos
   * @param string $addr
   * @return string Bitcoin hash
   * @access public
   */
  public static function addressToHash160($addr) {
    $addr = self::decodeBase58($addr);
    $addr = substr($addr, 2, strlen($addr) - 10);
    return $addr;
  }

  /**
   * Determine if a string is a valid Bitcoin address
   *
   * @author theymos
   * @param string $addr String to test
   * @param string $addressversion
   * @return boolean
   * @access public
   */
  public static function checkAddress($addr, $addressversion = BITCOIN_ADDRESS_VERSION) {
    $addr = self::decodeBase58($addr);
    if (strlen($addr) != 50) {
      return false;
    }
    $version = substr($addr, 0, 2);
    if (hexdec($version) > hexdec($addressversion)) {
      return false;
    }
    $check = substr($addr, 0, strlen($addr) - 8);
    $check = pack("H*", $check);
    $check = strtoupper(hash("sha256", hash("sha256", $check, true)));
    $check = substr($check, 0, 8);
    return $check == substr($addr, strlen($addr) - 8);
  }

  /**
   * Convert the input to its 160-bit Bitcoin hash
   *
   * @param string $data
   * @return string
   * @access private
   */
  private function hash160($data) {
    $data = pack("H*", $data);
    return strtoupper(hash("ripemd160", hash("sha256", $data, true)));
  }

  /**
   * Convert a Bitcoin public key to a 160-bit Bitcoin hash
   *
   * @param string $pubkey
   * @return string
   * @access public
   */
  public static function pubKeyToAddress($pubkey) {
    return self::hash160ToAddress($this->hash160($pubkey));
  }

  /**
   * Remove leading "0x" from a hex value if present.
   *
   * @param string $string
   * @return string
   * @access public
   */
  public static function remove0x($string) {
    if (substr($string, 0, 2) == "0x" || substr($string, 0, 2) == "0X") {
      $string = substr($string, 2);
    }
    return $string;
  }
}

/**
 * Exception class for BitcoinClient
 *
 * @author Mike Gogulski
 * http://www.gogulski.com/ http://www.nostate.com/
 */
class BitcoinClientException extends ErrorException {
  // Redefine the exception so message isn't optional
  public function __construct($message, $code = 0, $severity = E_USER_NOTICE, Exception $previous = null) {
    parent::__construct($message, $code, $severity, $previous);
  }

  public function __toString() {
    return __CLASS__ . ": [{$this->code}]: {$this->message}\n";
  }
}

require_once(dirname(__FILE__) . "/includes/xmlrpc.inc");
require_once(dirname(__FILE__) . "/includes/jsonrpc.inc");

/**
 * Bitcoin client class for access to a Bitcoin server via JSON-RPC-HTTP[S]
 *
 * Implements the methods documented at https://www.bitcoin.org/wiki/doku.php?id=api
 *
 * @version 0.3.19
 * @author Mike Gogulski
 * http://www.gogulski.com/ http://www.nostate.com/
 */
class BitcoinClient extends jsonrpc_client {

}
