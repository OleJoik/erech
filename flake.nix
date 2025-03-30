{
  inputs = {
    nixpkgs.url = "github:cachix/devenv-nixpkgs/rolling";
    devenv.url = "github:cachix/devenv";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = { self, nixpkgs, devenv, ... } @ inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;
    in
    {
      devShells.${system}.default = devenv.lib.mkShell {
        inherit inputs pkgs;
        modules = [
          ({ pkgs, config, lib, ... }: {
            packages = [
              pkgs.uv
            ];

            languages.python = {
              enable = true;
              package = python;
            };

            env.LD_LIBRARY_PATH = lib.makeLibraryPath [
              pkgs.ruff-lsp
            ];

            scripts = {
              test-watch = {
                description = "Runs unit test in watch mode";
                exec = "ptw . --runner pytest tests -vv";
              };

              hh = {
                exec = ''
                  echo "Welcome to the tikkn devenv!"
                  echo 🦾 Helper scripts you can run to make your development richer:
                  echo 🦾
                  ${pkgs.gnused}/bin/sed -e 's| |••|g' -e 's|=| |' <<EOF | ${pkgs.util-linuxMinimal}/bin/column -t | ${pkgs.gnused}/bin/sed -e 's|^|🦾 |' -e 's|••| |g'
                  ${lib.generators.toKeyValue {} (lib.mapAttrs (name: value: value.description) config.scripts)}
                  EOF
                  echo
                '';
                description = "Get help for nix scripts or whatever";
              };
            };

            enterShell = ''
                hh
              '';

          })
        ];
      };
    };
}
