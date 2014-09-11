Changelog
#########

v0.1a
=====

- API to store resources (data + metadata)
- API to store dataset configuration
- Support for running asynchronous tasks through Celery
- Basic plugin interface, offering functionality to:

  - expose extra API views, using a blueprint
  - expose some "hooks" to extend core / other plugins' functionality
  - expose celery-powered asynchronous tasks
