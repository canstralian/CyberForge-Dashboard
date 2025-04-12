{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.libxcrypt
    pkgs.libyaml
    pkgs.glibcLocales
  ];
}
