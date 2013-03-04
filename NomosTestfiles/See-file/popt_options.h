/**
 * @file popt_options.h
 * option parsing
 *
 * This provides a simple facility for adding command-line
 * options, and parsing them.
 *
 * You can add a number of options and then call parse_options()
 * to process them, for example :
 *
 * \code
 * bool allow_frob;
 * string frob;
 * static popt::option allow_frob_opt(allow_frob, "allow-frob", 'a', "allow frobs");
 * static popt::option frob_opt(frob, "frob", 'f', "what to frob", "name");
 *
 * ...
 * popt::parse_options(argc, argv, add_params);
 * \endcode
 *
 * Note than if you try to implement an option for an unsupported type  like :
 * \code
 * static unsigned int i;
 * static popt::option i_opt(i, ....);
 * \endcode
 * you don't get a compile time error but a link time error.
 *
 * The call to parse_options() will fill in allow_frob and frob, if they
 * are passed to the program (myfrobber --allow-frob --frob foo), and place
 * any left over command line arguments in the add_params vector. Note
 * that the template parameter denotes the type of the option argument.
 *
 * When the template parameter type is bool, option starting with "no-" prefix
 * are implicitely considered as negated before writing the associated bool so
 * this will work as expected:
 * \code
 * bool demangle;
 * popt::option(demangle, "demangle", 'd', "demangle C++ symbols"),
 * popt::option(demangle, "no-demangle", '\0', "don't demangle C++ symbols"),
 * \endcode
 *
 * @remark Copyright 2002 OProfile authors
 * @remark Read the file COPYING
 *
 * @author Philippe Elie
 * @author John Levon
 */

#ifndef POPT_OPTIONS_H
#define POPT_OPTIONS_H

#include <string>
#include <vector>

namespace popt {
 
/**
 * parse_options - parse command line options
 * @param argc like the parameter of main()
 * @param argv like the parameter of main()
 * @param additional_params additional options are stored here
 *
 * Parse the given command line with the previous
 * options created. Multiple additional arguments
 * that are not recognised will be added to the additional_params
 * vector.
 */
void parse_options(int argc, char const ** argv,
                   std::vector<std::string> & additional_params);

class option_base;

/**
 * option - base class for a command line option
 *
 * Every command line option added before calling parse_options()
 * is of this type.
 */
class option {
public:
	/**
	 * Templatized constructor for an option. This adds the option
	 * to the option list on construction. This is specialized for
	 * each recognised option value type below.
	 */
	template <class T> option(T &, char const * option_name,
	                          char short_name, char const * help_str,
	                          char const * arg_help_str);

	/**
	 * boolean operations don't get the same set of parameters as other
	 * option, as there is no argument to give help for.
	 * Due to a bug in gcc 2.95 we can't use a default parameter
	 * in the templatized ctor above because 2.95 is unable to match
	 * the right ctor. So on we add a non-templatized ctor with an exact
	 * match for boolean option.
	 */
	option(bool &, char const * option_name,
	       char short_name, char const * help_str);

	~option();

private:
	option_base * the_option;
};


/**
 * The supported option type, boolean option are matched by a non templatized
 * ctor above.
 */
template <> option::option(int &, char const * option_name, char short_name,
                           char const * help_str, char const * arg_help_str);
template <> option::option(std::string &, char const * option_name,
                           char short_name, char const * help_str,
                           char const * arg_help_str);
template <> option::option(std::vector<std::string> &,
                           char const * option_name, char short_name,
                           char const * help_str, char const * arg_help_str);

} // namespace popt

#endif // POPT_OPTIONS_H
