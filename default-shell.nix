{ pkgs ? import <nixpkgs> { } }:

with pkgs;

let
  pythonEnv = python3.withPackages (ps:
    with ps; [
      # fire tortilla starlette peewee in github
      mock
      pycurl
      prometheus_client
      psycopg2
      fastapi
      uvicorn
      alembic
      sqlalchemy-utils
      pip
      black
      mypy
      pylint
      flake8
      pytest
      pytestcov
      sphinx
    ]);

in mkShell {
  nativeBuildInputs = [ pythonEnv cacert git wget curl ];
  buildInputs = [ less postgresql pythonEnv ]
    ++ lib.optionals (stdenv.hostPlatform.isLinux) [ # glibcLocales sssd
    ];

  shellHook = ''
    export SSL_CERT_FILE=${cacert}/etc/ssl/certs/ca-bundle.crt
    export PYTHONPATH=$PWD:$PYTHONPATH
    echo ""
    echo "Welcome to the developer shell of submission report"
    echo ""
    echo ""
    echo "You may want to run the postgresql database manually (run all the following commands):"
    echo ""    
    echo "export PGDATABASE=srdb"
    echo "export PGDATA=\$PWD/nix/pgdata"
    echo "export PGHOST=\$PWD/nix/sockets"
    echo "export PGPORT=5433"
    echo "export PGUSER=$USER"
    echo "export PGPASS="
    echo "trap \"\$PWD/nix/client remove\" EXIT"
    echo "\$PWD/nix/client add"
    echo "export PYTHONPATH=\$PWD:\$PYTHONPATH"
    echo "export DEBUG_SUBMISSION_REPORTS_SQL=ENABLED"
    echo ""
  '';

}
