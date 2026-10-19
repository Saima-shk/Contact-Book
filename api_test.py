
import requests

url = "https://jsonplaceholder.typicode.com/users"

try:
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        users = response.json()

        print("API connected successfully!")
        print("Total users:", len(users))

        for user in users[:5]:
            print(user["name"], "-", user["email"])
    else:
        print("API Error:", response.status_code)

except requests.RequestException as error:
    print("Connection failed:", error)
