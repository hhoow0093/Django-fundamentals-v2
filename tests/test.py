from django.test import TestCase


class TestHelloWorld(TestCase):
    def test_hello(self) -> None:
        hello = "Hello world!"
        self.assertCountEqual(hello, "Hello world!")
