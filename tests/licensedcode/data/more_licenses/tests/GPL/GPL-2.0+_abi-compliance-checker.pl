#!/usr/bin/perl
###########################################################################
# ABI-compliance-checker v1.13, lightweight tool for statically checking
# backward binary compatibility of shared C/C++ libraries in Linux.
# Copyright (C) The Linux Foundation
# Copyright (C) Institute for System Programming, RAS
# Author: Andrey Ponomarenko
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
###########################################################################
use Getopt::Long;
Getopt::Long::Configure ("posix_default", "no_ignore_case");
use Data::Dumper;

my $ABI_COMPLIANCE_CHECKER_VERSION = "1.13";
my ($Help, $ShowVersion, %Descriptor, $TargetLibraryName, $HeaderCheckingMode_Separately, $GenerateDescriptor, $TestSystem, $DumpInfo_DescriptorPath, $CheckHeadersOnly, $InterfacesListPath, $AppPath, $ShowExpendTime);

my $CmdName = get_FileName($0);
GetOptions("h|help!" => \$Help,
"v|version!" => \$ShowVersion,
#general options
"l|library=s" => \$TargetLibraryName,
"d1|descriptor1=s" => \$Descriptor{1}{"Path"},
"d2|descriptor2=s" => \$Descriptor{2}{"Path"},
#extra options
"app|application=s" => \$AppPath,
"symbols_list|int_list=s" => \$InterfacesListPath,
"dump_abi|dump_info=s" => \$DumpInfo_DescriptorPath,
"headers_only!" => \$CheckHeadersOnly,
#other options
"d|descriptor_template!" => \$GenerateDescriptor,
"separately!" => \$HeaderCheckingMode_Separately,
"test!" => \$TestSystem,
"time!" => \$ShowExpendTime
) or exit(1);

sub HELP_MESSAGE()
{
print STDERR <<"EOM"

NAME:
$CmdName - check ABI compatibility of shared C/C++ library versions

DESCRIPTION:
Lightweight tool for statically checking backward binary compatibility of shared C/C++ libraries
in Linux. It checks header files along with shared objects in two library versions and searches
for ABI changes that may lead to incompatibility. Breakage of the binary compatibility may result
in crashing or incorrect behavior of applications built with an old version of a library when
it is running with a new one.

ABI Compliance Checker was intended for library developers that are interested in ensuring
backward binary compatibility. Also it can be used for checking forward binary compatibility
and checking applications portability to the new library version.

This tool is free software: you can redistribute it and/or modify it under the terms of the GNU GPL.

USAGE:
$CmdName [options]

EXAMPLE OF USE:
$CmdName -l <library_name> -d1 <1st_version_descriptor> -d2 <2nd_version_descriptor>

GENERAL OPTIONS:
-h|-help
Print this help.

-v|-version
Print version.

-l|-library <name>
Library name (without version).
It affects only on the path and the title of the report.

-d1|-descriptor1 <path>
Path to descriptor of 1st library version.

-d2|-descriptor2 <path>
Path to descriptor of 2nd library version.

EXTRA OPTIONS:
-app|-application <path>
This option allow to specify the application that should be tested for portability
to the new library version.

-dump_abi|-dump_info <descriptor_path>
Dump library ABI information using specified descriptor.
This command will create '<library>_<ver1>.abi.tar.gz' file in the directory 'abi_dumps/<library>/'.
You can transfer it anywhere and pass instead of library descriptor.

-headers_only
Check header files without shared objects. It is easy to run, but may provide
a low quality ABI compliance report with false positives and without
detecting of added/withdrawn interfaces.

-symbols_list|-int_list <path>
This option allow to specify a file with a list of interfaces (mangled names in C++)
that should be checked, other library interfaces will not be checked.

OTHER OPTIONS:
-d|-descriptor_template
Create library descriptor template 'library-descriptor.xml' in the current directory.

-separately
Check headers individually. This mode requires more time for checking ABI compliance,
but possible compiler errors in one header can't affect others.

-test
Run internal tests (create two binary-incompatible versions of an artificial library
and run ABI-Compliance-Checker on it).

DESCRIPTOR EXAMPLE:
<version>
1.28.0
</version>

<headers>
/usr/local/atk/atk-1.28.0/include/
</headers>

<libs>
/usr/local/atk/atk-1.28.0/lib/libatk-1.0.so
</libs>

<include_paths>
/usr/include/glib-2.0/
/usr/lib/glib-2.0/include/
</include_paths>


Report bugs to <abi-compliance-checker\@linuxtesting.org>
For more information, please see: http://ispras.linux-foundation.org/index.php/ABI_compliance_checker
EOM
;
}

my $Descriptor_Template = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<descriptor>

<!-- Template for the library version descriptor -->

<!--
Necessary sections
-->

<version>
<!-- Version of the library -->
</version>

<headers>
<!-- The list of paths to header files and/or
directories with header files, one per line -->
</headers>

<libs>
<!-- The list of paths to shared objects and/or
directories with shared objects, one per line -->
</libs>

<!--
Additional sections
-->

<include_paths>
<!-- The list of paths to be searched for header files
needed for compiling of library headers, one per line -->
</include_paths>

<gcc_options>
<!-- Additional gcc options, one per line -->
</gcc_options>

<opaque_types>
<!-- The list of opaque types, one per line -->
</opaque_types>

<skip_interfaces>
<!-- The list of functions (mangled/symbol names in C++)
that should be skipped while testing, one per line -->
</skip_interfaces>

<include_preamble>
<!-- The list of header files that should be included before other headers, one per line.
For example, it is a tree.h for libxml2 and ft2build.h for freetype2 -->
</include_preamble>

