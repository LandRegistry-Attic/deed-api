import logging
import requests
import uuid

from kombu import Connection, Exchange, Producer, Queue
from kombu.mixins import ConsumerMixin

logger = logging.getLogger("esec-signing")


DEFAULT_PORT = 5672
DEFAULT_VHOST = '/'
BROKER_URL_TEMPLATE = 'amqp://{userid}:{password}@{hostname}:{port}/{virtual_host}'


def broker_url(hostname, userid, password, port=DEFAULT_PORT, virtual_host=DEFAULT_VHOST):
    """Build an AMQP URL from the supplied parameters."""
    return BROKER_URL_TEMPLATE.format(**locals())


class Worker(ConsumerMixin):

    def __init__(self, connection, queues, process_message_func=None):
        self.connection = connection
        self.queues = queues
        logger.info("Worker created")
        self.process_message_func = process_message_func

    def get_consumers(self, Consumer, channel):
        logger.debug("Getting consumers")
        return [Consumer(queues=self.queues,
                         accept=["json"],
                         callbacks=[self.handle_message])]

    def on_connection_error(self, ex, interval):  # pragma: nocover
        logger.error('Connection error ({}s since broken): {} {}'.format(
            interval, ex.__class__.__name__, ex))

    def on_connection_revived(self):  # pragma: nocover
        """Called when connection revived (e.g. after a heartbeat timeout)."""
        logger.info('Connection revived')

    def on_iteration(self, *args, **kwargs):  # pragma: nocover
        """Called on each iteration."""

    def on_decode_error(self, message, exc):
        raise

    def handle_message(self, body, message):
        # Using LoggingAdapter to add extra contextual information to processing the
        # message i.e. the X-Trace-ID that is added to the header (generating it if not provided)
        trace_id = message.headers.get("X-Trace-ID", uuid.uuid4().hex)
        logger_adapter = logging.LoggerAdapter(logger, {"trace_id": trace_id})
        # We also create a new requests object for the app to use with the header
        # pre-set, so other APIs will receive it.
        new_requests = requests.Session()
        new_requests.headers.update({'X-Trace-ID': trace_id})

        logger_adapter.debug("Handling message")
        if self.process_message_func:
            self.process_message_func(body, message, logger_adapter, new_requests)
        logger_adapter.debug("Message handled")


