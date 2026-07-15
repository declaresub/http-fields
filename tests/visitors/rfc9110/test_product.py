from http_headers.visitors.rfc9110.product import Product


def test_product_str():
    product = Product("Mozilla", "5.0")
    assert str(product) == "Mozilla/5.0"
