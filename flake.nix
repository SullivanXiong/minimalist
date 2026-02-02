{
  description = "Minimalist Todo App - wxPython + Django";

  inputs = {
    devenv-root = {
      url = "file+file:///dev/null";
      flake = false;
    };
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:cachix/devenv-nixpkgs/rolling";
    nixpkgs-unstable.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    devenv.url = "github:cachix/devenv";
    nix2container.url = "github:nlewo/nix2container";
    nix2container.inputs.nixpkgs.follows = "nixpkgs";
    mk-shell-bin.url = "github:rrbutani/nix-mk-shell-bin";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = inputs@{ flake-parts, devenv-root, ... }:
    flake-parts.lib.mkFlake { inherit inputs; }
      {
        imports = [
          inputs.devenv.flakeModule
        ];

        systems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];

        perSystem = { config, self', inputs', pkgs, system, ... }:
          let
            pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };
            uv = pkgs-unstable.uv;
            python = pkgs.python311;
          in
          {
            formatter = pkgs.nixpkgs-fmt;

            devenv.shells.default = {
              name = "minimalist";

              packages = with pkgs; [
                python
                uv
                gnumake
                pkg-config
              ] ++ pkgs.lib.optionals pkgs.stdenv.isLinux [
                # wxPython build dependencies (Linux only)
                gcc
                gtk3
                webkitgtk_4_1
                glib
                cairo
                pango
              ];

              # Python with uv
              languages.python.enable = true;
              languages.python.package = python;
              languages.python.uv.enable = true;
              languages.python.uv.package = uv;
              languages.python.venv.enable = true;

              # PostgreSQL service
              services.postgres.enable = true;
              services.postgres.package = pkgs.postgresql_15;
              services.postgres.listen_addresses = "localhost";
              services.postgres.port = 5432;
              services.postgres.initialDatabases = [
                { name = "todoapp"; }
              ];

              # Redis service
              services.redis.enable = true;
              services.redis.port = 6379;

              # Git hooks (pre-commit)
              git-hooks.hooks = {
                ruff = {
                  enable = true;
                  args = [ "--fix" ];
                };
                ruff-format = {
                  enable = true;
                };
              };

              enterShell = ''
                echo ""
                echo "Minimalist Todo App Development Environment"
                echo "============================================"
                echo ""
                echo "Services (start with 'devenv up'):"
                echo "  PostgreSQL: localhost:5432 (database: todoapp)"
                echo "  Redis:      localhost:6379"
                echo ""
                echo "Commands:"
                echo "  make setup-server  - Install server dependencies"
                echo "  make setup-client  - Install client dependencies"
                echo "  make dev-server    - Run Django server"
                echo "  make dev-client    - Run wxPython client"
                echo "  make migrate       - Run database migrations"
                echo "  ./format_code.sh   - Format code with ruff"
                echo ""
                echo "Python: $(python --version)"
                echo "uv: $(uv --version)"
              '';
            };
          };

        flake = { };
      };
}
