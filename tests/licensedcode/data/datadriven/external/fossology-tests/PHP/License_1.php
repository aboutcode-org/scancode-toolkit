<?php
/**
 * Abstract base class for licenses
 *
 * PHP versions 5
 *
 * LICENSE: This source file is subject to version 3.0 of the PHP license
 * that is available through the world-wide-web at the following URI:
 * http://www.php.net/license/3_0.txt.  If you did not receive a copy of
 * the PHP License and are unable to obtain it through the web, please
 * send a note to license@php.net so we can mail you a copy immediately.
 *
 * @category   Tools and Utilities
 * @package    CodeGen
 * @author     Hartmut Holzgraefe <hartmut@php.net>
 * @copyright  2005 Hartmut Holzgraefe
 * @license    http://www.php.net/license/3_0.txt  PHP License 3.0
 * @version    CVS: $Id: License.php 191282 2005-07-23 16:28:01Z hholzgra $
 * @link       http://pear.php.net/package/CodeGen
 */


/**
 * Abstract base class for licenses
 *
 * @category   Tools and Utilities
 * @package    CodeGen
 * @author     Hartmut Holzgraefe <hartmut@php.net>
 * @copyright  2005 Hartmut Holzgraefe
 * @license    http://www.php.net/license/3_0.txt  PHP License 3.0
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/CodeGen
 */
abstract class CodeGen_License
{
    /**
     * Constructor
     *
     * @access private
     * @param  License options
     */
    function __construct($options = array()) 
    {
        $this->options = $options;
    }

    /**
     * Takes a License shortname and returns an instantiated object of that license
     *
     * @access  public
     * @param   string  License shortname, e.g. PHP, BSD, LGPL
     * @param   array   License options
     * @returns object  License instance
     */
    static function factory($name, $options=array()) 
    {
        $classname = "CodeGen_License_".strtoupper($name);
        $classfile = str_replace("_", "/", $classname).".php";

        if (!class_exists($classname)) {
            if (!@include_once "$classfile")
                PEAR::raiseError("Unknown license type '$name' ", E_USER_WARNING);
        }

        return 
            class_exists($classname) 
            ? new $classname($options) 
            : false;
    }

    /**
     * Writes the License text to a file
     *
     * @param   string Filename to write to (default is ./LICENSE) 
     * @return  bool   Success state
     * @access  public
     */
    function writeToFile($path = "./LICENSE") 
    {
        $fp = fopen($path, "w");

        if (is_resource($fp)) {
            fputs($fp, $this->getText()); 
            fclose($fp);
            return true;
        }

        return false;
    }
    
    /**
     * Returns a string suitable for insertion into comment headers
     * 
     * @return string    License comment
     * @access public
     */
    abstract function getComment();

    /**
     * Returns the complete license text as string
     * 
     * @return string    License text
     * @access public
     */
    abstract function getText();
}

/*
 * Local variables:
 * tab-width: 4
 * c-basic-offset: 4
 * indent-tabs-mode:nil
 * End:
 */

?>