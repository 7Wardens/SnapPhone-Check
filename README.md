# SnapChat Phone Checker

Check if a phone number is linked to a SnapChat account

## Installation

Install via pip:

    github https://github.com/7Wardens/SnapPhone-Check.git



## Usage

```python3 snapchat_checker.py [-h] -l filepath [-p proxies_path] [-t threads]```

The combolist must be in the following format:

```phone_number:country_code```

Example of combolist numbers:

```
7140000000:US
4430000000:US
8080000000:US
8500000000:US
```

Example output:
![Code Execution Video Sample](https://github.com/7Wardens/SnapPhone-Check/blob/master/VideoExample/exec_example.gif)

#### Notes
- If you constantly get ```'[phone_number]' is invalid - Check the phone number and country code```, it is NOT a code error. Each country has certain formats and rules. For example, US does not allow a 0 or 1 after the area-code.

- There is the posibility of a bug when using proxies and too many threads. Because the way threads are handled, if there are more threads than proxies the request will be made with no proxy. Also, if a thread does not have an available proxy to change into when a request fails it may cause an error. 
    - It is recommended to have at least double the amount of threads as proxies



<sub><sup><sub>**DISCLAIMER**: This code was created for educational purposes ONLY. Only use the code on targets who have given permission. The author is not responsible for any malicious use. </sub></sup></sub>