</descriptor>";

my %Operator_Indication = (
"not" => "~",
"assign" => "=",
"andassign" => "&=",
"orassign" => "|=",
"xorassign" => "^=",
"or" => "|",
"xor" => "^",
"addr" => "&",
"and" => "&",
"lnot" => "!",
"eq" => "==",
"ne" => "!=",
"lt" => "<",
"lshift" => "<<",
"lshiftassign" => "<<=",
"rshiftassign" => ">>=",
"call" => "()",
"mod" => "%",
"modassign" => "%=",
"subs" => "[]",
"land" => "&&",
"lor" => "||",
"rshift" => ">>",
"ref" => "->",
"le" => "<=",
"deref" => "*",
"mult" => "*",
"preinc" => "++",
"delete" => " delete",
"vecnew" => " new[]",
"vecdelete" => " delete[]",
"predec" => "--",
"postinc" => "++",
"postdec" => "--",
"plusassign" => "+=",
"plus" => "+",
"minus" => "-",
"minusassign" => "-=",
"gt" => ">",
"ge" => ">=",
"new" => " new",
"multassign" => "*=",
"divassign" => "/=",
"div" => "/",
"neg" => "-",
"pos" => "+",
"memref" => "->*",
"compound" => ","
);

sub num_to_str($)
{
my $Number = $_[0];
if(int($Number)>3)
{
return $Number."th";
}
elsif(int($Number)==1)
{
return "1st";
}
elsif(int($Number)==2)
{
return "2nd";
}
elsif(int($Number)==3)
{
return "3rd";
}
else
{
return "";
}
}

#Global variables
my $REPORT_PATH;
my %ERR_PATH;
my $POINTER_SIZE;
my $MAX_COMMAND_LINE_ARGUMENTS = 4096;
my %Cache;
my %FuncAttr;
my %LibInfo;
my %HeaderCompileError;
my $StartTime;
my %CompilerOptions;
my %AddedInt;
my %WithdrawnInt;
my @RecurLib;
my %CheckedSoLib;

#Constants checking
my %ConstantsSrc;
my %Constants;

#Types
my %TypeDescr;
my %TemplateInstance_Func;
my %TemplateInstance;
my %OpaqueTypes;
my %Tid_TDid;
my %CheckedTypes;
my %Typedef_BaseName;
my %StdCxxTypedef;
my %TName_Tid;
my %EnumMembName_Id;

#Interfaces
my %FuncDescr;
my %ClassFunc;
my %ClassVirtFunc;
my %ClassIdVirtFunc;
my %ClassId;
my %tr_name;
my %mangled_name;
my %InternalInterfaces;
my %InterfacesList;
my %InterfacesList_App;
my %CheckedInterfaces;
my %DepInterfaces;

#Headers
my %Include_Preamble;
my %Headers;
my %HeaderName_Destinations;
my %Header_Dependency;

#Shared objects
my %SoLib_DefaultPath;

#Merging
my %CompleteSignature;
my @RecurTypes;
my %Interface_Library;
my %Library_Interface;
my %Language;
my %SoNames_All;
my $Version;

#Symbols versioning
my %SymVer;

#Problem descriptions
my %CompatProblems;
my %ConstantProblems;

#Rerorts
my $ContentID = 1;
my $ContentSpanStart = "<span class=\"section\" onclick=\"javascript:showContent(this, 'CONTENT_ID')\">\n";
my $ContentSpanEnd = "</span>\n";
my $ContentDivStart = "<div id=\"CONTENT_ID\" style=\"display:none;\">\n";
my $ContentDivEnd = "</div>\n";
my $Content_Counter = 0;

sub readDescriptor($)
{
my $LibVersion = $_[0];
if(not -e $Descriptor{$LibVersion}{"Path"})
{
return;
}
my $Descriptor_File = readFile($Descriptor{$LibVersion}{"Path"});
$Descriptor_File =~ s/\/\*(.|\n)+?\*\///g;
$Descriptor_File =~ s/<\!--(.|\n)+?-->//g;
if(not $Descriptor_File)
{
print "ERROR: descriptor d$LibVersion is empty\n";
exit(1);
}
$Descriptor{$LibVersion}{"Version"} = parseTag(\$Descriptor_File, "version");
if(not $Descriptor{$LibVersion}{"Version"})
{
print "ERROR: version in the descriptor d$LibVersion was not specified (section <version>)\n\n";
exit(1);
}
$Descriptor{$LibVersion}{"Headers"} = parseTag(\$Descriptor_File, "headers");
if(not $Descriptor{$LibVersion}{"Headers"})
{
print "ERROR: header files in the descriptor d$LibVersion were not specified (section <headers>)\n";
exit(1);
}
if(not $CheckHeadersOnly)
{
$Descriptor{$LibVersion}{"Libs"} = parseTag(\$Descriptor_File, "libs");
if(not $Descriptor{$LibVersion}{"Libs"})
{
print "ERROR: shared objects in the descriptor d$LibVersion were not specified (section <libs>)\n";
exit(1);
}
}
$Descriptor{$LibVersion}{"Include_Paths"} = parseTag(\$Descriptor_File, "include_paths");
$Descriptor{$LibVersion}{"Gcc_Options"} = parseTag(\$Descriptor_File, "gcc_options");
foreach my $Option (split("\n", $Descriptor{$LibVersion}{"Gcc_Options"}))
{
$Option =~ s/\A\s+|\s+\Z//g;
next if(not $Option);
$CompilerOptions{$LibVersion} .= " ".$Option;
}
$Descriptor{$LibVersion}{"Opaque_Types"} = parseTag(\$Descriptor_File, "opaque_types");
foreach my $Type_Name (split("\n", $Descriptor{$LibVersion}{"Opaque_Types"}))
{
$Type_Name =~ s/\A\s+|\s+\Z//g;
next if(not $Type_Name);
$OpaqueTypes{$LibVersion}{$Type_Name} = 1;
}
$Descriptor{$LibVersion}{"Skip_interfaces"} = parseTag(\$Descriptor_File, "skip_interfaces");
foreach my $Interface_Name (split("\n", $Descriptor{$LibVersion}{"Skip_interfaces"}))
{
$Interface_Name =~ s/\A\s+|\s+\Z//g;
next if(not $Interface_Name);
$InternalInterfaces{$LibVersion}{$Interface_Name} = 1;
}
$Descriptor{$LibVersion}{"Include_Preamble"} = parseTag(\$Descriptor_File, "include_preamble");
my $Position = 0;
foreach my $Header_Name (split("\n", $Descriptor{$LibVersion}{"Include_Preamble"}))
{
$Header_Name =~ s/\A\s+|\s+\Z//g;
next if(not $Header_Name);
$Include_Preamble{$LibVersion}{$Header_Name}{"Position"} = $Position;
$Position+=1;
}
my $Descriptors_Dir = "descriptors_storage/$TargetLibraryName";
system("mkdir", "-p", $Descriptors_Dir);
my $Descriptor_Name = $TargetLibraryName."_".$Descriptor{$LibVersion}{"Version"}.".desc";
if($Descriptor{$LibVersion}{"Path"} ne $Descriptors_Dir."/".$Descriptor_Name)
{
system("cp", "-f", $Descriptor{$LibVersion}{"Path"}, $Descriptors_Dir."/".$Descriptor_Name);
}
$ERR_PATH{$LibVersion} = "header_compile_errors/$TargetLibraryName/".$Descriptor{$LibVersion}{"Version"};
}

