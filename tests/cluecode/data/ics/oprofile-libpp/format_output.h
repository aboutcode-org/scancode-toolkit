 * @file format_output.h
 * outputting format for symbol lists
 *
 * @remark Copyright 2002 OProfile authors
 * @remark Read the file COPYING
 *
			    size_t pc, counts_t & c,
			    extra_images const & extra, double d = 0.0)
			: symbol(sym), sample(s), pclass(pc),
			  counts(c), extra(extra), diff(d) {}
		symbol_entry const & symbol;
		sample_entry const & sample;