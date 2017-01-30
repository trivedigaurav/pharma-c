import requests

def send_notification(title, message, push_url, url_title):
    url = "https://api.pushover.net/1/messages.json"
    
    token = "[TOKEN]"
    user = "[USER]"

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"token\"\r\n\r\n" + token + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"user\"\r\n\r\n" + user + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"device\"\r\n\r\nsamsung-sm-g900a\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"title\"\r\n\r\n" + title + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"message\"\r\n\r\n" + message +"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"url\"\r\n\r\n" + push_url + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"url_title\"\r\n\r\n" + url_title + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"html\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'postman-token': "751f89cd-3c03-9f47-7410-8214a17e8a88"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    # print(response.text)

if __name__ == "__main__":
    #Send test
    send_notification( "Title", "Python Message <a href=\"http://pharma_c.me/test\"> Test </a>", "http://pharma_c.me/", "Test action")