sub parseTag($$)
{
my ($CodeRef, $Tag) = @_;
return "" if(not $CodeRef or not ${$CodeRef} or not $Tag);
if(${$CodeRef} =~ s/\<$Tag\>((.|\n)+?)\<\/$Tag\>//)
{
my $Content = $1;
$Content=~s/(\A\s+|\s+\Z)//g;
return $Content;
}
else
{
return "";
}
}

my %check_node=(
"array_type"=>1,
"binfo"=>1,
"boolean_type"=>1,
"complex_type"=>1,
"const_decl"=>1,
"enumeral_type"=>1,
"field_decl"=>1,
"function_decl"=>1,
"function_type"=>1,
"identifier_node"=>1,
"integer_cst"=>1,
"integer_type"=>1,
"method_type"=>1,
"namespace_decl"=>1,
"parm_decl"=>1,
"pointer_type"=>1,
"real_cst"=>1,
"real_type"=>1,
"record_type"=>1,
"reference_type"=>1,
"string_cst"=>1,
"template_decl"=>1,
"template_type_parm"=>1,
"tree_list"=>1,
"tree_vec"=>1,
"type_decl"=>1,
"union_type"=>1,
"var_decl"=>1,
"void_type"=>1);

sub getInfo($)
{
  my $InfoPath = $_[0];
return if(not $InfoPath or not -f $InfoPath);
my $InfoPath_New = $InfoPath.".1";
#my $Keywords = join("\\|", keys(%check_node));#|grep "$Keywords"
system("sed ':a;N;\$!ba;s/\\n[^\@]//g' ".esc($InfoPath)."|sed 's/ [ ]\\+/ /g' > ".esc($InfoPath_New));
system("rm", "-fr", $InfoPath);
#getting info
open(INFO, $InfoPath_New) || die ("can't open file '\$InfoPath_New\': $!\n");
while(<INFO>)
{
chomp;
if(/\A@([0-9]+)[ ]+([a-zA-Z_]+)[ ]+(.*)\Z/)
{
next if(not $check_node{$2});
$LibInfo{$Version}{$1}{"info_type"}=$2;
$LibInfo{$Version}{$1}{"info"}=$3;
}
}
close(INFO);
system("rm", "-fr", $InfoPath_New);
#processing info
  setTemplateParams_All();
  getTypeDescr_All();
  getFuncDescr_All();
  getVarDescr_All();
%LibInfo = ();
%TemplateInstance = ();
}

sub setTemplateParams_All()
{
foreach (keys(%{$LibInfo{$Version}}))
{
if($LibInfo{$Version}{$_}{"info_type"} eq "template_decl")
{
setTemplateParams($_);
}
}
}

sub setTemplateParams($)
{
my $TypeInfoId = $_[0];
my $Info = $LibInfo{$Version}{$TypeInfoId}{"info"};
if($Info =~ /(inst|spcs)[ ]*:[ ]*@([0-9]+) /)
{
my $TmplInst_InfoId = $2;
setTemplateInstParams($TmplInst_InfoId);
my $TmplInst_Info = $LibInfo{$Version}{$TmplInst_InfoId}{"info"};
while($TmplInst_Info =~ /chan[ ]*:[ ]*@([0-9]+) /)
{
$TmplInst_InfoId = $1;
$TmplInst_Info = $LibInfo{$Version}{$TmplInst_InfoId}{"info"};
setTemplateInstParams($TmplInst_InfoId);
}
}
}

sub setTemplateInstParams($)
{
my $TmplInst_Id = $_[0];
my $Info = $LibInfo{$Version}{$TmplInst_Id}{"info"};
my ($Params_InfoId, $ElemId) = ();
if($Info =~ /purp[ ]*:[ ]*@([0-9]+) /)
{
$Params_InfoId = $1;
}
if($Info =~ /valu[ ]*:[ ]*@([0-9]+) /)
{
$ElemId = $1;
}
if($Params_InfoId and $ElemId)
{
my $Params_Info = $LibInfo{$Version}{$Params_InfoId}{"info"};
while($Params_Info =~ s/ ([0-9]+)[ ]*:[ ]*@([0-9]+) //)
{
my ($Param_Pos, $Param_TypeId) = ($1, $2);
return if($LibInfo{$Version}{$Param_TypeId}{"info_type"} eq "template_type_parm");
if($LibInfo{$ElemId}{"info_type"} eq "function_decl")
{
$TemplateInstance_Func{$Version}{$ElemId}{$Param_Pos} = $Param_TypeId;
}
else
{
$TemplateInstance{$Version}{getTypeDeclId($ElemId)}{$ElemId}{$Param_Pos} = $Param_TypeId;
}
}
}
}

sub getTypeDeclId($)
{
  my $TypeInfo = $LibInfo{$Version}{$_[0]}{"info"};
  if($TypeInfo =~ /name[ ]*:[ ]*@([0-9]+)/)
{
return $1;
}
else
{
return "";
}
}

sub isFuncPtr($)
{
my $Ptd = pointTo($_[0]);
  if($Ptd)
  {
    if(($LibInfo{$Version}{$_[0]}{"info"} =~ m/unql[ ]*:/) and not ($LibInfo{$Version}{$_[0]}{"info"} =~ m/qual[ ]*:/))
    {
      return 0;
    }
    elsif(($LibInfo{$Version}{$_[0]}{"info_type"} eq "pointer_type") and ($LibInfo{$Version}{$Ptd}{"info_type"} eq "function_type" or $LibInfo{$Version}{$Ptd}{"info_type"} eq "method_type"))
    {
      return 1;
    }
    else
    {
      return 0;
    }
  }
  else
  {
    return 0;
  }
}

sub pointTo($)
{
  my $TypeInfo = $LibInfo{$Version}{$_[0]}{"info"};
  if($TypeInfo =~ /ptd[ ]*:[ ]*@([0-9]+)/)
{
   return $1;
}
else
{
return "";
}
}

sub getTypeDescr_All()
{
foreach (sort {int($a)<=>int($b)} keys(%{$LibInfo{$Version}}))
{
if($LibInfo{$Version}{$_}{"info_type"}=~/_type\Z/ and $LibInfo{$Version}{$_}{"info_type"}!~/function_type|method_type/)
{
getTypeDescr(getTypeDeclId($_), $_);
}
}
$TypeDescr{$Version}{""}{-1}{"Name"} = "...";
$TypeDescr{$Version}{""}{-1}{"Type"} = "Intrinsic";
$TypeDescr{$Version}{""}{-1}{"Tid"} = -1;
}

sub getTypeDescr($$)
{
my ($TypeDeclId, $TypeId) = @_;
$Tid_TDid{$Version}{$TypeId} = $TypeDeclId;
%{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}} = getTypeAttr($TypeDeclId, $TypeId);
if(not $TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"})
{
delete($TypeDescr{$Version}{$TypeDeclId}{$TypeId});
return;
}
if(not $TName_Tid{$Version}{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"}})
{
$TName_Tid{$Version}{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"}} = $TypeId;
}
}

sub getTypeAttr($$)
{
my ($TypeDeclId, $TypeId) = @_;
my ($BaseTypeSpec, %TypeAttr) = ();
if($TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"})
{
return %{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}};
}
$TypeAttr{"Tid"} = $TypeId;
$TypeAttr{"TDid"} = $TypeDeclId;
$TypeAttr{"Type"} = getTypeType($TypeDeclId, $TypeId);
if($TypeAttr{"Type"} eq "Unknown")
{
return ();
}
elsif($TypeAttr{"Type"} eq "FuncPtr")
{
%{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}} = getFuncPtrAttr(pointTo($TypeId), $TypeDeclId, $TypeId);
$TName_Tid{$Version}{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"}} = $TypeId;
return %{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}};
}
elsif($TypeAttr{"Type"} eq "Array")
{
($TypeAttr{"BaseType"}{"Tid"}, $TypeAttr{"BaseType"}{"TDid"}, $BaseTypeSpec) = selectBaseType($TypeDeclId, $TypeId);
my %BaseTypeAttr = getTypeAttr($TypeAttr{"BaseType"}{"TDid"}, $TypeAttr{"BaseType"}{"Tid"});
my $ArrayElemNum = getSize($TypeId)/8;
$ArrayElemNum = $ArrayElemNum/$BaseTypeAttr{"Size"} if($BaseTypeAttr{"Size"});
$TypeAttr{"Size"} = $ArrayElemNum;
if($ArrayElemNum)
{
$TypeAttr{"Name"} = $BaseTypeAttr{"Name"}."[".$ArrayElemNum."]";
}
else
{
$TypeAttr{"Name"} = $BaseTypeAttr{"Name"}."[]";
}
$TypeAttr{"Name"} = correctName($TypeAttr{"Name"});
$TypeAttr{"Library"} = $BaseTypeAttr{"Library"};
$TypeAttr{"Header"} = $BaseTypeAttr{"Header"};
%{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}} = %TypeAttr;
$TName_Tid{$Version}{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"}} = $TypeId;
return %TypeAttr;
}
elsif($TypeAttr{"Type"} =~ /Intrinsic|Union|Struct|Enum|Class/)
{
if($TemplateInstance{$Version}{$TypeDeclId}{$TypeId})
{
my @Template_Params = ();
foreach my $Param_Pos (sort {int($a)<=>int($b)} keys(%{$TemplateInstance{$Version}{$TypeDeclId}{$TypeId}}))
{
my $Type_Id = $TemplateInstance{$Version}{$TypeDeclId}{$TypeId}{$Param_Pos};
my $Param = get_TemplateParam($Type_Id);
if($Param eq "")
{
return ();
}
@Template_Params = (@Template_Params, $Param);
}
%{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}} = getTrivialTypeAttr($TypeDeclId, $TypeId);
$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"} = $TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"}."< ".join(", ", @Template_Params)." >";
$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"} = correctName($TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"});
$TName_Tid{$Version}{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"}} = $TypeId;
return %{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}};
}
else
{
%{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}} = getTrivialTypeAttr($TypeDeclId, $TypeId);
return %{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}};
}
}
else
{
($TypeAttr{"BaseType"}{"Tid"}, $TypeAttr{"BaseType"}{"TDid"}, $BaseTypeSpec) = selectBaseType($TypeDeclId, $TypeId);
my %BaseTypeAttr = getTypeAttr($TypeAttr{"BaseType"}{"TDid"}, $TypeAttr{"BaseType"}{"Tid"});
if($BaseTypeSpec and $BaseTypeAttr{"Name"})
{
if(($TypeAttr{"Type"} eq "Pointer") and $BaseTypeAttr{"Name"}=~/\([\*]+\)/)
{
$TypeAttr{"Name"} = $BaseTypeAttr{"Name"};
$TypeAttr{"Name"} =~ s/\(([*]+)\)/($1*)/g;
}
else
{
$TypeAttr{"Name"} = $BaseTypeAttr{"Name"}." ".$BaseTypeSpec;
}
}
elsif($BaseTypeAttr{"Name"})
{
$TypeAttr{"Name"} = $BaseTypeAttr{"Name"};
}
if($TypeAttr{"Type"} eq "Typedef")
{
$TypeAttr{"Name"} = getNameByInfo($TypeDeclId);
$TypeAttr{"NameSpace"} = getNameSpace($TypeDeclId);
if($TypeAttr{"NameSpace"})
{
$TypeAttr{"Name"} = $TypeAttr{"NameSpace"}."::".$TypeAttr{"Name"};
}
($TypeAttr{"Header"}, $TypeAttr{"Line"}) = getLocation($TypeDeclId);
if($TypeAttr{"NameSpace"}=~/\Astd(::|\Z)/ and $BaseTypeAttr{"NameSpace"}=~/\Astd(::|\Z)/)
{
$StdCxxTypedef{$Version}{$BaseTypeAttr{"Name"}} = $TypeAttr{"Name"};
}
$Typedef_BaseName{$Version}{$TypeAttr{"Name"}} = $BaseTypeAttr{"Name"};
}
if(not $TypeAttr{"Size"})
{
if($TypeAttr{"Type"} eq "Pointer")
{
$TypeAttr{"Size"} = $POINTER_SIZE;
}
else
{
$TypeAttr{"Size"} = $BaseTypeAttr{"Size"};
}
}
$TypeAttr{"Name"} = correctName($TypeAttr{"Name"});
$TypeAttr{"Library"} = $BaseTypeAttr{"Library"};
$TypeAttr{"Header"} = $BaseTypeAttr{"Header"} if(not $TypeAttr{"Header"});
%{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}} = %TypeAttr;
$TName_Tid{$Version}{$TypeDescr{$Version}{$TypeDeclId}{$TypeId}{"Name"}} = $TypeId;
return %TypeAttr;
}
}

