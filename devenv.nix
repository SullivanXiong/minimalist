{ pkgs, ... }:

{
  # https://devenv.sh/basics/
  env.GREET = "wxPython Django Todo App";
  env.PROJECT_NAME = "minimalist";

  # https://devenv.sh/packages/
  packages = with pkgs; [
    git
    gnumake
    uv
    jq
  ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    version = "3.11";
    uv.enable = true;
  };

  # https://devenv.sh/services/
  services.postgres = {
    enable = true;
    package = pkgs.postgresql_15;
    initialDatabases = [
      { name = "todoapp"; }
    ];
    listen_addresses = "127.0.0.1";
    port = 5432;
  };

  services.redis = {
    enable = true;
    port = 6379;
  };

  # https://devenv.sh/scripts/
  scripts.hello.exec = ''
    echo "Welcome to $GREET development environment!"
    echo "Run 'make setup' to initialize the project."
  '';

  enterShell = ''
    # Load spacetime configuration if available
    if [ -f "$HOME/.config/spacetime/spacetime.rc" ]; then
      source "$HOME/.config/spacetime/spacetime.rc"
    fi
    
    # Load project-specific spacetime config
    if [ -f "$PWD/.spacetime" ]; then
      source "$PWD/.spacetime"
    fi
    
    hello
  '';

  # https://devenv.sh/pre-commit-hooks/
  pre-commit.hooks = {
    black.enable = true;
    flake8.enable = true;
  };
}





