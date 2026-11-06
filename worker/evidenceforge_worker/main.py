import logging
import time

from evidenceforge_worker.config import get_settings
from evidenceforge_worker.queue import create_sqs_client, poll_once


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = get_settings()
    client = create_sqs_client(settings)
    queue_url = client.get_queue_url(QueueName=settings.sqs_queue_name)["QueueUrl"]
    while True:
        poll_once(client, queue_url)
        time.sleep(0.25)


if __name__ == "__main__":
    main()
