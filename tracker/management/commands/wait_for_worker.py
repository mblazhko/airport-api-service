import subprocess
import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Wait for Celery worker to be ready"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE("Waiting for Celery worker to be ready...")
        )

        while True:
            result = subprocess.run(
                ["celery", "-A", "airport_api_service", "inspect", "ping"],
                capture_output=True,
            )
            if result.returncode == 0:
                break
            time.sleep(2)

        self.stdout.write(self.style.SUCCESS("Celery worker is ready!"))
