package main

func main() {
	function()
	var animal Animal = Animal{name: "Tom"}
	animal.function()
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

type MyType Animal
