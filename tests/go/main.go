package main

func main() {
	var h Human = Human{name: "", age: 1, float: 100}
	println(h.float)
}

type Human struct {
	name  string
	age   int8
	float float32
}
