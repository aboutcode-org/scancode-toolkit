"""
Minimal lexer for Ruby.
Derived from pygments.lexers.ruby and significantly modified
copyright: Copyright 2006-2022 by the Pygments team, see pygments.AUTHORS.
SPDX-License-Identifier: BSD-2-Clause
"""

import re

from pygments.lexer import ExtendedRegexLexer, include, \
    bygroups, default, LexerContext, words

from pygments import token

Keyword = token.Keyword
Name = token.Name
String = token.String
Text = token.Text
Comment = token.Comment
Operator = token.Operator
Number = token.Number
Punctuation = token.Punctuation
Error = token.Error

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
        yield start, Operator.Heredoc, match.group(1)  # <<[-~]?
        yield match.start(2), String.Heredoc, match.group(2)  # quote ", ', `
        yield match.start(3), String.HeredocDelimiter, match.group(3)  # heredoc name
        yield match.start(4), String.Heredoc, match.group(4)  # quote again

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
                        yield match.start(), String.HeredocDelimiter, match.group()
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

    def gen_rubystrings_rules():  # NOQA

        def intp_regex_callback(self, match, ctx):
            yield match.start(1), String.Regex, match.group(1)  # begin
            nctx = LexerContext(match.group(3), 0, ['interpolated-regex'])
            for i, t, v in self.get_tokens_unprocessed(context=nctx):
                yield match.start(3) + i, t, v
            yield match.start(4), String.Regex, match.group(4)  # end[mixounse]*
            ctx.pos = match.end()

        def intp_string_callback(self, match, ctx):
            yield match.start(1), String.Other, match.group(1)
            nctx = LexerContext(match.group(3), 0, ['interpolated-string'])
            for i, t, v in self.get_tokens_unprocessed(context=nctx):
                yield match.start(3) + i, t, v
            yield match.start(4), String.Other, match.group(4)  # end
            ctx.pos = match.end()

        states = {}
        states['strings'] = [
            # Gem/Pod bare :colo strings used as hash keys
            # groups/scopes
            (
                r'\:(development|debug|test|default|source|platforms?|require|groups?|name'
                r'|engine|engine_version|patchlevel|git|tag|branch|ref|git_source|github|gist|bitbucket|path)',
                String.ColonSymbol,
             ),

            # Podspec
            (
                r'\:(type|file|text|commit|submodules|hg|revision|svn|folder|http|headers|flatten'
                r'|sha1|sha256|osx|ios|watchos|tvos|configurations|sha256)',
                String.ColonSymbol,
            ),

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
        for name, ttype, end, endttype in (
            ('string-double', String.Value, '"', String.Double.Quote),
            ('string-single', String.Value, "'", String.Single.Quote),
            ('sym', String.Symbol, '"', String.Double.Quote),
            ('backtick', String.Value, '`', String.Backtick.Quote),
        ):
            states['simple-' + name] = [
                include('string-intp-escaped'),
                (r'[^\\%s#]+' % end, ttype),
                (r'[\\#]', ttype),
                (end, endttype, '#pop'),
            ]

        # braced quoted strings
        for lbrace, rbrace, bracecc, name in \
                ('\\{', '\\}', '{}', 'cb'), \
                ('\\[', '\\]', '\\[\\]', 'sb'), \
                ('\\(', '\\)', '()', 'pa'), \
                ('<', '>', '<>', 'ab'):
            states[name + '-intp-string'] = [
                (r'\\[\\' + bracecc + ']', String.Value),
                (lbrace, String.Other.Lbrace, '#push'),
                (rbrace, String.Other.Rbrace, '#pop'),
                include('string-intp-escaped'),
                (r'[\\#' + bracecc + ']', String.Value),
                (r'[^\\#' + bracecc + ']+', String.Value),
            ]
            states['strings'].append((r'%[QWx]?' + lbrace, String.Other.Lbrace,
                                      name + '-intp-string'))
            states[name + '-string'] = [
                (r'\\[\\' + bracecc + ']', String.Other),
                (lbrace, String.Other.Lbrace, '#push'),
                (rbrace, String.Other.Rbrace, '#pop'),
                (r'[\\#' + bracecc + ']', String.Value),
                (r'[^\\#' + bracecc + ']+', String.Value),
            ]
            states['strings'].append((r'%[qsw]' + lbrace, String.Other.Lbrace,
                                      name + '-string'))
            states[name + '-regex'] = [
                (r'\\[\\' + bracecc + ']', String.Regex),
                (lbrace, String.Regex, '#push'),
                (rbrace + '[mixounse]*', String.Regex, '#pop'),
                include('string-intp'),
                (r'[\\#' + bracecc + ']', String.Regex),
                (r'[^\\#' + bracecc + ']+', String.Regex),
            ]
            states['strings'].append((r'%r' + lbrace, String.Regex,
                                      name + '-regex'))

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

            # in any ruby code
            (words(('BEGIN', 'begin',), suffix=r'\b'), Keyword.Begin),
            (words(('END', 'end',), suffix=r'\b'), Keyword.End),
            (words(('do',), suffix=r'\b'), Keyword.Do),

            # in Gemfile: source "https://rubygems.org"
            (words(('source',), suffix=r'\b'), Keyword.Attribute.Source),

            # in Gemfile, a single URL as in: source "https://rubygems.org". has extra arguments
            # ruby "2.0.0", :patchlevel => "247"
            (words(('ruby',), suffix=r'\b'), Keyword.Attribute.Ruby),

            # in Gemfile
            # gem "RedCloth", ">= 4.1.0", "< 4.2.0"
            # gem "nokogiri", :require => "nokogiri"
            # gem "nokogiri", :require => true
            # gem "redis", :require => ["redis/connection/hiredis", "redis"]
            # gem "rspec", :group => :test
            # gem "wirble", :groups => [:development, :test]
            # gem "ruby-debug", :platforms => :mri_18
            # gem "nokogiri",   :platforms => [:mri_18, :jruby]
            # gem "some_internal_gem", :source => "https://gems.example.com"
            # gem "rack", :git => "git://github.com/rack/rack.git"
            # gem "rails", :git => "https://github.com/rails/rails.git", :branch => "5-0-stable"
            # gem "rails", :git => "https://github.com/rails/rails.git", :tag => "v5.0.0"
            # gem "rails", :git => "https://github.com/rails/rails.git", :ref => "4aded"
            # gem "rack", :git => "git://github.com/rack/rack.git" :submodules => true
            # git_source(:stash){ |repo_name| "https://stash.corp.acme.pl/#{repo_name}.git" }
            # gem 'rails', :stash => 'forks/rails'
            # gem "rails", :github => "rails/rails"
            # gem "rails", :github => "https://github.com/rails/rails/pull/43753"
            # gem "the_hatch", :gist => "4815162342"
            # gem "the_hatch", :git => "https://gist.github.com/4815162342.git"
            # gem "rails", :bitbucket => "rails/rails"
            # gem "rails", :path => "vendor/rails"
            # path 'components' do
            #   gem 'admin_ui'
            #   gem 'public_ui'
            # end
            # git "https://github.com/rails/rails.git" do
            #   gem "activesupport"
            #   gem "actionpack"
            # end
            # group :development, :optional => true do
            #   gem "wirble"
            #   gem "faker"
            # end
            # source "https://gems.example.com" do
            #   gem "some_internal_gem"
            #   gem "another_internal_gem"
            # end
            (words(('gem',), suffix=r'\b'), Keyword.Gem),

            # includes a gemspec in the Gemfile
            (words(('gemspec',), suffix=r'\b'), Keyword.Gemspec),

            (words(('require',), suffix=r'\b'), Keyword.Attribute.Require),
            (words(('versions',), suffix=r'\b'), Keyword.Attribute.Versions),

            (words(('git',), suffix=r'\b'), Keyword.Attribute.Git),
            (words(('group',), suffix=r'\b'), Keyword.Attribute.Group),
            (words(('platforms',), suffix=r'\b'), Keyword.Attribute.Platforms),
            (words(('path',), suffix=r'\b'), Keyword.Attribute.Path),

            # pods
            # this is a function as in:
            # pod 'ShareKit/Twitter',  '2.0'
            (words(('pod',), suffix=r'\b'), Keyword.Pod),

            # in podspec
            # TODO: this is typically nested with spect.func
            # this is a function as in:
            #     s.subspec 'Core' do |cs|
            #       cs.dependency 'RestKit/ObjectMapping'
            #       cs.dependency 'RestKit/Network'
            #       cs.dependency 'RestKit/CoreData'
            #     end
            (words(('subspec',), suffix=r'\b'), Keyword.Attribute.Subspec),
            (words(('test_spec',), suffix=r'\b'), Keyword.Attribute.Subspec),
            (words(('app_spec',), suffix=r'\b'), Keyword.Attribute.Subspec),
            (words(('app_spec',), suffix=r'\b'), Keyword.Attribute.Subspec),

            # keywords
            (words((
                'alias', 'begin', 'break', 'case', 'defined?',
                'else', 'elsif', 'end', 'ensure', 'for', 'if', 'in', 'next', 'redo',
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

            # important declarations
            (r'Gem::Specification', Name.Spec.Gem),
            (r'Pod::Spec', Name.Spec.Pod),

            # other constants
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

            # see https://github.com/CocoaPods/Core/blob/master/lib/cocoapods-core/specification/dsl.rb

            # in gemspec and in podspec
            (
                r'(\.)('
                r'name'
                r'|version'
                r'|summary'
                r'|description'

                # gemspec has author:string or authors:list.
                # podspec has author:string authors:list of names and authors:mapping {name: email}
                r'|authors?'

                # URL to home
                r'|homepage'

                # gemspec has license:string or license:list
                # podspec has license:string or license:mapping with type/file/text keys
                r'|licenses?'

                ')',
                bygroups(Operator.Dot, Name.Attribute.Spec),
             ),

            (
                r'(\.)('
                # in podspec:
                # a mapping point to the source VCS or a plain download
                # type keys are: git/svn/hg/http and point to a URL
                # and then each type has different attributes name/values
                # :git  => [:tag, :branch, :commit, :submodules]
                # :svn  => [:folder, :tag, :revision]
                # :hg   => [:revision]
                # :http => [:flatten, :type, :sha256, :sha1, :headers]
                r'source'

                ')',
                bygroups(Operator.Dot, Name.Attribute.Spec),
             ),

            # in gemspec only
            (
                r'(\.)('
                # gemspec only  email:string or email:list
                r'email'

                # spec.required_ruby_version = '>= 2.7.0'
                r'|required_ruby_version'
                r'|required_rubygems_version'
                r'|date'
                r'|platform'
                # legacy as rubyforge is dead
                r'|rubyforge_project'

                # listrs to append to. spec.requirements << 'libmagick, v6.0'
                r'|requirements'

                # a list of strings
                r'|require_paths'

                r'|files'
                # gemspec attributes related to "files"
                r'|test_files'
                # a single path
                r'|bindir'

                # spec.extra_rdoc_files = ['README', 'doc/user-guide.txt']
                r'|extra_rdoc_files'

                # lists wher you append
                # spec.executables << 'rake'
                r'|executables'
                # spec.extensions << 'ext/rmagic/extconf.rb'
                r'|extensions'

                ')',
                bygroups(Operator.Dot, Name.Attribute.Spec),
             ),

            # gempsec only
            # spec.add_development_dependency 'example', '~> 1.1', '>= 1.1.4'
            # spec.add_runtime_dependency 'example', '~> 1.1', '>= 1.1.4'
            (
                r'(\.)(add_runtime_dependency|add_dependency)',
                bygroups(Operator.Dot, Name.AddGemDependency.Runtime),
             ),
            (
                r'(\.)(add_development_dependency)',
                bygroups(Operator.Dot, Name.AddGemDependency.Dev),
             ),

            # gemspec  has a mmaping and doc suggest using theses:
            #     "bug_tracker_uri"   => "https://example.com/user/bestgemever/issues",
            #     "changelog_uri"     => "https://example.com/user/bestgemever/CHANGELOG.md",
            #     "documentation_uri" => "https://www.example.info/gems/bestgemever/0.0.1",
            #     "homepage_uri"      => "https://bestgemever.example.io",
            #     "mailing_list_uri"  => "https://groups.example.com/bestgemever",
            #     "source_code_uri"   => "https://example.com/user/bestgemever",
            #     "wiki_uri"          => "https://example.com/user/bestgemever/wiki"
            #     "funding_uri"       => "https://example.com/donate"
            (
                r'(\.)(metadata)',
                bygroups(Operator.Dot, Name.Attribute.GemMetadata),
             ),

            # in podspec only
            (
                r'(\.)('
                # lists of glob-style patterns as 'Classes/**/*.{h,m}'
                r'source_files'
                r'|public_header_files'
                r'|project_header_files'
                r'|private_header_files'
                r'|project_header_files'
                r'|vendored_frameworks'
                r'|vendored_library|vendored_libraries'
                # a string, list or mapping of glob-style patterns
                r'|on_demand_resources?'
                # a mapping to string or list of glob-style patterns for each res bundle
                r'|resource_bundles?'
                # a string, list of glob-style patterns
                r'|resources?'
                # a list of glob-style patterns
                r'|exclude_files'
                # a list of glob-style patterns
                r'|preserve_paths?'

                # a mapping of platform-name:version : osx, macos, ios, tvos, ...
                r'|platforms'

                # string or list as in spec.frameworks = 'QuartzCore', 'CoreData'
                r'|frameworks?'
                r'|weak_frameworks?'
                r'|library|libraries'

                r'|module_name'

                # a string or list of versions
                r'|swift_versions?'
                # a version constraint
                r'|cocoapods_version'

                # single URLs to markdown file
                r'|social_media_url'
                r'|readme'
                r'|changelog'
                r'|documentation_url'

                # podspec only: single URL or list of URLs
                r'|screenshots?'

                # boolean
                r'|static_framework'

                # boolean, string
                r'|deprecated|deprecated_in_favor_of'

                r'|deployment_target'

                # mapping of name/values added to plist
                r'|info_plist'
                r')',
                bygroups(Operator.Dot, Name.Attribute.PodSpec),
            ),

            # in podspec
            # as spec.dependency 'AFNetworking', '~> 1.0'
            # or with an optional extra named arg: configurations as in
            # spec.dependency 'RestKit/CoreData', '~> 0.20.0', :configurations => :debug
            # or as spec.ios.dependency 'MBProgressHUD', '~> 0.5'
            (
                r'(\.)('
                r'dependency'
                r')',
                bygroups(Operator.Dot, Name.PodDependency),
             ),

            # catchall for dot.name
            (r'(\.)([a-zA-Z_]\w*[!?]?|[*%&^`~+\-/\[<>=])',
             bygroups(Operator.Dot, Name)),

            (r'[a-zA-Z_]\w*[!?]?', Name),
            (r'(\[)', Operator.Open_Square_Bracket),
            (r'(\])', Operator.Close_Square_Bracket),
            (r'(\{)', Operator.Open_Curly_Brace),
            (r'(\})', Operator.Close_Curly_Brace),
            (r'=>', Operator.Rocket),
            (r'(\[|\]|\*\*|<<?|>>?|>=|<=|<=>|=~|={3}|'
             r'!~|&&?|\|\||\.{1,3})', Operator),
            (r'[-+/*%<>&!^|~]=?', Operator),
            (r'[=]=?', Operator.Equal),
            (r',', Punctuation.Comma),
            (r'[(){};,/?\\]', Punctuation),
            (r':', Punctuation.Colon),
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
