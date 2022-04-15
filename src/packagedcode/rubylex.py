"""
Minimal lexer for Ruby.
Derived from pygments.lexers.ruby and significantly modified
copyright: Copyright 2006-2022 by the Pygments team, see pygments.AUTHORS.
SPDX-License-Identifier: BSD-2-Clause
"""

import re

from pygments.lexer import ExtendedRegexLexer, include, \
    bygroups, default, LexerContext, words
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Error


line_re = re.compile('.*?\n')


RUBY_OPERATORS = (
    '*', '**', '-', '+', '-@', '+@', '/', '%', '&', '|', '^', '`', '~',
    '[]', '[]=', '<<', '>>', '<', '<>', '<=>', '>', '>=', '==', '==='
)


class RubyLexer(ExtendedRegexLexer):
    """
    For Ruby source code.
    """

    name = 'Ruby'
    url = 'http://www.ruby-lang.org'
    aliases = ['ruby', 'rb', 'duby']
    filenames = ['*.rb', '*.rbw', 'Rakefile', '*.rake', '*.gemspec',
                 '*.rbx', '*.duby', 'Gemfile', 'Vagrantfile']
    mimetypes = ['text/x-ruby', 'application/x-ruby']

    flags = re.DOTALL | re.MULTILINE

    def heredoc_callback(self, match, ctx):
        # okay, this is the hardest part of parsing Ruby...
        # match: 1 = <<[-~]?, 2 = quote? 3 = name 4 = quote? 5 = rest of line

        start = match.start(1)
        yield start, Operator, match.group(1)        # <<[-~]?
        yield match.start(2), String.Heredoc, match.group(2)   # quote ", ', `
        yield match.start(3), String.Delimiter, match.group(3) # heredoc name
        yield match.start(4), String.Heredoc, match.group(4)   # quote again

        heredocstack = ctx.__dict__.setdefault('heredocstack', [])
        outermost = not bool(heredocstack)
        heredocstack.append((match.group(1) in ('<<-', '<<~'), match.group(3)))

        ctx.pos = match.start(5)
        ctx.end = match.end(5)
        # this may find other heredocs, so limit the recursion depth
        if len(heredocstack) < 100:
            yield from self.get_tokens_unprocessed(context=ctx)
        else:
            yield ctx.pos, String.Heredoc, match.group(5)
        ctx.pos = match.end()

        if outermost:
            # this is the outer heredoc again, now we can process them all
            for tolerant, hdname in heredocstack:
                lines = []
                for match in line_re.finditer(ctx.text, ctx.pos):
                    if tolerant:
                        check = match.group().strip()
                    else:
                        check = match.group().rstrip()
                    if check == hdname:
                        for amatch in lines:
                            yield amatch.start(), String.Heredoc, amatch.group()
                        yield match.start(), String.Delimiter, match.group()
                        ctx.pos = match.end()
                        break
                    else:
                        lines.append(match)
                else:
                    # end of heredoc not found -- error!
                    for amatch in lines:
                        yield amatch.start(), Error, amatch.group()
            ctx.end = len(ctx.text)
            del heredocstack[:]

    def gen_rubystrings_rules():
        def intp_regex_callback(self, match, ctx):
            yield match.start(1), String.Regex, match.group(1)  # begin
            nctx = LexerContext(match.group(3), 0, ['interpolated-regex'])
            for i, t, v in self.get_tokens_unprocessed(context=nctx):
                yield match.start(3)+i, t, v
            yield match.start(4), String.Regex, match.group(4)  # end[mixounse]*
            ctx.pos = match.end()

        def intp_string_callback(self, match, ctx):
            yield match.start(1), String.Other, match.group(1)
            nctx = LexerContext(match.group(3), 0, ['interpolated-string'])
            for i, t, v in self.get_tokens_unprocessed(context=nctx):
                yield match.start(3)+i, t, v
            yield match.start(4), String.Other, match.group(4)  # end
            ctx.pos = match.end()

        states = {}
        states['strings'] = [
            # Gemfile
            # groups/scopes
            (r'\:development', String.Symbol.Development),
            (r'\:debug', String.Symbol.Debug),
            (r'\:test', String.Symbol.Test),
            (r'\:default', String.Symbol.Default),

            (r'\:source', String.Symbol.Source),
            (r'\:platform', String.Symbol.Platform),
            (r'\:platforms', String.Symbol.Platforms),

            (r'\:require', String.Symbol.Require),
            (r'\:group', String.Symbol.Group),
            (r'\:groups', String.Symbol.Groups),
            (r'\:name', String.Symbol.Name),

            (r'\:engine', String.Symbol.Engine),
            (r'\:engine_version', String.Symbol.Engine_version),
            (r'\:patchlevel', String.Symbol.Patchlevel),

            (r'\:git', String.Symbol.Git),
            
            (r'\:tag', String.Symbol.Tag),
            (r'\:branch', String.Symbol.Branch),
            (r'\:ref', String.Symbol.Ref),

            (r'\:git_source', String.Symbol.Git_source),
            (r'\:github', String.Symbol.GitHub),
            (r'\:gist', String.Symbol.Gist),
            (r'\:bitbucket', String.Symbol.Bitbucket),

            (r'\:path', String.Symbol.Path),
            

            # Podspec
            (r'\:type', String.Symbol.Type),

            (r'\:file', String.Symbol.File),
            (r'\:text', String.Symbol.Text),
            
            (r'\:commit', String.Symbol.Commit),
            (r'\:submodules', String.Symbol.Submodules),

            (r'\:hg', String.Symbol.Hg),
            (r'\:revision', String.Symbol.Revision),
            
            (r'\:svn', String.Symbol.Svn),
            (r'\:folder', String.Symbol.Folder),

            (r'\:http', String.Symbol.Http),
            (r'\:headers', String.Symbol.Headers),
            (r'\:flatten', String.Symbol.Flatten),
            (r'\:sha1', String.Symbol.Sha1),
            (r'\:sha256', String.Symbol.Sha256),

            (r'\:osx', String.Symbol.Osx),
            (r'\:ios', String.Symbol.Ios),
            (r'\:watchos', String.Symbol.Watchos),
            (r'\:tvos', String.Symbol.Tvos),
            (r'\:configurations', String.Symbol.Configurations),
            (r'\:sha256', String.Symbol.Sha256),

            # easy ones
            (r'\:@{0,2}[a-zA-Z_]\w*[!?]?', String.Symbol),
            (words(RUBY_OPERATORS, prefix=r'\:@{0,2}'), String.Symbol),
            (r":'(\\\\|\\[^\\]|[^'\\])*'", String.Symbol),
            (r':"', String.Symbol, 'simple-sym'),
            (r'([a-zA-Z_]\w*)(:)(?!:)',
             bygroups(String.Symbol, Punctuation)),  # Since Ruby 1.9
            (r'"', String.Double.Quote, 'simple-string-double'),
            (r"'", String.Single.Quote, 'simple-string-single'),
            (r'(?<!\.)`', String.Backtick.Quote, 'simple-backtick'),
        ]

        # quoted string and symbol
        for name, ttype, end in ('string-double', String.Double.Value, '"'), \
                                ('string-single', String.Single.Value, "'"),\
                                ('sym', String.Symbol, '"'), \
                                ('backtick', String.Backtick.Value, '`'):
            states['simple-'+name] = [
                include('string-intp-escaped'),
                (r'[^\\%s#]+' % end, ttype),
                (r'[\\#]', ttype),
                (end, ttype, '#pop'),
            ]

        # braced quoted strings
        for lbrace, rbrace, bracecc, name in \
                ('\\{', '\\}', '{}', 'cb'), \
                ('\\[', '\\]', '\\[\\]', 'sb'), \
                ('\\(', '\\)', '()', 'pa'), \
                ('<', '>', '<>', 'ab'):
            states[name+'-intp-string'] = [
                (r'\\[\\' + bracecc + ']', String.Other),
                (lbrace, String.Other, '#push'),
                (rbrace, String.Other, '#pop'),
                include('string-intp-escaped'),
                (r'[\\#' + bracecc + ']', String.Other),
                (r'[^\\#' + bracecc + ']+', String.Other),
            ]
            states['strings'].append((r'%[QWx]?' + lbrace, String.Other,
                                      name+'-intp-string'))
            states[name+'-string'] = [
                (r'\\[\\' + bracecc + ']', String.Other),
                (lbrace, String.Other, '#push'),
                (rbrace, String.Other, '#pop'),
                (r'[\\#' + bracecc + ']', String.Other),
                (r'[^\\#' + bracecc + ']+', String.Other),
            ]
            states['strings'].append((r'%[qsw]' + lbrace, String.Other,
                                      name+'-string'))
            states[name+'-regex'] = [
                (r'\\[\\' + bracecc + ']', String.Regex),
                (lbrace, String.Regex, '#push'),
                (rbrace + '[mixounse]*', String.Regex, '#pop'),
                include('string-intp'),
                (r'[\\#' + bracecc + ']', String.Regex),
                (r'[^\\#' + bracecc + ']+', String.Regex),
            ]
            states['strings'].append((r'%r' + lbrace, String.Regex,
                                      name+'-regex'))

        # these must come after %<brace>!
        states['strings'] += [
            # %r regex
            (r'(%r([\W_]))((?:\\\2|(?!\2).)*)(\2[mixounse]*)',
             intp_regex_callback),
            # regular fancy strings with qsw
            (r'%[qsw]([\W_])((?:\\\1|(?!\1).)*)\1', String.Other),
            (r'(%[QWx]([\W_]))((?:\\\2|(?!\2).)*)(\2)',
             intp_string_callback),
            # special forms of fancy strings after operators or
            # in method calls with braces
            (r'(?<=[-+/*%=<>&!^|~,(])(\s*)(%([\t ])(?:(?:\\\3|(?!\3).)*)\3)',
             bygroups(Text, String.Other, None)),
            # and because of fixed width lookbehinds the whole thing a
            # second time for line startings...
            (r'^(\s*)(%([\t ])(?:(?:\\\3|(?!\3).)*)\3)',
             bygroups(Text, String.Other, None)),
            # all regular fancy strings without qsw
            (r'(%([^a-zA-Z0-9\s]))((?:\\\2|(?!\2).)*)(\2)',
             intp_string_callback),
        ]

        return states

    tokens = {
        'root': [
            (r'\A#!.+?$', Comment.Hashbang),
            (r'#.*?$', Comment.Single),
            (r'=begin\s.*?\n=end.*?$', Comment.Multiline),

            # keywords
            
            # gem
            (words(('BEGIN', 'begin',), suffix=r'\b'), Keyword.Begin),
            (words(('END', 'end',), suffix=r'\b'), Keyword.End),
            (words(('do',), suffix=r'\b'), Keyword.Do),

            (words(('ruby',), suffix=r'\b'), Keyword.Ruby),
            (words(('gem',), suffix=r'\b'), Keyword.Gem),
            (words(('gemspec',), suffix=r'\b'), Keyword.Gemspec),

            (words(('require',), suffix=r'\b'), Keyword.Require),
            (words(('versions',), suffix=r'\b'), Keyword.Versions),
            (words(('source',), suffix=r'\b'), Keyword.Source),
            (words(('git',), suffix=r'\b'), Keyword.Git),
            (words(('group',), suffix=r'\b'), Keyword.Group),
            (words(('platforms',), suffix=r'\b'), Keyword.Platforms),
            (words(('path',), suffix=r'\b'), Keyword.Pth),

            # pods
            (words(('pod',), suffix=r'\b'), Keyword.Pod),
            (words(('subspec',), suffix=r'\b'), Keyword.Subspec),
            
            # keywords
            (words((
                'BEGIN', 'END', 'alias', 'begin', 'break', 'case', 'defined?',
                'do', 'else', 'elsif', 'end', 'ensure', 'for', 'if', 'in', 'next', 'redo',
                'rescue', 'raise', 'retry', 'return', 'super', 'then', 'undef',
                'unless', 'until', 'when', 'while', 'yield'), suffix=r'\b'),
             Keyword),
            # start of function, class and module names
            (r'(module)(\s+)([a-zA-Z_]\w*'
             r'(?:::[a-zA-Z_]\w*)*)',
             bygroups(Keyword, Text, Name.Namespace)),
            (r'(def)(\s+)', bygroups(Keyword, Text), 'funcname'),
            (r'def(?=[*%&^`~+-/\[<>=])', Keyword, 'funcname'),
            (r'(class)(\s+)', bygroups(Keyword, Text), 'classname'),
            # special methods
            (words((
                'initialize', 'new', 'loop', 'include', 'extend', 'raise', 'attr_reader',
                'attr_writer', 'attr_accessor', 'attr', 'catch', 'throw', 'private',
                'module_function', 'public', 'protected', 'true', 'false', 'nil'),
                suffix=r'\b'),
             Keyword.Pseudo),
            (r'(not|and|or)\b', Operator.Word.AndOrNot),
            (words((
                'autoload', 'block_given', 'const_defined', 'eql', 'equal', 'frozen', 'include',
                'instance_of', 'is_a', 'iterator', 'kind_of', 'method_defined', 'nil',
                'private_method_defined', 'protected_method_defined',
                'public_method_defined', 'respond_to', 'tainted'), suffix=r'\?'),
             Name.Builtin),
            (r'(chomp|chop|exit|gsub|sub)!', Name.Builtin),
            (words((
                'Array', 'Float', 'Integer', 'String', '__id__', '__send__', 'abort',
                'ancestors', 'at_exit', 'autoload', 'binding', 'callcc', 'caller',
                'catch', 'chomp', 'chop', 'class_eval', 'class_variables',
                'clone', 'const_defined?', 'const_get', 'const_missing', 'const_set',
                'constants', 'display', 'dup', 'eval', 'exec', 'exit', 'extend', 'fail', 'fork',
                'format', 'freeze', 'getc', 'gets', 'global_variables', 'gsub',
                'hash', 'id', 'included_modules', 'inspect', 'instance_eval',
                'instance_method', 'instance_methods',
                'instance_variable_get', 'instance_variable_set', 'instance_variables',
                'lambda', 'load', 'local_variables', 'loop',
                'method', 'method_missing', 'methods', 'module_eval', 'name',
                'object_id', 'open', 'p', 'print', 'printf', 'private_class_method',
                'private_instance_methods',
                'private_methods', 'proc', 'protected_instance_methods',
                'protected_methods', 'public_class_method',
                'public_instance_methods', 'public_methods',
                'putc', 'puts', 'raise', 'rand', 'readline', 'readlines', 'require',
                'scan', 'select', 'self', 'send', 'set_trace_func', 'singleton_methods', 'sleep',
                'split', 'sprintf', 'srand', 'sub', 'syscall', 'system', 'taint',
                'test', 'throw', 'to_a', 'to_s', 'trace_var', 'trap', 'untaint',
                'untrace_var', 'warn'), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
            (r'__(FILE|LINE)__\b', Name.Builtin.Pseudo),
            # normal heredocs
            (r'(?<!\w)(<<[-~]?)(["`\']?)([a-zA-Z_]\w*)(\2)(.*?\n)',
             heredoc_callback),
            # empty string heredocs
            (r'(<<[-~]?)("|\')()(\2)(.*?\n)', heredoc_callback),
            (r'__END__', Comment.Preproc, 'end-part'),
            # multiline regex (after keywords or assignments)
            (r'(?:^|(?<=[=<>~!:])|'
             r'(?<=(?:\s|;)when\s)|'
             r'(?<=(?:\s|;)or\s)|'
             r'(?<=(?:\s|;)and\s)|'
             r'(?<=\.index\s)|'
             r'(?<=\.scan\s)|'
             r'(?<=\.sub\s)|'
             r'(?<=\.sub!\s)|'
             r'(?<=\.gsub\s)|'
             r'(?<=\.gsub!\s)|'
             r'(?<=\.match\s)|'
             r'(?<=(?:\s|;)if\s)|'
             r'(?<=(?:\s|;)elsif\s)|'
             r'(?<=^when\s)|'
             r'(?<=^index\s)|'
             r'(?<=^scan\s)|'
             r'(?<=^sub\s)|'
             r'(?<=^gsub\s)|'
             r'(?<=^sub!\s)|'
             r'(?<=^gsub!\s)|'
             r'(?<=^match\s)|'
             r'(?<=^if\s)|'
             r'(?<=^elsif\s)'
             r')(\s*)(/)', bygroups(Text, String.Regex), 'multiline-regex'),
            # multiline regex (in method calls or subscripts)
            (r'(?<=\(|,|\[)/', String.Regex, 'multiline-regex'),
            # multiline regex (this time the funny no whitespace rule)
            (r'(\s+)(/)(?![\s=])', bygroups(Text, String.Regex),
             'multiline-regex'),
            # lex numbers and ignore following regular expressions which
            # are division operators in fact (grrrr. i hate that. any
            # better ideas?)
            # since pygments 0.7 we also eat a "?" operator after numbers
            # so that the char operator does not work. Chars are not allowed
            # there so that you can use the ternary operator.
            # stupid example:
            #   x>=0?n[x]:""
            (r'(0_?[0-7]+(?:_[0-7]+)*)(\s*)([/?])?',
             bygroups(Number.Oct, Text, Operator)),
            (r'(0x[0-9A-Fa-f]+(?:_[0-9A-Fa-f]+)*)(\s*)([/?])?',
             bygroups(Number.Hex, Text, Operator)),
            (r'(0b[01]+(?:_[01]+)*)(\s*)([/?])?',
             bygroups(Number.Bin, Text, Operator)),
            (r'([\d]+(?:_\d+)*)(\s*)([/?])?',
             bygroups(Number.Integer, Text, Operator)),
            # Names
            (r'@@[a-zA-Z_]\w*', Name.Variable.Class),
            (r'@[a-zA-Z_]\w*', Name.Variable.Instance),
            (r'\$\w+', Name.Variable.Global),
            (r'\$[!@&`\'+~=/\\,;.<>_*$?:"^-]', Name.Variable.Global),
            (r'\$-[0adFiIlpvw]', Name.Variable.Global),
            (r'::', Operator.Double_Colon),
            include('strings'),
            # chars
            (r'\?(\\[MC]-)*'  # modifiers
             r'(\\([\\abefnrstv#"\']|x[a-fA-F0-9]{1,2}|[0-7]{1,3})|\S)'
             r'(?!\w)',
             String.Char),
            (r'[A-Z]\w+', Name.Constant),
            # this is needed because ruby attributes can look
            # like keywords (class) or like this: ` ?!?
            (words(RUBY_OPERATORS, prefix=r'(::)'),
             bygroups(Operator, Name.Operator.Double_Colon)),
            (words(RUBY_OPERATORS, prefix=r'(\.)'),
             bygroups(Operator, Name.Operator.Dot)),
            (r'(::)([a-zA-Z_]\w*[!?]?|[*%&^`~+\-/\[<>=])',
             bygroups(Operator.Double_Colon, Name)),
            (r'(\.)(new)', bygroups(Operator.Dot, Name.New)),

            # required in gemspec
            (r'(\.)(name)', bygroups(Operator.Dot, Name.Name)),
            (r'(\.)(version)', bygroups(Operator.Dot, Name.Version)),
            (r'(\.)(summary)', bygroups(Operator.Dot, Name.Summary)),
            (r'(\.)(files)', bygroups(Operator.Dot, Name.Files)),

            (r'(\.)(authors)', bygroups(Operator.Dot, Name.Authors)),
            # optional form for single author
            (r'(\.)(author)', bygroups(Operator.Dot, Name.Author)),

            # recommended in gemspec
            (r'(\.)(description)', bygroups(Operator.Dot, Name.Description)),
            (r'(\.)(homepage)', bygroups(Operator.Dot, Name.Homepage)),
            (r'(\.)(email)', bygroups(Operator.Dot, Name.Email)),
            (r'(\.)(license)', bygroups(Operator.Dot, Name.License)),
            (r'(\.)(licenses)', bygroups(Operator.Dot, Name.Licenses)),
            (r'(\.)(metadata)', bygroups(Operator.Dot, Name.Metadata)),
            (r'(\.)(required_ruby_version)', bygroups(Operator.Dot, Name.Required_Ruby_Version)),

            (r'(\.)(date)', bygroups(Operator.Dot, Name.Date)),
            (r'(\.)(platform)', bygroups(Operator.Dot, Name.Platform)),

            (r'(\.)(required_rubygems_version)', bygroups(Operator.Dot, Name.Required_RubyGems_Version)),
            (r'(\.)(rubyforge_project)', bygroups(Operator.Dot, Name.Rubyforge_Project)),

            (r'(\.)(add_runtime_dependency)', bygroups(Operator.Dot, Name.Add_Runtime_Dependency)),
            (r'(\.)(add_development_dependency)', bygroups(Operator.Dot, Name.Add_Development_Dependency)),
            (r'(\.)(add_dependency)', bygroups(Operator.Dot, Name.Add_Dependency)),
            
            (r'(\.)(requirements)', bygroups(Operator.Dot, Name.Requirements)),

            (r'(\.)(extensions)', bygroups(Operator.Dot, Name.Extensions)),
            (r'(\.)(test_files)', bygroups(Operator.Dot, Name.Test_Files)),
            (r'(\.)(executables)', bygroups(Operator.Dot, Name.Executables)),
            (r'(\.)(extra_rdoc_files)', bygroups(Operator.Dot, Name.Extra_Rdoc_Files)),
            (r'(\.)(require_paths)', bygroups(Operator.Dot, Name.Require_Paths)),
            (r'(\.)(bindir)', bygroups(Operator.Dot, Name.Bindir)),
            
            # in podspec
            (r'(\.)(source)', bygroups(Operator.Dot, Name.Source)),
            (r'(\.)(source_files)', bygroups(Operator.Dot, Name.Source_files)),
            (r'(\.)(public_header_files)', bygroups(Operator.Dot, Name.Public_header_files)),

            (r'(\.)(framework)', bygroups(Operator.Dot, Name.Framework)),
            (r'(\.)(frameworks)', bygroups(Operator.Dot, Name.Frameworks)),
            
            (r'(\.)(weak_framework)', bygroups(Operator.Dot, Name.Weak_framework)),
            (r'(\.)(weak_frameworks)', bygroups(Operator.Dot, Name.Weak_frameworks)),
            
            (r'(\.)(vendored_framework)', bygroups(Operator.Dot, Name.Vendored_framework)),
            (r'(\.)(vendored_frameworks)', bygroups(Operator.Dot, Name.Vendored_frameworks)),
            
            (r'(\.)(vendored_library)', bygroups(Operator.Dot, Name.Vendored_library)),
            (r'(\.)(vendored_libraries)', bygroups(Operator.Dot, Name.Vendored_libraries)),

            (r'(\.)(library)', bygroups(Operator.Dot, Name.Library)),
            (r'(\.)(libraries)', bygroups(Operator.Dot, Name.Libraries)),

            (r'(\.)(module_name)', bygroups(Operator.Dot, Name.Module_Name)),
            (r'(\.)(dependency)', bygroups(Operator.Dot, Name.Dependency)),
            
            (r'(\.)(swift_version)', bygroups(Operator.Dot, Name.Swift_Version)),
            (r'(\.)(swift_versions)', bygroups(Operator.Dot, Name.Swift_Versions)),
            
            (r'(\.)(cocoapods_version)', bygroups(Operator.Dot, Name.Cocoapods_Version)),
            (r'(\.)(social_media_url)', bygroups(Operator.Dot, Name.Social_media_url)),
            
            (r'(\.)(readme)', bygroups(Operator.Dot, Name.Readme)),
            (r'(\.)(changelog)', bygroups(Operator.Dot, Name.Changelog)),

            (r'(\.)(resource)', bygroups(Operator.Dot, Name.Resource)),
            (r'(\.)(resources)', bygroups(Operator.Dot, Name.Resources)),

            (r'(\.)(screenshot)', bygroups(Operator.Dot, Name.Screenshot)),
            (r'(\.)(screenshots)', bygroups(Operator.Dot, Name.Screenshots)),
            
            (r'(\.)(documentation_url)', bygroups(Operator.Dot, Name.Documentation_url)),
            (r'(\.)(static_framework)', bygroups(Operator.Dot, Name.Static_framework)),
            (r'(\.)(deprecated)', bygroups(Operator.Dot, Name.Deprecated)),
            (r'(\.)(deprecated_in_favor_of)', bygroups(Operator.Dot, Name.Deprecated_in_favor_of)),
            
            # spec.ios.deployment_target = '6.0'
            (r'(\.)(deployment_target)', bygroups(Operator.Dot, Name.Deployment_target)),
            (r'(\.)(info_plist)', bygroups(Operator.Dot, Name.Info_plist)),

            (r'(\.)([a-zA-Z_]\w*[!?]?|[*%&^`~+\-/\[<>=])',
             bygroups(Operator.Dot, Name)),
            (r'[a-zA-Z_]\w*[!?]?', Name),
            (r'(\[)', Operator.Open_Square_Bracket),
            (r'(\])', Operator.Close_Square_Bracket),
            (r'(\{)', Operator.Open_Curly_Brace),
            (r'(\})', Operator.Close_Curly_Brace),
            (r'(\[|\]|\*\*|<<?|>>?|>=|<=|<=>|=~|={3}|'
             r'!~|&&?|\|\||\.{1,3})', Operator),
            (r'[-+/*%<>&!^|~]=?', Operator),
            (r'[=]=?', Operator.Equal),
            (r',', Punctuation.Comma),
            (r'[(){};,/?:\\]', Punctuation),
            (r'\n+', Text.Whitespace.Newline),
            (r'\s+', Text.Whitespace),
        ],
        'funcname': [
            (r'\(', Punctuation, 'defexpr'),
            (r'(?:([a-zA-Z_]\w*)(\.))?'  # optional scope name, like "self."
             r'('
                r'[a-zA-Z\u0080-\uffff][a-zA-Z0-9_\u0080-\uffff]*[!?=]?'  # method name
                r'|!=|!~|=~|\*\*?|[-+!~]@?|[/%&|^]|<=>|<[<=]?|>[>=]?|===?'  # or operator override
                r'|\[\]=?'  # or element reference/assignment override
                r'|`'  # or the undocumented backtick override
             r')',
             bygroups(Name.Class, Operator, Name.Function), '#pop'),
            default('#pop')
        ],
        'classname': [
            (r'\(', Punctuation, 'defexpr'),
            (r'<<', Operator, '#pop'),
            (r'[A-Z_]\w*', Name.Class, '#pop'),
            default('#pop')
        ],
        'defexpr': [
            (r'(\))(\.|::)?', bygroups(Punctuation, Operator), '#pop'),
            (r'\(', Operator, '#push'),
            include('root')
        ],
        'in-intp': [
            (r'\{', String.Interpol, '#push'),
            (r'\}', String.Interpol, '#pop'),
            include('root'),
        ],
        'string-intp': [
            (r'#\{', String.Interpol, 'in-intp'),
            (r'#@@?[a-zA-Z_]\w*', String.Interpol),
            (r'#\$[a-zA-Z_]\w*', String.Interpol)
        ],
        'string-intp-escaped': [
            include('string-intp'),
            (r'\\([\\abefnrstv#"\']|x[a-fA-F0-9]{1,2}|[0-7]{1,3})',
             String.Escape)
        ],
        'interpolated-regex': [
            include('string-intp'),
            (r'[\\#]', String.Regex),
            (r'[^\\#]+', String.Regex),
        ],
        'interpolated-string': [
            include('string-intp'),
            (r'[\\#]', String.Other),
            (r'[^\\#]+', String.Other),
        ],
        'multiline-regex': [
            include('string-intp'),
            (r'\\\\', String.Regex),
            (r'\\/', String.Regex),
            (r'[\\#]', String.Regex),
            (r'[^\\/#]+', String.Regex),
            (r'/[mixounse]*', String.Regex, '#pop'),
        ],
        'end-part': [
            (r'.+', Comment.Preproc, '#pop')
        ]
    }
    tokens.update(gen_rubystrings_rules())

