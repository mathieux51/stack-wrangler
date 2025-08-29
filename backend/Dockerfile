FROM rust:1.75

WORKDIR /app

RUN cargo install cargo-watch

COPY Cargo.toml ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo fetch
RUN rm -rf src

COPY . .

EXPOSE 8000

CMD ["cargo", "watch", "-x", "run"]