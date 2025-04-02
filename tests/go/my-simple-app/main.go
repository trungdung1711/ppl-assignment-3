package main

import (
	"fmt"
	"go/ast"
	"go/importer"
	"go/parser"
	"go/token"
	"go/types"
	"os"

	"github.com/trungdung1711/go-inspection/inspect"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run main.go <filename.go>")
		return
	}
	filename := os.Args[1]

	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, filename, nil, parser.ParseComments)
	if err != nil {
		fmt.Printf("Error parsing file: %v\n", err)
		os.Exit(1)
	}

	info := &types.Info{
		Defs:   make(map[*ast.Ident]types.Object),
		Uses:   make(map[*ast.Ident]types.Object),
		Scopes: make(map[ast.Node]*types.Scope),
	}
	conf := types.Config{Importer: importer.Default()}
	pkg, err := conf.Check("main", fset, []*ast.File{file}, info)
	if err != nil {
		fmt.Printf("Type checking error: %v\n", err)
		os.Exit(1)
	}

	fmt.Print("AST================================\n")
	inspect.PrintAst(filename)
	fmt.Print("SEMANTIC ANALYSIS==================\n")
	inspect.PrintScope(pkg.Scope(), 0)
}
