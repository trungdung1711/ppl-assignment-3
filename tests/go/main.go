package main

var GLOBAL int = 100

func main() {
	// in Go := is used for short declaration
	a := 100
	println(a)
	// assignment
	GLOBAL = 200
}

type Human struct {
	name  string
	age   int8
	float float32
}
