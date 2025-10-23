#!/bin/bash
# Setup script for Cursor environment with spacetime integration

set -e

echo "🚀 Setting up Cursor environment for minimalist project..."

# Install basic dependencies
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends \
    ca-certificates curl git sudo xz-utils bzip2 locales tmux jq &&
    sudo rm -rf /var/lib/apt/lists/*

# Install Nix
NIX_VERSION=2.29.1
if ! command -v nix &> /dev/null; then
    echo "📦 Installing Nix..."
    curl -fsSL https://releases.nixos.org/nix/nix-${NIX_VERSION}/install | sh -s -- --no-daemon
fi

# Configure Nix
mkdir -p ~/.config/nix
printf "experimental-features = nix-command flakes\naccept-flake-config = true\n" > ~/.config/nix/nix.conf

# Add Nix to PATH in bashrc
if ! grep -Fxq 'PATH=$HOME/.nix-profile/bin:$PATH' ~/.bashrc; then
    echo 'PATH=$HOME/.nix-profile/bin:$PATH' >> ~/.bashrc
fi

# Source Nix
if [ -f ~/.nix-profile/etc/profile.d/nix.sh ]; then
    source ~/.nix-profile/etc/profile.d/nix.sh
fi

# Setup spacetime integration
echo "🌌 Setting up spacetime integration..."
SPACETIME_DIR="${HOME}/spacetime"

if [ ! -d "$SPACETIME_DIR" ]; then
    echo "📥 Cloning spacetime..."
    git clone https://github.com/SullivanXiong/spacetime.git "$SPACETIME_DIR"
    cd "$SPACETIME_DIR"
    chmod +x setup.sh scripts/*
    ./setup.sh
else
    echo "✅ spacetime already installed"
fi

# Load spacetime configuration
if [ -f "$HOME/.config/spacetime/spacetime.rc" ]; then
    source "$HOME/.config/spacetime/spacetime.rc"
fi

echo "✨ Cursor environment setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Restart your terminal or run: source ~/.bashrc"
echo "   2. Run: direnv allow"
echo "   3. Start development: make setup"

