{
  description = "wxPython Django Todo App Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python and package management
            python311
            uv
            
            # PostgreSQL
            postgresql_15
            
            # Redis for Django Channels
            redis
            
            # Build tools
            gnumake
            gcc
            pkg-config
            
            # wxPython dependencies (Linux)
            gtk3
            webkitgtk
            glib
            cairo
            pango
            
            # Docker for production builds
            docker
            docker-compose
          ];

          shellHook = ''
            echo "wxPython Django Todo App Development Environment"
            echo "================================================"
            echo "Available commands:"
            echo "  make setup        - Initial project setup"
            echo "  make dev-server   - Run Django server"
            echo "  make dev-client   - Run wxPython client"
            echo "  make migrate      - Run database migrations"
            echo "  make services-up  - Start PostgreSQL and Redis"
            echo ""
            echo "Python version: $(python --version)"
            echo "uv version: $(uv --version)"
          '';
        };
      }
    );
}





