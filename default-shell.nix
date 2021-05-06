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
    echo "You may be interested in the SQL queries :"
    echo "export DEBUG_SPEEDO_SQL=ENABLED"
    echo ""
  '';

}
