# 🌌 KubuVerse

KubuVerse is an **AI-native, blockchain-ready, cloud-first ecosystem** for building scalable and decentralized applications. It brings together FastAPI, Rust/WASM, Dart/JavaScript, PostgreSQL, and Kubernetes-oriented tooling.

## Highlights

- AI-powered tooling and CI/CD automation
- Blockchain and Rust/WASM experimentation
- Kubernetes-oriented deployment tooling
- Multilingual development across Python, Rust, Dart, and JavaScript

## Documentation

Read the [full KubuVerse documentation and architecture overview](docs/full_README.md).

## Quickstart

Clone this repository and inspect the available Compose configuration before starting the stack:

```sh
git clone https://github.com/auraecosystem/Kubuverse.git
cd Kubuverse
docker compose -f Docker-compose.yml config
docker compose -f Docker-compose.yml up --build
```

The Compose validation command checks the configuration before containers are started. Review required environment variables and service prerequisites in the documentation.

---

Built by the KubuVerse project maintainers.
