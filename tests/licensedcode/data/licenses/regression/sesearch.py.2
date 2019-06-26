#!/usr/bin/env python
# Copyright 2014-2015, Tresys Technology, LLC
#
# This file is part of SETools.
#
# SETools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# SETools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SETools.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import print_function
import setools
import argparse
import sys
import logging

parser = argparse.ArgumentParser(
    description="SELinux policy rule search tool.",
    epilog="TE/MLS rule searches cannot be mixed with RBAC rule searches.")
parser.add_argument("--version", action="version", version=setools.__version__)
parser.add_argument("policy", help="Path to the SELinux policy to search.", nargs="?")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Print extra informational messages")
parser.add_argument("--debug", action="store_true", dest="debug", help="Enable debugging.")

rtypes = parser.add_argument_group("TE Rule Types")
rtypes.add_argument("-A", action="store_true", help="Search allow and allowxperm rules.")
rtypes.add_argument("--allow", action="append_const",
                    const="allow", dest="tertypes",
                    help="Search allow rules.")
rtypes.add_argument("--allowxperm", action="append_const",
                    const="allowxperm", dest="tertypes",
                    help="Search allowxperm rules.")
rtypes.add_argument("--auditallow", action="append_const",
                    const="auditallow", dest="tertypes",
                    help="Search auditallow rules.")
rtypes.add_argument("--auditallowxperm", action="append_const",
                    const="auditallowxperm", dest="tertypes",
                    help="Search auditallowxperm rules.")
rtypes.add_argument("--dontaudit", action="append_const",
                    const="dontaudit", dest="tertypes",
                    help="Search dontaudit rules.")
rtypes.add_argument("--dontauditxperm", action="append_const",
                    const="dontauditxperm", dest="tertypes",
                    help="Search dontauditxperm rules.")
rtypes.add_argument("--neverallow", action="append_const",
                    const="neverallow", dest="tertypes",
                    help="Search neverallow rules.")
rtypes.add_argument("--neverallowxperm", action="append_const",
                    const="neverallowxperm", dest="tertypes",
                    help="Search neverallowxperm rules.")
rtypes.add_argument("-T", "--type_trans", action="append_const",
                    const="type_transition", dest="tertypes",
                    help="Search type_transition rules.")
rtypes.add_argument("--type_change", action="append_const",
                    const="type_change", dest="tertypes",
                    help="Search type_change rules.")
rtypes.add_argument("--type_member", action="append_const",
                    const="type_member", dest="tertypes",
                    help="Search type_member rules.")
rbacrtypes = parser.add_argument_group("RBAC Rule Types")
rbacrtypes.add_argument("--role_allow", action="append_const",
                        const="allow", dest="rbacrtypes",
                        help="Search role allow rules.")
rbacrtypes.add_argument("--role_trans", action="append_const",
                        const="role_transition", dest="rbacrtypes",
                        help="Search role_transition rules.")

mlsrtypes = parser.add_argument_group("MLS Rule Types")
mlsrtypes.add_argument("--range_trans", action="append_const",
                       const="range_transition", dest="mlsrtypes",
                       help="Search range_transition rules.")

expr = parser.add_argument_group("Expressions")
expr.add_argument("-s", "--source",
                  help="Source type/role of the TE/RBAC rule.")
expr.add_argument("-t", "--target",
                  help="Target type/role of the TE/RBAC rule.")
expr.add_argument("-c", "--class", dest="tclass",
                  help="Comma separated list of object classes")
expr.add_argument("-p", "--perms", metavar="PERMS",
                  help="Comma separated list of permissions.")
expr.add_argument("-x", "--xperms", metavar="XPERMS",
                  help="Comma separated list of extended permissions.")
expr.add_argument("-D", "--default",
                  help="Default of the rule. (type/role/range transition rules)")
expr.add_argument("-b", "--bool", dest="boolean", metavar="BOOL",
                  help="Comma separated list of Booleans in the conditional expression.")

opts = parser.add_argument_group("Search options")
opts.add_argument("-eb", action="store_true", dest="boolean_equal",
                  help="Match Boolean list exactly instead of matching any listed Boolean.")
opts.add_argument("-ep", action="store_true", dest="perms_equal",
                  help="Match permission set exactly instead of matching any listed permission.")
opts.add_argument("-ex", action="store_true", dest="xperms_equal",
                  help="Match extended permission set exactly instead of matching any listed "
                  "permission.")
opts.add_argument("-ds", action="store_false", dest="source_indirect",
                  help="Match source attributes directly instead of matching member types/roles.")
