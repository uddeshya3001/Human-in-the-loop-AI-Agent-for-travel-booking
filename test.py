def is_armstrong(n: int) -> bool:
    """Return True if n is an Armstrong number."""
    if n < 0:
        return False
    digits = str(n)
    power = len(digits)
    return sum(int(d) ** power for d in digits) == n


if __name__ == "__main__":
    try:
        num = int(input("Enter a non-negative integer: ").strip())
    except ValueError:
        print("Invalid input: please enter an integer.")
    else:
        if is_armstrong(num):
            print(f"{num} is an Armstrong number.")
        else:
            print(f"{num} is not an Armstrong number.")
