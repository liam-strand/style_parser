from check_length_nesting import generate_report
import termcolor as tc
import sys
import os.path

def main():
    
    files = get_files(sys.argv[1])

    print("name       long_fns  deep_fns")
    print("-----------------------------")

    for file in files:
        name = file.split('/')[-2]
        ll, ls, ld, ds = generate_report(file)
        print(f"{name:<10}", end=" ") 
        if ll == 0:
            print(f"{ll:>2} {ls:>5.1f}", end=" ")
        else:
            tc.cprint(f"{ll:>2} {ls:>5.1f}", "red", attrs=["bold"], end=" ")
        
        if ld == 0:
            print(f"{ld:>2} {ds:>5.1f}")
        else:
            tc.cprint(f"{ld:>2} {ds:>5.1f}", "red", attrs=["bold"])

    
def get_files(start_path: str) -> list:
    files = []

    for dirpath, _, filenames in os.walk(start_path):
        for filename in [f for f in filenames if f.endswith(".cpp")]:
            files.append(os.path.join(dirpath, filename))

    return files

if __name__ == "__main__":
    main()