sub get_TemplateParam($)
{
my $Type_Id = $_[0];
if(getNodeType($Type_Id) eq "integer_cst")
{
return getNodeIntCst($Type_Id);
}
elsif(getNodeType($Type_Id) eq "string_cst")
{
return getNodeStrCst($Type_Id);
}
else
{
my $Type_DId = getTypeDeclId($Type_Id);
my %ParamAttr = getTypeAttr($Type_DId, $Type_Id);
if(not $ParamAttr{"Name"})
{
return "";
}
if($ParamAttr{"Name"}=~/\>/)
{
if($StdCxxTypedef{$Version}{$ParamAttr{"Name"}})
{
return $StdCxxTypedef{$Version}{$ParamAttr{"Name"}};
}
elsif(my $Covered = cover_stdcxx_typedef($ParamAttr{"Name"}))
{
return $Covered;
}
else
{
return $ParamAttr{"Name"};
}
}
else
{
return $ParamAttr{"Name"};
}
}
}

sub cover_stdcxx_typedef($)
{
my $TypeName = $_[0];
my $TypeName_Covered = $TypeName;
while($TypeName=~s/>[ ]*(const|volatile|restrict| |\*|\&)\Z/>/g){};
if(my $Cover = $StdCxxTypedef{$Version}{$TypeName})
{
$TypeName = esc_l($TypeName);
$TypeName_Covered=~s/$TypeName/$Cover /g;
}
return correctName($TypeName_Covered);
}

