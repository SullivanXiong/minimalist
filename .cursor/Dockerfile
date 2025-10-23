# ubuntu-nix.dockerfile
FROM ubuntu:22.04

# Allow up to ~3 days of future-dated repo metadata and ignore 'Valid-Until'
# (the latter helps in CI where cache mirrors sometimes serve stale metadata)
RUN printf 'Acquire::Max-FutureTime "259200";\nAcquire::Check-Valid-Until "false";\n' \
      > /etc/apt/apt.conf.d/99-time-skew

# Minimal tools for headless dev + Nix install
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
      ca-certificates curl git sudo xz-utils bzip2 locales tmux && \
    rm -rf /var/lib/apt/lists/*

# (optional) sane locale
RUN locale-gen en_US.UTF-8 || true
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Create non-root user (Postgres won't init as root)
RUN useradd -m -u 1000 -s /bin/bash dev && \
    echo "dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dev

USER dev
ENV USER=dev HOME=/home/dev SHELL=/bin/bash

# Install Nix in single-user mode (no systemd needed in container)
ARG NIX_VERSION=2.29.1
RUN bash -lc 'curl -fsSL https://releases.nixos.org/nix/nix-${NIX_VERSION}/install | sh -s -- --no-daemon'

# Make Nix available in non-login shells and enable flakes
ENV PATH=/home/dev/.nix-profile/bin:$PATH

# Install nix-direnv for automatic environment loading
RUN nix-env -iA nixpkgs.direnv nixpkgs.nix-direnv

RUN mkdir -p /home/dev/.config/nix && \
    printf "experimental-features = nix-command flakes\naccept-flake-config = true\n" \
      > /home/dev/.config/nix/nix.conf

WORKDIR /home/dev/workspace

RUN mkdir -p /home/dev/workspace/.devenv/root
RUN direnv allow /home/dev/workspace || true

CMD ["bash"]

