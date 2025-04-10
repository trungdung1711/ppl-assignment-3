gen :
	toilet -f smblock --metal "gen"
	python run.py gen

lex :
	toilet -f smblock --metal "lexer"
	python run.py test LexerSuite

par : 
	toilet -f smblock --metal "parser"
	python run.py test ParserSuite

ast :
	toilet -f smblock --metal "ast"
	python run.py test ASTGenSuite

check :
	toilet -f smblock --metal "semantic"
	python run.py test CheckSuite

all :
	toilet -f smblock --metal "test all"
	zsh ./run.sh

.PHONY : gen ast all lex par check
