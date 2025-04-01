gen :
	toilet --metal -t --font mono12  "gen"
	python run.py gen

lex :
	toilet --metal -t --font mono12  "lexer"
	python run.py test LexerSuite

par : 
	toilet --metal -t --font mono12  "parser"
	python run.py test ParserSuite

ast :
	toilet --metal -t --font mono12  "ast"
	python run.py test ASTGenSuite

check :
	toilet --metal -t --font mono12  "semantic"
	python run.py test CheckSuite

all :
	toilet --metal -t --font mono12  "test all"
	zsh ./run.sh

.PHONY : gen ast all lex par check