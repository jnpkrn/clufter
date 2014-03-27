" highlight the string enclosed by ' triples as XSLT
unlet b:current_syntax
syntax include @XSLT syntax/xslt.vim
syntax region xsltSnip start="^.\+'''[\\]\?\n" end="^'''" contains=@XSLT
syn match xslElement '\%(clufter:\)\@<=descent'
syn match xslElement '\%(clufter:\)\@<=descent-mix'
syn match xslElement '\%(clufter:\)\@<=message'
syn match xslElement '\%(clufter:\)\@<=snippet'
