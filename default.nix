{ pkgs ? import <nokxpkgs> { }, tag ? "dev" }:

let
  packageOverrides = python-self: python-super: {
    speedo_client = python-super.speedo_client.overrideAttrs (oldAttrs: rec {
      src = ./.; # pkgs.nix-gitignore.gitignoreSource [ ".git" ] ./.;
      propagatedBuildInputs = oldAttrs.propagatedBuildInputs
        ++ (with python-self; [ mock ]);
    });
    speedo = python-super.speedo.overrideAttrs (oldAttrs: rec {
      version = "local";
      pname = "${oldAttrs.pname}-${version}";
      src = ./.; # pkgs.nix-gitignore.gitignoreSource [ ".git" ] ./.;
      propagatedBuildInputs = oldAttrs.propagatedBuildInputs
        ++ (with python-self; [
          # psycopg2 and alembic are used for the docker postgresql migration
          psycopg2
          alembic
          uvicorn
          # additional speedo server packages comes here
          # prometheus_client fastapi alembic sqlalchemy-utils
        ]);
    });
    dev = python-self.speedo.overrideAttrs (oldAttrs: rec {
      version = "dev";
      pname = "${oldAttrs.pname}-${version}";
      src = pkgs.nix-gitignore.gitignoreSource [ ".git" ] ./.;
      nativeBuildInputs = (with pkgs; [ less cacert git curl postgresql ]);
      propagatedBuildInputs = oldAttrs.propagatedBuildInputs
        ++ python-self.speedo_client.propagatedBuildInputs
        ++ (with python-super; [
          pip
          black
          mypy
          pylint
          flake8
          pytest
          pytestcov
          sphinx
        ]);
      propagatedNativeBuildInputs = (with python-super; [
        pip
        black
        mypy
        pylint
        flake8
        pytest
        pytestcov
        sphinx
        uvicorn
        alembic
      ]);
    });
  };

  python3 = pkgs.python3.override (old: {
    packageOverrides =
      pkgs.stdenv.lib.composeExtensions (old.packageOverrides or (_: _: { }))
      packageOverrides;
  });

  python3Packages = python3.pkgs;

  speedo = python3Packages.speedo;
  dev = python3Packages.dev;

  speedo-docker-image = pkgs.dockerTools.buildLayeredImage {
    inherit tag;
    name = "speedo";
    created = "now";
    contents = [ speedo ];
    config = {
      Cmd = [ "speedo" ];
      Env = [ "SPEEDO_ALEMBIC=ENABLED" ];
      ExposedPorts = { "8000" = { }; };
    };
  };

in pkgs // { inherit python3 python3Packages dev speedo-docker-image; }
