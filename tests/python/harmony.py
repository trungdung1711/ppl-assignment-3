def harmony(x, y):
    return (2 * x * y ) / (x + y)


if __name__ == '__main__':
    x = float(input('Number of x: '))
    y = float(input('Number of y: '))
    print(harmony(x, y))