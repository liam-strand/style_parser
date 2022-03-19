from check_length import generate_report
import sys

if __name__ == "__main__":
    print(f"{sys.argv[1].split('/')[-1].split('.')[0]:8} {generate_report(sys.argv[1], 30)[-1]:>5.1f}")
