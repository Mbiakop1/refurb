# these will match

def f(x, y):
    pass


lambda: print()
lambda x: bool(x)
lambda x, q: f(x, q)


# these will not

lambda: f(True, False)
lambda x: f(x, True)
lambda x, y: f(y, x)
lambda x: bool(x + 1)
lambda x: x + 1
lambda: True