sub getNodeType($)
{
return $LibInfo{$Version}{$_[0]}{"info_type"};
}

sub getNodeIntCst($)
{
my $CstId = $_[0];
my $CstTypeId = getTreeAttr($CstId, "type");
if($EnumMembName_Id{$Version}{$CstId})
{
return $EnumMembName_Id{$Version}{$CstId};
}
elsif($LibInfo{$Version}{$_[0]}{"info"} =~ /low[ ]*:[ ]*([^ ]+) /)
{
if($1 eq "0")
{
if(getNodeType($CstTypeId) eq "boolean_type")
{
return "false";
}
else
{
return "0";
}
}
elsif($1 eq "1")
{
if(getNodeType($CstTypeId) eq "boolean_type")
{
return "true";
}
else
{
return "1";
}
}
else
{
return $1;
}
}
else
{
return "";
}
}

sub getNodeStrCst($)
{
if($LibInfo{$Version}{$_[0]}{"info"} =~ /low[ ]*:[ ]*(.+)[ ]+lngt/)
{
return $1;
}
else
{
return "";
}
}

sub esc_l($)
{
my $String = $_[0];
$String=~s/([()*])/\\$1/g;
return $String;
}

sub getFuncPtrAttr($$$)
{
my ($FuncTypeId, $TypeDeclId, $TypeId) = @_;
my $FuncInfo = $LibInfo{$Version}{$FuncTypeId}{"info"};
my $FuncInfo_Type = $LibInfo{$Version}{$FuncTypeId}{"info_type"};
my $FuncPtrCorrectName = "";
my %TypeAttr = ("Size"=>$POINTER_SIZE, "Type"=>"FuncPtr", "TDid"=>$TypeDeclId, "Tid"=>$TypeId);
my @ParamTypeName;
if($FuncInfo =~ /retn[ ]*:[ ]*\@([0-9]+) /)
{
my $ReturnTypeId = $1;
my %ReturnAttr = getTypeAttr(getTypeDeclId($ReturnTypeId), $ReturnTypeId);
$FuncPtrCorrectName .= $ReturnAttr{"Name"};
$TypeAttr{"Return"} = $ReturnTypeId;
}
if($FuncInfo =~ /prms[ ]*:[ ]*@([0-9]+) /)
{
my $ParamTypeInfoId = $1;
my $Position = 0;
while($ParamTypeInfoId)
{
my $ParamTypeInfo = $LibInfo{$Version}{$ParamTypeInfoId}{"info"};
last if($ParamTypeInfo !~ /valu[ ]*:[ ]*@([0-9]+) /);
my $ParamTypeId = $1;
my %ParamAttr = getTypeAttr(getTypeDeclId($ParamTypeId), $ParamTypeId);
last if($ParamAttr{"Name"} eq "void");
$TypeAttr{"Memb"}{$Position}{"type"} = $ParamTypeId;
push(@ParamTypeName, $ParamAttr{"Name"});
last if($ParamTypeInfo !~ /chan[ ]*:[ ]*@([0-9]+) /);
$ParamTypeInfoId = $1;
$Position+=1;
}
}
if($FuncInfo_Type eq "function_type")
{
$FuncPtrCorrectName .= " (*) (".join(", ", @ParamTypeName).")";
}
elsif($FuncInfo_Type eq "method_type")
{
if($FuncInfo =~ /clas[ ]*:[ ]*@([0-9]+) /)
{
my $ClassId = $1;
my $ClassName = $TypeDescr{$Version}{getTypeDeclId($ClassId)}{$ClassId}{"Name"};
if($ClassName)
{
$FuncPtrCorrectName .= " ($ClassName\:\:*) (".join(", ", @ParamTypeName).")";
}
else
{
$FuncPtrCorrectName .= " (*) (".join(", ", @ParamTypeName).")";
}
}
else
{
$FuncPtrCorrectName .= " (*) (".join(", ", @ParamTypeName).")";
}
}
$TypeAttr{"Name"} = correctName($FuncPtrCorrectName);
return %TypeAttr;
}

