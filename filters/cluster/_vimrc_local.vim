" highlight the string enclosed by ' triples as XSLT
unlet b:current_syntax
syntax include @XSLT syntax/xslt.vim
syntax region xsltSnip start="^.\+'''[\\]\?\n" end="^'''" contains=@XSLT
