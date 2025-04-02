package main

func main() {
	var Animal Animal = Animal{name: ""}
	println(Animal.name)
}

var Global int = 100

type Animal struct {
	name string
}
