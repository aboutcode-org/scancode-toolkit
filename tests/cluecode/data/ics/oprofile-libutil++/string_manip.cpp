 * @file string_manip.cpp
 * std::string helpers
 *
 * @remark Copyright 2002 OProfile authors
 * @remark Read the file COPYING
 *

string split(string & s, char c)
{
	string::size_type i = s.find_first_of(c);
	if (i == string::npos)
		return string();