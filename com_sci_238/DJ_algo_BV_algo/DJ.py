import random as rand
import time

def generate_balanced_map(n, seed):
    """returns a map of input to output for balanced function, a map of a balanced function"""
    # for consistency
    rand.seed(seed)
    # generate a sequence of 2**n/2 1s and 0s 
    num_input = 2 ** n
    num_half = num_input // 2
    output = [0]*num_half + [1]*num_half
    # make the sequence random
    rand.shuffle(output)
    return output

def generate_constant_map(n):
    """returns a map that is either all zeros or all ones, a map of a constant function"""
    element = rand.choice([0, 1])
    vector = n*[element]
    return vector

def DJ_classic(input):
    """determine wether a function is balanced or constaint"""

    """SOME THOUGH: 
    the input function is discribed by a map in this program. 
    But the function in the problem is treated as a black box, 
    so I'm investigating the map one input-output pair at a time, 
    simulating how a black box would act."""

    length = len(input)
    init_element = input[0]
    for i in range(1, length//2 + 1):
        if(input[i] != init_element):
            return "balanced"
    return "constant"

def flip_a_coin():
    """generate 1 or 0 at 50/50 probability"""
    return rand.choice([0, 1])
# length of input
n = 16

#repeat it several times (if needed)
repeat = 10

# time it
time_start = time.time()

# the main loop
for i in range(repeat):
    coin = flip_a_coin()
    if (coin == 0):
        map = generate_balanced_map(n, 0)
        print("No.", i + 1, "\ninput: balanced")
    else:
        map = generate_constant_map(n)
        print("No.", i + 1, "\ninput: constant")

    func_type = DJ_classic(map)
    print("output:", func_type)

# result
time_end = time.time()
print("average time", (time_end - time_start)/repeat)