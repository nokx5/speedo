{ pkgs ? import <nokxpkgs> { }, tag ? "dev" }:

let
  packageOverrides = python-self: python-super: {
    speedo_client = python-super.speedo_client.overrideAttrs (oldAttrs: rec {
      src = ./.;
      propagatedBuildInputs = oldAttrs.propagatedBuildInputs
        ++ (with python-self; [ mock ]);
    });
    speedo = python-super.speedo.overrideAttrs (oldAttrs: rec {
      version = "local";
      pname = "${oldAttrs.pname}-${version}";
      src = ./.;
      propagatedBuildInputs = oldAttrs.propagatedBuildInputs
        ++ (with python-self;
          [
            # psycopg2 is used for the docker postgresql migration
            psycopg2
          ]);
    });
    speedo_full = python-super.speedo.overrideAttrs (oldAttrs: rec {
      nativeBuildInputs = (with pkgs; [ curl postgresql ]);
      propagatedBuildInputs = oldAttrs.propagatedBuildInputs
        ++ python-self.speedo_client.propagatedBuildInputs
        ++ (with python-self; [ sphinx ]);
      propagatedNativeBuildInputs = (with python-self; [ sphinx ]);
    });
    dev = python-self.speedo_full.overrideAttrs (oldAttrs: rec {
      nativeBuildInputs = (with pkgs; [ cacert git less ]);
      propagatedBuildInputs = oldAttrs.propagatedBuildInputs
        ++ (with python-self; [
          pip
          black
          mypy
          pylint
          flake8
          pytest
          pytestcov
          sphinx
        ]);
      propagatedNativeBuildInputs = (with python-self; [
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
      shellHook = ''
                export SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt
            	export PYTHONPATH=$PWD:$PYTHONPATH
        	echo ""
        	echo "You may be interested in the SQL queries :"
                echo "export DEBUG_SPEEDO_SQL=ENABLED"
        	echo ""
            '';
    });
  };

  python3 = pkgs.python3.override (old: {
    packageOverrides =
      pkgs.lib.composeExtensions (old.packageOverrides or (_: _: { }))
      packageOverrides;
  });

  python3Packages = python3.pkgs;
  dev = python3Packages.dev;

  speedo-docker-image = pkgs.dockerTools.buildLayeredImage {
    inherit tag;
    name = "speedo";
    created = "now";
    contents = [ python3Packages.speedo ];
    config = {
      Cmd = [ "speedo" ];
      Env = [ "SPEEDO_ALEMBIC=ENABLED" ];
      ExposedPorts = { "8000" = { }; };
    };
  };

in pkgs // { inherit python3 python3Packages dev speedo-docker-image; }