sub getTypeName($)
{
  my $Info = $LibInfo{$Version}{$_[0]}{"info"};
  if($Info =~ /name[ ]*:[ ]*@([0-9]+) /)
  {
    return getNameByInfo($1);
  }
  else
  {
    if($LibInfo{$Version}{$_[0]}{"info_type"} eq "integer_type")
    {
      if($LibInfo{$Version}{$_[0]}{"info"} =~ /unsigned/)
      {
        return "unsigned int";
      }
      else
      {
        return "int";
      }
    }
    else
    {
      return "";
    }
  }
}

sub selectBaseType($$)
{
  my ($TypeDeclId, $TypeId) = @_;
  my $TypeInfo = $LibInfo{$Version}{$TypeId}{"info"};
  my $BaseTypeDeclId;
my $Type_Type = getTypeType($TypeDeclId, $TypeId);
  #qualifications
  if(($LibInfo{$Version}{$TypeId}{"info"} =~ /qual[ ]*:[ ]*c /) and ($LibInfo{$Version}{$TypeId}{"info"} =~ /unql[ ]*:[ ]*\@([0-9]+) /))
  {
    return ($1, getTypeDeclId($1), "const");
  }
  elsif(($LibInfo{$Version}{$TypeId}{"info"} =~ /qual[ ]*:[ ]*r /) and ($LibInfo{$Version}{$TypeId}{"info"} =~ /unql[ ]*:[ ]*\@([0-9]+) /))
  {
    return ($1, getTypeDeclId($1), "restrict");
  }
  elsif(($LibInfo{$Version}{$TypeId}{"info"} =~ /qual[ ]*:[ ]*v /) and ($LibInfo{$Version}{$TypeId}{"info"} =~ /unql[ ]*:[ ]*\@([0-9]+) /))
  {
    return ($1, getTypeDeclId($1), "volatile");
  }
  elsif((not ($LibInfo{$Version}{$TypeId}{"info"} =~ /qual[ ]*:/)) and ($LibInfo{$Version}{$TypeId}{"info"} =~ /unql[ ]*:[ ]*\@([0-9]+) /))
  {#typedefs
    return ($1, getTypeDeclId($1), "");
  }
  elsif($LibInfo{$Version}{$TypeId}{"info_type"} eq "reference_type")
  {
    if($TypeInfo =~ /refd[ ]*:[ ]*@([0-9]+) /)
{
     return ($1, getTypeDeclId($1), "&");
}
else
{
return (0, 0, "");
}
  }
  elsif($LibInfo{$Version}{$TypeId}{"info_type"} eq "array_type")
  {
    if($TypeInfo =~ /elts[ ]*:[ ]*@([0-9]+) /)
{
     return ($1, getTypeDeclId($1), "");
}
else
{
return (0, 0, "");
}
  }
  elsif($LibInfo{$Version}{$TypeId}{"info_type"} eq "pointer_type")
  {
    if($TypeInfo =~ /ptd[ ]*:[ ]*@([0-9]+) /)
{
     return ($1, getTypeDeclId($1), "*");
}
else
{
return (0, 0, "");
}
  }
  else
  {
    return (0, 0, "");
  }
}

