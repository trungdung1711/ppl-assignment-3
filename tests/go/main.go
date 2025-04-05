package main

func main() {
	function()
	var animal Animal = Animal{name: "Tom"}
	animal.function()
	println(Global)
}

type Animal struct {
	name string
}

func function() int {
	return 100
}

func (a *Animal) function() int {
	return 100
}

type Human interface {
	getName() string
}

var Global string = "This is a global variable\n"
