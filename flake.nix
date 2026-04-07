{
  description = "Minimalist - Linear-inspired project management tool";

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
            # Port configuration: reads from .devenv.local if it exists, then env vars, then defaults
            # Create .devenv.local with: echo '{"postgres_port":5433,"server_port":8080}' > .devenv.local
            localConfig = let
              configPath = builtins.getEnv "PWD" + "/.devenv.local";
              configExists = builtins.pathExists configPath;
              config = if configExists then builtins.fromJSON (builtins.readFile configPath) else {};
            in config;

            # Priority: env var > .devenv.local > default
            postgresPortEnv = builtins.getEnv "POSTGRES_PORT";
            effectivePostgresPort =
              if postgresPortEnv != "" then builtins.fromJSON postgresPortEnv
              else localConfig.postgres_port or 5432;

            serverPortEnv = builtins.getEnv "SERVER_PORT";
            effectiveServerPort =
              if serverPortEnv != "" then builtins.fromJSON serverPortEnv
              else localConfig.server_port or 8000;
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

              # PostgreSQL service (override port: POSTGRES_PORT=5433 direnv reload)
              services.postgres.enable = true;
              services.postgres.package = pkgs.postgresql_15;
              services.postgres.listen_addresses = "localhost";
              services.postgres.port = effectivePostgresPort;
              services.postgres.initialDatabases = [
                { name = "minimalist"; }
              ];

              # Redis service
              services.redis.enable = true;
              services.redis.port = 6379;

              # Export ports as environment variables (Django/client will read these)
              env.DATABASE_PORT = toString effectivePostgresPort;
              env.SERVER_PORT = toString effectiveServerPort;

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
                echo "Minimalist Development Environment"
                echo "============================================"
                echo ""
                echo "Services (start with 'devenv up'):"
                echo "  PostgreSQL: localhost:${toString effectivePostgresPort} (database: minimalist)"
                echo "  Redis:      localhost:6379"
                echo ""
                echo "Commands:"
                echo "  make setup-server              - Install server dependencies"
                echo "  make setup-client              - Install client dependencies"
                echo "  make dev-server                - Run Django server (port ${toString effectiveServerPort})"
                echo "  make dev-client                - Run wxPython client"
                echo "  make migrate                   - Run database migrations"
                echo "  ./format_code.sh               - Format code with ruff"
                echo ""
                echo "To change ports:"
                echo "  make set-ports POSTGRES_PORT=5433 SERVER_PORT=8080"
                echo "  direnv reload  # Run in each terminal"
                echo ""
                echo "Python: $(python --version)"
                echo "uv: $(uv --version)"
              '';
            };
          };

        flake = { };
      };
}