class Emitter(object):

    """Helper class for writing robust AMQP producers.

    An instance of this class will connect to the given AMQP broker,
    and allow you to send messages to an exchange on that broker with
    a given routing key, optionally also declaring a queue and and
    binding it to the exchange with that routing key.  Upon connection
    errors (either upon initial connection or message send) it will
    retry several times before giving up, and if a connection is
    interrupted it will recover gracefully on the next attempt to send
    a message.

    Short-lived connections
    -----------------------

    To create a short-lived connection which automatically
    releases/disconnects when you've finished, just use an instance of
    this class as a context manager; for example::

        url = broker_url('guest', 'guest', 'localhost')
        with Emitter(url, 'ex_name', 'key') as emitter:
            emitter.send_message({'status': 'success'}, serializer='json')

    Note the lack of any explicit `connect()` call here:
    `send_message()` calls it if it hasn't been called already, so you
    never need to call it explicitly (though you can).

    Note also the lack of any queue_name parameter in the Emitter
    constructor call: the message will be sent to the given exchange
    with the given routing key, but no queue declaration/binding takes
    place here (compare with the next example).

    Long-lived connections
    ----------------------

    Alternatively, you can just create an instance of this class and
    have it live for as long as you need it, in which case the
    connection will remain open until the instance falls out of scope
    or you call its `release()` method.

    To have an instance live for the lifetime of an application, a
    helpful pattern is to put it in a module-level global and lazily
    declare it on first use, e.g.::

        # Module-level global for the instance; initially nothing here.
        _emitter = None

        def send_message(msg, serializer):
            global _emitter
            if _emitter is None:
                url = broker_url('guest', 'guest', 'localhost')
                _emitter = Emitter(url, 'ex_name', 'key', 'q_name')
            _emitter.send_message(msg, serializer)

    Then you can just call this module's `send_message()` function
    whenever you need to send a message: it will connect to the broker
    on the first call, keep the connection open between calls, and
    attempt to reconnect on the next call if the connection ever goes
    away.

    Note also that in this example we do pass a queue_name to the
    Emitter constructor: upon connection, the Emitter will ensure that
    the named queue is declared, and bound to the given exchange with
    the given routing key.

    Customisation via subclassing
    -----------------------------

    You may wish to use a custom subclass to override certain
    behaviour around error handling.  In particular, you can override:

    * Various `CONN_*` and `SEND_*` class variables, which control
      connection/send retry behaviour.  E.g. `SEND_MAX_RETRIES`
      defines how many times to retry sending a message before giving
      up.

    * The `conn_errback()` callback method, which is called upon an
      error while connecting.

    * The `send_errback()` callback method, which is called upon an
      error while sending a message.

    * The `errback()` callback method, which (by default) is just what
      `conn_errback()` and `send_errback()` call - so override just this
      to change them both.  The default version just logs the error.

    For example, here's a class which retries connecting forever;
    waits up to 10 seconds between retries; only retries message sends
    once; and logs the full traceback for connect errors::

        class CustomEmitter(Emitter):

            CONN_MAX_RETRIES = None
            CONN_INTERVAL_MAX = 10
            SEND_MAX_RETRIES = 1

            def conn_errback(self, ex, interval):
                logger.error('Error: %r', ex, exc_info=1)
                logger.info('Retry in %s seconds.', interval)

    Note the following edge cases for `*_MAX_RETRIES`:

    * `None` - for both `CONN_` and `SEND_` this means "try forever".

    * 0 - for `CONN_` this means "try forever" but for `SEND_` this
      means "retry once", i.e. the same as `SEND_MAX_RETRIES = 1`;
      this seems to be a kombu bug.

    * Negative values - for `CONN_` this means "just try once/no
      retries", but for `SEND_` it just breaks things (it will never
      recover the connection); this seems to be a kombu bug.

    """

    CONN_MAX_RETRIES = 2     # Max retries when attempting to connect.
    CONN_INTERVAL_START = 2  # Seconds to wait between connect retries, initially.
    CONN_INTERVAL_STEP = 2   # Increase time between connect retries by this amount.
    CONN_INTERVAL_MAX = 4    # Maximum time between connect retries.

    SEND_MAX_RETRIES = 3     # Max retries when attempting to send.
    SEND_INTERVAL_START = 1  # Seconds to wait between send retries, initially.
    SEND_INTERVAL_STEP = 1   # Increase time between send retries by this amount.
    SEND_INTERVAL_MAX = 1    # Maximum time between send retries.

    def __init__(self, url, exchange_name, routing_key, queue_name=None, exchange_type='direct'):
        logger.debug('Initialising {}'.format(self.__class__.__name__))
        self.url = url
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.queue_name = queue_name
        self.exchange_type = exchange_type
        self._connection = None
        self._producer = None

    def conn_errback(self, ex, interval):
        """Callback called upon connection error."""
        self.errback(ex, interval)

    def send_errback(self, ex, interval):
        """Callback called upon send error."""
        self.errback(ex, interval)

    def errback(self, ex, interval):
        """Default callback called upon connection or send error."""
        logger.info('Error: {} - {}'.format(ex.__class__.__name__, str(ex)))
        logger.info('Retry in %s seconds.', interval)

    def connect(self):

        """Connect to broker and possibly ensure exchange/queue/routing declared.

        In case of errors, this will retry connecting several times
        (controlled by the `CONN_*` class variables), and gracefully
        recover if possible.

        If it never succeeds, the exception raised by the final
        attempt is re-raised.

        """

        logger.debug('Connecting to broker at: {}'.format(self.url))
        self._connection = Connection(self.url)

        # Kombu interprets interval_max incorrectly; work around that.
        interval_max = self.CONN_INTERVAL_MAX - self.CONN_INTERVAL_STEP
        self._connection.ensure_connection(
            errback=self.conn_errback,
            max_retries=self.CONN_MAX_RETRIES,
            interval_start=self.CONN_INTERVAL_START,
            interval_step=self.CONN_INTERVAL_STEP,
            interval_max=interval_max)

        exchange = Exchange(name=self.exchange_name, type=self.exchange_type)
        channel = self._connection.channel()
        self._producer = Producer(channel=channel, exchange=exchange, routing_key=self.routing_key)

        if self.queue_name:
            # Bind/declare queue.
            queue = Queue(name=self.queue_name, exchange=exchange, routing_key=self.routing_key)
            queue = queue(channel)  # Bind queue
            logger.debug('Declaring queue {}, on exchange {} at {}'.format(
                self.queue_name, self.exchange_name, self.url))
            queue.declare()

    def release(self):
        """Disconnect/release."""
        self._producer.release()
        self._connection.release()

    def __enter__(self):
        """Context manager entry: connect to the broker."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: disconnect/release."""
        self.release()

    def send_message(self, message, serializer='json', headers=None):

        """Send a message with retries (and connect to broker if necessary).

        In case of errors, this will retry sending several times
        (controlled by the `SEND_*` class variables), and gracefully
        recover if possible.

        If it never succeeds, the exception raised by the final
        attempt is re-raised.

        You can use the headers argument to pass in any custom headers. It
        is a dictionary {"a-custom-header": "a-custom-value"}.

        """

        logger.debug("Sending message...")

        if self._producer is None:
            self.connect()

        # Kombu interprets interval_max incorrectly; work around that.
        interval_max = self.SEND_INTERVAL_MAX - self.SEND_INTERVAL_STEP

        publish = self._connection.ensure(
            self._producer,
            self._producer.publish,
            errback=self.send_errback,
            max_retries=self.SEND_MAX_RETRIES,
            interval_start=self.SEND_INTERVAL_START,
            interval_step=self.SEND_INTERVAL_STEP,
            interval_max=interval_max)

        publish(message, serializer=serializer, headers=headers)


def publish_message(message, rabbit_url, exchange_name, routing_key, queue_name=None, exchange_type='direct', serializer="json", headers=None):
    """Convenience wrapper for sending a single message."""
    with Emitter(rabbit_url, exchange_name, routing_key, queue_name, exchange_type=exchange_type) as emitter:
        emitter.send_message(message, serializer, headers=headers)


def get_queue_count(rabbit_url, queue_name):
    with Connection(rabbit_url, heartbeat=4) as conn:
        channel = conn.channel()

        try:
            name, message_count, consumer_count = channel.queue_declare(queue=queue_name, passive=True)
        finally:
            channel.close()

        return message_count
