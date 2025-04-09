import unittest
from TestUtils import TestChecker
from AST import *

from enum import Enum

class ErrorKind(Enum):
    FUNCTION    = "Function"
    METHOD      = "Method"
    PARAMETER   = "Parameter"
    VARIABLE    = "Variable"
    CONSTANT    = "Constant"
    FIELD       = "Field"
    IDENTIFIER  = "Identifier"
    TYPE        = "Type"
    PROTOTYPE   = "Prototype"


def redeclared(kind: ErrorKind, name: str) -> str:
    return f'Redeclared {kind.value}: {name}' + '\n'


def undeclared(kind : ErrorKind, name : str) -> str:
    return f'Undeclared {kind.value}: {name}\n'


def type_mismatch(ast) -> str:
    return f'Type Mismatch: {str(ast)}\n'

class CheckSuite(unittest.TestCase):


    def test_401(self):
        input = \
        '''
        var a int = 100;
        var b int = 200;
        var c int = 300;
        var d int = 400;
        const e = 5.6
        const f = "string"

        type Human struct {
            a int;
            b int;
            c int;
            d int;
        }

        func g(a int, b, c float) int {
            var a int = 200;
            a := 300
        }

        func (h Human) eat() {
            var a int = 400;
        }

        type Computer interface {
            getName() string
            getType() string
            getCode() string
            start(code int) boolean
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,401))


    def test_402(self):
        input = """var a int; var b int; var a int; """
        expect = redeclared(ErrorKind.VARIABLE, 'a')
        self.assertTrue(TestChecker.test(input,expect,402))


    def test_403(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        func main() {
            var b int = 200
        }
        '''
        expect = redeclared(ErrorKind.FUNCTION, 'main')
        self.assertTrue(TestChecker.test(input,expect,403))


    def test_404(self):
        input = \
        '''
        var a int = 200
        var a float = 300
        func main() {
            var a int = 100
        }
        '''
        expect = redeclared(ErrorKind.VARIABLE, 'a')
        self.assertTrue(TestChecker.test(input,expect,404))


    def test_405(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var main float = 200
        '''
        expect = redeclared(ErrorKind.VARIABLE, 'main')
        self.assertTrue(TestChecker.test(input,expect,405))


    def test_406(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Human struct {
            name string
            age int
            money float
        }

        type Human struct {
            isDead boolean
            isGod boolean
        }
        '''
        expect = redeclared(ErrorKind.TYPE, 'Human')
        self.assertTrue(TestChecker.test(input,expect,406))


    def test_407(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Computer interface {
            getCode() string
            getName() string
        }

        func Computer() {
            var a int = 200
        }
        '''
        expect = redeclared(ErrorKind.FUNCTION, 'Computer')
        self.assertTrue(TestChecker.test(input,expect,407))


    def test_408(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var a int = 100

        var b int = 200

        type Monster struct {
            a int
            b int
        }

        type Weapon struct {
            a int
            b float
            c string
        }

        const Weapon = ""
        '''
        expect = redeclared(ErrorKind.CONSTANT, 'Weapon')
        self.assertTrue(TestChecker.test(input,expect,408))


    def test_409(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Animal interface {
            getType() string
        }

        type Monster struct {
            name string
        }

        type Monster interface {
            getDam() float
        }
        '''
        expect = redeclared(ErrorKind.TYPE, 'Monster')
        self.assertTrue(TestChecker.test(input,expect,409))


    def test_410(self):
        input = \
        '''
        var a int = 200
        const b = "something"
        var c float = 150
        var d boolean = false

        func doSomething(a int, b float, c Human) {
            var a int = 2
        }

        func main() {
            var a int = 100
        }

        func doSomething(a int, b string) {
            var c float = 4.5
        }
        '''
        expect = redeclared(ErrorKind.FUNCTION, 'doSomething')
        self.assertTrue(TestChecker.test(input,expect,410))


    def test_411(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const main = 100
        var a int = 100
        '''
        expect = redeclared(ErrorKind.CONSTANT, 'main')
        self.assertTrue(TestChecker.test(input,expect,411))


    def test_412(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Human struct {
            name string
            name int
        }
        '''
        expect = redeclared(ErrorKind.FIELD, 'name')
        self.assertTrue(TestChecker.test(input,expect,412))


    def test_413(self):
        input = \
        '''
        type Animal struct {
            animalType string
            name string
            age int
            sons [4]int
            name string
        }

        func main() {
            var a int = 100
        }
        '''
        expect = redeclared(ErrorKind.FIELD, 'name')
        self.assertTrue(TestChecker.test(input,expect,413))


    def test_414(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const SIZE = 2 + 4 - 1
        const SIZE_10 = SIZE * 2


        type Human struct {
            sons [SIZE_10]Human
            sons [100]int
        }
        '''
        expect = redeclared(ErrorKind.FIELD, 'sons')
        self.assertTrue(TestChecker.test(input,expect,414))


    def test_415(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const ERROR = "a" + 100
        '''
        expect = type_mismatch(
            BinaryOp(
                '+',
                StringLiteral('"a"'),
                IntLiteral(100)
            )
        )
        self.assertTrue(TestChecker.test(input,expect,415))


    def test_416(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const SIZE = 1 + 1
        const PI = 3.14 + SIZE
        const TRUE = true && false

        const ERROR = 100 * false

        '''
        expect = type_mismatch(
            BinaryOp(
                '*',
                IntLiteral(100),
                BooleanLiteral(False)
            )
        )
        self.assertTrue(TestChecker.test(input,expect,416))


    def test_417(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const array = 4

        type Animal struct {
            a int
            b float
            c string
            d [array]Animal
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,417))


    def test_418(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const SIZE = 12

        type Animal struct {
            a int
            b string
            c Animal
            d [SIZE][2][3][4][5]Animal
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,418))


    def test_419(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const SIZE = A * 100 - 200 + 500 / 100
        '''
        expect = undeclared(ErrorKind.IDENTIFIER, 'A')
        self.assertTrue(TestChecker.test(input,expect,419))


    def test_420(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const NUM = 100 / SIZE
        '''
        expect = undeclared(ErrorKind.IDENTIFIER, 'SIZE')
        self.assertTrue(TestChecker.test(input,expect,420))


    def test_421(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const SIZE = 100

        type Dog struct {
            name string
            age int
        }

        type Animal interface {
            eat(a int) [SIZE]Dog
            attack(d Dog) float
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,421))


    def test_422(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Animal interface {
            getName() string
            getAge() int
            setName(name string)
            getName()
        }
        '''
        expect = redeclared(ErrorKind.PROTOTYPE, 'getName')
        self.assertTrue(TestChecker.test(input,expect,422))


    def test_423(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const NUM = 30

        type Key struct {
            name string
        }

        type KeyBoard struct {
            keys [NUM]Key
        }

        type Computer interface {
            getKeyBoard() KeyBoard
            getKeyBoard() [NUM]Key
        }
        '''
        expect = redeclared(ErrorKind.PROTOTYPE, 'getKeyBoard')
        self.assertTrue(TestChecker.test(input,expect,423))


    def test_424(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        const A = 10
        const B = "string"
        const C = F
        const D = ""
        const E = ""
        const F = 5.6
        const G = 1.2
        '''
        expect = undeclared(ErrorKind.IDENTIFIER, 'F')
        self.assertTrue(TestChecker.test(input,expect,424))


    def test_425(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        func add(a int, b int) int {
            return a + b
        }

        func sub(a int, a int) int {
            return a - b
        }
        '''
        expect = redeclared(ErrorKind.PARAMETER, 'a')
        self.assertTrue(TestChecker.test(input,expect,425))


    def test_426(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Human struct {
            a int
            b string
            c Human
            d [4]Human
        }

        func doSomething(h Human, h Human, i int) {
            return h.a
        }
        '''
        expect = redeclared(ErrorKind.PARAMETER, 'h')
        self.assertTrue(TestChecker.test(input,expect,426))


    def test_427(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Human struct {
            a int 
            b [3]Human
            c int
        }

        func (h Human) a(a int, b int) int {
            return a + b
        }
        '''
        expect = redeclared(ErrorKind.METHOD, 'a')
        self.assertTrue(TestChecker.test(input,expect,427))


    def test_428(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Human struct {
            a int
            b float
            c string
            d [3]int
        }

        func (h Human) eat() int {
            return 100
        }

        func (h Human) eat() float {
            return 1.5
        }
        '''
        expect = redeclared(ErrorKind.METHOD, 'eat')
        self.assertTrue(TestChecker.test(input,expect,428))


    def test_429(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Food struct {
            calories float
        }

        func (h Human) eat(f Food) int {
            return f.calories
        }

        type Human struct {
            name string
            age int
        }

        func (m Human) name() string {
            return m.name
        }
        '''
        expect = redeclared(ErrorKind.METHOD, 'name')
        self.assertTrue(TestChecker.test(input,expect,429))


    def test_430(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        type Animal struct {
            arr [4]int
            son Animal
            parent Animal
            isDead boolean
        }

        func killAnimal(a Animal) {
            a.isDead := true
        }

        func (a Animal) son() Animal {
            return a.son
        }
        '''
        expect = redeclared(ErrorKind.METHOD, 'son')
        self.assertTrue(TestChecker.test(input,expect,430))


    def test_431(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var a int = 4.5
        '''
        expect = type_mismatch(
            VarDecl(
                'a',
                IntType(),
                FloatLiteral(4.5)
            )
        )
        self.assertTrue(TestChecker.test(input,expect,431))


    def test_432(self):
        input = \
        '''
        var a string = 100
        func main() {
            var a int = 100
        }
        '''
        expect = type_mismatch(
            VarDecl(
                'a',
                StringType(),
                IntLiteral(100)
            )
        )
        self.assertTrue(TestChecker.test(input,expect,432))


    def test_433(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,433))


    def test_434(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var a float = 100
        var b float = 1.4
        var c float = 2
        var d Animal = Tiger {name : "", blood : 100, dam : 500.0}
        var e boolean = true
        var f string = "some thing\\n"
        var g int = 100
        var h float = g
        var i [4]int = [4]int{1, 2, 3, 4}
        var j [3][2][1]float = [3][2][1]int{{{1}, {2}}, {{3}, {4}}, {{5}, {6}}}

        type Animal interface {
            attack(a Animal) float
            eat(a Animal)
        }

        func (t Tiger) attack(a Animal) float {
            return 0.5
        }

        func (t Tiger) eat(a Animal) {
            t.blood := 100
        }

        type Tiger struct {
            name string
            blood int
            dam float
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,434))


    def test_435(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var arr [5][5]string = [1][1]string{{"string"}}
        '''
        expect = type_mismatch(
            VarDecl(
                'arr',
                ArrayType(
                    [
                        IntLiteral(5),
                        IntLiteral(5)
                    ],
                    StringType()
                ),
                ArrayLiteral(
                    [
                        IntLiteral(1),
                        IntLiteral(1)
                    ],
                    StringType(),
                    [
                        [
                            StringLiteral('"string"')
                        ]
                    ]
                )
            )
        )
        self.assertTrue(TestChecker.test(input,expect,435))


    def test_436(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var w Weapon = Axe{}

        type Human struct {
            name string
            age int
            blood float
        }

        type Weapon interface {
            attack(a int, b string, c float, d Human)
        }

        type Axe struct {
            dam float
        }

        func (a Axe) attack(a float, b string, c float, d Human) {
            d.blood := d.blood - a.dam
        }
        '''
        expect = type_mismatch(
            VarDecl(
                'w',
                Id('Weapon'),
                StructLiteral(
                    'Axe',
                    []
                )
            )
        )
        self.assertTrue(TestChecker.test(input,expect,436))


    def test_437(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var e1 Entity = Herobrine{}
        var e2 Entity = Player{}

        type Herobrine struct {
            power int
        }

        func (h Herobrine) getBlood() int {
            return 99999
        }

        type Entity interface {
            getBlood() int
        }

        type Player struct {
            name string
        }

        func (p Player) getBlood() int {
            return 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,437))


    def test_438(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var a int = (200 - 2)
        var b string = "b"
        var c = b + "c"
        var d = b + c + c + c + b + "this one"
        var e = d + 10.4
        '''
        expect = type_mismatch(
            BinaryOp(
                '+',
                Id('d'),
                FloatLiteral(10.4)
            )
        )
        self.assertTrue(TestChecker.test(input,expect,438))


    def test_439(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var a = ""
        var b = 100
        var c = true || false
        var e = [4]int{1, 2, 3, 4}
        var f = e
        var m = f
        var n int = f
        '''
        expect = type_mismatch(
            VarDecl(
                'n',
                IntType(),
                Id('f')
            )
        )
        self.assertTrue(TestChecker.test(input,expect,439))


    def test_440(self):
        input = \
        '''
        func main() {
            var a int = 100
        }

        var a = 100 // int
        var b = 1.5 // float
        var c = false // boolean
        var e = "string" //string
        var f = "string"
        var g [5]string
        var h [3]string = g
        '''
        expect = type_mismatch(
            VarDecl(
                'h',
                ArrayType(
                    [
                        IntLiteral(3)
                    ],
                    StringType()
                ),
                Id('g')
            )
        )
        self.assertTrue(TestChecker.test(input,expect,440))


    def test_441(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,441))

    def test_442(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,442))

    def test_443(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,443))

    def test_444(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,444))

    def test_445(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,445))

    def test_446(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,446))

    def test_447(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,447))

    def test_448(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,448))

    def test_449(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,449))

    def test_450(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,450))

    def test_451(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,451))

    def test_452(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,452))

    def test_453(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,453))

    def test_454(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,454))

    def test_455(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,455))

    def test_456(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,456))

    def test_457(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,457))

    def test_458(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,458))

    def test_459(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,459))

    def test_460(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,460))

    def test_461(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,461))

    def test_462(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,462))

    def test_463(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,463))

    def test_464(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,464))

    def test_465(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,465))

    def test_466(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,466))

    def test_467(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,467))

    def test_468(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,468))

    def test_469(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,469))

    def test_470(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,470))

    def test_471(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,471))

    def test_472(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,472))

    def test_473(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,473))

    def test_474(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,474))

    def test_475(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,475))

    def test_476(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,476))

    def test_477(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,477))

    def test_478(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,478))

    def test_479(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,479))

    def test_480(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,480))

    def test_481(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,481))

    def test_482(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,482))

    def test_483(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,483))

    def test_484(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,484))

    def test_485(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,485))

    def test_486(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,486))

    def test_487(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,487))

    def test_488(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,488))

    def test_489(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,489))

    def test_490(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,490))

    def test_491(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,491))

    def test_492(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,492))

    def test_493(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,493))

    def test_494(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,494))

    def test_495(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,495))

    def test_496(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,496))

    def test_497(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,497))

    def test_498(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,498))

    def test_499(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,499))

    def test_500(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,500))


    # def test_sample(self):
    #     input = \
    #     '''
    #     func main() {
    #         var a int = 100
    #     }
    #     '''
    #     expect = ''
    #     self.assertTrue(TestChecker.test(input,expect,40))



    # def test_type_mismatch(self):
    #     input = """var a int = 1.2;"""
    #     expect = "Type Mismatch: VarDecl(a,IntType,FloatLiteral(1.2))\n"
    #     self.assertTrue(TestChecker.test(input,expect,403))


    # def test_undeclared_identifier(self):
    #     input = Program([VarDecl("a",IntType(),Id("b"))])
    #     expect = "Undeclared Identifier: b\n"
    #     self.assertTrue(TestChecker.test(input,expect,404))