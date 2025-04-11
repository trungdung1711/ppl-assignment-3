def add(*args):
    print(args)
    return sum(args)


def print_something(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

arguments = {
    'first' : 100,
    'second' : 200,
    'third' : 300,
    'fourth' : 400,
    'fifth' : 500,
}
print_something(**arguments)