sub getFuncDescr_All()
{
  foreach (sort {int($b)<=>int($a)} keys(%{$LibInfo{$Version}}))
  {
    if($LibInfo{$Version}{$_}{"info_type"} eq "function_decl")
    {
      getFuncDescr($_);
    }
  }
}

sub getVarDescr_All()
{
  foreach (sort {int($b)<=>int($a)} keys(%{$LibInfo{$Version}}))
  {
    if($LibInfo{$Version}{$_}{"info_type"} eq "var_decl")
    {
      getVarDescr($_);
    }
  }
}

sub getVarDescr($)
{
  my $FuncInfoId = $_[0];
if($LibInfo{$Version}{getNameSpaceId($FuncInfoId)}{"info_type"} eq "function_decl")
{
return;
}
($FuncDescr{$Version}{$FuncInfoId}{"Header"}, $FuncDescr{$Version}{$FuncInfoId}{"Line"}) = getLocation($FuncInfoId);
if((not $FuncDescr{$Version}{$FuncInfoId}{"Header"}) or ($FuncDescr{$Version}{$FuncInfoId}{"Header"}=~/\<built\-in\>|\<internal\>/))
{
delete($FuncDescr{$Version}{$FuncInfoId});
return;
}
$FuncDescr{$Version}{$FuncInfoId}{"ShortName"} = getNameByInfo($FuncInfoId);
$FuncDescr{$Version}{$FuncInfoId}{"MnglName"} = getFuncMnglName($FuncInfoId);
if($FuncDescr{$Version}{$FuncInfoId}{"MnglName"} and $FuncDescr{$Version}{$FuncInfoId}{"MnglName"}!~/\A_Z/)
{
delete($FuncDescr{$Version}{$FuncInfoId});
return;
}
if(not $FuncDescr{$Version}{$FuncInfoId}{"MnglName"})
{
$FuncDescr{$Version}{$FuncInfoId}{"Name"} = $FuncDescr{$Version}{$FuncInfoId}{"ShortName"};
$FuncDescr{$Version}{$FuncInfoId}{"MnglName"} = $FuncDescr{$Version}{$FuncInfoId}{"ShortName"};
}
if(not is_in_library($FuncDescr{$Version}{$FuncInfoId}{"MnglName"}, $Version) and not $CheckHeadersOnly)
{
delete $FuncDescr{$Version}{$FuncInfoId};
return;
}
  $FuncDescr{$Version}{$FuncInfoId}{"Return"} = getTypeId($FuncInfoId);
delete($FuncDescr{$Version}{$FuncInfoId}{"Return"}) if(not $FuncDescr{$Version}{$FuncInfoId}{"Return"});
  $FuncDescr{$Version}{$FuncInfoId}{"Data"} = 1;
  set_Class_And_Namespace($FuncInfoId);
  setFuncAccess($FuncInfoId);
  if($FuncDescr{$Version}{$FuncInfoId}{"MnglName"} =~ /\A_ZTV/)
{
delete($FuncDescr{$Version}{$FuncInfoId}{"Return"});
}
if($FuncDescr{$Version}{$FuncInfoId}{"ShortName"} =~ /\A_Z/)
{
delete($FuncDescr{$Version}{$FuncInfoId}{"ShortName"});
}
}

sub getTrivialTypeAttr($$)
{
  my ($TypeInfoId, $TypeId) = @_;
my %TypeAttr = ();
return if(getTypeTypeByTypeId($TypeId)!~/Intrinsic|Union|Struct|Enum/);
  setTypeAccess($TypeId, \%TypeAttr);
  ($TypeAttr{"Header"}, $TypeAttr{"Line"}) = getLocation($TypeInfoId);
  if(($TypeAttr{"Header"} eq "<built-in>") or ($TypeAttr{"Header"} eq "<internal>"))
  {
delete($TypeAttr{"Header"});
  }
$TypeAttr{"Name"} = getNameByInfo($TypeInfoId);
$TypeAttr{"Name"} = getTypeName($TypeId) if(not $TypeAttr{"Name"});
my $NameSpaceId = getNameSpaceId($TypeInfoId);
if($NameSpaceId ne $TypeId)
{
$TypeAttr{"NameSpace"} = getNameSpace($TypeInfoId);
}
if($TypeAttr{"NameSpace"} and isNotAnon($TypeAttr{"Name"}))
{
$TypeAttr{"Name"} = $TypeAttr{"NameSpace"}."::".$TypeAttr{"Name"};
}
$TypeAttr{"Name"} = correctName($TypeAttr{"Name"});
  if(isAnon($TypeAttr{"Name"}))
  {
    $TypeAttr{"Name"} = "anon-";
    $TypeAttr{"Name"} .= $TypeAttr{"Header"}."-".$TypeAttr{"Line"};
  }
  $TypeAttr{"Size"} = getSize($TypeId)/8;
  $TypeAttr{"Type"} = getTypeType($TypeInfoId, $TypeId);
if($TypeAttr{"Type"} eq "Struct" and has_methods($TypeId))
{
$TypeAttr{"Type"} = "Class";
}
if(($TypeAttr{"Type"} eq "Struct") or ($TypeAttr{"Type"} eq "Class"))
{
setBaseClasses($TypeInfoId, $TypeId, \%TypeAttr);
}
  setTypeMemb($TypeInfoId, $TypeId, \%TypeAttr);
$TypeAttr{"Tid"} = $TypeId;
$TypeAttr{"TDid"} = $TypeInfoId;
$Tid_TDid{$Version}{$TypeId} = $TypeInfoId;
if(not $TName_Tid{$Version}{$TypeAttr{"Name"}})
{
$TName_Tid{$Version}{$TypeAttr{"Name"}} = $TypeId;
}
return %TypeAttr;
}

