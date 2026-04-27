from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from taxi.models import Manufacturer, Car


MANUFACTURER_LIST_URL = reverse("taxi:manufacturer-list")
DRIVER_LIST_URL = reverse("taxi:driver-list")
CAR_LIST_URL = reverse("taxi:car-list")


class PublicManufacturerTests(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(MANUFACTURER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateManufacturerTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="test1234"
        )
        self.client.force_login(self.user)

    def test_retrieve_manufacturer(self):
        Manufacturer.objects.create(
            name="BAIC",
            country="China"
        )
        Manufacturer.objects.create(
            name="BMW",
            country="Germany"
        )
        response = self.client.get(MANUFACTURER_LIST_URL)
        self.assertEqual(response.status_code, 200)

        manufacturers = Manufacturer.objects.all()
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(manufacturers)
        )
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")

    def test_manufacturer_create(self):
        form_data = {
            "name": "BMW",
            "country": "Germany"
        }
        self.client.post(reverse("taxi:manufacturer-create"), data=form_data)
        new_manufacturer = Manufacturer.objects.get(name=form_data["name"])

        self.assertEqual(
            new_manufacturer.name,
            form_data["name"]
        )
        self.assertEqual(
            new_manufacturer.country,
            form_data["country"]
        )


class PublicDriverTests(TestCase):
    def test_login_required(self):
        response = self.client.get(DRIVER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateDriverTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="test1234"
        )
        self.client.force_login(self.user)

    def test_retrieve_driver(self):
        get_user_model().objects.create_user(
            username="username1",
            password="test1234",
            first_name="test_first_name",
            last_name="test_last_name",
            license_number="test_licence",
        )
        get_user_model().objects.create_user(
            username="username2",
            password="test12345",
            first_name="driver_first_name",
            last_name="driver_last_name",
            license_number="test_licence123",
        )
        response = self.client.get(DRIVER_LIST_URL)
        self.assertEqual(response.status_code, 200)

        drivers = get_user_model().objects.all()
        self.assertEqual(
            list(response.context["driver_list"]),
            list(drivers)
        )
        self.assertTemplateUsed(response, "taxi/driver_list.html")

    def test_create_driver(self):
        form_data = {
            "username": "new_user",
            "password1": "user12pass",
            "password2": "user12pass",
            "first_name": "Test frist name",
            "last_name": "Test last name",
            "license_number": "AFS12441"
        }
        self.client.post(reverse("taxi:driver-create"), data=form_data)
        new_user = get_user_model().objects.get(username=form_data["username"])

        self.assertEqual(new_user.first_name, form_data["first_name"])
        self.assertEqual(new_user.last_name, form_data["last_name"])
        self.assertEqual(new_user.license_number, form_data["license_number"])


class PublicCarTests(TestCase):
    def test_login_required(self):
        response = self.client.get(CAR_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateCarTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="test1234"
        )
        self.client.force_login(self.user)

        self.manufacturer = Manufacturer.objects.create(
            name="Mitsubishi",
            country="Japan"
        )

    def test_retrieve_car(self):
        Car.objects.create(
            model="Mitsubishi Lancer",
            manufacturer=self.manufacturer
        )
        Car.objects.create(
            model="Mitsubishi Eclipse",
            manufacturer=self.manufacturer
        )
        response = self.client.get(CAR_LIST_URL)
        self.assertEqual(response.status_code, 200)

        cars = Car.objects.all()
        self.assertEqual(
            list(response.context["car_list"]),
            list(cars)
        )
        self.assertTemplateUsed(response, "taxi/car_list.html")

    def test_car_create(self):
        driver = get_user_model().objects.create_user(
            username="username1",
            password="test1234",
            first_name="test_first_name",
            last_name="test_last_name",
            license_number="test_licence",
        )
        form_data = {
            "model": "Mitsubishi Eclipse",
            "manufacturer": self.manufacturer.id,
            "drivers": [driver.id]
        }
        self.client.post(reverse("taxi:car-create"), data=form_data)
        new_car = Car.objects.get(model=form_data["model"])

        self.assertEqual(
            new_car.model,
            form_data["model"]
        )
        self.assertEqual(
            new_car.manufacturer.id,
            form_data["manufacturer"]
        )
        self.assertEqual(new_car.drivers.count(), 1)
        self.assertIn(driver, new_car.drivers.all())
