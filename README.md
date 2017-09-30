# easy_mail
Easy mail sending using Python3

## Installation
```zsh
$> cd <your_folder>
$> git clone https://github.com/pBouillon/easy_mail.git
$> cd easy_mail
$> python3 setup.py install
```

## Usage


### Without configuration file

From your program, do the following:
```python
import easy_mail
from easy_mail import Email

if __name__ == '__main__':
    header  = 'My mail header'
    message = 'This is my mail, sent with Python'

    mail = Email('sender@mail.com', 'receiver@mail.com')
    mail.prepare(header, message[, type])
    mail.send('smtp.server.addr', 'login@mail.com', 'password')
```

### With a configuration file
Define all fields in a `.json` file:
```json
{
    "header"  : "Python3 mail",
    "content" : "This mail is sent with Python3",
    "type"    : "plain",

    "login"     : "",
    "password"  : "",
    "smtp_addr" : "",

    "receiver": "",
    "sender"  : ""
}
```
Then, just use the class method `send_from_source_file(<path>)` and specify the path as:
```python
import easy_mail
from easy_mail import Email

if __name__ == '__main__':
    Email.send_from_source_file('my/custom/path/myfile.json')
```

## Other
* `README.md` made with the help of [this website](https://jbt.github.io/markdown-editor/)
* `setup.py` made with the help of [this repository](https://github.com/kennethreitz/setup.py)

Contributions are welcome