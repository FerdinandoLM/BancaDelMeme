# Interactive command line tool for performing test calculations for investment return
import math

from formula import calculate

def find_threshold(fixed_b, min_a, max_a, target):
    # print(f"min: {min_a}, max: {max_a}, target: {target}")

    if abs(max_a - min_a) <= 1:
        # print("Reached base case")

        v = calculate(min_a, fixed_b)
        # print(f"v: {v}")

        return min_a

    mid_a = (max_a + min_a) / 2
    # print(f"mid: {mid_a}")

    v = calculate(mid_a, fixed_b)
    # print(f"v: {v}")

    if v < target:
        # print("Below the target - guessing higher")
        return find_threshold(fixed_b, mid_a, max_a, target)
    else:
        # print("Above the target - guessing lower")
        return find_threshold(fixed_b, min_a, mid_a, target)

def main():
    startings = [1, 5, 10, 20, 50]
    limit = 230
    deltas = [2, 5, 10, 20]
    threshs = [1, 1.25, 1.5, 2, 2.5]
    min_n = 0
    max_n = 1000
    print('Inizio | Fine | Totale | Rendimento')
    print('---|---|----|----')
    for starting in startings:
        endings = list([d * starting for d in deltas])
        for t in threshs:
            endings.append(find_threshold(starting, min_n, max_n, t))
        endings = set([int(math.ceil(e)) for e in endings if e and e <= limit])
        endings = sorted(endings)
        for ending in endings:
            ret = calculate(ending, starting)
            print('{:d} | {:d} | {:.2f} | {:+.2f}'.format(starting, ending, ret, ret - 1))


if __name__ == "__main__":
    main()
