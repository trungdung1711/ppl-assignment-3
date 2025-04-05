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
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,411))

    def test_412(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,412))

    def test_413(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,413))

    def test_414(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,414))

    def test_415(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,415))

    def test_416(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,416))

    def test_417(self):
        input = \
        '''
        func main() {
            var a int = 100
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
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,418))

    def test_419(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,419))

    def test_420(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,420))

    def test_421(self):
        input = \
        '''
        func main() {
            var a int = 100
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
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,422))

    def test_423(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,423))

    def test_424(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,424))

    def test_425(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,425))

    def test_426(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,426))

    def test_427(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,427))

    def test_428(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,428))

    def test_429(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,429))

    def test_430(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,430))

    def test_431(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,431))

    def test_432(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
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
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,434))

    def test_435(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,435))

    def test_436(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,436))

    def test_437(self):
        input = \
        '''
        func main() {
            var a int = 100
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
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,438))

    def test_439(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
        self.assertTrue(TestChecker.test(input,expect,439))

    def test_440(self):
        input = \
        '''
        func main() {
            var a int = 100
        }
        '''
        expect = ''
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