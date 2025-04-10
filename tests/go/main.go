package main

func main() {
	var arr [2][2]int = [2][2]int{{1, 2}, {3, 4}}
	println(arr[1][1][1])
}

type Human struct {
	name  string
	age   int8
	float float32
}
