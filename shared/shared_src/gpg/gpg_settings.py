import os

PGP_PEMFILE_KEY = os.environ.get("PGP_PEMFILE_KEY", "voice/gpgprivkey.pem")
PGP_PASSPHRASE_KEY = os.environ.get("PGP_PASSPHRASE_KEY", "voice/gpgprivkeypass")