sub has_methods($)
{
my $TypeId = $_[0];
my $Info = $LibInfo{$Version}{$TypeId}{"info"};
return ($Info=~/(fncs)[ ]*:[ ]*@([0-9]+) /);
}

sub setBaseClasses($$$)
{
my ($TypeInfoId, $TypeId, $TypeAttr) = @_;
my $Info = $LibInfo{$Version}{$TypeId}{"info"};
if($Info =~ /binf[ ]*:[ ]*@([0-9]+) /)
{
$Info = $LibInfo{$Version}{$1}{"info"};
while($Info =~ /accs[ ]*:[ ]*([a-z]+) /)
{
last if($Info !~ s/accs[ ]*:[ ]*([a-z]+) //);
my $Access = $1;
last if($Info !~ s/binf[ ]*:[ ]*@([0-9]+) //);
my $BInfoId = $1;
my $ClassId = getBinfClassId($BInfoId);
if($Access eq "pub")
{
$TypeAttr->{"BaseClass"}{$ClassId} = "public";
}
elsif($Access eq "prot")
{
$TypeAttr->{"BaseClass"}{$ClassId} = "protected";
}
elsif($Access eq "priv")
{
$TypeAttr->{"BaseClass"}{$ClassId} = "private";
}
else
{
$TypeAttr->{"BaseClass"}{$ClassId} = "private";
}
}
}
}

sub getBinfClassId($)
{
my $Info = $LibInfo{$Version}{$_[0]}{"info"};
$Info =~ /type[ ]*:[ ]*@([0-9]+) /;
return $1;
}

sub get_func_signature($)
{
my $FuncInfoId = $_[0];
my $PureSignature = $FuncDescr{$Version}{$FuncInfoId}{"ShortName"};
my @ParamTypes = ();
foreach my $ParamPos (sort {int($a) <=> int($b)} keys(%{$FuncDescr{$Version}{$FuncInfoId}{"Param"}}))
{#checking parameters
my $ParamType_Id = $FuncDescr{$Version}{$FuncInfoId}{"Param"}{$ParamPos}{"type"};
my $ParamType_Name = uncover_typedefs($TypeDescr{$Version}{getTypeDeclId($ParamType_Id)}{$ParamType_Id}{"Name"});
@ParamTypes = (@ParamTypes, $ParamType_Name);
}
$PureSignature = $PureSignature."(".join(", ", @ParamTypes).")";
$PureSignature = delete_keywords($PureSignature);
return correctName($PureSignature);
}

sub delete_keywords($)
{
my $TypeName = $_[0];
$TypeName =~ s/(\W|\A)(enum |struct |union |class )/$1/g;
return $TypeName;
}

sub uncover_typedefs($)
{
my $TypeName = $_[0];
return "" if(not $TypeName);
return $Cache{"uncover_typedefs"}{$Version}{$TypeName} if(defined $Cache{"uncover_typedefs"}{$Version}{$TypeName});
my ($TypeName_New, $TypeName_Pre) = (correctName($TypeName), "");
while($TypeName_New ne $TypeName_Pre)
{
$TypeName_Pre = $TypeName_New;
my $TypeName_Copy = $TypeName_New;
my %Words = ();
while($TypeName_Copy=~s/(\W|\A)([a-z_][\w:]*)(\W|\Z)//io)
{
my $Word = $2;
next if(not $Word or $Word=~/\A(true|false|const|int|long|void|short|float|unsigned|char|double|class|struct|union|enum)\Z/);
$Words{$Word} = 1;
}
foreach my $Word (keys(%Words))
{
my $BaseType_Name = $Typedef_BaseName{$Version}{$Word};
next if($TypeName_New=~/(\W|\A)(struct $Word|union $Word|enum $Word)(\W|\Z)/);
next if(not $BaseType_Name);
if($BaseType_Name=~/\([*]+\)/)
{
$TypeName_New =~ /$Word(.*)\Z/;
my $Type_Suffix = $1;
$TypeName_New = $BaseType_Name;
if($TypeName_New =~ s/\(([*]+)\)/($1 $Type_Suffix)/)
{
$TypeName_New = correctName($TypeName_New);
}
}
else
{
if($TypeName_New =~ s/(\W|\A)$Word(\W|\Z)/$1$BaseType_Name$2/g)
{
$TypeName_New = correctName($TypeName_New);
}
}
}
}
$Cache{"uncover_typedefs"}{$Version}{$TypeName} = $TypeName_New;
return $TypeName_New;
}

