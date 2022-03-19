from check_length import generate_report
import sys
import os.path

def main():
    
    files = get_files(sys.argv[1])

    for file in files:
        print(f"{file.split('/')[-1].split('.')[0]:8} {generate_report(file, 30)[-1]:>5.1f}")
    
def get_files(start_path: str) -> list:
    files = []

    for dirpath, _, filenames in os.walk(start_path):
        for filename in [f for f in filenames if f.endswith(".cpp")]:
            files.append(os.path.join(dirpath, filename))

    return files

if __name__ == "__main__":
    main()