opts.add_argument("-dt", action="store_false", dest="target_indirect",
                  help="Match target attributes directly instead of matching member types/roles.")
opts.add_argument("-rs", action="store_true", dest="source_regex",
                  help="Use regular expression matching for the source type/role.")
opts.add_argument("-rt", action="store_true", dest="target_regex",
                  help="Use regular expression matching for the target type/role.")
opts.add_argument("-rc", action="store_true", dest="tclass_regex",
                  help="Use regular expression matching for the object class.")
opts.add_argument("-rd", action="store_true", dest="default_regex",
                  help="Use regular expression matching for the default type/role.")
opts.add_argument("-rb", action="store_true", dest="boolean_regex",
                  help="Use regular expression matching for Booleans.")

args = parser.parse_args()

if args.A:
    try:
        args.tertypes.extend(["allow", "allowxperm"])
    except AttributeError:
        args.tertypes = ["allow", "allowxperm"]

if not args.tertypes and not args.mlsrtypes and not args.rbacrtypes:
    parser.error("At least one rule type must be specified.")

if args.debug:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s|%(levelname)s|%(name)s|%(message)s')
elif args.verbose:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
else:
    logging.basicConfig(level=logging.WARNING, format='%(message)s')

try:
    p = setools.SELinuxPolicy(args.policy)

    if args.tertypes:
        q = setools.TERuleQuery(p,
                                ruletype=args.tertypes,
                                source=args.source,
                                source_indirect=args.source_indirect,
                                source_regex=args.source_regex,
                                target=args.target,
                                target_indirect=args.target_indirect,
                                target_regex=args.target_regex,
                                tclass_regex=args.tclass_regex,
                                perms_equal=args.perms_equal,
                                xperms_equal=args.xperms_equal,
                                default=args.default,
                                default_regex=args.default_regex,
                                boolean_regex=args.boolean_regex,
                                boolean_equal=args.boolean_equal)

        # these are broken out from the above statement to prevent making a list
        # with an empty string in it (split on empty string)
        if args.tclass:
            if args.tclass_regex:
                q.tclass = args.tclass
            else:
                q.tclass = args.tclass.split(",")

        if args.perms:
            q.perms = args.perms.split(",")

        if args.xperms:
            xperms = []
            for item in args.xperms.split(","):
                rng = item.split("-")
                if len(rng) == 2:
                    xperms.append((int(rng[0], base=16), int(rng[1], base=16)))
                elif len(rng) == 1:
                    xperms.append((int(rng[0], base=16), int(rng[0], base=16)))
                else:
                    parser.error("Enter an extended permission or extended permission range, e.g. "
                                 "0x5411 or 0x8800-0x88ff.")

            q.xperms = xperms

        if args.boolean:
            if args.boolean_regex:
                q.boolean = args.boolean
            else:
                q.boolean = args.boolean.split(",")

        for r in sorted(q.results()):
            print(r)

    if args.rbacrtypes:
        q = setools.RBACRuleQuery(p,
                                  ruletype=args.rbacrtypes,
                                  source=args.source,
                                  source_indirect=args.source_indirect,
                                  source_regex=args.source_regex,
                                  target=args.target,
                                  target_indirect=args.target_indirect,
                                  target_regex=args.target_regex,
                                  default=args.default,
                                  default_regex=args.default_regex,
                                  tclass_regex=args.tclass_regex)

        # these are broken out from the above statement to prevent making a list
        # with an empty string in it (split on empty string)
        if args.tclass:
            if args.tclass_regex:
                q.tclass = args.tclass
            else:
                q.tclass = args.tclass.split(",")

        for r in sorted(q.results()):
            print(r)

    if args.mlsrtypes:
        q = setools.MLSRuleQuery(p,
                                 ruletype=args.mlsrtypes,
                                 source=args.source,
                                 source_indirect=args.source_indirect,
                                 source_regex=args.source_regex,
                                 target=args.target,
                                 target_indirect=args.target_indirect,
                                 target_regex=args.target_regex,
                                 tclass_regex=args.tclass_regex,
                                 default=args.default)

        # these are broken out from the above statement to prevent making a list
        # with an empty string in it (split on empty string)
        if args.tclass:
            if args.tclass_regex:
                q.tclass = args.tclass
            else:
                q.tclass = args.tclass.split(",")

        for r in sorted(q.results()):
            print(r)

except Exception as err:
    if args.debug:
        logging.exception(str(err))
    else:
        print(err)

    sys.exit(1)
