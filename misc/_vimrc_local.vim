" highlight the string enclosed by ' triples as XSLT
unlet b:current_syntax
syn include @XSLT syntax/xslt.vim
syn region xsltSnip start="'''" end="'''" contains=@XSLT
syn match xslElement '\%(clufter:\)\@8<=descent'
syn match xslElement '\%(clufter:\)\@8<=descent-mix'
syn match xslElement '\%(clufter:\)\@8<=message'
syn match xslElement '\%(clufter:\)\@8<=snippet'
