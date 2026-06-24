from locust import HttpUser, task, between

class LoadBalancerUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(1)
    def test_round_robin(self):
        self.client.get("/rr")

    @task(1)
    def test_least_connections(self):
        self.client.get("/lc")