import pika
import sys

def test_rabbitmq_connection():
    try:
        # Establish connection
        credentials = pika.PlainCredentials('Fairweather', 'test1234')
        parameters = pika.ConnectionParameters(
            '127.0.0.1',
            5672,
            'cherry_broker',
            credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Try to declare a test queue (this will verify permissions)
        channel.queue_declare(queue='test_queue', durable=True)
        
        # Try to publish a message
        channel.basic_publish(
            exchange='',
            routing_key='test_queue',
            body='Hello World!'
        )
        
        print("✅ Successfully connected to RabbitMQ!")
        print("✅ Successfully created queue!")
        print("✅ Successfully published message!")
        
        # Try to receive the message
        method_frame, header_frame, body = channel.basic_get('test_queue')
        if method_frame:
            print(f"✅ Successfully received message: {body.decode()}")
            channel.basic_ack(method_frame.delivery_tag)
        
        # Clean up
        channel.queue_delete(queue='test_queue')
        connection.close()
        print("✅ Successfully cleaned up resources!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing RabbitMQ connection...")
    success = test_rabbitmq_connection()
    if success:
        print("\n🎉 All tests passed! RabbitMQ is configured correctly!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Please check your RabbitMQ configuration.")
        sys.exit(1)