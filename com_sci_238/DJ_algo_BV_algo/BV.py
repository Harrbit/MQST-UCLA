import random as rand

def inner_product_mod(vec1, vec2):
    if (len(vec1) != len(vec2)):
        raise ValueError("vec1 and vec2 are not of the same length, they should be")
    
    inner_product = sum(a*b for a, b in zip(vec1, vec2))

    return inner_product % 2

def plus_mod(input_1, input_2):
    return (input_1 + input_2) % 2

def BV_function(a, b, x):
    ax = inner_product_mod(a, x)
    return plus_mod(ax, b)

n = 8
repeat = 10
seed = rand.seed(0)

all_zeros = [0]*n
for j in range(repeat):
    a = [rand.choice([0, 1]) for _ in range(n)]
    b = rand.choice([0, 1])
    a_answer = [0]*n
    b_answer = BV_function(a, b, all_zeros)

    for i in range(n):
        get_one_digit = all_zeros.copy()
        get_one_digit[i] = 1
        a_answer[i] = (BV_function(a, b, get_one_digit) + b_answer) % 2

    print("No.", j + 1, " a:", a, "b:", b)
    print("a_answer:", a_answer, "b_answer:", b_answer, "\n")
    if(a != a_answer):
        raise ValueError("a_answer not correct")
    if(b != b_answer):
        raise ValueError("b_answer not correct")