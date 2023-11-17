# Use the official Rust image as the base image
FROM rust:latest

# Install dependencies required for SSH and Git, nginx, and a default JRE for ASCIIDOC
RUN apt-get update && apt-get install -y \
    git \
    nginx \
    asciidoctor

# Install gem for rouge code formatter
RUN gem install rouge

# Install nightly rust toolchain
RUN rustup install nightly

# Create a directory for your Rust application
WORKDIR /workspace

RUN git config --global --add safe.directory /workspace

# Prepare NGINX to serve /aoc-rust
EXPOSE 8080
COPY nginx.conf /etc/nginx/nginx.conf

# Disable host key checking for SSH to avoid known_hosts issues
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config
