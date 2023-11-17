#!/bin/sh

# start web server
nginx

# Execute the main command (e.g., your Rust application)
exec "$@"
