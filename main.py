import sys
from backup_app import CLI

def main():
    if len(sys.argv) == 1:
        sys.argv.append('run')
    CLI()
    
if __name__ == '__main__':
    main()