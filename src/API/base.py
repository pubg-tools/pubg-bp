import requests



base_url = "http://127.0.0.1:18081"


# 发起请求
def QtRequest(url, method="GET", data=None):
    """
    发起请求。

    Args:
        url (str): 请求的url。
        method (str, optional): 请求的方法，默认为"GET"。
        data (dict, optional): 请求的数据，默认为None。

    Returns:
        tuple: 包含状态码和数据的元组。

    """
    match method:
        case "GET":
            response = requests.get(base_url + url)
        case "POST":
            response = requests.post(base_url + url, json=data)
        case "PUT":
            response = requests.put(base_url + url, data)
        case "DELETE":
            response = requests.delete(base_url + url)
        case "PATCH":
            response = requests.patch(base_url + url, data)
        case _:
            return 404, "Not Found"
    return response.status_code, response.json()
