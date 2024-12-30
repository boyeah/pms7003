from pms7003.test_utils.loopback import read

max_failures = 3

if __name__ == "__main__":
    read("/dev/ttyAMA0", max_failures=max_failures)
