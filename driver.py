from check_length_nesting import generate_report
import sys
import os.path

def main():
    
    files = get_files(sys.argv[1])

    for file in files:
        print(f"{file.split('/')[-1].split('.')[0]:8}")
        ll, ls, ld, ds = generate_report(file)
        print(f"{ll:>2} {ls:>5.1f} {ld:>2} {ds:>5.1f}")

    
def get_files(start_path: str) -> list:
    files = []

    for dirpath, _, filenames in os.walk(start_path):
        for filename in [f for f in filenames if f.endswith(".cpp")]:
            files.append(os.path.join(dirpath, filename))

    return files

if __name__ == "__main__":
    main()

