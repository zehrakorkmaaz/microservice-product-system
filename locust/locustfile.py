from locust import HttpUser, task, between


class MicroserviceUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.admin_token = None
        self.user_token = None

        admin_login_response = self.client.post(
            "/auth/login",
            json={
                "username": "admin",
                "password": "1234"
            }
        )

        if admin_login_response.status_code == 200:
            self.admin_token = admin_login_response.json().get("token")

        user_login_response = self.client.post(
            "/auth/login",
            json={
                "username": "zehra",
                "password": "1234"
            }
        )

        if user_login_response.status_code == 200:
            self.user_token = user_login_response.json().get("token")

    @task(4)
    def list_products(self):
        if self.user_token:
            self.client.get(
                "/products",
                headers={
                    "Authorization": f"Bearer {self.user_token}"
                }
            )

    @task(2)
    def create_order(self):
        if self.user_token:
            self.client.post(
                "/orders",
                json={
                    "product_name": "Laptop",
                    "quantity": 1
                },
                headers={
                    "Authorization": f"Bearer {self.user_token}"
                }
            )

    @task(1)
    def create_product_as_admin(self):
        if self.admin_token:
            self.client.post(
                "/products",
                json={
                    "name": "Test Product",
                    "price": 999
                },
                headers={
                    "Authorization": f"Bearer {self.admin_token}"
                }
            )