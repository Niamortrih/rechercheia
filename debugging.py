from Solver import Solver

def print_lines(lines):
    for line in lines:
        print(line)

connection = Solver(solver="D:\Jesolver\jesolver_pro_avx2_1085.exe")


r = connection.command(line="set_isomorphism 0 0")
print_lines(r)

r = connection.command(line="set_isomorphism 0 0")
print_lines(r)